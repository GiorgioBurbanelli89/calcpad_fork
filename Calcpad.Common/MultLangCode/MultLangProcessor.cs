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
    public class MultLangProcessor
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

                    // Special handling for markdown - render to HTML
                    if (language.Equals("markdown", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing MARKDOWN block\n");
                        }
                        catch { }

                        // Process inline Calcpad code: @{calcpad:...}
                        // Then render markdown to HTML
                        var processedCode = ProcessInlineCalcpad(block.Code);
                        output = RenderMarkdown(processedCode);
                    }
                    // Special handling for HTML - process inline Calcpad
                    else if (language.Equals("html", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] MultLangProcessor: Processing HTML block, calling ProcessInlineCalcpad...\n");
                        }
                        catch { }

                        // Process inline Calcpad code: @{calcpad:...}
                        // For HTML, we return the processed content DIRECTLY, not wrapped
                        output = ProcessInlineCalcpad(block.Code);
                    }
                    // C#, XAML, WPF always execute (handled specially in LanguageExecutor)
                    else if (language.Equals("csharp", StringComparison.OrdinalIgnoreCase) ||
                             language.Equals("xaml", StringComparison.OrdinalIgnoreCase) ||
                             language.Equals("wpf", StringComparison.OrdinalIgnoreCase) ||
                             MultLangManager.IsLanguageAvailable(language))
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
                        output = LanguageHtmlGenerator.GenerateNotAvailable(language, block.Code);
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
    }
}
