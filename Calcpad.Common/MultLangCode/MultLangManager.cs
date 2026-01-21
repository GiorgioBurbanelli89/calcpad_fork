using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace Calcpad.Common.MultLangCode
{
    /// <summary>
    /// Main manager for multi-language code execution
    /// Works in both WPF and CLI environments - ALWAYS synchronized via external JSON
    /// </summary>
    public static class MultLangManager
    {
        private static MultLangConfig _config;
        private static readonly object _lock = new();
        private static readonly Dictionary<string, bool> _availableLanguages = new();
        private static string _configFilePath;
        private static DateTime _lastConfigLoad;

        /// <summary>
        /// Path to the shared MultLangConfig.json file
        /// </summary>
        public static string ConfigFilePath
        {
            get
            {
                if (string.IsNullOrEmpty(_configFilePath))
                    _configFilePath = FindConfigFile();
                return _configFilePath;
            }
            set => _configFilePath = value;
        }

        /// <summary>
        /// Gets the loaded configuration (auto-reloads if file changed)
        /// </summary>
        public static MultLangConfig Config
        {
            get
            {
                lock (_lock)
                {
                    if (_config == null || ConfigFileChanged())
                        LoadConfig();
                    return _config;
                }
            }
        }

        /// <summary>
        /// Checks if config file has been modified since last load
        /// </summary>
        private static bool ConfigFileChanged()
        {
            if (string.IsNullOrEmpty(ConfigFilePath) || !File.Exists(ConfigFilePath))
                return false;

            var lastWrite = File.GetLastWriteTime(ConfigFilePath);
            return lastWrite > _lastConfigLoad;
        }

        /// <summary>
        /// Finds the MultLangConfig.json file in known locations
        /// Priority: 1) Project root, 2) Next to executable, 3) Common AppData
        /// </summary>
        private static string FindConfigFile()
        {
            var possiblePaths = new List<string>();

            // 1. PROJECT ROOT (search upwards from assembly location for .sln file)
            var projectRoot = FindProjectRoot();
            if (!string.IsNullOrEmpty(projectRoot))
            {
                possiblePaths.Add(Path.Combine(projectRoot, "MultLangConfig.json"));
                possiblePaths.Add(Path.Combine(projectRoot, "Calcpad.Common", "MultLangCode", "MultLangConfig.json"));
            }

            // 2. Next to the Calcpad.Common.dll (fallback for deployed apps)
            var assemblyDir = Path.GetDirectoryName(typeof(MultLangManager).Assembly.Location);
            if (!string.IsNullOrEmpty(assemblyDir))
            {
                possiblePaths.Add(Path.Combine(assemblyDir, "MultLangConfig.json"));
                possiblePaths.Add(Path.Combine(assemblyDir, "MultLangCode", "MultLangConfig.json"));
            }

            // 3. Current working directory
            possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangConfig.json"));
            possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangCode", "MultLangConfig.json"));

            // 4. Common AppData (for system-wide installations)
            var commonAppData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
            possiblePaths.Add(Path.Combine(commonAppData, "Calcpad", "MultLangConfig.json"));

            // Return first existing file
            foreach (var path in possiblePaths)
            {
                if (File.Exists(path))
                {
                    LogDebug($"Found config at: {path}");
                    return path;
                }
            }

            // If none found, create in project root if we can find it, otherwise next to assembly
            var defaultPath = !string.IsNullOrEmpty(projectRoot)
                ? Path.Combine(projectRoot, "MultLangConfig.json")
                : possiblePaths.FirstOrDefault() ?? "MultLangConfig.json";

            LogDebug($"No config found. Will create at: {defaultPath}");
            return defaultPath;
        }

        /// <summary>
        /// Finds the project root by searching for directory containing both Calcpad.Common and Calcpad.Cli
        /// </summary>
        private static string FindProjectRoot()
        {
            try
            {
                var assemblyDir = Path.GetDirectoryName(typeof(MultLangManager).Assembly.Location);
                if (string.IsNullOrEmpty(assemblyDir))
                    return null;

                var currentDir = new DirectoryInfo(assemblyDir);

                // Search upwards max 10 levels
                for (int i = 0; i < 10 && currentDir != null; i++)
                {
                    // Check if this directory contains both Calcpad.Common and Calcpad.Cli subdirectories
                    // This indicates the project root
                    var hasCommon = Directory.Exists(Path.Combine(currentDir.FullName, "Calcpad.Common"));
                    var hasCli = Directory.Exists(Path.Combine(currentDir.FullName, "Calcpad.Cli"));

                    if (hasCommon && hasCli)
                    {
                        LogDebug($"Found project root (has Calcpad.Common + Calcpad.Cli): {currentDir.FullName}");
                        return currentDir.FullName;
                    }

                    currentDir = currentDir.Parent;
                }
            }
            catch (Exception ex)
            {
                LogDebug($"Error finding project root: {ex.Message}");
            }

            return null;
        }

        /// <summary>
        /// Logs debug messages to temp file
        /// </summary>
        private static void LogDebug(string message)
        {
            try
            {
                var logPath = Path.Combine(Path.GetTempPath(), "calcpad_multilang_debug.txt");
                File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] {message}\n");
            }
            catch { }
        }

        /// <summary>
        /// Loads configuration from external JSON file
        /// </summary>
        public static void LoadConfig()
        {
            lock (_lock)
            {
                try
                {
                    var logPath = Path.Combine(Path.GetTempPath(), "calcpad_multilang_debug.txt");
                    File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Looking for config at: {ConfigFilePath}\n");

                    if (File.Exists(ConfigFilePath))
                    {
                        var json = File.ReadAllText(ConfigFilePath);
                        _config = JsonSerializer.Deserialize<MultLangConfig>(json) ?? CreateDefaultConfig();
                        _lastConfigLoad = DateTime.Now;
                        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Config loaded. Languages count: {_config.Languages.Count}\n");
                        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Has csharp: {_config.Languages.ContainsKey("csharp")}\n");
                        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Languages: {string.Join(", ", _config.Languages.Keys)}\n");
                    }
                    else
                    {
                        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Config file NOT found. Using default config.\n");
                        // Create default config file
                        _config = CreateDefaultConfig();
                        SaveConfig();
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading MultLangConfig.json: {ex.Message}");
                    _config = CreateDefaultConfig();
                }
            }
        }

        /// <summary>
        /// Saves current configuration to JSON file
        /// </summary>
        public static void SaveConfig()
        {
            try
            {
                var dir = Path.GetDirectoryName(ConfigFilePath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                var options = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(_config, options);
                File.WriteAllText(ConfigFilePath, json);
                _lastConfigLoad = DateTime.Now;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error saving MultLangConfig.json: {ex.Message}");
            }
        }

        /// <summary>
        /// Creates default configuration with common languages
        /// </summary>
        private static MultLangConfig CreateDefaultConfig()
        {
            return new MultLangConfig
            {
                Languages = new Dictionary<string, LanguageDefinition>
                {
                    ["python"] = new LanguageDefinition
                    {
                        Command = "python",
                        Extension = ".py",
                        Directive = "@{python}",
                        EndDirective = "@{end python}",
                        CommentPrefix = "#",
                        Keywords = new[] { "def", "class", "import", "from", "if", "elif", "else", "for", "while", "try", "except", "with", "return", "yield", "lambda", "and", "or", "not", "in", "is", "True", "False", "None" },
                        Builtins = new[] { "print", "len", "range", "str", "int", "float", "list", "dict", "set", "tuple", "open", "input", "type", "isinstance" }
                    },
                    ["powershell"] = new LanguageDefinition
                    {
                        Command = "pwsh",
                        Extension = ".ps1",
                        Directive = "@{powershell}",
                        EndDirective = "@{end powershell}",
                        CommentPrefix = "#",
                        Keywords = new[] { "function", "param", "if", "else", "elseif", "switch", "foreach", "for", "while", "do", "try", "catch", "finally", "return", "throw" },
                        Builtins = new[] { "Write-Host", "Write-Output", "Get-Content", "Set-Content", "Get-Item", "Set-Item", "New-Item", "Remove-Item" }
                    },
                    ["octave"] = new LanguageDefinition
                    {
                        Command = "octave-gui",
                        Extension = ".m",
                        Directive = "@{octave}",
                        EndDirective = "@{end octave}",
                        CommentPrefix = "%",
                        Keywords = new[] { "function", "end", "if", "else", "elseif", "endif", "for", "endfor", "while", "endwhile", "switch", "case", "otherwise", "return" },
                        Builtins = new[] { "disp", "printf", "fprintf", "plot", "zeros", "ones", "eye", "linspace", "sin", "cos", "sqrt", "abs" },
                        RunArgs = "--no-gui --quiet \"{file}\""
                    },
                    ["julia"] = new LanguageDefinition
                    {
                        Command = "julia",
                        Extension = ".jl",
                        Directive = "@{julia}",
                        EndDirective = "@{end julia}",
                        CommentPrefix = "#",
                        Keywords = new[] { "function", "end", "if", "else", "elseif", "for", "while", "try", "catch", "finally", "return", "struct", "module", "using", "import" },
                        Builtins = new[] { "println", "print", "length", "size", "typeof", "convert", "parse", "string" }
                    },
                    ["cpp"] = new LanguageDefinition
                    {
                        Command = "g++",
                        Extension = ".cpp",
                        Directive = "@{cpp}",
                        EndDirective = "@{end cpp}",
                        CommentPrefix = "//",
                        Keywords = new[] { "int", "double", "float", "char", "void", "bool", "if", "else", "for", "while", "do", "switch", "case", "return", "class", "struct", "public", "private", "protected" },
                        Builtins = new[] { "cout", "cin", "endl", "printf", "scanf", "malloc", "free", "new", "delete" },
                        RequiresCompilation = true,
                        CompileArgs = "{input} -o {output}"
                    },
                    ["bash"] = new LanguageDefinition
                    {
                        Command = "bash",
                        Extension = ".sh",
                        Directive = "@{bash}",
                        EndDirective = "@{end bash}",
                        CommentPrefix = "#",
                        Keywords = new[] { "if", "then", "else", "elif", "fi", "for", "do", "done", "while", "until", "case", "esac", "function", "return", "exit" },
                        Builtins = new[] { "echo", "read", "printf", "cd", "pwd", "ls", "cat", "grep", "sed", "awk" }
                    },
                    ["cmd"] = new LanguageDefinition
                    {
                        Command = "cmd",
                        Extension = ".bat",
                        Directive = "@{cmd}",
                        EndDirective = "@{end cmd}",
                        CommentPrefix = "REM",
                        Keywords = new[] { "if", "else", "for", "do", "goto", "call", "exit", "set", "setlocal", "endlocal" },
                        Builtins = new[] { "echo", "dir", "cd", "copy", "move", "del", "mkdir", "rmdir", "type" }
                    },
                    ["r"] = new LanguageDefinition
                    {
                        Command = "Rscript",
                        Extension = ".R",
                        Directive = "@{r}",
                        EndDirective = "@{end r}",
                        CommentPrefix = "#",
                        Keywords = new[] { "function", "if", "else", "for", "while", "repeat", "break", "next", "return", "in", "TRUE", "FALSE", "NULL", "NA" },
                        Builtins = new[] { "print", "cat", "paste", "c", "list", "data.frame", "matrix", "length", "sum", "mean" }
                    },
                    ["markdown"] = new LanguageDefinition
                    {
                        Command = "",
                        Extension = ".md",
                        Directive = "@{markdown}",
                        EndDirective = "@{end markdown}",
                        CommentPrefix = "",
                        Keywords = Array.Empty<string>(),
                        Builtins = Array.Empty<string>()
                    },
                    ["csharp"] = new LanguageDefinition
                    {
                        Command = "dotnet",
                        Extension = ".cs",
                        Directive = "@{csharp}",
                        EndDirective = "@{end csharp}",
                        CommentPrefix = "//",
                        Keywords = new[] { "class", "using", "namespace", "public", "private", "static", "void", "int", "string", "double", "bool", "if", "else", "for", "while", "foreach", "return", "new", "var" },
                        Builtins = new[] { "Console", "WriteLine", "ReadLine", "Parse", "ToString", "Length", "Count", "Add", "Remove" },
                        RequiresCompilation = true
                    },
                    ["xaml"] = new LanguageDefinition
                    {
                        Command = "dotnet",
                        Extension = ".xaml",
                        Directive = "@{xaml}",
                        EndDirective = "@{end xaml}",
                        CommentPrefix = "<!--",
                        Keywords = Array.Empty<string>(),
                        Builtins = Array.Empty<string>(),
                        RequiresCompilation = true
                    },
                    ["wpf"] = new LanguageDefinition
                    {
                        Command = "dotnet",
                        Extension = ".xaml",
                        Directive = "@{wpf}",
                        EndDirective = "@{end wpf}",
                        CommentPrefix = "<!--",
                        Keywords = Array.Empty<string>(),
                        Builtins = Array.Empty<string>(),
                        RequiresCompilation = true
                    },
                    ["c"] = new LanguageDefinition
                    {
                        Command = "gcc",
                        Extension = ".c",
                        Directive = "@{c}",
                        EndDirective = "@{end c}",
                        CommentPrefix = "//",
                        Keywords = new[] { "int", "float", "double", "char", "void", "if", "else", "for", "while", "do", "switch", "case", "return", "struct", "typedef", "sizeof", "const", "static", "extern" },
                        Builtins = new[] { "printf", "scanf", "malloc", "free", "sizeof", "strlen", "strcpy", "strcmp" },
                        RequiresCompilation = true,
                        CompileArgs = "{input} -o {output}"
                    },
                    ["fortran"] = new LanguageDefinition
                    {
                        Command = "gfortran",
                        Extension = ".f90",
                        Directive = "@{fortran}",
                        EndDirective = "@{end fortran}",
                        CommentPrefix = "!",
                        Keywords = new[] { "program", "end", "implicit", "none", "integer", "real", "double", "character", "if", "then", "else", "do", "while", "subroutine", "function", "return", "call" },
                        Builtins = new[] { "print", "write", "read", "allocate", "deallocate" },
                        RequiresCompilation = true,
                        CompileArgs = "{input} -o {output}"
                    }
                },
                Settings = new MultLangSettings
                {
                    Timeout = 30000,
                    MaxOutputLines = 1000,
                    TempDirectory = "temp_multilang",
                    ShareVariables = true
                }
            };
        }

        /// <summary>
        /// Adds a new language to the configuration
        /// </summary>
        public static void AddLanguage(string name, LanguageDefinition definition)
        {
            Config.Languages[name.ToLower()] = definition;
            SaveConfig();
            _availableLanguages[name.ToLower()] = IsCommandAvailable(definition.Command);
        }

        /// <summary>
        /// Removes a language from the configuration
        /// </summary>
        public static void RemoveLanguage(string name)
        {
            var key = name.ToLower();
            if (Config.Languages.ContainsKey(key))
            {
                Config.Languages.Remove(key);
                SaveConfig();
                _availableLanguages.Remove(key);
            }
        }

        /// <summary>
        /// Checks which configured languages are available in PATH
        /// </summary>
        private static void CheckAvailableLanguages()
        {
            // Load config if not already loaded
            if (_config == null)
                LoadConfig();

            _availableLanguages.Clear();
            foreach (var (name, lang) in _config!.Languages)
            {
                _availableLanguages[name] = IsCommandAvailable(lang.Command);
            }
        }

        /// <summary>
        /// Checks if a command is available in PATH
        /// </summary>
        public static bool IsCommandAvailable(string command)
        {
            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = command,
                    Arguments = "--version",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(startInfo);
                process?.WaitForExit(5000);
                return process != null;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Gets whether a specific language is available
        /// </summary>
        public static bool IsLanguageAvailable(string languageName)
        {
            if (_availableLanguages.Count == 0)
                CheckAvailableLanguages();

            return _availableLanguages.TryGetValue(languageName.ToLower(), out var available) && available;
        }

        /// <summary>
        /// Gets all available languages
        /// </summary>
        public static IEnumerable<string> GetAvailableLanguages()
        {
            if (_availableLanguages.Count == 0)
                CheckAvailableLanguages();

            return _availableLanguages.Where(kv => kv.Value).Select(kv => kv.Key);
        }

        /// <summary>
        /// Detects if a line contains a language directive
        /// </summary>
        public static (bool found, string languageName, bool isEnd) DetectDirective(string line)
        {
            var trimmed = line.Trim();

            foreach (var (name, lang) in Config.Languages)
            {
                if (trimmed.Equals(lang.Directive, StringComparison.OrdinalIgnoreCase))
                    return (true, name, false);

                if (trimmed.Equals(lang.EndDirective, StringComparison.OrdinalIgnoreCase))
                    return (true, name, true);
            }

            return (false, string.Empty, false);
        }

        /// <summary>
        /// Extracts code blocks for each language from Calcpad code
        /// </summary>
        public static Dictionary<string, List<CodeBlock>> ExtractCodeBlocks(string code)
        {
            var blocks = new Dictionary<string, List<CodeBlock>>();
            var lines = code.Split('\n');

            string currentLanguage = null;
            int blockStart = -1;
            var currentBlock = new StringBuilder();

            for (int i = 0; i < lines.Length; i++)
            {
                var (found, langName, isEnd) = DetectDirective(lines[i]);

                if (found)
                {
                    if (isEnd && currentLanguage == langName)
                    {
                        // End of block
                        if (!blocks.ContainsKey(currentLanguage))
                            blocks[currentLanguage] = new List<CodeBlock>();

                        blocks[currentLanguage].Add(new CodeBlock
                        {
                            Language = currentLanguage,
                            Code = currentBlock.ToString().TrimEnd(),
                            StartLine = blockStart,
                            EndLine = i
                        });

                        currentLanguage = null;
                        currentBlock.Clear();
                    }
                    else if (!isEnd && currentLanguage == null)
                    {
                        // Start of block
                        currentLanguage = langName;
                        blockStart = i;
                    }
                }
                else if (currentLanguage != null)
                {
                    currentBlock.AppendLine(lines[i]);
                }
            }

            return blocks;
        }

        /// <summary>
        /// Checks if there's any language code in the given Calcpad code
        /// </summary>
        public static bool HasLanguageCode(string code)
        {
            try
            {
                var logPath = Path.Combine(Path.GetTempPath(), "calcpad_haslangcode_debug.txt");
                File.AppendAllText(logPath, $"\n[{DateTime.Now:HH:mm:ss}] === HasLanguageCode called ===\n");
                File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Code length: {code.Length}\n");
                File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] First 200 chars: {(code.Length > 200 ? code.Substring(0, 200) : code)}\n");
                File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Config.Languages count: {Config.Languages.Count}\n");

                foreach (var lang in Config.Languages.Values)
                {
                    File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] Checking directive: '{lang.Directive}'\n");
                    if (code.Contains(lang.Directive, StringComparison.OrdinalIgnoreCase))
                    {
                        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] FOUND: '{lang.Directive}' in code! Returning TRUE\n");
                        return true;
                    }
                }
                File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] No directives found. Returning FALSE\n");
            }
            catch { }

            return false;
        }

        /// <summary>
        /// Reloads configuration from file (force reload)
        /// </summary>
        public static void ReloadConfig()
        {
            _lastConfigLoad = DateTime.MinValue;
            LoadConfig();
        }
    }

    /// <summary>
    /// Represents a block of code in a specific language
    /// </summary>
    public class CodeBlock
    {
        public string Language { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
        public int StartLine { get; set; }
        public int EndLine { get; set; }
    }
}
