#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Web;
using Markdig;

namespace Calcpad.Common.MultLangCode
{
    /// <summary>
    /// Processes Calcpad code to execute external language blocks
    /// and replace them with HTML output results.
    ///
    /// Variable sharing:
    /// - To export a variable from external code to Calcpad, print a line with format:
    ///   CALCPAD:variable_name=value
    ///   Example in Python: print("CALCPAD:resultado=3.14159")
    ///   Example in C++: cout << "CALCPAD:resultado=3.14159" << endl;
    /// - The variable will be available in subsequent Calcpad calculations
    /// </summary>
    public partial class MultLangProcessor
    {
        private readonly LanguageExecutor _executor;
        private readonly Dictionary<string, object> _exportedVariables;
        private ExecutionTracker? _tracker;

        // Pattern to match CALCPAD:name=value lines
        private static readonly Regex CalcpadVarPattern = new(@"^CALCPAD:(\w+)=(.+)$", RegexOptions.Multiline);

        public MultLangProcessor(ExecutionTracker? tracker = null)
        {
            _tracker = tracker;
            _executor = new LanguageExecutor(_tracker);
            _exportedVariables = new Dictionary<string, object>();
        }

        /// <summary>
        /// Gets variables exported from external language blocks
        /// </summary>
        public IReadOnlyDictionary<string, object> ExportedVariables => _exportedVariables;

        /// <summary>
        /// Processes the code, executes language blocks, and returns modified code with results
        /// </summary>
        /// <param name="code">Original Calcpad code with language blocks</param>
        /// <param name="variables">Optional variables to inject from Calcpad</param>
        /// <param name="returnHtml">If true, returns HTML output directly; if false, returns Calcpad comments</param>
        /// <param name="enableCollapse">If true, adds collapse/expand buttons (+/-) to language output blocks</param>
        /// <param name="progressCallback">Optional callback for progress updates (e.g., "Compilando... 5ms")</param>
        /// <param name="partialResultCallback">Optional callback for partial HTML results as they become available</param>
        /// <returns>Code with language blocks replaced by output and variable assignments</returns>
        public string Process(string code, Dictionary<string, object>? variables = null, bool returnHtml = true, bool enableCollapse = true, Action<string>? progressCallback = null, Action<string>? partialResultCallback = null)
        {
            // Reset IFC import map flag for new document
            IfcLanguageHandler.ResetImportMapFlag();

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor.Process() START - returnHtml={returnHtml}, enableCollapse={enableCollapse}\n");
            }
            catch { }

            if (!MultLangManager.HasLanguageCode(code))
            {
                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: NO language code found, returning original\n");
                }
                catch { }
                return code;
            }

            var blocks = MultLangManager.ExtractCodeBlocks(code);
            if (blocks.Count == 0)
            {
                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: blocks.Count = 0, returning original\n");
                }
                catch { }
                return code;
            }

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Found {blocks.Count} language types\n");
            }
            catch { }

            // Split by newlines and remove any trailing \r from each line to avoid double line breaks
            var lines = code.Split('\n').Select(l => l.TrimEnd('\r')).ToArray();
            var result = new StringBuilder();
            var processedRanges = new List<(int start, int end, string output, List<(string name, string value)> vars)>();

            // Execute each block and collect results
            foreach (var (language, codeBlocks) in blocks)
            {
                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing language '{language}', {codeBlocks.Count} blocks\n");
                }
                catch { }

                foreach (var block in codeBlocks)
                {
                    string output;
                    var extractedVars = new List<(string name, string value)>();

                    // Special handling for @{code} and @{ucode} wrappers
                    // @{code}...@{end code} wraps @{html-ifc} blocks with full HTML/JS code
                    // @{ucode}...@{end ucode} wraps @{html-ifc} blocks with simplified directives OR direct IFC directives
                    if (language.Equals("code", StringComparison.OrdinalIgnoreCase) ||
                        language.Equals("ucode", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing {language.ToUpper()} wrapper block\n");
                        }
                        catch { }

                        string innerContent = block.Code ?? "";

                        // @{ucode} ALWAYS processes IFC directives directly
                        // Remove any @{html-ifc} wrapper if present (user error)
                        if (language.Equals("ucode", StringComparison.OrdinalIgnoreCase))
                        {
                            // Strip @{html-ifc}...@{end html-ifc} wrapper if present
                            innerContent = System.Text.RegularExpressions.Regex.Replace(
                                innerContent,
                                @"@\{html-ifc\}\s*\r?\n?",
                                "",
                                System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                            innerContent = System.Text.RegularExpressions.Regex.Replace(
                                innerContent,
                                @"\s*@\{end\s+html-ifc\}",
                                "",
                                System.Text.RegularExpressions.RegexOptions.IgnoreCase);

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing UCODE - cleaned content:\n{innerContent.Substring(0, Math.Min(200, innerContent.Length))}\n");
                            }
                            catch { }

                            // Process directly as IFC viewer with simplified directives
                            output = IfcLanguageHandler.GenerateInlineViewerHtml(innerContent, "@{ucode}");
                        }
                        else
                        {
                            // @{code} wrapper - process inner content recursively
                            output = Process(innerContent, variables, returnHtml, enableCollapse, progressCallback, partialResultCallback);
                        }
                    }
                    // Special handling for @{calcpad} - explicit Calcpad math blocks
                    // Generates a marker that will be processed by ExpressionParser later
                    else if (language.Equals("calcpad", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing CALCPAD block\n");
                        }
                        catch { }

                        // Encode Calcpad code as base64 marker for later processing
                        string calcpadCode = block.Code ?? "";
                        string base64Code = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(calcpadCode));
                        output = $"<!--CALCPAD_INLINE:{base64Code}-->";
                    }
                    // Special handling for mcdx - convert Mathcad Prime file to Calcpad
                    else if (language.Equals("mcdx", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing MCDX block\n");
                        }
                        catch { }

                        // The code content should be a file path to .mcdx file
                        var mcdxPath = block.Code.Trim();
                        output = ProcessMcdxFile(mcdxPath);
                    }
                    // Special handling for image - embed Base64 images
                    else if (language.Equals("image", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing IMAGE block, directive='{block.StartDirective}'\n");
                        }
                        catch { }

                        output = ProcessImageBlock(block.Code, block.StartDirective);
                    }
                    // Special handling for IFC - 3D viewer with Three.js and web-ifc
                    // Supports: @{ifc}path/to/file.ifc@{end ifc} or @{ifc base64}...@{end ifc}
                    // Also supports: @{ifc-fragment} for ThatOpen Fragments optimization
                    // NOTE: html-ifc is handled separately below (uses GenerateInlineViewerHtml)
                    else if (language.Equals("ifc", StringComparison.OrdinalIgnoreCase) ||
                             language.Equals("ifc-fragment", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing IFC block, directive='{block.StartDirective}'\n");
                        }
                        catch { }

                        // Detect if running in WPF context and use Virtual Host URLs
                        var isWpf = AppDomain.CurrentDomain.FriendlyName.Contains("Calcpad.exe") ||
                                    AppDomain.CurrentDomain.FriendlyName.Contains("Calcpad.Wpf");

                        string wasmPath;
                        string outputDirectory = null;

                        // Use current working directory for output (where HTML will be generated)
                        // This ensures fragment files are placed next to the HTML for HTTP server access
                        outputDirectory = System.IO.Directory.GetCurrentDirectory();

                        // Verify IFC file exists
                        var ifcFilePath = block.Code?.Trim();
                        if (string.IsNullOrEmpty(ifcFilePath) || !System.IO.File.Exists(ifcFilePath))
                        {
                            // IFC file not found, will be handled by ProcessIfcBlock
                        }

                        if (isWpf)
                        {
                            // WPF: Use Virtual Host (mapped in MainWindow.xaml.cs InitializeWebViewer)
                            // https://calcpad.ifc/ifc/ maps to {AppInfo.Path}/resources/ifc/
                            wasmPath = "https://calcpad.ifc/ifc";

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: Detected WPF context\n" +
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: AppDomain.FriendlyName = '{AppDomain.CurrentDomain.FriendlyName}'\n" +
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: Using Virtual Host wasmPath = '{wasmPath}'\n");
                            }
                            catch { }
                        }
                        else
                        {
                            // CLI: Use local libs to avoid CDN Tracking Prevention issues in Edge
                            wasmPath = "./libs";

                            // Copy libs to output directory if needed
                            if (!string.IsNullOrEmpty(outputDirectory))
                            {
                                CopyIfcLibsToDirectory(outputDirectory);
                            }

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: Detected CLI context\n" +
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: wasmPath = '{wasmPath}' (local libs)\n" +
                                    $"[{DateTime.Now:HH:mm:ss}] IFC: outputDirectory = '{outputDirectory}'\n");
                            }
                            catch { }
                        }

                        output = IfcLanguageHandler.ProcessIfcBlock(block.Code, block.StartDirective, wasmPath, outputDirectory);
                    }
                    // Special handling for markdown - render to HTML
                    // Supports: @{calcpad:expr}, $varName for variable values, keywords #val, #nosub, etc.
                    else if (language.Equals("markdown", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing MARKDOWN block\n");
                        }
                        catch { }

                        // Process variable substitution: $varName -> value
                        var codeWithVars = ProcessMarkdownVariables(block.Code, variables);
                        // Process inline Calcpad code: @{calcpad:...}
                        var processedCode = ProcessInlineCalcpad(codeWithVars);
                        // Then render markdown to HTML
                        output = RenderMarkdown(processedCode);
                    }
                    // Special handling for table - generate HTML table from matrix/vector
                    // Syntax: @{table}
                    //         matrixName
                    //         headers=A,B,C style=bordered export=file.xlsx
                    //         @{end table}
                    else if (language.Equals("table", StringComparison.OrdinalIgnoreCase))
                    {
                        output = ProcessTableBlock(block.Code, variables);
                    }
                    // Special handling for plot - generate SVG chart from vectors
                    // Syntax: @{plot}
                    //         x: vectorX   or  x: [1; 2; 3]
                    //         y: vectorY   or  y: [4; 5; 6]
                    //         xlabel: "X axis"
                    //         ylabel: "Y axis"
                    //         title: "Chart Title"
                    //         xlim: 0, 10
                    //         ylim: 0, 100
                    //         grid: true
                    //         legend: "Serie 1"
                    //         color: #0000FF
                    //         style: solid|dash|dot
                    //         @{end plot}
                    else if (language.Equals("plot", StringComparison.OrdinalIgnoreCase))
                    {
                        output = ProcessPlotBlock(block.Code, variables);
                    }
                    // Special handling for columns - multi-column layout
                    // Syntax: @{columns N}
                    //         content1
                    //         @{column}
                    //         content2
                    //         @{end columns}
                    else if (language.StartsWith("columns", StringComparison.OrdinalIgnoreCase))
                    {
                        // Pass block.StartDirective to preserve parameters like "@{columns 4}"
                        output = ProcessColumnsBlock(block.StartDirective, block.Code, variables, progressCallback);
                    }
                    // Special handling for html-ifc - inline IFC viewer embedded in output
                    // Syntax: @{html-ifc}path/to/file.ifc@{end html-ifc}
                    // This renders directly in the WebView2 output panel using Virtual Host
                    else if (language.Equals("html-ifc", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing HTML-IFC block, directive='{block.StartDirective}'\n");
                        }
                        catch { }

                        // html-ifc always uses Virtual Host URLs for WebView2 rendering
                        // This allows the IFC viewer to work directly in the Calcpad output panel
                        output = IfcLanguageHandler.GenerateInlineViewerHtml(block.Code?.Trim() ?? "", block.StartDirective);
                    }
                    // Special handling for ifc-create - create IFC geometry from commands
                    // Syntax: @{ifc-create}
                    //         WALL w1 = (0,0,0) to (10,0,0) height=3 thickness=0.3
                    //         BEAM b1 = (0,0,3) to (10,0,3) section=0.3x0.5
                    //         @{end ifc-create}
                    else if (language.Equals("ifc-create", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing IFC-CREATE block\n");
                        }
                        catch { }

                        output = ProcessIfcCreateBlock(block.Code ?? "", block.StartDirective);
                    }
                    // C#, XAML, WPF, CSS, HTML, three, vite always execute (handled specially in LanguageExecutor)
                    // Extract base language name for checking (e.g., "vite C:/path" -> "vite")
                    else
                    {
                        var baseLang = language.Contains(' ') ? language.Split(' ')[0] : language;
                        if (baseLang.Equals("csharp", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("xaml", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("wpf", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("css", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("html", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("html:embed", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("three", StringComparison.OrdinalIgnoreCase) ||
                            baseLang.Equals("vite", StringComparison.OrdinalIgnoreCase) ||
                            MultLangManager.IsLanguageAvailable(baseLang))
                        {
                            var execResult = _executor.Execute(block, variables, progressCallback);

                            // Extract CALCPAD:var=value from output
                            if (execResult.Success && !string.IsNullOrWhiteSpace(execResult.Output))
                            {
                                extractedVars = ExtractCalcpadVariables(execResult.Output);

                                // Store in exported variables dictionary
                                foreach (var (name, value) in extractedVars)
                                {
                                    if (double.TryParse(value, System.Globalization.NumberStyles.Any,
                                        System.Globalization.CultureInfo.InvariantCulture, out var numValue))
                                    {
                                        _exportedVariables[name] = numValue;
                                    }
                                    else
                                    {
                                        _exportedVariables[name] = value;
                                    }
                                }
                            }

                            // Generate output based on returnHtml mode
                            if (returnHtml)
                            {
                                // HTML mode: Generate formatted HTML output
                                output = LanguageHtmlGenerator.GenerateOutput(language, block.Code, execResult, enableCollapse);
                            }
                            else
                            {
                                // Mixed mode: Return plain text output (will be wrapped in Calcpad comments)
                                output = execResult.Success ? execResult.Output : execResult.Error;
                            }
                        }
                        else
                        {
                            output = LanguageHtmlGenerator.GenerateNotAvailable(baseLang, block.Code);
                        }
                    }
                    processedRanges.Add((block.StartLine, block.EndLine, output, extractedVars));

                    // PROGRESSIVE UPDATE: Send partial result to UI immediately
                    try
                    {
                        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Checking partial callback - partialResultCallback={(partialResultCallback != null ? "NOT NULL" : "NULL")}, returnHtml={returnHtml}, output.Length={output?.Length ?? 0}\n");
                    }
                    catch { }

                    if (partialResultCallback != null && returnHtml && !string.IsNullOrEmpty(output))
                    {
                        try
                        {
                            // Send partial HTML result to update OUTPUT while processing
                            partialResultCallback(output);

                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Sent partial result for {language} block (output length: {output.Length})\n");
                        }
                        catch (Exception ex)
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Error in partialResultCallback: {ex.Message}\n");
                        }
                    }
                }
            }

            // Sort ranges by start line (ascending to process in order)
            processedRanges.Sort((a, b) => a.start.CompareTo(b.start));

            // Build result by replacing blocks with output
            var skipRanges = new HashSet<int>();
            foreach (var (start, end, _, _) in processedRanges)
            {
                for (int i = start; i <= end; i++)
                    skipRanges.Add(i);
            }

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: skipRanges count = {skipRanges.Count}, ranges: {string.Join(", ", skipRanges.OrderBy(x => x).Take(20))}\n");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Total lines = {lines.Length}, processedRanges count = {processedRanges.Count}\n");
            }
            catch { }

            // Map start lines to their output and extracted variables
            var insertedContent = new Dictionary<int, (string output, List<(string name, string value)> vars)>();
            foreach (var (start, end, output, vars) in processedRanges)
            {
                insertedContent[start] = (output, vars);
            }

            if (returnHtml)
            {
                // Return HTML fragment (NOT full document - will be wrapped by HtmlApplyWorksheet)
                var htmlBuilder = new StringBuilder();

                for (int i = 0; i < lines.Length; i++)
                {
                    if (insertedContent.TryGetValue(i, out var content))
                    {
                        // Insert HTML output directly (LanguageHtmlGenerator already created the HTML)
                        htmlBuilder.AppendLine(content.output);

                        // Add variable assignments as HTML
                        if (content.vars.Count > 0)
                        {
                            htmlBuilder.AppendLine("<div style='background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0;'>");
                            htmlBuilder.AppendLine("<p><strong>Variables exportadas:</strong></p>");
                            htmlBuilder.AppendLine("<ul>");
                            foreach (var (name, value) in content.vars)
                            {
                                htmlBuilder.AppendLine($"<li><code style='background-color: #c8e6c9; padding: 2px 6px; border-radius: 3px;'>{name} = {value}</code></li>");
                            }
                            htmlBuilder.AppendLine("</ul>");
                            htmlBuilder.AppendLine("</div>");
                        }
                    }
                    else if (!skipRanges.Contains(i))
                    {
                        // Pass through non-code lines as HTML paragraphs
                        var trimmedLine = lines[i].Trim();
                        if (!string.IsNullOrWhiteSpace(trimmedLine))
                        {
                            // Convert Calcpad comments to HTML
                            if (trimmedLine.StartsWith("'") || trimmedLine.StartsWith("\""))
                            {
                                var text = trimmedLine.TrimStart('\'', '"').Trim();
                                htmlBuilder.AppendLine($"<p style='color: #333; margin: 10px 0;'>{HttpUtility.HtmlEncode(text)}</p>");
                            }
                            else
                            {
                                htmlBuilder.AppendLine($"<pre style='background-color: #f5f5f5; padding: 10px; border-radius: 4px;'>{HttpUtility.HtmlEncode(lines[i])}</pre>");
                            }
                        }
                    }
                }

                // Add JavaScript for toggle functionality (only if enabled)
                if (enableCollapse)
                {
                    htmlBuilder.AppendLine("<script>");
                    htmlBuilder.AppendLine("function toggleLangOutput(id) {");
                    htmlBuilder.AppendLine("    var content = document.getElementById(id);");
                    htmlBuilder.AppendLine("    var icon = document.getElementById(id + '-icon');");
                    htmlBuilder.AppendLine("    if (content.style.display === 'none') {");
                    htmlBuilder.AppendLine("        content.style.display = 'block';");
                    htmlBuilder.AppendLine("        icon.textContent = '▼';");
                    htmlBuilder.AppendLine("    } else {");
                    htmlBuilder.AppendLine("        content.style.display = 'none';");
                    htmlBuilder.AppendLine("        icon.textContent = '▶';");
                    htmlBuilder.AppendLine("    }");
                    htmlBuilder.AppendLine("}");
                    htmlBuilder.AppendLine("</script>");
                }

                var finalHtml = htmlBuilder.ToString();

                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    var markerCount = System.Text.RegularExpressions.Regex.Matches(finalHtml, @"<!--CALCPAD_INLINE:").Count;
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor FINAL HTML: {markerCount} markers, length: {finalHtml.Length}\n");
                }
                catch { }

                return finalHtml;
            }
            else
            {
                // Return Calcpad code with HTML markers for external block outputs
                // HTML markers will be preserved by ExpressionParser and processed later
                for (int i = 0; i < lines.Length; i++)
                {
                    if (insertedContent.TryGetValue(i, out var content))
                    {
                        // Check if output looks like HTML (contains tags)
                        var outputTrimmed = content.output?.Trim() ?? "";
                        var isHtmlOutput = outputTrimmed.StartsWith("<") ||
                                          outputTrimmed.Contains("<div") ||
                                          outputTrimmed.Contains("<p") ||
                                          outputTrimmed.Contains("<span") ||
                                          outputTrimmed.Contains("<!DOCTYPE");

                        if (isHtmlOutput)
                        {
                            // For HTML output: use a special marker that ExpressionParser will preserve
                            // Format: <!--MULTILANG_OUTPUT:base64-->
                            var base64Output = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(content.output));
                            result.AppendLine($"<!--MULTILANG_OUTPUT:{base64Output}-->");
                        }
                        else
                        {
                            // For plain text output: insert as Calcpad comments
                            var outputLines = content.output?.Split('\n') ?? Array.Empty<string>();
                            foreach (var outputLine in outputLines)
                            {
                                var trimmedLine = outputLine.TrimEnd('\r');
                                if (!string.IsNullOrWhiteSpace(trimmedLine))
                                {
                                    // Don't show CALCPAD:var=value lines in output
                                    if (!trimmedLine.StartsWith("CALCPAD:"))
                                    {
                                        // Use double quotes if line contains single quotes to avoid comment termination
                                        // Calcpad interprets ' and " as comment start, and uses the same char to end
                                        var hasSingle = trimmedLine.Contains('\'');
                                        var hasDouble = trimmedLine.Contains('"');

                                        if (hasSingle && hasDouble)
                                        {
                                            // Both quotes present - escape single quotes and use single quote prefix
                                            var escaped = trimmedLine.Replace("'", "\\'");
                                            result.AppendLine($"'{escaped}");
                                        }
                                        else
                                        {
                                            var commentChar = hasSingle ? '"' : '\'';
                                            result.AppendLine($"{commentChar}{trimmedLine}");
                                        }
                                    }
                                }
                            }
                        }

                        // Add variable assignments to Calcpad
                        if (content.vars.Count > 0)
                        {
                            result.AppendLine("'Variables exportadas:");
                            foreach (var (name, value) in content.vars)
                            {
                                // Create Calcpad assignment: name = value
                                result.AppendLine($"{name} = {value}");
                            }
                        }
                    }
                    else if (!skipRanges.Contains(i))
                    {
                        result.AppendLine(lines[i]);
                    }
                    // else: skip this line (it's part of an external code block)
                }

                var finalResult = result.ToString().TrimEnd('\r', '\n');

                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor returnHtml=FALSE output length: {finalResult.Length}\n");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor returnHtml=FALSE first 500 chars: {finalResult.Substring(0, Math.Min(500, finalResult.Length))}\n");
                }
                catch { }

                return finalResult;
            }
        }

        /// <summary>
        /// Extracts CALCPAD:name=value pairs from output
        /// </summary>
        private static List<(string name, string value)> ExtractCalcpadVariables(string output)
        {
            var vars = new List<(string name, string value)>();
            var matches = CalcpadVarPattern.Matches(output);

            foreach (Match match in matches)
            {
                if (match.Groups.Count >= 3)
                {
                    var name = match.Groups[1].Value;
                    var value = match.Groups[2].Value.Trim();
                    vars.Add((name, value));
                }
            }

            return vars;
        }

        /// <summary>
        /// Checks if the code contains any language blocks
        /// </summary>
        public static bool HasLanguageBlocks(string code)
        {
            return MultLangManager.HasLanguageCode(code);
        }

        /// <summary>
        /// Gets a list of languages used in the code
        /// </summary>
        public static IEnumerable<string> GetUsedLanguages(string code)
        {
            var blocks = MultLangManager.ExtractCodeBlocks(code);
            return blocks.Keys;
        }

        /// <summary>
        /// Processes a Mathcad Prime (.mcdx) file and converts it to Calcpad format
        /// </summary>
        private string ProcessMcdxFile(string mcdxPath)
        {
            try
            {
                // Resolve relative paths
                if (!System.IO.Path.IsPathRooted(mcdxPath))
                {
                    // Try to find the file relative to current directory or temp
                    var currentDir = Environment.CurrentDirectory;
                    var fullPath = System.IO.Path.Combine(currentDir, mcdxPath);
                    if (System.IO.File.Exists(fullPath))
                        mcdxPath = fullPath;
                }

                if (!System.IO.File.Exists(mcdxPath))
                {
                    return $"' ERROR: Archivo Mathcad no encontrado: {mcdxPath}\n" +
                           "' Verifique la ruta del archivo .mcdx";
                }

                var converter = new McdxConverter();
                var result = converter.Convert(mcdxPath);

                // Add any warnings as comments
                if (converter.Warnings.Count > 0)
                {
                    var sb = new StringBuilder();
                    sb.AppendLine(result);
                    sb.AppendLine();
                    sb.AppendLine("' === Advertencias de conversion ===");
                    foreach (var warning in converter.Warnings)
                    {
                        sb.AppendLine($"' {warning}");
                    }
                    result = sb.ToString();
                }

                return result;
            }
            catch (Exception ex)
            {
                return $"' ERROR al convertir archivo Mathcad: {ex.Message}\n" +
                       $"' Archivo: {mcdxPath}";
            }
        }

        /// <summary>
        /// Renders markdown content to HTML
        /// </summary>
        private string RenderMarkdown(string markdownCode)
        {
            try
            {
                // WORKAROUND: Markdig.Signed 0.43.0 UsePipeTables() doesn't work
                // Manually convert markdown tables to HTML before processing
                var processedCode = ConvertTablesToHtml(markdownCode);

                // Process rest of markdown normally
                var pipeline = new MarkdownPipelineBuilder()
                    .UseEmphasisExtras()
                    .UseListExtras()
                    .UseAutoIdentifiers()  // Enable automatic heading IDs for internal links
                    .Build();

                var html = Markdown.ToHtml(processedCode, pipeline);

                return html;
            }
            catch (Exception ex)
            {
                return $"<div class=\"error\">Error rendering markdown: {ex.Message}</div>";
            }
        }

        private string ConvertTablesToHtml(string markdown)
        {
            var lines = markdown.Split('\n');
            var result = new StringBuilder();
            var i = 0;

            while (i < lines.Length)
            {
                var line = lines[i].Trim();

                // Detect table: line with |
                if (line.Contains('|') && i + 1 < lines.Length)
                {
                    var nextLine = lines[i + 1].Trim();
                    // Check if next line is separator (contains | and -)
                    if (nextLine.Contains('|') && nextLine.Contains('-'))
                    {
                        // This is a table! Add inline styles for borders
                        result.AppendLine("<table style=\"border-collapse: collapse; width: 100%; margin: 10px 0;\">");

                        // Parse header
                        var headers = line.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
                        result.AppendLine("<thead><tr>");
                        foreach (var header in headers)
                            result.AppendLine($"<th style=\"border: 1px solid #ddd; padding: 8px 12px; background-color: #f0f0f0; font-weight: bold;\">{ProcessInlineMarkdown(header)}</th>");
                        result.AppendLine("</tr></thead>");

                        // Skip separator line
                        i += 2;

                        // Parse rows
                        result.AppendLine("<tbody>");
                        while (i < lines.Length && lines[i].Trim().Contains('|'))
                        {
                            var rowLine = lines[i].Trim();
                            var cells = rowLine.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
                            result.AppendLine("<tr>");
                            foreach (var cell in cells)
                                result.AppendLine($"<td style=\"border: 1px solid #ddd; padding: 8px 12px;\">{ProcessInlineMarkdown(cell)}</td>");
                            result.AppendLine("</tr>");
                            i++;
                        }
                        result.AppendLine("</tbody></table>");
                        continue;
                    }
                }

                result.AppendLine(lines[i]);
                i++;
            }

            return result.ToString();
        }

        private string ProcessInlineMarkdown(string text)
        {
            // Process inline markdown: **bold**, *italic*, `code`, etc.
            text = System.Text.RegularExpressions.Regex.Replace(text, @"\*\*(.+?)\*\*", "<strong>$1</strong>");
            text = System.Text.RegularExpressions.Regex.Replace(text, @"\*(.+?)\*", "<em>$1</em>");
            text = System.Text.RegularExpressions.Regex.Replace(text, @"`(.+?)`", "<code>$1</code>");
            return text;
        }

        /// <summary>
        /// Cleanup temporary files
        /// </summary>
        public void Cleanup()
        {
            _executor.Cleanup();
        }

        /// <summary>
        /// Process inline Calcpad code blocks: @{calcpad:...}
        /// Extracts and marks them for later processing
        /// </summary>
        private string ProcessInlineCalcpad(string content)
        {
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessInlineCalcpad CALLED! Content length: {content.Length}\n");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] Content preview: {content.Substring(0, Math.Min(200, content.Length))}\n");
            }
            catch { }

            // Pattern to match @{calcpad:...}
            var result = new StringBuilder();
            int i = 0;

            while (i < content.Length)
            {
                // Look for start marker: @{calcpad:
                if (i + 10 < content.Length &&
                    content.Substring(i, 10) == "@{calcpad:")
                {
                    i += 10; // Skip the marker

                    // Find closing }
                    int braceCount = 1;
                    int start = i;

                    while (i < content.Length && braceCount > 0)
                    {
                        if (content[i] == '{')
                            braceCount++;
                        else if (content[i] == '}')
                        {
                            braceCount--;
                            if (braceCount == 0)
                            {
                                // Found closing }
                                string calcpadCode = content.Substring(start, i - start);

                                // Wrap in a special marker that will be processed later
                                // Format: <!--CALCPAD_INLINE:base64encodedcode-->
                                var encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(calcpadCode));
                                result.Append($"<!--CALCPAD_INLINE:{encoded}-->");

                                i++; // Skip }
                                break;
                            }
                        }
                        i++;
                    }
                }
                else
                {
                    result.Append(content[i]);
                    i++;
                }
            }

            var resultString = result.ToString();

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                var markerCount = System.Text.RegularExpressions.Regex.Matches(resultString, @"<!--CALCPAD_INLINE:").Count;
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessInlineCalcpad RESULT: {markerCount} markers created, result length: {resultString.Length}\n");
                if (markerCount > 0)
                {
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] Result preview: {resultString.Substring(0, Math.Min(300, resultString.Length))}\n");
                }
            }
            catch { }

            return resultString;
        }

        /// <summary>
        /// Process image block with Base64 data
        /// Format: @{image png base64}
        ///         [base64 data here]
        ///         @{end image}
        /// </summary>
        /// <param name="content">The Base64 content (without the directive line)</param>
        /// <param name="startDirective">The original start directive (e.g., "@{image png base64}")</param>
        private string ProcessImageBlock(string content, string startDirective = "")
        {
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessImageBlock: Content length = {content.Length}, directive = '{startDirective}'\n");
            }
            catch { }

            try
            {
                // Default format
                var format = "png";

                // Extract format from start directive (e.g., "@{image png base64}" -> "png")
                if (!string.IsNullOrEmpty(startDirective))
                {
                    var directiveLower = startDirective.ToLower();
                    if (directiveLower.Contains("jpg") || directiveLower.Contains("jpeg"))
                        format = "jpeg";
                    else if (directiveLower.Contains("bmp"))
                        format = "bmp";
                    else if (directiveLower.Contains("gif"))
                        format = "gif";
                    else if (directiveLower.Contains("png"))
                        format = "png";
                }

                // The content is already pure Base64 data (no metadata line)
                var base64Content = content;

                // Clean up the Base64 string (remove whitespace, newlines)
                base64Content = base64Content
                    .Replace("\n", "")
                    .Replace("\r", "")
                    .Replace(" ", "")
                    .Replace("\t", "")
                    .Trim();

                if (string.IsNullOrWhiteSpace(base64Content))
                {
                    return "<p style='color:red;'>Error: No se encontró contenido Base64</p>";
                }

                // Validate Base64 format (basic check)
                if (base64Content.Length % 4 != 0)
                {
                    // Add padding if needed
                    int padding = 4 - (base64Content.Length % 4);
                    if (padding < 4)
                    {
                        base64Content += new string('=', padding);
                    }
                }

                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] ProcessImageBlock: Format={format}, Base64 length={base64Content.Length}\n");
                }
                catch { }

                // Generate HTML with embedded image
                var html = $"<div style='text-align:center; margin: 20px 0;'>" +
                          $"<img src='data:image/{format};base64,{base64Content}' " +
                          $"style='max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);' " +
                          $"alt='Imagen embebida' />" +
                          $"</div>";

                return html;
            }
            catch (Exception ex)
            {
                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] ProcessImageBlock ERROR: {ex.Message}\n");
                }
                catch { }

                return $"<p style='color:red;'>Error al procesar imagen: {ex.Message}</p>";
            }
        }

        /// <summary>
        /// Process variable substitution in markdown: $varName -> value
        /// This allows writing clean markdown with embedded variable values
        /// Example: "El resultado es $x" -> "El resultado es 42"
        /// </summary>
        private string ProcessMarkdownVariables(string content, Dictionary<string, object> variables)
        {
            if (variables == null || variables.Count == 0)
                return content;

            var result = content;

            // Replace $varName with variable value
            // Pattern: $followed by word characters, not preceded by backslash
            result = System.Text.RegularExpressions.Regex.Replace(
                result,
                @"(?<!\\)\$([a-zA-Z_][a-zA-Z0-9_]*)",
                m =>
                {
                    var varName = m.Groups[1].Value;
                    if (variables.TryGetValue(varName, out var value))
                    {
                        // Format based on type
                        if (value is double d)
                            return d.ToString("G10", System.Globalization.CultureInfo.InvariantCulture);
                        else if (value is int i)
                            return i.ToString();
                        else if (value is double[] arr)
                            return "[" + string.Join(", ", arr.Select(x => x.ToString("G6", System.Globalization.CultureInfo.InvariantCulture))) + "]";
                        else if (value is double[,] matrix)
                            return FormatMatrixCompact(matrix);
                        else
                            return value?.ToString() ?? "";
                    }
                    return m.Value; // Keep original if variable not found
                }
            );

            // Allow escaping: \$ -> $
            result = result.Replace("\\$", "$");

            return result;
        }

        /// <summary>
        /// Format a 2D matrix in compact form for markdown display
        /// </summary>
        private string FormatMatrixCompact(double[,] matrix)
        {
            var rows = matrix.GetLength(0);
            var cols = matrix.GetLength(1);
            var sb = new StringBuilder("[");
            for (int i = 0; i < rows; i++)
            {
                if (i > 0) sb.Append("; ");
                for (int j = 0; j < cols; j++)
                {
                    if (j > 0) sb.Append(", ");
                    sb.Append(matrix[i, j].ToString("G6", System.Globalization.CultureInfo.InvariantCulture));
                }
            }
            sb.Append("]");
            return sb.ToString();
        }

        /// <summary>
        /// Process @{table} block - generates HTML table from Calcpad matrix/vector
        /// Syntax:
        ///   @{table}
        ///   matrixName
        ///   headers=A,B,C  (optional column headers)
        ///   rows=1,2,3     (optional row headers)
        ///   style=bordered (optional: bordered, striped, minimal)
        ///   export=file.xlsx (optional: export to Excel)
        ///   @{end table}
        /// </summary>
        public string ProcessTableBlockPublic(string content, Dictionary<string, object> variables)
        {
            return ProcessTableBlock(content, variables);
        }

        private string ProcessTableBlock(string content, Dictionary<string, object> variables)
        {
            try
            {
                var lines = content.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(l => l.Trim())
                    .Where(l => !string.IsNullOrEmpty(l))
                    .ToList();

                if (lines.Count == 0)
                    return "<p style='color:red;'>Error: Bloque @{table} vacío</p>";

                // First line should be the matrix/vector name
                var matrixName = lines[0];
                string[] headers = null;
                string[] rowHeaders = null;
                string style = "bordered";
                string exportFile = null;

                // Parse options from remaining lines
                for (int i = 1; i < lines.Count; i++)
                {
                    var line = lines[i].ToLower();
                    if (line.StartsWith("headers="))
                        headers = lines[i].Substring(8).Split(',').Select(h => h.Trim()).ToArray();
                    else if (line.StartsWith("rows="))
                        rowHeaders = lines[i].Substring(5).Split(',').Select(r => r.Trim()).ToArray();
                    else if (line.StartsWith("style="))
                        style = lines[i].Substring(6).Trim().ToLower();
                    else if (line.StartsWith("export="))
                        exportFile = lines[i].Substring(7).Trim();
                }

                // Get matrix/vector from variables
                if (!variables.TryGetValue(matrixName, out var data))
                    return $"<p style='color:red;'>Error: Variable '{matrixName}' no encontrada</p>";

                // Convert to 2D array if needed
                double[,] matrix;
                if (data is double[,] m)
                    matrix = m;
                else if (data is double[] arr)
                {
                    // Convert vector to single-row or single-column matrix
                    matrix = new double[1, arr.Length];
                    for (int j = 0; j < arr.Length; j++)
                        matrix[0, j] = arr[j];
                }
                else if (data is double d)
                {
                    // Single value
                    matrix = new double[1, 1] { { d } };
                }
                else
                    return $"<p style='color:red;'>Error: '{matrixName}' no es un matriz/vector numérico</p>";

                // Generate HTML table
                var sb = new StringBuilder();
                var tableStyle = GetTableStyle(style);

                sb.Append($"<table style='{tableStyle}'>");

                // Header row
                if (headers != null && headers.Length > 0)
                {
                    sb.Append("<thead><tr>");
                    if (rowHeaders != null) sb.Append("<th></th>"); // Empty corner cell
                    foreach (var h in headers)
                        sb.Append($"<th style='padding: 8px; text-align: center;'>{System.Web.HttpUtility.HtmlEncode(h)}</th>");
                    sb.Append("</tr></thead>");
                }

                // Data rows
                sb.Append("<tbody>");
                var rows = matrix.GetLength(0);
                var cols = matrix.GetLength(1);

                for (int i = 0; i < rows; i++)
                {
                    sb.Append("<tr>");

                    // Row header
                    if (rowHeaders != null && i < rowHeaders.Length)
                        sb.Append($"<th style='padding: 8px; text-align: left;'>{System.Web.HttpUtility.HtmlEncode(rowHeaders[i])}</th>");

                    // Data cells
                    for (int j = 0; j < cols; j++)
                    {
                        var value = matrix[i, j];
                        var formatted = FormatNumber(value);
                        sb.Append($"<td style='padding: 8px; text-align: right;'>{formatted}</td>");
                    }
                    sb.Append("</tr>");
                }
                sb.Append("</tbody></table>");

                // Export to file if requested
                if (!string.IsNullOrEmpty(exportFile))
                {
                    try
                    {
                        ExportTableToFile(matrix, headers, rowHeaders, exportFile);
                        sb.Append($"<p style='font-size:0.8em; color:#666;'>Exportado a: {System.Web.HttpUtility.HtmlEncode(exportFile)}</p>");
                    }
                    catch (Exception ex)
                    {
                        sb.Append($"<p style='color:orange;'>Advertencia: No se pudo exportar: {ex.Message}</p>");
                    }
                }

                return sb.ToString();
            }
            catch (Exception ex)
            {
                return $"<p style='color:red;'>Error en @{{table}}: {ex.Message}</p>";
            }
        }

        /// <summary>
        /// Get CSS style for table based on style name
        /// </summary>
        private string GetTableStyle(string style)
        {
            return style switch
            {
                "bordered" => "border-collapse: collapse; border: 1px solid #333; width: 100%;",
                "striped" => "border-collapse: collapse; width: 100%;",
                "minimal" => "border-collapse: collapse; width: 100%; border: none;",
                _ => "border-collapse: collapse; border: 1px solid #333; width: 100%;"
            };
        }

        /// <summary>
        /// Format number for table display
        /// </summary>
        private string FormatNumber(double value)
        {
            if (Math.Abs(value) < 1e-10) return "0";
            if (Math.Abs(value) >= 1e6 || Math.Abs(value) < 1e-3)
                return value.ToString("0.####E+0", System.Globalization.CultureInfo.InvariantCulture);
            return value.ToString("G6", System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>
        /// Process @{plot} block - generate SVG chart from vectors
        /// Syntax:
        ///   @{plot}
        ///   x: vectorX   or  x: [1; 2; 3]
        ///   y: vectorY   or  y: [4; 5; 6]
        ///   xlabel: "X axis label"
        ///   ylabel: "Y axis label"
        ///   title: "Chart Title"
        ///   xlim: min, max
        ///   ylim: min, max
        ///   grid: true|false
        ///   legend: "Serie Name"
        ///   color: #0000FF
        ///   style: solid|dash|dot
        ///   @{end plot}
        /// </summary>
        private string ProcessPlotBlock(string content, Dictionary<string, object> variables)
        {
            try
            {
                var lines = content.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(l => l.Trim())
                    .Where(l => !string.IsNullOrEmpty(l))
                    .ToList();

                if (lines.Count == 0)
                    return "<p style='color:red;'>Error: Bloque @{plot} vacío</p>";

                // Parse plot options - global settings
                string xData = null;
                string xlabel = "x", ylabel = "y", title = null;
                double? xmin = null, xmax = null, ymin = null, ymax = null;
                bool grid = true;
                bool showLegend = true;
                string background = "paper";  // "paper" (azul milimetrado) or "white" (blanco limpio)
                int width = 600, height = 400;

                // Multiple series support - track current series being configured
                var series = new List<PlotSeries>();
                PlotSeries currentSeries = null;

                // Default colors for multiple series (similar to Mathcad/Matlab)
                var defaultColors = new[] { "#0033CC", "#CC0000", "#006600", "#9900CC", "#FF6600", "#00CCCC", "#CC00CC", "#666666" };

                // Annotations: text, arrows, lines, shapes
                var annotations = new List<PlotAnnotation>();

                foreach (var line in lines)
                {
                    var colonIdx = line.IndexOf(':');
                    if (colonIdx <= 0) continue;

                    var key = line.Substring(0, colonIdx).Trim().ToLower();
                    var value = line.Substring(colonIdx + 1).Trim();

                    // Handle annotations specially (don't strip quotes yet)
                    if (key == "text" || key == "texto" || key == "label" || key == "etiqueta")
                    {
                        var annotation = ParseTextAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    if (key == "arrow" || key == "flecha")
                    {
                        var annotation = ParseArrowAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    if (key == "line" || key == "linea" || key == "hline" || key == "vline")
                    {
                        var annotation = ParseLineAnnotation(key, value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    if (key == "rect" || key == "rectangulo" || key == "circle" || key == "circulo")
                    {
                        var annotation = ParseShapeAnnotation(key, value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Projection lines from point to axes (like in derivative diagrams)
                    if (key == "proj" || key == "projection" || key == "proyeccion")
                    {
                        var annotation = ParseProjectionAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Axis tick labels (custom labels at specific positions)
                    if (key == "xtick" || key == "ytick" || key == "tickx" || key == "ticky")
                    {
                        var annotation = ParseTickAnnotation(key, value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Angle annotation (arc with label)
                    if (key == "angle" || key == "angulo")
                    {
                        var annotation = ParseAngleAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Dimension bracket/brace (curly braces)
                    if (key == "brace" || key == "bracket" || key == "llave")
                    {
                        var annotation = ParseBraceAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Filled point/dot marker
                    if (key == "point" || key == "punto" || key == "dot")
                    {
                        var annotation = ParsePointAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }
                    // Dimension with double-headed arrow (like in technical drawings)
                    if (key == "dim" || key == "dimension" || key == "cota" || key == "measure")
                    {
                        var annotation = ParseDimensionAnnotation(value);
                        if (annotation != null) annotations.Add(annotation);
                        continue;
                    }

                    // Remove quotes from string values
                    if (value.StartsWith("\"") && value.EndsWith("\""))
                        value = value.Substring(1, value.Length - 2);
                    else if (value.StartsWith("'") && value.EndsWith("'"))
                        value = value.Substring(1, value.Length - 2);

                    // Check for numbered keys (y2, color2, etc.)
                    var numMatch = System.Text.RegularExpressions.Regex.Match(key, @"^(.+?)(\d+)$");
                    int seriesIndex = 0;
                    string baseKey = key;
                    if (numMatch.Success)
                    {
                        baseKey = numMatch.Groups[1].Value;
                        seriesIndex = int.Parse(numMatch.Groups[2].Value) - 1; // y2 -> index 1
                    }

                    // Ensure series list is large enough
                    while (series.Count <= seriesIndex)
                    {
                        var newSeries = new PlotSeries();
                        newSeries.Color = defaultColors[series.Count % defaultColors.Length];
                        series.Add(newSeries);
                    }

                    switch (baseKey)
                    {
                        case "x": xData = value; break;
                        case "y":
                            series[seriesIndex].YData = value;
                            currentSeries = series[seriesIndex];
                            break;
                        case "xlabel": xlabel = value; break;
                        case "ylabel": ylabel = value; break;
                        case "title": title = value; break;
                        case "xlim":
                            var xlimParts = value.Split(',');
                            if (xlimParts.Length >= 2)
                            {
                                if (double.TryParse(xlimParts[0].Trim(), out var xminVal)) xmin = xminVal;
                                if (double.TryParse(xlimParts[1].Trim(), out var xmaxVal)) xmax = xmaxVal;
                            }
                            break;
                        case "ylim":
                            var ylimParts = value.Split(',');
                            if (ylimParts.Length >= 2)
                            {
                                if (double.TryParse(ylimParts[0].Trim(), out var yminVal)) ymin = yminVal;
                                if (double.TryParse(ylimParts[1].Trim(), out var ymaxVal)) ymax = ymaxVal;
                            }
                            break;
                        case "grid":
                            grid = !value.Equals("false", StringComparison.OrdinalIgnoreCase) &&
                                   !value.Equals("0", StringComparison.OrdinalIgnoreCase);
                            break;
                        case "showlegend":
                        case "mostrarleyenda":
                            if (value.Equals("false", StringComparison.OrdinalIgnoreCase) ||
                                value.Equals("0", StringComparison.OrdinalIgnoreCase) ||
                                value.Equals("no", StringComparison.OrdinalIgnoreCase))
                                showLegend = false;
                            break;
                        case "background":
                        case "bg":
                        case "fondo":
                            background = value.ToLower();
                            break;
                        case "legend":
                            series[seriesIndex].Legend = value;
                            break;
                        case "color":
                            series[seriesIndex].Color = value;
                            break;
                        case "style":
                            series[seriesIndex].LineStyle = value.ToLower();
                            break;
                        case "symbol":
                        case "marker":
                            series[seriesIndex].Symbol = value.ToLower();
                            break;
                        case "symbolsize":
                        case "markersize":
                            if (int.TryParse(value, out var ss)) series[seriesIndex].SymbolSize = ss;
                            break;
                        case "linewidth":
                        case "lw":
                            if (double.TryParse(value, System.Globalization.NumberStyles.Any,
                                System.Globalization.CultureInfo.InvariantCulture, out var lw))
                                series[seriesIndex].LineWidth = lw;
                            break;
                        case "width":
                            if (int.TryParse(value, out var w)) width = w;
                            break;
                        case "height":
                            if (int.TryParse(value, out var h)) height = h;
                            break;
                        case "smooth":
                        case "suavizado":
                        case "spline":
                            series[seriesIndex].Smooth = !value.Equals("false", StringComparison.OrdinalIgnoreCase) &&
                                     !value.Equals("0", StringComparison.OrdinalIgnoreCase) &&
                                     !value.Equals("no", StringComparison.OrdinalIgnoreCase);
                            break;
                        case "tension":
                        case "smoothtension":
                            if (double.TryParse(value, System.Globalization.NumberStyles.Any,
                                System.Globalization.CultureInfo.InvariantCulture, out var t))
                                series[seriesIndex].SmoothTension = Math.Max(0, Math.Min(1, t));
                            break;
                    }
                }

                // Remove series without data
                series = series.Where(s => !string.IsNullOrEmpty(s.YData)).ToList();

                if (series.Count == 0)
                    return "<p style='color:red;'>Error: No se definieron datos y para graficar</p>";

                // Get X data
                double[] xValues = GetPlotData(xData, variables);
                if (xValues == null)
                    return "<p style='color:red;'>Error: No se pudo obtener datos para x</p>";

                // Get all Y data and validate
                var allYValues = new List<double[]>();
                foreach (var s in series)
                {
                    var yVals = GetPlotData(s.YData, variables);
                    if (yVals == null)
                        return $"<p style='color:red;'>Error: No se pudo obtener datos para y</p>";
                    if (yVals.Length != xValues.Length)
                        return $"<p style='color:red;'>Error: Las longitudes de x ({xValues.Length}) y y ({yVals.Length}) no coinciden</p>";
                    allYValues.Add(yVals);
                }

                if (xValues.Length < 2)
                    return "<p style='color:red;'>Error: Se necesitan al menos 2 puntos para graficar</p>";

                // Calculate limits if not specified (considering all series)
                if (!xmin.HasValue) xmin = xValues.Min() - (xValues.Max() - xValues.Min()) * 0.05;
                if (!xmax.HasValue) xmax = xValues.Max() + (xValues.Max() - xValues.Min()) * 0.05;

                double globalYMin = allYValues.SelectMany(y => y).Min();
                double globalYMax = allYValues.SelectMany(y => y).Max();
                if (!ymin.HasValue) ymin = globalYMin - (globalYMax - globalYMin) * 0.05;
                if (!ymax.HasValue) ymax = globalYMax + (globalYMax - globalYMin) * 0.05;

                // Handle case where all values are the same
                if (Math.Abs(xmax.Value - xmin.Value) < 1e-10) { xmin -= 1; xmax += 1; }
                if (Math.Abs(ymax.Value - ymin.Value) < 1e-10) { ymin -= 1; ymax += 1; }

                // Generate SVG with multiple series
                return GeneratePlotSvgMultiSeries(xValues, allYValues, series, xmin.Value, xmax.Value, ymin.Value, ymax.Value,
                    xlabel, ylabel, title, grid, showLegend, background, width, height, annotations);
            }
            catch (Exception ex)
            {
                return $"<p style='color:red;'>Error en @{{plot}}: {ex.Message}</p>";
            }
        }

        /// <summary>
        /// Series class for multiple data series in a plot
        /// </summary>
        private class PlotSeries
        {
            public string YData { get; set; }
            public string Color { get; set; } = "#4169E1";
            public string LineStyle { get; set; } = "solid";
            public string Symbol { get; set; } = "none";
            public int SymbolSize { get; set; } = 6;
            public double LineWidth { get; set; } = 2.0;
            public string Legend { get; set; }
            public bool Smooth { get; set; } = false;
            public double SmoothTension { get; set; } = 0.3;
        }

        /// <summary>
        /// Annotation class for plot elements
        /// </summary>
        private class PlotAnnotation
        {
            public string Type { get; set; } = "text";  // text, arrow, line, hline, vline, rect, circle
            public double X { get; set; }
            public double Y { get; set; }
            public double X2 { get; set; }  // For arrows, lines, rects
            public double Y2 { get; set; }
            public string Text { get; set; } = "";
            public string Color { get; set; } = "#003366";
            public int FontSize { get; set; } = 12;
            public string Anchor { get; set; } = "start";  // start, middle, end
            public bool Bold { get; set; } = false;
            public bool Italic { get; set; } = true;
            public double Rotation { get; set; } = 0;
            public double StrokeWidth { get; set; } = 1.5;
            public string Fill { get; set; } = "none";
        }

        /// <summary>
        /// Parse text annotation: x, y, "text" [, color, fontsize, anchor, bold, italic, rotation]
        /// </summary>
        private PlotAnnotation ParseTextAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "text" };

                // Find the quoted text
                int quoteStart = value.IndexOf('"');
                int quoteEnd = value.LastIndexOf('"');
                if (quoteStart < 0 || quoteEnd <= quoteStart)
                {
                    quoteStart = value.IndexOf('\'');
                    quoteEnd = value.LastIndexOf('\'');
                }

                if (quoteStart < 0 || quoteEnd <= quoteStart)
                    return null;

                annotation.Text = value.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);

                // Parse coordinates before the quote
                var coordsPart = value.Substring(0, quoteStart).Trim().TrimEnd(',');
                var coords = coordsPart.Split(',');
                if (coords.Length >= 2)
                {
                    double.TryParse(coords[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(coords[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    annotation.X = x;
                    annotation.Y = y;
                }

                // Parse options after the quote
                if (quoteEnd < value.Length - 1)
                {
                    var optionsPart = value.Substring(quoteEnd + 1).Trim().TrimStart(',');
                    var options = optionsPart.Split(',');
                    foreach (var opt in options)
                    {
                        var o = opt.Trim().ToLower();
                        if (o.StartsWith("#") || o.StartsWith("rgb"))
                            annotation.Color = opt.Trim();
                        else if (int.TryParse(o, out var fs) && fs >= 6 && fs <= 72)
                            annotation.FontSize = fs;
                        else if (o == "start" || o == "middle" || o == "end" || o == "center")
                            annotation.Anchor = o == "center" ? "middle" : o;
                        else if (o == "bold" || o == "negrita")
                            annotation.Bold = true;
                        else if (o == "italic" || o == "cursiva")
                            annotation.Italic = true;
                        else if (o == "normal")
                            annotation.Italic = false;
                        else if (o.StartsWith("rot") || o.EndsWith("°") || o.EndsWith("deg"))
                        {
                            var rotVal = o.Replace("rot", "").Replace("°", "").Replace("deg", "").Trim();
                            double.TryParse(rotVal, System.Globalization.NumberStyles.Any,
                                System.Globalization.CultureInfo.InvariantCulture, out var rot);
                            annotation.Rotation = rot;
                        }
                    }
                }

                return annotation;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Parse arrow annotation: x1, y1, x2, y2 [, color, strokewidth]
        /// </summary>
        private PlotAnnotation ParseArrowAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "arrow" };
                var parts = value.Split(',');
                if (parts.Length >= 4)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x1);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y1);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x2);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y2);
                    annotation.X = x1;
                    annotation.Y = y1;
                    annotation.X2 = x2;
                    annotation.Y2 = y2;

                    // Parse optional color and strokewidth
                    for (int i = 4; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#") || p.StartsWith("rgb"))
                            annotation.Color = p;
                        else if (double.TryParse(p, System.Globalization.NumberStyles.Any,
                            System.Globalization.CultureInfo.InvariantCulture, out var sw))
                            annotation.StrokeWidth = sw;
                    }
                }
                return annotation;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Parse line annotation: x1, y1, x2, y2 or hline: y or vline: x [, color, strokewidth]
        /// </summary>
        private PlotAnnotation ParseLineAnnotation(string key, string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = key };
                var parts = value.Split(',');

                if (key == "hline")
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    annotation.Y = y;
                    // Parse optional color
                    for (int i = 1; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#")) annotation.Color = p;
                    }
                }
                else if (key == "vline")
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    annotation.X = x;
                    for (int i = 1; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#")) annotation.Color = p;
                    }
                }
                else if (parts.Length >= 4)
                {
                    annotation.Type = "line";
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x1);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y1);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x2);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y2);
                    annotation.X = x1;
                    annotation.Y = y1;
                    annotation.X2 = x2;
                    annotation.Y2 = y2;
                    for (int i = 4; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#")) annotation.Color = p;
                    }
                }
                return annotation;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Parse shape annotation: rect x, y, w, h or circle x, y, r [, color, fill]
        /// </summary>
        private PlotAnnotation ParseShapeAnnotation(string key, string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = key.StartsWith("rect") ? "rect" : "circle" };
                var parts = value.Split(',');

                if (annotation.Type == "rect" && parts.Length >= 4)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var w);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var h);
                    annotation.X = x;
                    annotation.Y = y;
                    annotation.X2 = w;  // width
                    annotation.Y2 = h;  // height
                    for (int i = 4; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#"))
                        {
                            if (string.IsNullOrEmpty(annotation.Fill) || annotation.Fill == "none")
                                annotation.Color = p;
                            else
                                annotation.Fill = p;
                        }
                        else if (p == "fill" || p == "filled" || p == "lleno")
                            annotation.Fill = annotation.Color;
                    }
                }
                else if (annotation.Type == "circle" && parts.Length >= 3)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var r);
                    annotation.X = x;
                    annotation.Y = y;
                    annotation.X2 = r;  // radius
                    for (int i = 3; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#"))
                        {
                            if (string.IsNullOrEmpty(annotation.Fill) || annotation.Fill == "none")
                                annotation.Color = p;
                            else
                                annotation.Fill = p;
                        }
                        else if (p == "fill" || p == "filled" || p == "lleno")
                            annotation.Fill = annotation.Color;
                    }
                }
                return annotation;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Parse projection annotation: x, y [, color, style]
        /// Draws dashed lines from point (x,y) to both axes
        /// </summary>
        private PlotAnnotation ParseProjectionAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "projection" };
                var parts = value.Split(',');

                if (parts.Length >= 2)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    annotation.X = x;
                    annotation.Y = y;
                    annotation.Color = "#666666";  // Default gray dashed
                    annotation.StrokeWidth = 1;

                    for (int i = 2; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#")) annotation.Color = p;
                    }
                }
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Parse tick annotation: value, "label" [, color]
        /// Adds custom label at axis position
        /// </summary>
        private PlotAnnotation ParseTickAnnotation(string key, string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = key.Contains("x") ? "xtick" : "ytick" };

                // Find quoted text
                int quoteStart = value.IndexOf('"');
                int quoteEnd = value.LastIndexOf('"');
                if (quoteStart < 0 || quoteEnd <= quoteStart)
                {
                    quoteStart = value.IndexOf('\'');
                    quoteEnd = value.LastIndexOf('\'');
                }

                if (quoteStart >= 0 && quoteEnd > quoteStart)
                {
                    annotation.Text = value.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);
                    var beforeQuote = value.Substring(0, quoteStart).Trim().TrimEnd(',');
                    double.TryParse(beforeQuote, System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var pos);

                    if (annotation.Type == "xtick")
                        annotation.X = pos;
                    else
                        annotation.Y = pos;

                    // Parse options after quote
                    if (quoteEnd < value.Length - 1)
                    {
                        var afterQuote = value.Substring(quoteEnd + 1).Split(',');
                        foreach (var p in afterQuote)
                        {
                            var pt = p.Trim();
                            if (pt.StartsWith("#")) annotation.Color = pt;
                        }
                    }
                }
                annotation.FontSize = 12;
                annotation.Italic = true;
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Parse angle annotation: x, y, startAngle, endAngle, radius, "label" [, color]
        /// Draws an arc indicating an angle
        /// </summary>
        private PlotAnnotation ParseAngleAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "angle" };

                // Find quoted text for label
                int quoteStart = value.IndexOf('"');
                int quoteEnd = value.LastIndexOf('"');
                if (quoteStart < 0 || quoteEnd <= quoteStart)
                {
                    quoteStart = value.IndexOf('\'');
                    quoteEnd = value.LastIndexOf('\'');
                }

                string numericPart = quoteStart > 0 ? value.Substring(0, quoteStart) : value;
                var parts = numericPart.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

                if (parts.Length >= 5)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var startAngle);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var endAngle);
                    double.TryParse(parts[4].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var radius);

                    annotation.X = x;
                    annotation.Y = y;
                    annotation.X2 = startAngle;  // Store start angle
                    annotation.Y2 = endAngle;    // Store end angle
                    annotation.Rotation = radius; // Store radius (reusing Rotation field)
                }

                if (quoteStart >= 0 && quoteEnd > quoteStart)
                {
                    annotation.Text = value.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);
                }

                // Parse color after quote
                if (quoteEnd > 0 && quoteEnd < value.Length - 1)
                {
                    var afterQuote = value.Substring(quoteEnd + 1).Split(',');
                    foreach (var p in afterQuote)
                    {
                        var pt = p.Trim();
                        if (pt.StartsWith("#")) annotation.Color = pt;
                    }
                }

                annotation.FontSize = 11;
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Parse brace/bracket annotation: x1, y1, x2, y2, "label" [, color, position]
        /// Draws a curly brace between two points with a label
        /// position: above/below/left/right
        /// </summary>
        private PlotAnnotation ParseBraceAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "brace" };

                // Find quoted text
                int quoteStart = value.IndexOf('"');
                int quoteEnd = value.LastIndexOf('"');
                if (quoteStart < 0 || quoteEnd <= quoteStart)
                {
                    quoteStart = value.IndexOf('\'');
                    quoteEnd = value.LastIndexOf('\'');
                }

                string numericPart = quoteStart > 0 ? value.Substring(0, quoteStart) : value;
                var parts = numericPart.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

                if (parts.Length >= 4)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x1);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y1);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x2);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y2);

                    annotation.X = x1;
                    annotation.Y = y1;
                    annotation.X2 = x2;
                    annotation.Y2 = y2;
                }

                if (quoteStart >= 0 && quoteEnd > quoteStart)
                {
                    annotation.Text = value.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);
                }

                // Parse options after quote
                annotation.Anchor = "below";  // Default position
                if (quoteEnd > 0 && quoteEnd < value.Length - 1)
                {
                    var afterQuote = value.Substring(quoteEnd + 1).Split(',');
                    foreach (var p in afterQuote)
                    {
                        var pt = p.Trim().ToLower();
                        if (pt.StartsWith("#")) annotation.Color = pt;
                        else if (pt == "above" || pt == "arriba" || pt == "top") annotation.Anchor = "above";
                        else if (pt == "below" || pt == "abajo" || pt == "bottom") annotation.Anchor = "below";
                        else if (pt == "left" || pt == "izquierda") annotation.Anchor = "left";
                        else if (pt == "right" || pt == "derecha") annotation.Anchor = "right";
                    }
                }

                annotation.FontSize = 11;
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Parse point annotation: x, y [, color, size, filled]
        /// Draws a point/dot marker
        /// </summary>
        private PlotAnnotation ParsePointAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "point" };
                var parts = value.Split(',');

                if (parts.Length >= 2)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y);
                    annotation.X = x;
                    annotation.Y = y;
                    annotation.X2 = 5;  // Default radius
                    annotation.Fill = "filled";  // Default filled

                    for (int i = 2; i < parts.Length; i++)
                    {
                        var p = parts[i].Trim();
                        if (p.StartsWith("#")) annotation.Color = p;
                        else if (double.TryParse(p, System.Globalization.NumberStyles.Any,
                            System.Globalization.CultureInfo.InvariantCulture, out var size))
                            annotation.X2 = size;
                        else if (p == "empty" || p == "vacio" || p == "outline")
                            annotation.Fill = "none";
                        else if (p == "filled" || p == "lleno" || p == "fill")
                            annotation.Fill = "filled";
                    }
                }
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Parse dimension annotation with double-headed arrow: x1, y1, x2, y2, "label" [, color, offset]
        /// Draws a line with arrows at both ends and a label
        /// </summary>
        private PlotAnnotation ParseDimensionAnnotation(string value)
        {
            try
            {
                var annotation = new PlotAnnotation { Type = "dimension" };

                // Find quoted text
                int quoteStart = value.IndexOf('"');
                int quoteEnd = value.LastIndexOf('"');
                if (quoteStart < 0 || quoteEnd <= quoteStart)
                {
                    quoteStart = value.IndexOf('\'');
                    quoteEnd = value.LastIndexOf('\'');
                }

                string numericPart = quoteStart > 0 ? value.Substring(0, quoteStart) : value;
                var parts = numericPart.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

                if (parts.Length >= 4)
                {
                    double.TryParse(parts[0].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x1);
                    double.TryParse(parts[1].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y1);
                    double.TryParse(parts[2].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var x2);
                    double.TryParse(parts[3].Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var y2);

                    annotation.X = x1;
                    annotation.Y = y1;
                    annotation.X2 = x2;
                    annotation.Y2 = y2;
                }

                if (quoteStart >= 0 && quoteEnd > quoteStart)
                {
                    annotation.Text = value.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);
                }

                // Parse options after quote
                annotation.Rotation = 0;  // Used for offset
                annotation.Color = "#333333";
                if (quoteEnd > 0 && quoteEnd < value.Length - 1)
                {
                    var afterQuote = value.Substring(quoteEnd + 1).Split(',');
                    foreach (var p in afterQuote)
                    {
                        var pt = p.Trim();
                        if (pt.StartsWith("#")) annotation.Color = pt;
                        else if (double.TryParse(pt, System.Globalization.NumberStyles.Any,
                            System.Globalization.CultureInfo.InvariantCulture, out var offset))
                            annotation.Rotation = offset;  // Store offset in Rotation
                    }
                }

                annotation.FontSize = 11;
                return annotation;
            }
            catch { return null; }
        }

        /// <summary>
        /// Get plot data from variable name or inline array
        /// </summary>
        private double[] GetPlotData(string dataSpec, Dictionary<string, object> variables)
        {
            if (string.IsNullOrEmpty(dataSpec)) return null;

            // Check if it's an inline array: [1; 2; 3] or [1, 2, 3]
            if (dataSpec.StartsWith("[") && dataSpec.EndsWith("]"))
            {
                var inner = dataSpec.Substring(1, dataSpec.Length - 2);
                var values = inner.Split(new[] { ';', ',' }, StringSplitOptions.RemoveEmptyEntries);
                var result = new List<double>();
                foreach (var v in values)
                {
                    var cleanVal = v.Trim();
                    // Remove unit if present (e.g., "2.5'm" -> "2.5")
                    var quoteIdx = cleanVal.IndexOf('\'');
                    if (quoteIdx > 0) cleanVal = cleanVal.Substring(0, quoteIdx);

                    if (double.TryParse(cleanVal, System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var val))
                        result.Add(val);
                }
                return result.Count > 0 ? result.ToArray() : null;
            }

            // It's a variable name
            var varName = dataSpec.Trim();
            if (!variables.TryGetValue(varName, out var data))
                return null;

            // Convert to double array
            if (data is double[] arr) return arr;
            if (data is double d) return new[] { d };
            if (data is double[,] matrix)
            {
                // Flatten matrix (column-first)
                var rows = matrix.GetLength(0);
                var cols = matrix.GetLength(1);
                var flat = new double[rows * cols];
                int idx = 0;
                for (int c = 0; c < cols; c++)
                    for (int r = 0; r < rows; r++)
                        flat[idx++] = matrix[r, c];
                return flat;
            }

            return null;
        }

        /// <summary>
        /// Generate SVG plot with Mathcad Prime style (arrows, grid paper, italic labels, markers, annotations)
        /// </summary>
        private string GeneratePlotSvg(double[] x, double[] y, double xmin, double xmax, double ymin, double ymax,
            string xlabel, string ylabel, string title, string legend, string color, string lineStyle,
            string symbol, int symbolSize, double lineWidth, bool showGrid, int width, int height,
            bool smooth = false, double smoothTension = 0.3, List<PlotAnnotation> annotations = null)
        {
            const int margin = 70;
            const int marginTop = 30;
            const int marginRight = 30;
            const int marginBottom = 50;

            var plotWidth = width - margin - marginRight;
            var plotHeight = height - marginTop - marginBottom;

            var scaleX = plotWidth / (xmax - xmin);
            var scaleY = plotHeight / (ymax - ymin);

            var sb = new StringBuilder();

            // SVG header with defs for arrow markers
            sb.Append($"<svg class=\"plot\" width=\"{width}\" height=\"{height}\" xmlns=\"http://www.w3.org/2000/svg\">");

            // Define arrow markers (for axes and annotations)
            sb.Append("<defs>");
            sb.Append("<marker id=\"arrowhead\" markerWidth=\"10\" markerHeight=\"7\" refX=\"9\" refY=\"3.5\" orient=\"auto\">");
            sb.Append("<polygon points=\"0 0, 10 3.5, 0 7\" fill=\"#333\"/>");
            sb.Append("</marker>");
            sb.Append("<marker id=\"arrowhead-annotation\" markerWidth=\"8\" markerHeight=\"6\" refX=\"7\" refY=\"3\" orient=\"auto\">");
            sb.Append("<polygon points=\"0 0, 8 3, 0 6\" fill=\"currentColor\"/>");
            sb.Append("</marker>");
            sb.Append("</defs>");

            // Background - papel milimetrado (azul claro)
            sb.Append($"<rect width=\"{width}\" height=\"{height}\" fill=\"#f0f8ff\"/>");

            // Plot area background - slightly lighter
            sb.Append($"<rect x=\"{margin}\" y=\"{marginTop}\" width=\"{plotWidth}\" height=\"{plotHeight}\" fill=\"#f8fbff\"/>");

            // Grid - papel milimetrado style
            if (showGrid)
            {
                sb.Append(GenerateMathcadGrid(margin, marginTop, plotWidth, plotHeight, xmin, xmax, ymin, ymax, scaleX, scaleY));
            }

            // Axes with arrows (drawn over grid)
            // Y-axis with arrow pointing up
            sb.Append($"<line x1=\"{margin}\" y1=\"{marginTop + plotHeight}\" x2=\"{margin}\" y2=\"{marginTop - 10}\" stroke=\"#333\" stroke-width=\"1.5\" marker-end=\"url(#arrowhead)\"/>");
            // X-axis with arrow pointing right
            sb.Append($"<line x1=\"{margin}\" y1=\"{marginTop + plotHeight}\" x2=\"{margin + plotWidth + 15}\" y2=\"{marginTop + plotHeight}\" stroke=\"#333\" stroke-width=\"1.5\" marker-end=\"url(#arrowhead)\"/>");

            // Convert line style to SVG dash array
            string dashArray = lineStyle switch
            {
                "dash" or "dashed" or "---" => "10,5",
                "dot" or "dotted" or "..." => "3,3",
                "dashdot" or "-.-" => "10,3,3,3",
                "longdash" or "--" => "15,5",
                "shortdash" => "5,3",
                "none" => "0,1000", // effectively invisible line
                _ => "" // solid
            };

            // Calculate point coordinates
            var points = new List<(double px, double py)>();
            for (int i = 0; i < x.Length; i++)
            {
                var px = margin + (x[i] - xmin) * scaleX;
                var py = marginTop + plotHeight - (y[i] - ymin) * scaleY;
                // Clip to plot area
                px = Math.Max(margin, Math.Min(margin + plotWidth, px));
                py = Math.Max(marginTop, Math.Min(marginTop + plotHeight, py));
                points.Add((px, py));
            }

            // Data line (if style is not "none")
            if (lineStyle != "none")
            {
                if (smooth && points.Count >= 2)
                {
                    // Use smooth Bezier curves (Catmull-Rom spline converted to cubic Bezier)
                    sb.Append($"<path d=\"{GenerateSmoothPath(points, smoothTension)}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"{lineWidth:F1}\"");
                }
                else
                {
                    // Use straight line segments (polyline)
                    sb.Append($"<polyline points=\"");
                    foreach (var (px, py) in points)
                    {
                        sb.Append($"{px:F2},{py:F2} ");
                    }
                    sb.Append($"\" fill=\"none\" stroke=\"{color}\" stroke-width=\"{lineWidth:F1}\"");
                }
                if (!string.IsNullOrEmpty(dashArray))
                    sb.Append($" stroke-dasharray=\"{dashArray}\"");
                sb.Append("/>");
            }

            // Draw markers/symbols at each data point
            if (symbol != "none" && symbol != "ninguno")
            {
                foreach (var (px, py) in points)
                {
                    sb.Append(GenerateMarker(px, py, symbol, symbolSize, color));
                }
            }

            // Draw annotations (text, arrows, lines, shapes)
            if (annotations != null && annotations.Count > 0)
            {
                sb.Append(GenerateAnnotations(annotations, margin, marginTop, plotWidth, plotHeight, xmin, xmax, ymin, ymax, scaleX, scaleY));
            }

            // X-axis label (italic, with underline like Mathcad)
            var xlabelX = margin + plotWidth / 2;
            var xlabelY = height - 8;
            sb.Append($"<text x=\"{xlabelX}\" y=\"{xlabelY}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"14\" font-style=\"italic\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(xlabel)}</text>");
            // Underline for x label
            var xlabelWidth = xlabel.Length * 7;
            sb.Append($"<line x1=\"{xlabelX - xlabelWidth/2}\" y1=\"{xlabelY + 3}\" x2=\"{xlabelX + xlabelWidth/2}\" y2=\"{xlabelY + 3}\" stroke=\"#003366\" stroke-width=\"1\"/>");

            // Y-axis label (italic, rotated, with underline like Mathcad)
            var ylabelX = 15;
            var ylabelY = marginTop + plotHeight / 2;
            sb.Append($"<g transform=\"rotate(-90, {ylabelX}, {ylabelY})\">");
            sb.Append($"<text x=\"{ylabelX}\" y=\"{ylabelY}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"14\" font-style=\"italic\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(ylabel)}</text>");
            // Underline for y label (fixed: was using xlabelX instead of ylabelX)
            var ylabelWidth = ylabel.Length * 7;
            sb.Append($"<line x1=\"{ylabelX - ylabelWidth/2}\" y1=\"{ylabelY + 3}\" x2=\"{ylabelX + ylabelWidth/2}\" y2=\"{ylabelY + 3}\" stroke=\"#003366\" stroke-width=\"1\"/>");
            sb.Append("</g>");

            // Title (if provided)
            if (!string.IsNullOrEmpty(title))
            {
                sb.Append($"<text x=\"{width / 2}\" y=\"18\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"13\" font-weight=\"bold\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(title)}</text>");
            }

            // Legend (if provided)
            if (!string.IsNullOrEmpty(legend))
            {
                var legendX = margin + plotWidth - 90;
                var legendY = marginTop + 20;
                sb.Append($"<rect x=\"{legendX - 5}\" y=\"{legendY - 12}\" width=\"95\" height=\"22\" fill=\"white\" fill-opacity=\"0.9\" stroke=\"#ccc\" rx=\"3\"/>");
                // Legend line
                sb.Append($"<line x1=\"{legendX}\" y1=\"{legendY}\" x2=\"{legendX + 20}\" y2=\"{legendY}\" stroke=\"{color}\" stroke-width=\"{lineWidth:F1}\"");
                if (!string.IsNullOrEmpty(dashArray))
                    sb.Append($" stroke-dasharray=\"{dashArray}\"");
                sb.Append("/>");
                // Legend marker
                if (symbol != "none" && symbol != "ninguno")
                {
                    sb.Append(GenerateMarker(legendX + 10, legendY, symbol, symbolSize, color));
                }
                sb.Append($"<text x=\"{legendX + 25}\" y=\"{legendY + 4}\" font-family=\"Times New Roman, serif\" font-size=\"11\" font-style=\"italic\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(legend)}</text>");
            }

            sb.Append("</svg>");
            return sb.ToString();
        }

        /// <summary>
        /// Generate SVG plot with multiple data series support
        /// </summary>
        private string GeneratePlotSvgMultiSeries(double[] x, List<double[]> allYValues, List<PlotSeries> series,
            double xmin, double xmax, double ymin, double ymax,
            string xlabel, string ylabel, string title, bool showGrid, bool showLegend, string background, int width, int height,
            List<PlotAnnotation> annotations = null)
        {
            const int margin = 70;
            const int marginTop = 30;
            const int marginRight = 30;
            const int marginBottom = 50;

            var plotWidth = width - margin - marginRight;
            var plotHeight = height - marginTop - marginBottom;

            var scaleX = plotWidth / (xmax - xmin);
            var scaleY = plotHeight / (ymax - ymin);

            var sb = new StringBuilder();

            // SVG header with defs for arrow markers
            sb.Append($"<svg class=\"plot\" width=\"{width}\" height=\"{height}\" xmlns=\"http://www.w3.org/2000/svg\">");

            // Define arrow markers (for axes and annotations)
            sb.Append("<defs>");
            sb.Append("<marker id=\"arrowhead\" markerWidth=\"10\" markerHeight=\"7\" refX=\"9\" refY=\"3.5\" orient=\"auto\">");
            sb.Append("<polygon points=\"0 0, 10 3.5, 0 7\" fill=\"#333\"/>");
            sb.Append("</marker>");
            sb.Append("<marker id=\"arrowhead-annotation\" markerWidth=\"8\" markerHeight=\"6\" refX=\"7\" refY=\"3\" orient=\"auto\">");
            sb.Append("<polygon points=\"0 0, 8 3, 0 6\" fill=\"currentColor\"/>");
            sb.Append("</marker>");
            // Double-headed arrow markers for dimensions
            sb.Append("<marker id=\"arrowhead-start\" markerWidth=\"8\" markerHeight=\"6\" refX=\"1\" refY=\"3\" orient=\"auto\">");
            sb.Append("<polygon points=\"8 0, 0 3, 8 6\" fill=\"#333\"/>");
            sb.Append("</marker>");
            sb.Append("<marker id=\"arrowhead-end\" markerWidth=\"8\" markerHeight=\"6\" refX=\"7\" refY=\"3\" orient=\"auto\">");
            sb.Append("<polygon points=\"0 0, 8 3, 0 6\" fill=\"#333\"/>");
            sb.Append("</marker>");
            sb.Append("</defs>");

            // Background - depends on style
            bool isWhiteBackground = background == "white" || background == "blanco" || background == "clean" || background == "limpio";
            if (isWhiteBackground)
            {
                sb.Append($"<rect width=\"{width}\" height=\"{height}\" fill=\"white\"/>");
                sb.Append($"<rect x=\"{margin}\" y=\"{marginTop}\" width=\"{plotWidth}\" height=\"{plotHeight}\" fill=\"white\"/>");
            }
            else
            {
                sb.Append($"<rect width=\"{width}\" height=\"{height}\" fill=\"#f0f8ff\"/>");
                sb.Append($"<rect x=\"{margin}\" y=\"{marginTop}\" width=\"{plotWidth}\" height=\"{plotHeight}\" fill=\"#f8fbff\"/>");
            }

            // Grid
            if (showGrid)
            {
                if (isWhiteBackground)
                {
                    sb.Append(GenerateSimpleGrid(margin, marginTop, plotWidth, plotHeight, xmin, xmax, ymin, ymax, scaleX, scaleY));
                }
                else
                {
                    sb.Append(GenerateMathcadGrid(margin, marginTop, plotWidth, plotHeight, xmin, xmax, ymin, ymax, scaleX, scaleY));
                }
            }

            // Axes with arrows (drawn over grid)
            sb.Append($"<line x1=\"{margin}\" y1=\"{marginTop + plotHeight}\" x2=\"{margin}\" y2=\"{marginTop - 10}\" stroke=\"#333\" stroke-width=\"1.5\" marker-end=\"url(#arrowhead)\"/>");
            sb.Append($"<line x1=\"{margin}\" y1=\"{marginTop + plotHeight}\" x2=\"{margin + plotWidth + 15}\" y2=\"{marginTop + plotHeight}\" stroke=\"#333\" stroke-width=\"1.5\" marker-end=\"url(#arrowhead)\"/>");

            // Draw all data series
            for (int seriesIdx = 0; seriesIdx < series.Count && seriesIdx < allYValues.Count; seriesIdx++)
            {
                var s = series[seriesIdx];
                var y = allYValues[seriesIdx];

                // Convert line style to SVG dash array
                string dashArray = s.LineStyle switch
                {
                    "dash" or "dashed" or "---" => "10,5",
                    "dot" or "dotted" or "..." => "3,3",
                    "dashdot" or "-.-" => "10,3,3,3",
                    "longdash" or "--" => "15,5",
                    "shortdash" => "5,3",
                    "none" => "0,1000",
                    _ => ""
                };

                // Calculate point coordinates
                var points = new List<(double px, double py)>();
                for (int i = 0; i < x.Length; i++)
                {
                    var px = margin + (x[i] - xmin) * scaleX;
                    var py = marginTop + plotHeight - (y[i] - ymin) * scaleY;
                    px = Math.Max(margin, Math.Min(margin + plotWidth, px));
                    py = Math.Max(marginTop, Math.Min(marginTop + plotHeight, py));
                    points.Add((px, py));
                }

                // Data line (if style is not "none")
                if (s.LineStyle != "none")
                {
                    if (s.Smooth && points.Count >= 2)
                    {
                        sb.Append($"<path d=\"{GenerateSmoothPath(points, s.SmoothTension)}\" fill=\"none\" stroke=\"{s.Color}\" stroke-width=\"{s.LineWidth:F1}\"");
                    }
                    else
                    {
                        sb.Append($"<polyline points=\"");
                        foreach (var (px, py) in points)
                        {
                            sb.Append($"{px:F2},{py:F2} ");
                        }
                        sb.Append($"\" fill=\"none\" stroke=\"{s.Color}\" stroke-width=\"{s.LineWidth:F1}\"");
                    }
                    if (!string.IsNullOrEmpty(dashArray))
                        sb.Append($" stroke-dasharray=\"{dashArray}\"");
                    sb.Append("/>");
                }

                // Draw markers/symbols at each data point
                if (s.Symbol != "none" && s.Symbol != "ninguno")
                {
                    foreach (var (px, py) in points)
                    {
                        sb.Append(GenerateMarker(px, py, s.Symbol, s.SymbolSize, s.Color));
                    }
                }
            }

            // Draw annotations (text, arrows, lines, shapes)
            if (annotations != null && annotations.Count > 0)
            {
                sb.Append(GenerateAnnotations(annotations, margin, marginTop, plotWidth, plotHeight, xmin, xmax, ymin, ymax, scaleX, scaleY));
            }

            // X-axis label
            var xlabelX = margin + plotWidth / 2;
            var xlabelY = height - 8;
            sb.Append($"<text x=\"{xlabelX}\" y=\"{xlabelY}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"14\" font-style=\"italic\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(xlabel)}</text>");
            var xlabelWidth = xlabel.Length * 7;
            sb.Append($"<line x1=\"{xlabelX - xlabelWidth/2}\" y1=\"{xlabelY + 3}\" x2=\"{xlabelX + xlabelWidth/2}\" y2=\"{xlabelY + 3}\" stroke=\"#003366\" stroke-width=\"1\"/>");

            // Y-axis label
            var ylabelX = 15;
            var ylabelY = marginTop + plotHeight / 2;
            sb.Append($"<g transform=\"rotate(-90, {ylabelX}, {ylabelY})\">");
            sb.Append($"<text x=\"{ylabelX}\" y=\"{ylabelY}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"14\" font-style=\"italic\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(ylabel)}</text>");
            // Underline for y label (fixed: was using xlabelX instead of ylabelX)
            var ylabelWidth = ylabel.Length * 7;
            sb.Append($"<line x1=\"{ylabelX - ylabelWidth/2}\" y1=\"{ylabelY + 3}\" x2=\"{ylabelX + ylabelWidth/2}\" y2=\"{ylabelY + 3}\" stroke=\"#003366\" stroke-width=\"1\"/>");
            sb.Append("</g>");

            // Title (if provided)
            if (!string.IsNullOrEmpty(title))
            {
                sb.Append($"<text x=\"{width / 2}\" y=\"18\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"13\" font-weight=\"bold\" fill=\"#003366\">{System.Web.HttpUtility.HtmlEncode(title)}</text>");
            }

            // Legend for multiple series (only if showLegend is true)
            var legendSeries = series.Where(s => !string.IsNullOrEmpty(s.Legend)).ToList();
            if (showLegend && legendSeries.Count > 0)
            {
                var legendX = margin + plotWidth - 100;
                var legendY = marginTop + 15;
                var legendHeight = legendSeries.Count * 18 + 8;

                sb.Append($"<rect x=\"{legendX - 5}\" y=\"{legendY - 12}\" width=\"105\" height=\"{legendHeight}\" fill=\"white\" fill-opacity=\"0.9\" stroke=\"#ccc\" rx=\"3\"/>");

                for (int i = 0; i < legendSeries.Count; i++)
                {
                    var s = legendSeries[i];
                    var ly = legendY + i * 18;

                    // Legend line style
                    string dashArray = s.LineStyle switch
                    {
                        "dash" or "dashed" => "6,3",
                        "dot" or "dotted" => "2,2",
                        "dashdot" => "6,2,2,2",
                        _ => ""
                    };

                    sb.Append($"<line x1=\"{legendX}\" y1=\"{ly}\" x2=\"{legendX + 20}\" y2=\"{ly}\" stroke=\"{s.Color}\" stroke-width=\"{s.LineWidth:F1}\"");
                    if (!string.IsNullOrEmpty(dashArray))
                        sb.Append($" stroke-dasharray=\"{dashArray}\"");
                    sb.Append("/>");

                    if (s.Symbol != "none" && s.Symbol != "ninguno")
                    {
                        sb.Append(GenerateMarker(legendX + 10, ly, s.Symbol, s.SymbolSize, s.Color));
                    }

                    sb.Append($"<text x=\"{legendX + 25}\" y=\"{ly + 4}\" font-family=\"Times New Roman, serif\" font-size=\"11\" font-style=\"italic\" fill=\"{s.Color}\">{System.Web.HttpUtility.HtmlEncode(s.Legend)}</text>");
                }
            }

            sb.Append("</svg>");
            return sb.ToString();
        }

        /// <summary>
        /// Generate SVG for all annotations
        /// </summary>
        private string GenerateAnnotations(List<PlotAnnotation> annotations, int margin, int marginTop,
            int plotWidth, int plotHeight, double xmin, double xmax, double ymin, double ymax, double scaleX, double scaleY)
        {
            var sb = new StringBuilder();

            foreach (var ann in annotations)
            {
                // Convert data coordinates to pixel coordinates
                double px = margin + (ann.X - xmin) * scaleX;
                double py = marginTop + plotHeight - (ann.Y - ymin) * scaleY;
                double px2 = margin + (ann.X2 - xmin) * scaleX;
                double py2 = marginTop + plotHeight - (ann.Y2 - ymin) * scaleY;

                switch (ann.Type)
                {
                    case "text":
                        var fontStyle = ann.Italic ? "italic" : "normal";
                        var fontWeight = ann.Bold ? "bold" : "normal";
                        if (Math.Abs(ann.Rotation) > 0.01)
                        {
                            sb.Append($"<g transform=\"rotate({-ann.Rotation:F1}, {px:F1}, {py:F1})\">");
                            sb.Append($"<text x=\"{px:F1}\" y=\"{py:F1}\" text-anchor=\"{ann.Anchor}\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"{fontStyle}\" font-weight=\"{fontWeight}\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                            sb.Append("</g>");
                        }
                        else
                        {
                            sb.Append($"<text x=\"{px:F1}\" y=\"{py:F1}\" text-anchor=\"{ann.Anchor}\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"{fontStyle}\" font-weight=\"{fontWeight}\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                        }
                        break;

                    case "arrow":
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{py:F1}\" x2=\"{px2:F1}\" y2=\"{py2:F1}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" marker-end=\"url(#arrowhead-annotation)\"/>");
                        break;

                    case "line":
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{py:F1}\" x2=\"{px2:F1}\" y2=\"{py2:F1}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\"/>");
                        break;

                    case "hline":
                        // Horizontal line at Y value across full width
                        sb.Append($"<line x1=\"{margin}\" y1=\"{py:F1}\" x2=\"{margin + plotWidth}\" y2=\"{py:F1}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" stroke-dasharray=\"5,3\"/>");
                        break;

                    case "vline":
                        // Vertical line at X value across full height
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" stroke-dasharray=\"5,3\"/>");
                        break;

                    case "rect":
                        // Rectangle: X, Y is bottom-left corner; X2, Y2 are width and height in data units
                        var rectW = ann.X2 * scaleX;
                        var rectH = ann.Y2 * scaleY;
                        var rectY = py - rectH;  // SVG Y is at top
                        sb.Append($"<rect x=\"{px:F1}\" y=\"{rectY:F1}\" width=\"{rectW:F1}\" height=\"{rectH:F1}\" fill=\"{ann.Fill}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" fill-opacity=\"0.3\"/>");
                        break;

                    case "circle":
                        // Circle: X, Y is center; X2 is radius in data units (use average of X and Y scale)
                        var avgScale = (scaleX + scaleY) / 2;
                        var circleR = ann.X2 * avgScale;
                        sb.Append($"<circle cx=\"{px:F1}\" cy=\"{py:F1}\" r=\"{circleR:F1}\" fill=\"{ann.Fill}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" fill-opacity=\"0.3\"/>");
                        break;

                    case "projection":
                        // Projection lines from point to both axes (dashed)
                        var projAxisY = marginTop + plotHeight;  // X-axis
                        var projAxisX = margin;                   // Y-axis
                        // Horizontal line to Y-axis
                        sb.Append($"<line x1=\"{projAxisX}\" y1=\"{py:F1}\" x2=\"{px:F1}\" y2=\"{py:F1}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" stroke-dasharray=\"4,3\"/>");
                        // Vertical line to X-axis
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{py:F1}\" x2=\"{px:F1}\" y2=\"{projAxisY}\" stroke=\"{ann.Color}\" stroke-width=\"{ann.StrokeWidth:F1}\" stroke-dasharray=\"4,3\"/>");
                        break;

                    case "xtick":
                        // Custom X-axis tick label
                        var xtickY = marginTop + plotHeight + 18;
                        sb.Append($"<text x=\"{px:F1}\" y=\"{xtickY}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"italic\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                        // Tick mark
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop + plotHeight}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight + 5}\" stroke=\"{ann.Color}\" stroke-width=\"1\"/>");
                        break;

                    case "ytick":
                        // Custom Y-axis tick label - positioned to the LEFT of Y-axis
                        sb.Append($"<text x=\"{margin - 12}\" y=\"{py + 4:F1}\" text-anchor=\"end\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"italic\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                        // Tick mark - small horizontal line extending left from axis
                        sb.Append($"<line x1=\"{margin - 5}\" y1=\"{py:F1}\" x2=\"{margin}\" y2=\"{py:F1}\" stroke=\"{ann.Color}\" stroke-width=\"1\"/>");
                        break;

                    case "angle":
                        // Draw angle arc with label - Technical drawing style (angle dimension)
                        // Format: angle: x, y, startAngle, endAngle, radius, "label", color
                        // The arc represents the angle swept from startAngle to endAngle.
                        // Positive sweep (end > start) = counterclockwise in math = visually upward
                        // Negative sweep (end < start) = clockwise in math = visually downward

                        // Convert radius from data units to pixels
                        var angleRadiusPx = ann.Rotation * scaleX;
                        if (angleRadiusPx < 5) angleRadiusPx = 5;  // Minimum visible

                        // Get the two angles specified by user
                        var startAngleDeg = ann.X2;
                        var endAngleDeg = ann.Y2;

                        // Convert to radians for point calculation
                        var startAngleRad = startAngleDeg * Math.PI / 180.0;
                        var endAngleRad = endAngleDeg * Math.PI / 180.0;

                        // Arc points at radius distance from the vertex (px, py)
                        // In SVG, Y increases downward, so we subtract sin() to flip the Y coordinate
                        var arcStartX = px + angleRadiusPx * Math.Cos(startAngleRad);
                        var arcStartY = py - angleRadiusPx * Math.Sin(startAngleRad);
                        var arcEndX = px + angleRadiusPx * Math.Cos(endAngleRad);
                        var arcEndY = py - angleRadiusPx * Math.Sin(endAngleRad);

                        // Calculate angular difference (preserving sign for direction)
                        var angleDiff = endAngleDeg - startAngleDeg;

                        // The arc should represent the actual angle the user specified
                        // |angleDiff| is the size of the arc
                        // sign of angleDiff determines direction:
                        //   positive = counterclockwise in math (increasing angles)
                        //   negative = clockwise in math (decreasing angles)

                        // For SVG arc:
                        // - largeArc: 1 if |angle| > 180, 0 otherwise
                        // - sweepFlag: Controls arc direction (inverted due to SVG Y-axis)
                        //   * sweepFlag=0 for positive angles (arc curves inside the angle)
                        //   * sweepFlag=1 for negative angles (arc curves inside the angle)

                        int largeArc = Math.Abs(angleDiff) > 180 ? 1 : 0;
                        int sweepFlag = angleDiff >= 0 ? 0 : 1;

                        // Draw the arc
                        sb.Append($"<path d=\"M {arcStartX:F1},{arcStartY:F1} A {angleRadiusPx:F1},{angleRadiusPx:F1} 0 {largeArc},{sweepFlag} {arcEndX:F1},{arcEndY:F1}\" fill=\"none\" stroke=\"{ann.Color}\" stroke-width=\"1.5\"/>");

                        // Label at the midpoint of the arc
                        if (!string.IsNullOrEmpty(ann.Text))
                        {
                            // Midpoint is at the average of start and end angles
                            var midAngleDeg = (startAngleDeg + endAngleDeg) / 2.0;
                            var midAngleRad = midAngleDeg * Math.PI / 180.0;
                            // Label slightly outside the arc for readability
                            var labelRadius = angleRadiusPx + 15.0;
                            var labelX = px + labelRadius * Math.Cos(midAngleRad);
                            var labelY = py - labelRadius * Math.Sin(midAngleRad) + 4;
                            sb.Append($"<text x=\"{labelX:F1}\" y=\"{labelY:F1}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize + 2}\" font-style=\"italic\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                        }
                        break;

                    case "brace":
                        // Draw brace/bracket between two points with label
                        // Determine orientation based on points
                        var braceIsHorizontal = Math.Abs(ann.Y - ann.Y2) < Math.Abs(ann.X - ann.X2);
                        var midX = (px + px2) / 2;
                        var midY = (py + py2) / 2;
                        var braceOffset = 15;

                        if (braceIsHorizontal)
                        {
                            // Horizontal brace (for Δx)
                            var braceY = ann.Anchor == "above" || ann.Anchor == "top" ? Math.Min(py, py2) - braceOffset : Math.Max(py, py2) + braceOffset;
                            // Draw brace shape using path
                            var leftX = Math.Min(px, px2);
                            var rightX = Math.Max(px, px2);
                            var curveHeight = ann.Anchor == "above" || ann.Anchor == "top" ? -8 : 8;

                            // Simple brace: |_____|  with middle peak
                            sb.Append($"<path d=\"M {leftX:F1},{braceY - curveHeight:F1} L {leftX:F1},{braceY:F1} L {midX - 5:F1},{braceY:F1} L {midX:F1},{braceY + curveHeight:F1} L {midX + 5:F1},{braceY:F1} L {rightX:F1},{braceY:F1} L {rightX:F1},{braceY - curveHeight:F1}\" fill=\"none\" stroke=\"{ann.Color}\" stroke-width=\"1\"/>");

                            // Label
                            if (!string.IsNullOrEmpty(ann.Text))
                            {
                                var labelY2 = braceY + curveHeight * 2;
                                sb.Append($"<text x=\"{midX:F1}\" y=\"{labelY2:F1}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"italic\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                            }
                        }
                        else
                        {
                            // Vertical brace (for Δy)
                            var braceX = ann.Anchor == "left" || ann.Anchor == "izquierda" ? Math.Min(px, px2) - braceOffset : Math.Max(px, px2) + braceOffset;
                            var topY = Math.Min(py, py2);
                            var bottomY = Math.Max(py, py2);
                            var curveWidth = ann.Anchor == "left" || ann.Anchor == "izquierda" ? -8 : 8;

                            // Vertical brace
                            sb.Append($"<path d=\"M {braceX - curveWidth:F1},{topY:F1} L {braceX:F1},{topY:F1} L {braceX:F1},{midY - 5:F1} L {braceX + curveWidth:F1},{midY:F1} L {braceX:F1},{midY + 5:F1} L {braceX:F1},{bottomY:F1} L {braceX - curveWidth:F1},{bottomY:F1}\" fill=\"none\" stroke=\"{ann.Color}\" stroke-width=\"1\"/>");

                            // Label
                            if (!string.IsNullOrEmpty(ann.Text))
                            {
                                var labelX2 = braceX + curveWidth * 2;
                                sb.Append($"<text x=\"{labelX2:F1}\" y=\"{midY + 4:F1}\" text-anchor=\"{(ann.Anchor == "left" ? "end" : "start")}\" font-family=\"Times New Roman, serif\" font-size=\"{ann.FontSize}\" font-style=\"italic\" fill=\"{ann.Color}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                            }
                        }
                        break;

                    case "point":
                        // Draw point/dot at coordinates
                        var pointRadius = ann.X2;
                        if (ann.Fill == "filled")
                        {
                            sb.Append($"<circle cx=\"{px:F1}\" cy=\"{py:F1}\" r=\"{pointRadius:F1}\" fill=\"{ann.Color}\" stroke=\"none\"/>");
                        }
                        else
                        {
                            sb.Append($"<circle cx=\"{px:F1}\" cy=\"{py:F1}\" r=\"{pointRadius:F1}\" fill=\"white\" stroke=\"{ann.Color}\" stroke-width=\"1.5\"/>");
                        }
                        break;

                    case "dimension":
                        // Draw dimension line with double arrows at both ends (like technical drawings)
                        var dimX2 = margin + (ann.X2 - xmin) * scaleX;
                        var dimY2 = marginTop + plotHeight - (ann.Y2 - ymin) * scaleY;
                        var dimColor = string.IsNullOrEmpty(ann.Color) ? "#333333" : ann.Color;
                        var dimStroke = ann.FontSize > 0 ? 1.5 : 1.2;

                        // Determine if horizontal or vertical dimension
                        var isHorizontal = Math.Abs(dimY2 - py) < Math.Abs(dimX2 - px);

                        // Draw the dimension line with arrow markers
                        sb.Append($"<line x1=\"{px:F1}\" y1=\"{py:F1}\" x2=\"{dimX2:F1}\" y2=\"{dimY2:F1}\" stroke=\"{dimColor}\" stroke-width=\"{dimStroke:F1}\" marker-start=\"url(#arrowhead-start)\" marker-end=\"url(#arrowhead-end)\"/>");

                        // Draw extension lines (small perpendicular lines at the ends)
                        var extLen = 8.0;
                        if (isHorizontal)
                        {
                            // Vertical extension lines
                            sb.Append($"<line x1=\"{px:F1}\" y1=\"{py - extLen:F1}\" x2=\"{px:F1}\" y2=\"{py + extLen:F1}\" stroke=\"{dimColor}\" stroke-width=\"1\"/>");
                            sb.Append($"<line x1=\"{dimX2:F1}\" y1=\"{dimY2 - extLen:F1}\" x2=\"{dimX2:F1}\" y2=\"{dimY2 + extLen:F1}\" stroke=\"{dimColor}\" stroke-width=\"1\"/>");
                        }
                        else
                        {
                            // Horizontal extension lines
                            sb.Append($"<line x1=\"{px - extLen:F1}\" y1=\"{py:F1}\" x2=\"{px + extLen:F1}\" y2=\"{py:F1}\" stroke=\"{dimColor}\" stroke-width=\"1\"/>");
                            sb.Append($"<line x1=\"{dimX2 - extLen:F1}\" y1=\"{dimY2:F1}\" x2=\"{dimX2 + extLen:F1}\" y2=\"{dimY2:F1}\" stroke=\"{dimColor}\" stroke-width=\"1\"/>");
                        }

                        // Draw label in the middle
                        if (!string.IsNullOrEmpty(ann.Text))
                        {
                            var labelMidX = (px + dimX2) / 2;
                            var labelMidY = (py + dimY2) / 2;
                            var labelOffset = 12.0;

                            if (isHorizontal)
                            {
                                // Label above or below horizontal line
                                labelMidY -= labelOffset;
                            }
                            else
                            {
                                // Label to the right of vertical line
                                labelMidX += labelOffset;
                            }

                            sb.Append($"<text x=\"{labelMidX:F1}\" y=\"{labelMidY:F1}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"{(ann.FontSize > 0 ? ann.FontSize : 11)}\" font-style=\"italic\" fill=\"{dimColor}\">{System.Web.HttpUtility.HtmlEncode(ann.Text)}</text>");
                        }
                        break;
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generate SVG marker symbol at given coordinates
        /// </summary>
        private string GenerateMarker(double cx, double cy, string symbol, int size, string color)
        {
            var s = size / 2.0;
            var sb = new StringBuilder();

            switch (symbol.ToLower())
            {
                case "x":
                case "cross":
                    // X marker
                    sb.Append($"<line x1=\"{cx - s:F1}\" y1=\"{cy - s:F1}\" x2=\"{cx + s:F1}\" y2=\"{cy + s:F1}\" stroke=\"{color}\" stroke-width=\"2\"/>");
                    sb.Append($"<line x1=\"{cx + s:F1}\" y1=\"{cy - s:F1}\" x2=\"{cx - s:F1}\" y2=\"{cy + s:F1}\" stroke=\"{color}\" stroke-width=\"2\"/>");
                    break;

                case "+":
                case "plus":
                    // Plus marker
                    sb.Append($"<line x1=\"{cx}\" y1=\"{cy - s:F1}\" x2=\"{cx}\" y2=\"{cy + s:F1}\" stroke=\"{color}\" stroke-width=\"2\"/>");
                    sb.Append($"<line x1=\"{cx - s:F1}\" y1=\"{cy}\" x2=\"{cx + s:F1}\" y2=\"{cy}\" stroke=\"{color}\" stroke-width=\"2\"/>");
                    break;

                case "o":
                case "circle":
                case "circulo":
                    // Circle (outline)
                    sb.Append($"<circle cx=\"{cx:F1}\" cy=\"{cy:F1}\" r=\"{s:F1}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                case ".":
                case "dot":
                case "punto":
                    // Filled circle (dot)
                    sb.Append($"<circle cx=\"{cx:F1}\" cy=\"{cy:F1}\" r=\"{s:F1}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;

                case "s":
                case "square":
                case "cuadrado":
                    // Square (outline)
                    sb.Append($"<rect x=\"{cx - s:F1}\" y=\"{cy - s:F1}\" width=\"{size}\" height=\"{size}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                case "sf":
                case "squarefilled":
                case "cuadradolleno":
                    // Filled square
                    sb.Append($"<rect x=\"{cx - s:F1}\" y=\"{cy - s:F1}\" width=\"{size}\" height=\"{size}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;

                case "d":
                case "diamond":
                case "diamante":
                case "rombo":
                    // Diamond (outline)
                    sb.Append($"<polygon points=\"{cx},{cy - s:F1} {cx + s:F1},{cy} {cx},{cy + s:F1} {cx - s:F1},{cy}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                case "df":
                case "diamondfilled":
                    // Filled diamond
                    sb.Append($"<polygon points=\"{cx},{cy - s:F1} {cx + s:F1},{cy} {cx},{cy + s:F1} {cx - s:F1},{cy}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;

                case "^":
                case "t":
                case "triangle":
                case "triangulo":
                    // Triangle up (outline)
                    sb.Append($"<polygon points=\"{cx},{cy - s:F1} {cx + s:F1},{cy + s:F1} {cx - s:F1},{cy + s:F1}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                case "tf":
                case "trianglefilled":
                    // Filled triangle
                    sb.Append($"<polygon points=\"{cx},{cy - s:F1} {cx + s:F1},{cy + s:F1} {cx - s:F1},{cy + s:F1}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;

                case "v":
                case "triangledown":
                    // Triangle down (outline)
                    sb.Append($"<polygon points=\"{cx},{cy + s:F1} {cx + s:F1},{cy - s:F1} {cx - s:F1},{cy - s:F1}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                case "*":
                case "star":
                case "estrella":
                    // Star (5 points)
                    var outerR = s;
                    var innerR = s * 0.4;
                    var starPoints = new StringBuilder();
                    for (int i = 0; i < 10; i++)
                    {
                        var r = (i % 2 == 0) ? outerR : innerR;
                        var angle = Math.PI / 2 + i * Math.PI / 5;
                        var sx = cx + r * Math.Cos(angle);
                        var sy = cy - r * Math.Sin(angle);
                        starPoints.Append($"{sx:F1},{sy:F1} ");
                    }
                    sb.Append($"<polygon points=\"{starPoints}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;

                case "starempty":
                case "estrellavacia":
                    // Star outline
                    var outerR2 = s;
                    var innerR2 = s * 0.4;
                    var starPoints2 = new StringBuilder();
                    for (int i = 0; i < 10; i++)
                    {
                        var r = (i % 2 == 0) ? outerR2 : innerR2;
                        var angle = Math.PI / 2 + i * Math.PI / 5;
                        var sx = cx + r * Math.Cos(angle);
                        var sy = cy - r * Math.Sin(angle);
                        starPoints2.Append($"{sx:F1},{sy:F1} ");
                    }
                    sb.Append($"<polygon points=\"{starPoints2}\" fill=\"none\" stroke=\"{color}\" stroke-width=\"1.5\"/>");
                    break;

                default:
                    // Default: filled circle
                    if (symbol != "none" && symbol != "ninguno")
                        sb.Append($"<circle cx=\"{cx:F1}\" cy=\"{cy:F1}\" r=\"{s:F1}\" fill=\"{color}\" stroke=\"none\"/>");
                    break;
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generate smooth SVG path using Catmull-Rom spline converted to cubic Bezier curves
        /// This creates visually smooth curves passing through all data points
        /// </summary>
        private string GenerateSmoothPath(List<(double px, double py)> points, double tension = 0.3)
        {
            if (points.Count < 2) return "";

            var sb = new StringBuilder();

            // Start at first point
            sb.Append($"M {points[0].px:F2},{points[0].py:F2}");

            if (points.Count == 2)
            {
                // Just draw a line for 2 points
                sb.Append($" L {points[1].px:F2},{points[1].py:F2}");
                return sb.ToString();
            }

            // Use Catmull-Rom to Bezier conversion for smooth curves
            // tension parameter: 0 = straight lines, 1 = very curved
            double t = 1 - tension; // Invert so higher tension = smoother curves

            for (int i = 0; i < points.Count - 1; i++)
            {
                // Get 4 points for Catmull-Rom: P0, P1 (current), P2 (next), P3
                var p0 = i > 0 ? points[i - 1] : points[i];
                var p1 = points[i];
                var p2 = points[i + 1];
                var p3 = i < points.Count - 2 ? points[i + 2] : points[i + 1];

                // Convert Catmull-Rom to Bezier control points
                // CP1 = P1 + (P2 - P0) / (6 * t)
                // CP2 = P2 - (P3 - P1) / (6 * t)
                double scale = 6.0 * Math.Max(0.1, t);

                double cp1x = p1.px + (p2.px - p0.px) / scale;
                double cp1y = p1.py + (p2.py - p0.py) / scale;

                double cp2x = p2.px - (p3.px - p1.px) / scale;
                double cp2y = p2.py - (p3.py - p1.py) / scale;

                // Cubic Bezier curve to next point
                sb.Append($" C {cp1x:F2},{cp1y:F2} {cp2x:F2},{cp2y:F2} {p2.px:F2},{p2.py:F2}");
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generate simple subtle grid for white background plots
        /// </summary>
        private string GenerateSimpleGrid(int margin, int marginTop, int plotWidth, int plotHeight,
            double xmin, double xmax, double ymin, double ymax, double scaleX, double scaleY)
        {
            var sb = new StringBuilder();

            // Calculate tick intervals
            var xTicks = CalculateTicks(xmin, xmax, 8);
            var yTicks = CalculateTicks(ymin, ymax, 8);

            // Subtle gray grid lines
            foreach (var tick in xTicks)
            {
                var px = margin + (tick - xmin) * scaleX;
                if (px >= margin && px <= margin + plotWidth)
                {
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight}\" stroke=\"#e0e0e0\" stroke-width=\"0.5\"/>");
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop + plotHeight}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight + 5}\" stroke=\"#333\" stroke-width=\"1\"/>");
                    sb.Append($"<text x=\"{px:F1}\" y=\"{marginTop + plotHeight + 18}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"11\" fill=\"#333\">{FormatTickLabel(tick)}</text>");
                }
            }

            foreach (var tick in yTicks)
            {
                var py = marginTop + plotHeight - (tick - ymin) * scaleY;
                if (py >= marginTop && py <= marginTop + plotHeight)
                {
                    sb.Append($"<line x1=\"{margin}\" y1=\"{py:F1}\" x2=\"{margin + plotWidth}\" y2=\"{py:F1}\" stroke=\"#e0e0e0\" stroke-width=\"0.5\"/>");
                    sb.Append($"<line x1=\"{margin - 5}\" y1=\"{py:F1}\" x2=\"{margin}\" y2=\"{py:F1}\" stroke=\"#333\" stroke-width=\"1\"/>");
                    sb.Append($"<text x=\"{margin - 8}\" y=\"{py + 4:F1}\" text-anchor=\"end\" font-family=\"Times New Roman, serif\" font-size=\"11\" fill=\"#333\">{FormatTickLabel(tick)}</text>");
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generate SVG grid with Mathcad Prime / graph paper style
        /// </summary>
        private string GenerateMathcadGrid(int margin, int marginTop, int plotWidth, int plotHeight,
            double xmin, double xmax, double ymin, double ymax, double scaleX, double scaleY)
        {
            var sb = new StringBuilder();

            // Calculate nice tick intervals for major grid
            var xTicks = CalculateTicks(xmin, xmax, 8);
            var yTicks = CalculateTicks(ymin, ymax, 8);

            // Calculate minor grid spacing (5 subdivisions)
            double xMajorInterval = xTicks.Length > 1 ? xTicks[1] - xTicks[0] : (xmax - xmin) / 5;
            double yMajorInterval = yTicks.Length > 1 ? yTicks[1] - yTicks[0] : (ymax - ymin) / 5;
            double xMinorInterval = xMajorInterval / 5;
            double yMinorInterval = yMajorInterval / 5;

            // Minor grid lines (thin, light blue - paper milimetrado)
            for (double x = Math.Floor(xmin / xMinorInterval) * xMinorInterval; x <= xmax; x += xMinorInterval)
            {
                var px = margin + (x - xmin) * scaleX;
                if (px >= margin && px <= margin + plotWidth)
                {
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight}\" stroke=\"#cce0ff\" stroke-width=\"0.5\"/>");
                }
            }
            for (double y = Math.Floor(ymin / yMinorInterval) * yMinorInterval; y <= ymax; y += yMinorInterval)
            {
                var py = marginTop + plotHeight - (y - ymin) * scaleY;
                if (py >= marginTop && py <= marginTop + plotHeight)
                {
                    sb.Append($"<line x1=\"{margin}\" y1=\"{py:F1}\" x2=\"{margin + plotWidth}\" y2=\"{py:F1}\" stroke=\"#cce0ff\" stroke-width=\"0.5\"/>");
                }
            }

            // Major grid lines (thicker, darker blue)
            foreach (var tick in xTicks)
            {
                var px = margin + (tick - xmin) * scaleX;
                if (px >= margin && px <= margin + plotWidth)
                {
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight}\" stroke=\"#99c2ff\" stroke-width=\"1\"/>");
                    // Tick mark on axis
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop + plotHeight}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight + 5}\" stroke=\"#333\" stroke-width=\"1\"/>");
                    // Tick label
                    sb.Append($"<text x=\"{px:F1}\" y=\"{marginTop + plotHeight + 18}\" text-anchor=\"middle\" font-family=\"Times New Roman, serif\" font-size=\"11\" fill=\"#333\">{FormatTickLabel(tick)}</text>");
                }
            }

            foreach (var tick in yTicks)
            {
                var py = marginTop + plotHeight - (tick - ymin) * scaleY;
                if (py >= marginTop && py <= marginTop + plotHeight)
                {
                    sb.Append($"<line x1=\"{margin}\" y1=\"{py:F1}\" x2=\"{margin + plotWidth}\" y2=\"{py:F1}\" stroke=\"#99c2ff\" stroke-width=\"1\"/>");
                    // Tick mark on axis
                    sb.Append($"<line x1=\"{margin - 5}\" y1=\"{py:F1}\" x2=\"{margin}\" y2=\"{py:F1}\" stroke=\"#333\" stroke-width=\"1\"/>");
                    // Tick label
                    sb.Append($"<text x=\"{margin - 8}\" y=\"{py + 4:F1}\" text-anchor=\"end\" font-family=\"Times New Roman, serif\" font-size=\"11\" fill=\"#333\">{FormatTickLabel(tick)}</text>");
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generate SVG grid lines and tick labels (legacy)
        /// </summary>
        private string GenerateGrid(int margin, int marginTop, int plotWidth, int plotHeight,
            double xmin, double xmax, double ymin, double ymax, double scaleX, double scaleY)
        {
            var sb = new StringBuilder();

            // Calculate nice tick intervals
            var xTicks = CalculateTicks(xmin, xmax, 6);
            var yTicks = CalculateTicks(ymin, ymax, 6);

            // Vertical grid lines and X tick labels
            foreach (var tick in xTicks)
            {
                var px = margin + (tick - xmin) * scaleX;
                if (px >= margin && px <= margin + plotWidth)
                {
                    sb.Append($"<line x1=\"{px:F1}\" y1=\"{marginTop}\" x2=\"{px:F1}\" y2=\"{marginTop + plotHeight}\" stroke=\"#ddd\" stroke-width=\"1\"/>");
                    sb.Append($"<text x=\"{px:F1}\" y=\"{marginTop + plotHeight + 15}\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"10\">{FormatTickLabel(tick)}</text>");
                }
            }

            // Horizontal grid lines and Y tick labels
            foreach (var tick in yTicks)
            {
                var py = marginTop + plotHeight - (tick - ymin) * scaleY;
                if (py >= marginTop && py <= marginTop + plotHeight)
                {
                    sb.Append($"<line x1=\"{margin}\" y1=\"{py:F1}\" x2=\"{margin + plotWidth}\" y2=\"{py:F1}\" stroke=\"#ddd\" stroke-width=\"1\"/>");
                    sb.Append($"<text x=\"{margin - 5}\" y=\"{py + 4:F1}\" text-anchor=\"end\" font-family=\"Arial\" font-size=\"10\">{FormatTickLabel(tick)}</text>");
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Calculate nice tick values for axis
        /// </summary>
        private double[] CalculateTicks(double min, double max, int targetCount)
        {
            var range = max - min;
            var rawInterval = range / targetCount;

            // Find nice interval (1, 2, 5 or 10 times a power of 10)
            var magnitude = Math.Pow(10, Math.Floor(Math.Log10(rawInterval)));
            var normalized = rawInterval / magnitude;

            double niceInterval;
            if (normalized <= 1.5) niceInterval = magnitude;
            else if (normalized <= 3) niceInterval = 2 * magnitude;
            else if (normalized <= 7) niceInterval = 5 * magnitude;
            else niceInterval = 10 * magnitude;

            // Generate ticks
            var result = new List<double>();
            var start = Math.Ceiling(min / niceInterval) * niceInterval;
            for (var t = start; t <= max; t += niceInterval)
            {
                result.Add(t);
            }
            return result.ToArray();
        }

        /// <summary>
        /// Format tick label
        /// </summary>
        private string FormatTickLabel(double value)
        {
            if (Math.Abs(value) < 1e-10) return "0";
            if (Math.Abs(value) >= 1e4 || (Math.Abs(value) < 1e-2 && Math.Abs(value) > 0))
                return value.ToString("0.##E+0", System.Globalization.CultureInfo.InvariantCulture);
            return value.ToString("G4", System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>
        /// Export table to file (CSV or XLSX)
        /// </summary>
        private void ExportTableToFile(double[,] matrix, string[] headers, string[] rowHeaders, string filename)
        {
            var ext = System.IO.Path.GetExtension(filename).ToLower();
            var rows = matrix.GetLength(0);
            var cols = matrix.GetLength(1);

            if (ext == ".csv")
            {
                var sb = new StringBuilder();

                // Headers
                if (headers != null)
                {
                    if (rowHeaders != null) sb.Append(",");
                    sb.AppendLine(string.Join(",", headers.Select(h => $"\"{h}\"")));
                }

                // Data
                for (int i = 0; i < rows; i++)
                {
                    if (rowHeaders != null && i < rowHeaders.Length)
                        sb.Append($"\"{rowHeaders[i]}\",");

                    for (int j = 0; j < cols; j++)
                    {
                        if (j > 0) sb.Append(",");
                        sb.Append(matrix[i, j].ToString(System.Globalization.CultureInfo.InvariantCulture));
                    }
                    sb.AppendLine();
                }

                System.IO.File.WriteAllText(filename, sb.ToString());
            }
            else if (ext == ".xlsx")
            {
                // For xlsx, create a simple OpenXML file (requires OpenXML SDK which is already referenced)
                // For now, fallback to CSV with xlsx extension info
                var csvFile = System.IO.Path.ChangeExtension(filename, ".csv");
                ExportTableToFile(matrix, headers, rowHeaders, csvFile);
                throw new Exception($"XLSX export no implementado, se guardó como CSV: {csvFile}");
            }
            else
            {
                throw new Exception($"Formato no soportado: {ext}. Use .csv o .xlsx");
            }
        }

        /// <summary>
        /// Process @{columns N} block - generates multi-column HTML layout
        /// Syntax:
        ///   @{columns N}
        ///   content for column 1
        ///   @{column}
        ///   content for column 2
        ///   @{column}
        ///   content for column 3
        ///   @{end columns}
        /// </summary>
        public string ProcessColumnsBlockPublic(string directive, string content, Dictionary<string, object> variables, Action<string>? progressCallback)
        {
            return ProcessColumnsBlock(directive, content, variables, progressCallback);
        }

        private string ProcessColumnsBlock(string directive, string content, Dictionary<string, object> variables, Action<string>? progressCallback)
        {
            try
            {
                // DEBUG: Log the content received
                try
                {
                    var logPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-columns-debug.txt");
                    System.IO.File.AppendAllText(logPath,
                        $"\n[{DateTime.Now:HH:mm:ss}] === ProcessColumnsBlock START ===\n");
                    System.IO.File.AppendAllText(logPath,
                        $"[{DateTime.Now:HH:mm:ss}] Directive: '{directive}'\n");
                    System.IO.File.AppendAllText(logPath,
                        $"[{DateTime.Now:HH:mm:ss}] Content length: {content.Length}\n");
                    System.IO.File.AppendAllText(logPath,
                        $"[{DateTime.Now:HH:mm:ss}] Content lines: {content.Split('\n').Length}\n");
                    var contentPreview = content.Length > 500 ? content.Substring(0, 500) : content;
                    System.IO.File.AppendAllText(logPath,
                        $"[{DateTime.Now:HH:mm:ss}] Content preview:\n{contentPreview}\n...\n");
                }
                catch { }

                // Parse number of columns from directive "@{columns N}" or "columns N" or just "columns"
                int numColumns = 2; // Default
                // Extract number from directive (handle both "@{columns 4}" and "columns 4")
                var directiveText = directive.Trim().TrimStart('@', '{').TrimEnd('}');
                var parts = directiveText.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length >= 2 && int.TryParse(parts[1], out int n) && n >= 2 && n <= 4)
                {
                    numColumns = n;
                }

                // DEBUG: Log parsed numColumns
                try
                {
                    var logPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-columns-debug.txt");
                    System.IO.File.AppendAllText(logPath,
                        $"[{DateTime.Now:HH:mm:ss}] Parsed numColumns = {numColumns} from directive '{directive}' (directiveText='{directiveText}')\n");
                }
                catch { }

                // Split content by @{column} separator or by ---  (on its own line)
                // OR automatically distribute code blocks if no separators
                var columnContents = new List<string>();

                // Try splitting by "---" on its own line first (common pattern)
                var lines = content.Split(new[] { '\r', '\n' }, StringSplitOptions.None);
                var currentColumn = new StringBuilder();
                bool foundSeparator = false;

                foreach (var line in lines)
                {
                    var trimmed = line.Trim();

                    // Check if this line is a column separator
                    if (trimmed == "---" || trimmed.Equals("@{column}", StringComparison.OrdinalIgnoreCase))
                    {
                        columnContents.Add(currentColumn.ToString());
                        currentColumn.Clear();
                        foundSeparator = true;
                    }
                    else
                    {
                        currentColumn.AppendLine(line);
                    }
                }

                // Add the last column
                if (currentColumn.Length > 0 || foundSeparator)
                {
                    columnContents.Add(currentColumn.ToString());
                }

                // If no separators found, try to auto-distribute code blocks
                if (columnContents.Count == 0 || (columnContents.Count == 1 && !foundSeparator))
                {
                    // Extract code blocks from content and distribute them across columns
                    var codeBlocks = MultLangManager.ExtractCodeBlocks(content);
                    var allBlocks = new List<(int startLine, int endLine, string language, string code, string directive)>();

                    foreach (var (lang, blocks) in codeBlocks)
                    {
                        foreach (var block in blocks)
                        {
                            allBlocks.Add((block.StartLine, block.EndLine, block.Language, block.Code, block.StartDirective));
                        }
                    }

                    // Sort by start line to maintain order
                    allBlocks = allBlocks.OrderBy(b => b.startLine).ToList();

                    // DEBUG: Log how many blocks found and numColumns value
                    try
                    {
                        var logPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-columns-debug.txt");
                        System.IO.File.AppendAllText(logPath,
                            $"[{DateTime.Now:HH:mm:ss}] === DISTRIBUTION DEBUG ===\n");
                        System.IO.File.AppendAllText(logPath,
                            $"[{DateTime.Now:HH:mm:ss}] numColumns = {numColumns}\n");
                        System.IO.File.AppendAllText(logPath,
                            $"[{DateTime.Now:HH:mm:ss}] allBlocks.Count = {allBlocks.Count}\n");
                        foreach (var block in allBlocks)
                        {
                            System.IO.File.AppendAllText(logPath,
                                $"[{DateTime.Now:HH:mm:ss}]   - Block: {block.language} (line {block.startLine})\n");
                        }
                    }
                    catch { }

                    if (allBlocks.Count > 0)
                    {
                        // Distribute blocks across columns
                        columnContents.Clear();
                        for (int i = 0; i < numColumns; i++)
                        {
                            columnContents.Add("");
                        }

                        for (int i = 0; i < allBlocks.Count; i++)
                        {
                            var block = allBlocks[i];
                            int columnIndex = i % numColumns;

                            // DEBUG: Log distribution
                            try
                            {
                                var logPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-columns-debug.txt");
                                System.IO.File.AppendAllText(logPath,
                                    $"[{DateTime.Now:HH:mm:ss}] Block {i} ({block.language}) -> Column {columnIndex}\n");
                            }
                            catch { }

                            // Reconstruct the directive block
                            var blockContent = $"{block.directive}\n{block.code}\n@{{end {block.language}}}";
                            columnContents[columnIndex] += blockContent + "\n\n";
                        }
                    }
                    else
                    {
                        // No code blocks found, treat as single column
                        columnContents.Clear();
                        columnContents.Add(content);
                    }
                }

                // Calculate column width
                var widthPercent = 100.0 / numColumns;

                // Build HTML with flexbox layout
                var html = new StringBuilder();
                html.Append($"<div class=\"columns-container\" style=\"display:flex;gap:1em;flex-wrap:wrap;\">");

                foreach (var colContent in columnContents)
                {
                    html.Append($"<div class=\"column\" style=\"flex:1;min-width:{widthPercent - 5}%;max-width:{widthPercent + 5}%;\">");

                    // Process the column content - may contain other parsers
                    var trimmedContent = colContent.Trim();
                    if (!string.IsNullOrEmpty(trimmedContent))
                    {
                        // Check if content has external code blocks
                        var hasLangCode = MultLangManager.HasLanguageCode(trimmedContent);

                        try
                        {
                            var logPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-columns-debug.txt");
                            System.IO.File.AppendAllText(logPath,
                                $"[{DateTime.Now:HH:mm:ss}] Column length: {trimmedContent.Length}\n");
                            System.IO.File.AppendAllText(logPath,
                                $"[{DateTime.Now:HH:mm:ss}] Contains '@{{': {trimmedContent.Contains("@{")}\n");
                            System.IO.File.AppendAllText(logPath,
                                $"[{DateTime.Now:HH:mm:ss}] Contains 'symbolic': {trimmedContent.Contains("symbolic")}\n");
                            System.IO.File.AppendAllText(logPath,
                                $"[{DateTime.Now:HH:mm:ss}] HasLanguageCode: {hasLangCode}\n");
                            if (trimmedContent.Contains("@{"))
                            {
                                var atIndex = trimmedContent.IndexOf("@{");
                                var snippet = trimmedContent.Substring(atIndex, Math.Min(50, trimmedContent.Length - atIndex));
                                System.IO.File.AppendAllText(logPath,
                                    $"[{DateTime.Now:HH:mm:ss}] Snippet at @{{: '{snippet}'\n");
                            }
                            System.IO.File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] ---\n");
                        }
                        catch { }

                        if (hasLangCode)
                        {
                            // Recursively process external code in the column
                            var processedContent = Process(trimmedContent, returnHtml: true, enableCollapse: false, progressCallback: progressCallback);
                            html.Append(processedContent);
                        }
                        else
                        {
                            // Plain text/Calcpad content - wrap in paragraph
                            // Replace newlines with <br> for basic formatting
                            var escaped = System.Web.HttpUtility.HtmlEncode(trimmedContent);
                            escaped = escaped.Replace("\n", "<br/>");
                            html.Append($"<p>{escaped}</p>");
                        }
                    }

                    html.Append("</div>");
                }

                html.Append("</div>");
                return html.ToString();
            }
            catch (Exception ex)
            {
                return $"<p style='color:red;'>Error en @{{columns}}: {ex.Message}</p>";
            }
        }

        /// <summary>
        /// Process IFC creation block - creates IFC geometry from commands
        /// </summary>
        private string ProcessIfcCreateBlock(string content, string directive)
        {
            try
            {
                var creator = new IfcCreator();
                var ifcContent = creator.ProcessCommands(content);

                // Check for errors
                if (ifcContent.StartsWith("ERRORS:"))
                {
                    var errors = ifcContent.Replace("ERRORS:", "").Trim();
                    return $"<div style='color: red; padding: 10px; border: 1px solid red; margin: 10px 0; font-family: monospace; white-space: pre-wrap;'>Errores en IFC-CREATE:\n{System.Web.HttpUtility.HtmlEncode(errors)}</div>";
                }

                // Save IFC file to temp directory
                var tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad_ifc");
                if (!System.IO.Directory.Exists(tempDir))
                {
                    System.IO.Directory.CreateDirectory(tempDir);
                }

                var ifcFileName = $"created_{Guid.NewGuid():N}.ifc";
                var ifcFilePath = System.IO.Path.Combine(tempDir, ifcFileName);
                System.IO.File.WriteAllText(ifcFilePath, ifcContent);

                // Also copy to resources/ifc for WebView2 access
                var appPath = AppDomain.CurrentDomain.BaseDirectory;
                var ifcResourcePath = System.IO.Path.Combine(appPath, "resources", "ifc");
                if (!System.IO.Directory.Exists(ifcResourcePath))
                {
                    System.IO.Directory.CreateDirectory(ifcResourcePath);
                }
                var resourceIfcPath = System.IO.Path.Combine(ifcResourcePath, ifcFileName);
                System.IO.File.WriteAllText(resourceIfcPath, ifcContent);

                // Generate inline viewer using Virtual Host URL
                var viewerHtml = IfcLanguageHandler.GenerateInlineViewerHtml(resourceIfcPath, directive);

                // Add download link for the IFC file
                var downloadHtml = $@"
<div style='margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;'>
    <strong>IFC Creado:</strong> {ifcFileName}<br>
    <a href='file:///{ifcFilePath.Replace('\\', '/')}' style='color: #0078d4;' download>Descargar archivo IFC</a>
    <span style='color: #666; font-size: 11px;'> | Guardado en: {ifcFilePath}</span>
</div>";

                return downloadHtml + viewerHtml;
            }
            catch (Exception ex)
            {
                return $"<div style='color: red; padding: 10px; border: 1px solid red; margin: 10px 0;'>Error en @{{ifc-create}}: {ex.Message}</div>";
            }
        }

        /// <summary>
        /// Copy IFC viewer libraries to target directory for CLI usage
        /// This avoids CDN issues with Edge Tracking Prevention
        /// </summary>
        private void CopyIfcLibsToDirectory(string targetDirectory)
        {
            try
            {
                var libsDir = System.IO.Path.Combine(targetDirectory, "libs");
                if (!System.IO.Directory.Exists(libsDir))
                {
                    System.IO.Directory.CreateDirectory(libsDir);
                }

                // List of required files for IFC viewer
                var requiredFiles = new[]
                {
                    "three.module.js",
                    "OrbitControls.js",
                    "web-ifc-api-iife.js",
                    "web-ifc.wasm"
                };

                // Try to find source libs directory
                string sourceLibsDir = null;

                // First check in Examples/libs (development)
                var examplesLibs = System.IO.Path.Combine(
                    System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) ?? "",
                    "..", "..", "..", "..", "Examples", "libs");
                if (System.IO.Directory.Exists(examplesLibs))
                {
                    sourceLibsDir = System.IO.Path.GetFullPath(examplesLibs);
                }

                // Try other common locations
                if (sourceLibsDir == null)
                {
                    var possiblePaths = new[]
                    {
                        @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples\libs",
                        System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                            "Documents", "Calcpad-7.5.7", "Examples", "libs")
                    };

                    foreach (var path in possiblePaths)
                    {
                        if (System.IO.Directory.Exists(path))
                        {
                            sourceLibsDir = path;
                            break;
                        }
                    }
                }

                if (sourceLibsDir == null)
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] CopyIfcLibs: Source libs directory not found\n");
                    return;
                }

                // Copy each required file
                foreach (var fileName in requiredFiles)
                {
                    var sourceFile = System.IO.Path.Combine(sourceLibsDir, fileName);
                    var destFile = System.IO.Path.Combine(libsDir, fileName);

                    if (System.IO.File.Exists(sourceFile) && !System.IO.File.Exists(destFile))
                    {
                        System.IO.File.Copy(sourceFile, destFile);
                    }
                }

                var debugPath2 = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath2,
                    $"[{DateTime.Now:HH:mm:ss}] CopyIfcLibs: Copied libs to '{libsDir}'\n");
            }
            catch (Exception ex)
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] CopyIfcLibs ERROR: {ex.Message}\n");
            }
        }
    }
}
