#nullable enable
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace Calcpad.Common.MultLangCode
{
    /// <summary>
    /// Executes code in external languages (Python, Octave, C++, etc.)
    /// </summary>
    public class LanguageExecutor
    {
        private readonly MultLangConfig _config;
        private readonly string _tempDir;
        private ExecutionTracker? _tracker;

        public LanguageExecutor(ExecutionTracker? tracker = null)
        {
            _config = MultLangManager.Config;
            _tempDir = Path.Combine(Path.GetTempPath(), _config.Settings.TempDirectory);
            Directory.CreateDirectory(_tempDir);
            _tracker = tracker;
        }

        /// <summary>
        /// Executes a code block and returns the result
        /// </summary>
        /// <param name="block">Code block to execute</param>
        /// <param name="variables">Variables to inject</param>
        /// <param name="progressCallback">Callback for progress updates (e.g., "Compilando... 5ms")</param>
        public ExecutionResult Execute(CodeBlock block, Dictionary<string, object>? variables = null, Action<string>? progressCallback = null)
        {
            _tracker?.EnterMethod("LanguageExecutor", "Execute", $"Language: {block.Language}");

            _tracker?.ReportStep($"Checking if language '{block.Language}' is configured");
            if (!_config.Languages.TryGetValue(block.Language, out var langDef))
            {
                _tracker?.ReportStep($"ERROR: Language '{block.Language}' not found in config");
                return new ExecutionResult
                {
                    Success = false,
                    Error = $"Language '{block.Language}' not configured"
                };
            }

            _tracker?.ReportStep($"Language configured: Command={langDef.Command}, Extension={langDef.Extension}");

            // Special handling for XAML, WPF, Avalonia, and C#
            var language = block.Language.ToLower();
            if (language == "xaml" || language == "wpf")
            {
                _tracker?.ReportStep("Detected WPF project, routing to ExecuteWpfProject");
                return ExecuteWpfProject(block);
            }
            if (language == "avalonia")
            {
                _tracker?.ReportStep("Detected Avalonia project, routing to ExecuteAvaloniaProject");
                return ExecuteAvaloniaProject(block);
            }
            if (language == "csharp")
            {
                _tracker?.ReportStep("Detected C# project, routing to ExecuteCSharpProject");
                return ExecuteCSharpProject(block);
            }

            _tracker?.ReportStep($"Checking if '{block.Language}' is available in PATH");
            if (!MultLangManager.IsLanguageAvailable(block.Language))
            {
                _tracker?.ReportStep($"ERROR: '{block.Language}' not found in PATH");
                return new ExecutionResult
                {
                    Success = false,
                    Error = $"Language '{block.Language}' not found in PATH. Please install {langDef.Command}"
                };
            }

            _tracker?.ReportStep($"'{block.Language}' is available in PATH");

            // Prepare code with variable injection if needed
            var code = block.Code;
            if (_config.Settings.ShareVariables && variables != null)
            {
                code = InjectVariables(code, variables, langDef);
            }

            // Special handling for CSS, HTML, and TypeScript to work together
            if (language == "css")
            {
                // CSS: Just save to file, don't execute
                var cssPath = Path.Combine(_tempDir, "styles.css");
                File.WriteAllText(cssPath, code);
                return new ExecutionResult
                {
                    Success = true,
                    Output = $"CSS saved to: {cssPath}"
                };
            }

            if (language == "html")
            {
                // HTML: Save and inject references to CSS and JS if they exist
                var htmlPath = Path.Combine(_tempDir, "index.html");
                var modifiedHtml = InjectCssAndJsReferences(code, _tempDir);
                File.WriteAllText(htmlPath, modifiedHtml);

                // Open HTML in default browser
                try
                {
                    var process = new Process
                    {
                        StartInfo = new ProcessStartInfo(htmlPath)
                        {
                            UseShellExecute = true
                        }
                    };
                    process.Start();

                    return new ExecutionResult
                    {
                        Success = true,
                        Output = $"HTML opened in browser: {htmlPath}"
                    };
                }
                catch (Exception ex)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Failed to open HTML: {ex.Message}"
                    };
                }
            }

            if (language == "typescript" || language == "ts")
            {
                // TypeScript: Compile and save .js, then execute
                var tsPath = Path.Combine(_tempDir, "script.ts");
                var jsPath = Path.Combine(_tempDir, "script.js");

                File.WriteAllText(tsPath, code);

                // Execute with ts-node (this will compile and run)
                var result = ExecuteFile(tsPath, langDef, progressCallback);

                // After execution, if successful, try to get the compiled .js
                // (ts-node doesn't output .js by default, but we can compile separately)
                if (result.Success)
                {
                    try
                    {
                        // Compile TypeScript to JavaScript for the HTML to use
                        var tscResult = RunProcess("tsc", $"\"{tsPath}\" --outFile \"{jsPath}\" --target ES2015 --module none", "Compilando TS a JS", progressCallback);
                        if (tscResult.Success)
                        {
                            result.Output += $"\n\nJavaScript compiled to: {jsPath}";
                        }
                    }
                    catch { }
                }

                return result;
            }

            // Write code to temp file
            var fileName = $"calcpad_{Guid.NewGuid():N}{langDef.Extension}";
            var filePath = Path.Combine(_tempDir, fileName);

            try
            {
                File.WriteAllText(filePath, code);

                // Execute
                return ExecuteFile(filePath, langDef, progressCallback);
            }
            finally
            {
                // Cleanup (pero no borrar CSS, HTML, JS para que estén disponibles)
                if (language != "css" && language != "html" && language != "typescript" && language != "ts")
                {
                    if (File.Exists(filePath))
                        File.Delete(filePath);
                }
            }
        }

        /// <summary>
        /// Executes a file with the appropriate interpreter/compiler
        /// </summary>
        private ExecutionResult ExecuteFile(string filePath, LanguageDefinition langDef, Action<string>? progressCallback)
        {
            var result = new ExecutionResult();

            try
            {
                // Compiled languages (C++, C, Rust, etc.)
                if (langDef.RequiresCompilation)
                {
                    return ExecuteCompiledLanguage(filePath, langDef, progressCallback);
                }
                else
                {
                    // Interpreted languages (Python, PowerShell, etc.)
                    return ExecuteInterpretedLanguage(filePath, langDef, progressCallback);
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
            }

            return result;
        }

        /// <summary>
        /// Executes a compiled language (compile then run)
        /// </summary>
        private ExecutionResult ExecuteCompiledLanguage(string filePath, LanguageDefinition langDef, Action<string>? progressCallback)
        {
            var exePath = Path.ChangeExtension(filePath, ".exe");

            try
            {
                // Build compile arguments
                var compileArgs = langDef.CompileArgs
                    .Replace("{input}", $"\"{filePath}\"")
                    .Replace("{output}", $"\"{exePath}\"");

                // If no compile args defined, use default for g++
                if (string.IsNullOrEmpty(compileArgs))
                {
                    compileArgs = $"\"{filePath}\" -o \"{exePath}\"";
                }

                // Step 1: Compile
                var compileResult = RunProcess(langDef.Command, compileArgs, "Compilando", progressCallback);

                // g++ returns exit code 0 on success but may have warnings in stderr
                if (!compileResult.Success && compileResult.ExitCode != 0)
                {
                    // Return compilation error
                    var errorMsg = !string.IsNullOrEmpty(compileResult.Error)
                        ? compileResult.Error
                        : compileResult.Output;
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Compilation failed:\n{errorMsg}"
                    };
                }

                // Verify executable was created
                if (!File.Exists(exePath))
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Compilation succeeded but executable not found at: {exePath}"
                    };
                }

                // Wait a moment for the compiler to fully release the file
                // This prevents "Access denied" errors on Windows
                System.Threading.Thread.Sleep(500);

                // Step 2: Execute compiled binary with retry logic for access denied errors
                ExecutionResult runResult = null;
                int maxRetries = 3;
                int retryCount = 0;

                while (retryCount < maxRetries)
                {
                    try
                    {
                        runResult = RunProcess(exePath, "", "Ejecutando", progressCallback);

                        // If successful or not an access denied error, break
                        if (runResult.Success || !runResult.Error?.Contains("Access") == true)
                            break;

                        // Access denied - wait and retry
                        retryCount++;
                        if (retryCount < maxRetries)
                        {
                            System.Threading.Thread.Sleep(1000);
                        }
                    }
                    catch (System.ComponentModel.Win32Exception ex) when (ex.Message.Contains("Access"))
                    {
                        retryCount++;
                        if (retryCount >= maxRetries)
                        {
                            return new ExecutionResult
                            {
                                Success = false,
                                Error = $"Access denied after {maxRetries} retries. Windows may be blocking the executable. Try disabling antivirus temporarily or adding an exception for the temp folder."
                            };
                        }
                        System.Threading.Thread.Sleep(1000);
                    }
                }

                return runResult;
            }
            finally
            {
                // Cleanup executable
                // Don't delete immediately - may be locked by Windows Defender scan
                // Let Windows clean up temp files automatically
                // if (File.Exists(exePath))
                //     File.Delete(exePath);
            }
        }

        /// <summary>
        /// Executes an interpreted language
        /// </summary>
        private ExecutionResult ExecuteInterpretedLanguage(string filePath, LanguageDefinition langDef, Action<string>? progressCallback)
        {
            var arguments = langDef.RunArgs.Replace("{file}", filePath);

            // If RunArgs is empty, use default
            if (string.IsNullOrEmpty(langDef.RunArgs))
            {
                arguments = $"\"{filePath}\"";
            }

            // Debug: Log the command being executed
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ExecuteInterpretedLanguage: {langDef.Command} {arguments}\n");
            }
            catch { }

            return RunProcess(langDef.Command, arguments, "Ejecutando", progressCallback);
        }

        /// <summary>
        /// Runs a process and captures output
        /// </summary>
        /// <param name="command">Command to execute</param>
        /// <param name="arguments">Arguments for the command</param>
        /// <param name="actionPrefix">Prefix for progress messages (e.g., "Compilando", "Ejecutando")</param>
        /// <param name="progressCallback">Callback to report progress</param>
        private ExecutionResult RunProcess(string command, string arguments, string actionPrefix = "Ejecutando", Action<string>? progressCallback = null)
        {
            // Debug: Log the command being executed
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] RunProcess START: {command} {arguments}\n");
            }
            catch { }

            var result = new ExecutionResult();
            var output = new StringBuilder();
            var error = new StringBuilder();

            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = command,
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    // Don't hide window for Octave GUI - it needs console access
                    CreateNoWindow = !command.Contains("octave-gui", StringComparison.OrdinalIgnoreCase),
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8
                };

                // Add Qt/GTK DLL paths to PATH for compiled executables
                if (command.EndsWith(".exe", StringComparison.OrdinalIgnoreCase))
                {
                    var qtPath = @"C:\msys64\ucrt64\bin";
                    var gtkPath = @"C:\Program Files (x86)\GTK2-Runtime\bin";
                    var currentPath = startInfo.EnvironmentVariables["PATH"] ?? Environment.GetEnvironmentVariable("PATH") ?? "";
                    startInfo.EnvironmentVariables["PATH"] = $"{qtPath};{gtkPath};{currentPath}";
                }

                // Note: QT_QPA_PLATFORM=offscreen can cause issues with Octave and OpenSees
                // Octave needs proper Qt initialization
                // OpenSees uses Tcl/Tk, not Qt - setting offscreen can interfere with output
                if (!command.Contains("octave", StringComparison.OrdinalIgnoreCase) &&
                    !command.Contains("OpenSees", StringComparison.OrdinalIgnoreCase))
                {
                    startInfo.EnvironmentVariables["QT_QPA_PLATFORM"] = "offscreen";
                }

                using var process = new Process { StartInfo = startInfo };

                process.OutputDataReceived += (s, e) =>
                {
                    if (e.Data != null)
                        output.AppendLine(e.Data);
                };

                process.ErrorDataReceived += (s, e) =>
                {
                    if (e.Data != null)
                        error.AppendLine(e.Data);
                };

                // Retry logic for .exe files (Access Denied issues on Windows)
                bool processStarted = false;
                int retryCount = 0;
                int maxRetries = command.EndsWith(".exe", StringComparison.OrdinalIgnoreCase) ? 3 : 1;

                while (!processStarted && retryCount < maxRetries)
                {
                    try
                    {
                        // Log retry attempt
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] Attempting to start process (attempt {retryCount + 1}/{maxRetries}): {command}\n");
                        }
                        catch { }

                        process.Start();
                        processStarted = true;

                        // Log success
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] Process started successfully!\n");
                        }
                        catch { }
                    }
                    catch (System.ComponentModel.Win32Exception ex) when (ex.Message.Contains("Access") && retryCount < maxRetries - 1)
                    {
                        // Access denied on .exe - wait and retry
                        retryCount++;

                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] Access denied! Retry {retryCount}/{maxRetries}. Waiting 1s...\n");
                        }
                        catch { }

                        System.Threading.Thread.Sleep(1000);
                    }
                    catch (Exception ex)
                    {
                        // Log unexpected exception
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] Unexpected exception: {ex.GetType().Name}: {ex.Message}\n");
                        }
                        catch { }

                        throw;
                    }
                }

                if (!processStarted)
                {
                    throw new System.ComponentModel.Win32Exception("Access denied after retries. Windows may be blocking the executable.");
                }
                var startTime = Stopwatch.StartNew();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();

                // Poll with progress updates instead of simple WaitForExit
                const int pollInterval = 50; // Check every 50ms
                var timeout = _config.Settings.Timeout;
                bool completed = false;

                while (!completed && startTime.ElapsedMilliseconds < timeout)
                {
                    completed = process.WaitForExit(pollInterval);

                    // Report progress every poll
                    if (!completed && progressCallback != null)
                    {
                        var elapsedMs = startTime.ElapsedMilliseconds;
                        progressCallback($"{actionPrefix}... {elapsedMs}ms");
                    }
                }

                if (!completed)
                {
                    process.Kill();
                    result.Success = false;
                    result.Error = $"Execution timed out after {_config.Settings.Timeout}ms";
                    return result;
                }

                // Wait for async output/error streams to complete
                // This is necessary because WaitForExit(timeout) can return before async handlers finish
                process.WaitForExit();

                result.Success = process.ExitCode == 0;
                result.Output = output.ToString().TrimEnd();
                result.Error = error.ToString().TrimEnd();
                result.ExitCode = process.ExitCode;

                // Special handling for programs like OpenSees that write everything to stderr
                // If stdout is empty but stderr contains HTML output (not just error messages),
                // extract the HTML content from stderr as the actual output
                if (string.IsNullOrWhiteSpace(result.Output) && !string.IsNullOrWhiteSpace(result.Error) && result.Success)
                {
                    // Check if stderr contains HTML tags (like <p>, <ul>, <li>, etc.)
                    var stderrContent = result.Error;
                    if (stderrContent.Contains("<p>") || stderrContent.Contains("<ul>") ||
                        stderrContent.Contains("<li>") || stderrContent.Contains("<strong>"))
                    {
                        // Extract lines that look like HTML output (not banner/header text)
                        var lines = stderrContent.Split('\n');
                        var htmlOutput = new StringBuilder();
                        foreach (var line in lines)
                        {
                            var trimmed = line.Trim();
                            if (trimmed.StartsWith("<") && !string.IsNullOrWhiteSpace(trimmed))
                            {
                                htmlOutput.AppendLine(trimmed);
                            }
                        }
                        if (htmlOutput.Length > 0)
                        {
                            result.Output = htmlOutput.ToString().TrimEnd();
                            // Keep the banner/non-HTML parts as error for debugging
                            // but don't treat it as an error condition
                        }
                    }
                }

                // Debug: Log execution result
                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] RunProcess RESULT: ExitCode={process.ExitCode}, Success={result.Success}\n");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] RunProcess OUTPUT: {result.Output.Substring(0, Math.Min(200, result.Output.Length))}\n");
                    if (!string.IsNullOrEmpty(result.Error))
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] RunProcess ERROR: {result.Error.Substring(0, Math.Min(200, result.Error.Length))}\n");
                }
                catch { }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Error = ex.Message;
            }

            return result;
        }

        /// <summary>
        /// Injects CSS and JS references into HTML if the files exist
        /// </summary>
        private string InjectCssAndJsReferences(string html, string tempDir)
        {
            var cssPath = Path.Combine(tempDir, "styles.css");
            var jsPath = Path.Combine(tempDir, "script.js");

            var injections = new StringBuilder();

            // Inject CSS reference if file exists
            if (File.Exists(cssPath))
            {
                injections.AppendLine("    <link rel=\"stylesheet\" href=\"styles.css\">");
            }

            // Inject JS reference if file exists
            if (File.Exists(jsPath))
            {
                injections.AppendLine("    <script src=\"script.js\"></script>");
            }

            // If nothing to inject, return original HTML
            if (injections.Length == 0)
                return html;

            // Try to inject before </head> tag
            if (html.Contains("</head>", StringComparison.OrdinalIgnoreCase))
            {
                var closeHeadIndex = html.IndexOf("</head>", StringComparison.OrdinalIgnoreCase);
                return html.Insert(closeHeadIndex, injections.ToString());
            }

            // If no </head>, try to inject after <head>
            if (html.Contains("<head>", StringComparison.OrdinalIgnoreCase))
            {
                var openHeadIndex = html.IndexOf("<head>", StringComparison.OrdinalIgnoreCase) + 6;
                return html.Insert(openHeadIndex, "\n" + injections.ToString());
            }

            // If no <head> at all, inject at the beginning
            return injections.ToString() + html;
        }

        /// <summary>
        /// Injects Calcpad variables into the code
        /// </summary>
        private string InjectVariables(string code, Dictionary<string, object> variables, LanguageDefinition langDef)
        {
            var sb = new StringBuilder();

            // Add variable declarations at the top
            sb.AppendLine($"{langDef.CommentPrefix} Variables from Calcpad:");

            foreach (var (name, value) in variables)
            {
                var varLine = langDef.Extension switch
                {
                    ".py" => $"{name} = {FormatValue(value)}",
                    ".m" => $"{name} = {FormatValue(value)};",
                    ".cpp" => $"auto {name} = {FormatValue(value)};",
                    ".jl" => $"{name} = {FormatValue(value)}",
                    ".R" => $"{name} <- {FormatValue(value)}",
                    _ => $"{name} = {FormatValue(value)}"
                };
                sb.AppendLine(varLine);
            }

            sb.AppendLine();
            sb.Append(code);

            return sb.ToString();
        }

        /// <summary>
        /// Formats a value for the target language
        /// </summary>
        private static string FormatValue(object value)
        {
            return value switch
            {
                double d => d.ToString(System.Globalization.CultureInfo.InvariantCulture),
                int i => i.ToString(),
                bool b => b.ToString().ToLower(),
                string s => $"\"{s}\"",
                _ => value.ToString() ?? "null"
            };
        }

        /// <summary>
        /// Executes a C# console project
        /// </summary>
        private ExecutionResult ExecuteCSharpProject(CodeBlock block)
        {
            var projectName = $"CSharpTemp_{Guid.NewGuid():N}";
            var projectDir = Path.Combine(_tempDir, projectName);

            try
            {
                // Create console project
                var createResult = RunProcess("dotnet", $"new console -n {projectName} -o \"{projectDir}\"");
                if (!createResult.Success)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Failed to create C# project:\n{createResult.Error}"
                    };
                }

                // Modify .csproj to disable implicit usings and top-level statements
                var csprojPath = Path.Combine(projectDir, $"{projectName}.csproj");
                if (File.Exists(csprojPath))
                {
                    var csprojContent = File.ReadAllText(csprojPath);
                    csprojContent = csprojContent.Replace("</PropertyGroup>",
                        "    <ImplicitUsings>disable</ImplicitUsings>\n  </PropertyGroup>");
                    File.WriteAllText(csprojPath, csprojContent);
                }

                // Replace Program.cs with user code
                var programCsPath = Path.Combine(projectDir, "Program.cs");
                File.WriteAllText(programCsPath, block.Code);

                // Build project
                var buildResult = RunProcess("dotnet", $"build \"{projectDir}\" --configuration Release");
                if (!buildResult.Success || buildResult.ExitCode != 0)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Build failed:\n{buildResult.Error}\n{buildResult.Output}"
                    };
                }

                // Run project
                var runResult = RunProcess("dotnet", $"run --project \"{projectDir}\" --configuration Release --no-build");

                return new ExecutionResult
                {
                    Success = runResult.ExitCode == 0,
                    Output = runResult.Output,
                    Error = runResult.Error,
                    ExitCode = runResult.ExitCode
                };
            }
            catch (Exception ex)
            {
                return new ExecutionResult
                {
                    Success = false,
                    Error = $"C# execution failed: {ex.Message}"
                };
            }
            finally
            {
                // Cleanup project directory
                try
                {
                    if (Directory.Exists(projectDir))
                        Directory.Delete(projectDir, true);
                }
                catch { }
            }
        }

        /// <summary>
        /// Executes an Avalonia UI project
        /// </summary>
        private ExecutionResult ExecuteAvaloniaProject(CodeBlock block)
        {
            _tracker?.ReportStep("Executing Avalonia/C# code");
            var fileName = $"temp_avalonia_{Guid.NewGuid():N}";
            var sourceFile = Path.Combine(_tempDir, fileName + ".cs");
            var exeFile = Path.Combine(_tempDir, fileName + ".exe");

            try
            {
                // Write user code to file
                _tracker?.ReportStep($"Writing code to {sourceFile}");
                File.WriteAllText(sourceFile, block.Code);

                // Compile using C# compiler (simple console app approach)
                _tracker?.ReportStep("Compiling C# code");
                var compileArgs = $"/out:\"{exeFile}\" \"{sourceFile}\"";

                // Try csc first (if available)
                var compileResult = RunProcess("csc", compileArgs);

                if (!compileResult.Success || compileResult.ExitCode != 0)
                {
                    // Fallback to dotnet if csc fails
                    _tracker?.ReportStep("csc not found, trying dotnet build");

                    // Create a minimal .csproj for dotnet
                    var projectFile = Path.Combine(_tempDir, fileName + ".csproj");
                    var csprojContent = $@"<Project Sdk=""Microsoft.NET.Sdk"">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include=""{fileName}.cs"" />
  </ItemGroup>
</Project>";
                    File.WriteAllText(projectFile, csprojContent);

                    compileResult = RunProcess("dotnet", $"build \"{projectFile}\" -c Release -o \"{_tempDir}\"");

                    if (!compileResult.Success || compileResult.ExitCode != 0)
                    {
                        return new ExecutionResult
                        {
                            Success = false,
                            Error = $"Compilation failed:\n\n{compileResult.Error}\n\n{compileResult.Output}"
                        };
                    }

                    exeFile = Path.Combine(_tempDir, fileName + ".exe");
                }

                // Run the compiled executable
                _tracker?.ReportStep("Running compiled program");
                var runResult = RunProcess(exeFile, "", "Ejecutando");

                return new ExecutionResult
                {
                    Success = true,
                    Output = $"{runResult.Output}\n\n{runResult.Error}".Trim()
                };
            }
            catch (Exception ex)
            {
                _tracker?.ReportStep($"ERROR in execution: {ex.Message}");
                return new ExecutionResult
                {
                    Success = false,
                    Error = $"Execution failed: {ex.Message}"
                };
            }
            finally
            {
                // Clean up
                try
                {
                    if (File.Exists(sourceFile)) File.Delete(sourceFile);
                    if (File.Exists(exeFile)) File.Delete(exeFile);
                }
                catch { }
            }
        }

        /// <summary>
        /// Executes a WPF/XAML project with automatic screenshot
        /// </summary>
        private ExecutionResult ExecuteWpfProject(CodeBlock block)
        {
            var projectName = $"WpfTemp_{Guid.NewGuid():N}";
            var projectDir = Path.Combine(_tempDir, projectName);

            try
            {
                // Create WPF project
                var createResult = RunProcess("dotnet", $"new wpf -n {projectName} -o \"{projectDir}\"");
                if (!createResult.Success)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Failed to create WPF project:\n{createResult.Error}"
                    };
                }

                // Parse XAML and C# code (for #wpf)
                string xamlCode;
                string? csharpCode = null;

                var language = block.Language.ToLower();
                if (language == "wpf")
                {
                    // Parse block to extract XAML and C# sections
                    (xamlCode, csharpCode) = ParseWpfBlock(block.Code);
                }
                else
                {
                    // Just XAML
                    xamlCode = block.Code.Trim();
                }

                // Replace MainWindow.xaml
                // Ensure x:Class attribute exists
                if (!xamlCode.Contains("x:Class="))
                {
                    xamlCode = xamlCode.Replace("<Window ", $"<Window x:Class=\"{projectName}.MainWindow\" ");
                }
                var mainWindowXamlPath = Path.Combine(projectDir, "MainWindow.xaml");
                File.WriteAllText(mainWindowXamlPath, xamlCode);

                // If C# code provided, handle based on whether it has Main()
                if (!string.IsNullOrWhiteSpace(csharpCode))
                {
                    var hasMainMethod = csharpCode.Contains("static void Main");

                    if (hasMainMethod)
                    {
                        // Transform the code: extract Main() body and run it in MainWindow constructor
                        var transformedCode = TransformMainToConstructor(csharpCode, projectName);
                        var mainWindowCsPath = Path.Combine(projectDir, "MainWindow.xaml.cs");
                        File.WriteAllText(mainWindowCsPath, transformedCode);
                    }
                    else
                    {
                        // No Main method, safe to put in MainWindow.xaml.cs
                        var mainWindowCsPath = Path.Combine(projectDir, "MainWindow.xaml.cs");
                        File.WriteAllText(mainWindowCsPath, csharpCode);
                    }
                }

                // DON'T modify App.xaml.cs - leave the window open for user interaction
                // (Opción A: Usuario puede interactuar con la ventana WPF)

                // Build project
                var buildResult = RunProcess("dotnet", $"build \"{projectDir}\" --configuration Release");
                if (!buildResult.Success || buildResult.ExitCode != 0)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"Build failed:\n{buildResult.Error}\n{buildResult.Output}"
                    };
                }

                // Launch WPF application in the background (user can interact)
                var exePath = Path.Combine(projectDir, "bin", "Release", "net10.0-windows", $"{projectName}.exe");
                if (!File.Exists(exePath))
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Error = $"WPF executable not found at: {exePath}"
                    };
                }

                // Start the WPF app without waiting (user can interact)
                var startInfo = new ProcessStartInfo
                {
                    FileName = exePath,
                    UseShellExecute = true,  // Allow window to show
                    CreateNoWindow = false,  // Show the window
                    WindowStyle = ProcessWindowStyle.Normal
                };

                Process.Start(startInfo);

                return new ExecutionResult
                {
                    Success = true,
                    Output = $"WPF application launched successfully. You can interact with the window.\n(Close the window manually when done)"
                };
            }
            catch (Exception ex)
            {
                return new ExecutionResult
                {
                    Success = false,
                    Error = $"WPF execution failed: {ex.Message}"
                };
            }
            finally
            {
                // DON'T cleanup project directory for WPF - the app is still running
                // User will close it manually, temp files will be cleaned by OS eventually
                // (Para Opción A: la ventana WPF sigue abierta, no podemos borrar los archivos)
            }
        }

        /// <summary>
        /// Parses a #wpf block to extract XAML and C# sections
        /// </summary>
        private (string xaml, string csharp) ParseWpfBlock(string code)
        {
            var trimmedCode = code.Trim();

            // Auto-detect if code is pure C# (no XAML)
            var hasXmlTags = trimmedCode.Contains("<Window") || trimmedCode.Contains("<UserControl") ||
                            trimmedCode.Contains("<?xml") || trimmedCode.Contains("<Application");
            var hasCsharpKeywords = trimmedCode.Contains("using System") || trimmedCode.Contains("class ") ||
                                   trimmedCode.Contains("namespace ") || trimmedCode.Contains("static void Main");

            // If it's pure C# without XAML, generate a default XAML and return C# code
            if (!hasXmlTags && hasCsharpKeywords)
            {
                var defaultXaml = @"<Window xmlns=""http://schemas.microsoft.com/winfx/2006/xaml/presentation""
        xmlns:x=""http://schemas.microsoft.com/winfx/2006/xaml""
        Title=""WPF Application"" Height=""450"" Width=""800"">
    <Grid>
        <TextBlock Text=""WPF Application Running - Check Console Output""
                   HorizontalAlignment=""Center""
                   VerticalAlignment=""Center""
                   FontSize=""16""/>
    </Grid>
</Window>";
                return (defaultXaml, trimmedCode);
            }

            var lines = code.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            var xamlBuilder = new StringBuilder();
            var csharpBuilder = new StringBuilder();
            var currentSection = "xaml"; // Default to XAML first

            foreach (var line in lines)
            {
                var trimmed = line.Trim();

                // Detect section markers
                if (trimmed.StartsWith("// C#", StringComparison.OrdinalIgnoreCase) ||
                    trimmed.StartsWith("//C#", StringComparison.OrdinalIgnoreCase) ||
                    trimmed.Equals("---CSHARP---", StringComparison.OrdinalIgnoreCase))
                {
                    currentSection = "csharp";
                    continue;
                }
                else if (trimmed.StartsWith("<!-- XAML", StringComparison.OrdinalIgnoreCase) ||
                         trimmed.Equals("---XAML---", StringComparison.OrdinalIgnoreCase))
                {
                    currentSection = "xaml";
                    continue;
                }

                // Add to appropriate section
                if (currentSection == "xaml")
                    xamlBuilder.AppendLine(line);
                else
                    csharpBuilder.AppendLine(line);
            }

            return (xamlBuilder.ToString().Trim(), csharpBuilder.ToString().Trim());
        }

        /// <summary>
        /// Transforms user code with Main() into MainWindow code-behind
        /// </summary>
        private string TransformMainToConstructor(string csharpCode, string projectName)
        {
            // Extract using statements
            var usingStatements = new List<string>();
            var lines = csharpCode.Split(new[] { '\r', '\n' }, StringSplitOptions.None);

            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (trimmed.StartsWith("using ") && trimmed.EndsWith(";"))
                {
                    usingStatements.Add(line);
                }
            }

            // Extract Main() method body
            var mainMethodPattern = @"static\s+void\s+Main\s*\([^)]*\)\s*\{";
            var match = System.Text.RegularExpressions.Regex.Match(csharpCode, mainMethodPattern);

            if (!match.Success)
            {
                // Fallback: just wrap the whole code
                return GenerateMainWindowCodeBehind(projectName, usingStatements, csharpCode);
            }

            // Find the body of Main() method
            var startIndex = match.Index + match.Length;
            var braceCount = 1;
            var endIndex = startIndex;

            for (int i = startIndex; i < csharpCode.Length && braceCount > 0; i++)
            {
                if (csharpCode[i] == '{') braceCount++;
                else if (csharpCode[i] == '}') braceCount--;
                endIndex = i;
            }

            var mainBody = csharpCode.Substring(startIndex, endIndex - startIndex).Trim();

            return GenerateMainWindowCodeBehind(projectName, usingStatements, mainBody);
        }

        private string GenerateMainWindowCodeBehind(string projectName, List<string> usingStatements, string mainBody)
        {
            var usingsText = string.Join("\n", usingStatements);
            if (!usingsText.Contains("using System.Windows"))
            {
                usingsText = "using System.Windows;\n" + usingsText;
            }

            return $@"{usingsText}

namespace {projectName}
{{
    public partial class MainWindow : Window
    {{
        public MainWindow()
        {{
            InitializeComponent();

            // Execute user code
            ExecuteUserCode();
        }}

        private void ExecuteUserCode()
        {{
            {mainBody}
        }}
    }}
}}";
        }

        /// <summary>
        /// Modifies App.xaml.cs to automatically take screenshot and exit
        /// </summary>
        private void ModifyAppXamlCs(string projectDir)
        {
            var appXamlCsPath = Path.Combine(projectDir, "App.xaml.cs");

            var appCode = @"using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace " + Path.GetFileName(projectDir) + @"
{
    public partial class App : Application
    {
        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Wait for window to render
            await Task.Delay(2000);

            if (MainWindow != null)
            {
                try
                {
                    // Take screenshot
                    var screenshot = CaptureWindow(MainWindow);
                    var screenshotPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, ""../../../screenshot.png"");
                    SaveImage(screenshot, screenshotPath);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($""Screenshot failed: {ex.Message}"");
                }
            }

            // Exit application
            Shutdown();
        }

        private RenderTargetBitmap CaptureWindow(Window window)
        {
            var width = (int)window.ActualWidth;
            var height = (int)window.ActualHeight;

            var renderBitmap = new RenderTargetBitmap(
                width,
                height,
                96,
                96,
                PixelFormats.Pbgra32);

            renderBitmap.Render(window);
            return renderBitmap;
        }

        private void SaveImage(RenderTargetBitmap bitmap, string path)
        {
            var encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bitmap));

            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                Directory.CreateDirectory(directory);

            using var stream = File.Create(path);
            encoder.Save(stream);
        }
    }
}";

            File.WriteAllText(appXamlCsPath, appCode);
        }

        /// <summary>
        /// Saves generated web files (CSS, HTML, TypeScript, JavaScript) to a specified directory
        /// </summary>
        /// <param name="destinationDir">Directory where files should be saved</param>
        /// <returns>List of saved file paths</returns>
        public List<string> SaveWebFilesToDirectory(string destinationDir)
        {
            var savedFiles = new List<string>();

            try
            {
                // Create destination directory if it doesn't exist
                Directory.CreateDirectory(destinationDir);

                // Files to copy from temp directory
                var filesToCopy = new[]
                {
                    "styles.css",
                    "script.ts",
                    "script.js",
                    "index.html"
                };

                foreach (var fileName in filesToCopy)
                {
                    var sourcePath = Path.Combine(_tempDir, fileName);
                    if (File.Exists(sourcePath))
                    {
                        var destPath = Path.Combine(destinationDir, fileName);
                        File.Copy(sourcePath, destPath, overwrite: true);
                        savedFiles.Add(destPath);
                    }
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to save web files: {ex.Message}", ex);
            }

            return savedFiles;
        }

        /// <summary>
        /// Gets the path to the temporary directory where generated files are stored
        /// </summary>
        public string GetTempDirectory()
        {
            return _tempDir;
        }

        /// <summary>
        /// Checks if web files (CSS, HTML, JS) exist in the temporary directory
        /// </summary>
        public Dictionary<string, bool> GetGeneratedWebFilesStatus()
        {
            return new Dictionary<string, bool>
            {
                ["styles.css"] = File.Exists(Path.Combine(_tempDir, "styles.css")),
                ["script.ts"] = File.Exists(Path.Combine(_tempDir, "script.ts")),
                ["script.js"] = File.Exists(Path.Combine(_tempDir, "script.js")),
                ["index.html"] = File.Exists(Path.Combine(_tempDir, "index.html"))
            };
        }

        /// <summary>
        /// Cleans up temporary files
        /// </summary>
        public void Cleanup()
        {
            try
            {
                if (Directory.Exists(_tempDir))
                {
                    Directory.Delete(_tempDir, true);
                }
            }
            catch { }
        }
    }

    /// <summary>
    /// Result of code execution
    /// </summary>
    public class ExecutionResult
    {
        public bool Success { get; set; }
        public string Output { get; set; } = string.Empty;
        public string Error { get; set; } = string.Empty;
        public int ExitCode { get; set; }

        /// <summary>
        /// Gets formatted output for display
        /// </summary>
        public string GetDisplayOutput()
        {
            if (!Success && !string.IsNullOrEmpty(Error))
                return $"Error: {Error}";

            return Output;
        }
    }
}
