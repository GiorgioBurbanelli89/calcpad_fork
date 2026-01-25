#nullable enable
using System;
using System.Text;
using Calcpad.Common.MultLangCode;

namespace Calcpad.Common
{
    /// <summary>
    /// Parser Global - Decides whether to use external code execution OR Calcpad math parser
    /// NEVER both on the same content
    /// </summary>
    public class GlobalParser
    {
        private readonly MultLangProcessor _multLangProcessor;
        private ExecutionTracker? _tracker;

        public GlobalParser(ExecutionTracker? tracker = null)
        {
            _tracker = tracker;
            _multLangProcessor = new MultLangProcessor(_tracker);
        }

        /// <summary>
        /// Processes code by routing to EITHER external code processor OR Calcpad parser
        /// </summary>
        /// <param name="code">Input code</param>
        /// <param name="hasExternalCode">OUT: True if external code blocks were detected</param>
        /// <param name="progressCallback">Optional callback for progress updates during external code execution</param>
        /// <param name="partialResultCallback">Optional callback for partial HTML results as they become available</param>
        /// <returns>Processed code (either MultLang output or original code for Calcpad)</returns>
        public string Process(string code, out bool hasExternalCode, Action<string>? progressCallback = null, Action<string>? partialResultCallback = null)
        {
            _tracker?.EnterMethod("GlobalParser", "Process", $"Code length: {code.Length} chars");

            // CHECK FOR PAGE MODE: @{page markdown}
            // This switches the entire page to Markdown mode with Calcpad support
            if (IsMarkdownPageMode(code, out var markdownContent))
            {
                hasExternalCode = true; // Signal that we handled it externally (return HTML)
                return ProcessMarkdownPage(markdownContent, progressCallback);
            }

            // DECISION POINT: Check if there are external code blocks
            _tracker?.ReportStep("Checking for external language blocks");
            hasExternalCode = MultLangManager.HasLanguageCode(code);

            if (hasExternalCode)
            {
                // Check if there's ALSO Calcpad code (mixed mode)
                bool hasMixedCode = HasCalcpadCode(code);

                try
                {
                    var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] GlobalParser.Process: HasCalcpadCode={hasMixedCode}\n");
                }
                catch { }

                if (hasMixedCode)
                {
                    // PATH 1A: MIXED MODE - Has external code AND Calcpad code
                    // Preprocess: Replace external code blocks with Calcpad HTML comments
                    // Then return for ExpressionParser to process Calcpad code
                    hasExternalCode = false; // Signal to use ExpressionParser

                    try
                    {
                        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] PATH 1A: MIXED MODE - Setting hasExternalCode=false\n");
                    }
                    catch { }

                    return PreprocessMixedCode(code, progressCallback, partialResultCallback);
                }
                else
                {
                    // PATH 1B: PURE EXTERNAL - Only external code, no Calcpad
                    // Use MultLangProcessor and return HTML directly
                    // enableCollapse=false: Simple output without collapse/expand buttons

                    try
                    {
                        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] PATH 1B: PURE EXTERNAL - Processing with MultLangProcessor\n");
                    }
                    catch { }

                    return _multLangProcessor.Process(code, returnHtml: true, enableCollapse: false, progressCallback: progressCallback, partialResultCallback: partialResultCallback);
                }
            }
            else
            {
                // PATH 2: No external code - return original for Calcpad processing
                // MultLangProcessor was SKIPPED, ExpressionParser will handle it
                return code;
            }
        }

        /// <summary>
        /// Checks if code contains Calcpad calculations (not just external code and comments)
        /// </summary>
        private bool HasCalcpadCode(string code)
        {
            var lines = code.Split('\n');
            bool inExternalBlock = false;

            foreach (var line in lines)
            {
                var trimmed = line.Trim();

                // Track external code blocks
                if (trimmed.StartsWith("@{") && !trimmed.StartsWith("@{end"))
                {
                    inExternalBlock = true;
                    continue;
                }
                else if (trimmed.StartsWith("@{end"))
                {
                    inExternalBlock = false;
                    continue;
                }

                // Skip lines inside external blocks
                if (inExternalBlock)
                    continue;

                // Skip only empty lines
                if (string.IsNullOrWhiteSpace(trimmed))
                    continue;

                // Lines starting with ' or " are Calcpad text/headings - this IS Calcpad code
                if (trimmed.StartsWith("'") || trimmed.StartsWith("\""))
                    return true;

                // If we reach here, it's likely Calcpad code
                // Look for typical Calcpad patterns: assignments, calculations
                if (trimmed.Contains("=") || trimmed.Contains("+") || trimmed.Contains("*") ||
                    trimmed.Contains("/") || char.IsLetterOrDigit(trimmed[0]))
                {
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Preprocesses mixed code: executes external blocks and replaces them with HTML comments
        /// </summary>
        private string PreprocessMixedCode(string code, Action<string>? progressCallback, Action<string>? partialResultCallback)
        {
            // Process external code blocks to get their HTML output
            // returnHtml=false means it will return Calcpad comments with HTML
            return _multLangProcessor.Process(code, returnHtml: false, enableCollapse: false, progressCallback: progressCallback, partialResultCallback: partialResultCallback);
        }

        /// <summary>
        /// Quick check if code contains external language blocks
        /// </summary>
        public static bool HasExternalCode(string code)
        {
            return MultLangManager.HasLanguageCode(code);
        }

        /// <summary>
        /// Gets exported variables from external code execution
        /// </summary>
        public System.Collections.Generic.IReadOnlyDictionary<string, object> ExportedVariables
            => _multLangProcessor.ExportedVariables;

        /// <summary>
        /// Processes inline Calcpad code markers in HTML output
        /// This is called from the presentation layer with access to ExpressionParser
        /// </summary>
        /// <param name="htmlContent">HTML content with <!--CALCPAD_INLINE:base64--> markers</param>
        /// <param name="calcpadExecutor">Function that executes Calcpad code and returns HTML result</param>
        /// <returns>HTML with inline Calcpad results</returns>
        public static string ProcessCalcpadInlineMarkers(string htmlContent, System.Func<string, string> calcpadExecutor)
        {
            if (string.IsNullOrEmpty(htmlContent) || calcpadExecutor == null)
                return htmlContent;

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                var markerCount = System.Text.RegularExpressions.Regex.Matches(htmlContent, @"<!--CALCPAD_INLINE:").Count;
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessCalcpadInlineMarkers START: {markerCount} markers found in input\n");

                // Find first marker and show what's around it
                var firstMarkerIndex = htmlContent.IndexOf("<!--CALCPAD_INLINE:");
                if (firstMarkerIndex >= 0)
                {
                    var contextStart = Math.Max(0, firstMarkerIndex - 50);
                    var contextLength = Math.Min(150, htmlContent.Length - contextStart);
                    var context = htmlContent.Substring(contextStart, contextLength);
                    System.IO.File.AppendAllText(debugPath,
                        $"[{DateTime.Now:HH:mm:ss}] First marker at index {firstMarkerIndex}, context: '{context}'\n");
                }
            }
            catch { }

            var result = new StringBuilder();
            int i = 0;
            int markersProcessed = 0;

            while (i < htmlContent.Length)
            {
                // Debug: Check at index 622 (where first marker is)
                if (i == 622)
                {
                    try
                    {
                        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                        var substring = htmlContent.Substring(i, Math.Min(30, htmlContent.Length - i));
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] At index 622: '{substring}'\n");

                        // Show byte codes of first 20 characters
                        var bytes = Encoding.UTF8.GetBytes(substring.Substring(0, Math.Min(20, substring.Length)));
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] Bytes: {BitConverter.ToString(bytes)}\n");

                        var expected = "<!--CALCPAD_INLINE:";
                        var expectedBytes = Encoding.UTF8.GetBytes(expected);
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] Expected bytes: {BitConverter.ToString(expectedBytes)}\n");

                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] Comparing to '<!--CALCPAD_INLINE:' = {htmlContent.Substring(i, 20) == "<!--CALCPAD_INLINE:"}\n");
                    }
                    catch { }
                }

                // Look for marker: <!--CALCPAD_INLINE:
                // Use IndexOf instead of Substring comparison (more reliable)
                if (i < htmlContent.Length &&
                    htmlContent.IndexOf("<!--CALCPAD_INLINE:", i, StringComparison.Ordinal) == i)
                {
                    markersProcessed++;
                    try
                    {
                        var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                        System.IO.File.AppendAllText(debugPath,
                            $"[{DateTime.Now:HH:mm:ss}] ProcessCalcpadInlineMarkers: Found marker #{markersProcessed} at position {i}\n");
                    }
                    catch { }

                    i += 19; // Skip marker "<!--CALCPAD_INLINE:" (19 chars, not 20!)

                    // Find end of comment: -->
                    int endIndex = htmlContent.IndexOf("-->", i);
                    if (endIndex > i)
                    {
                        string base64Code = htmlContent.Substring(i, endIndex - i);

                        try
                        {
                            var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                            System.IO.File.AppendAllText(debugPath,
                                $"[{DateTime.Now:HH:mm:ss}] Decoding base64: {base64Code.Substring(0, Math.Min(20, base64Code.Length))}...\n");
                        }
                        catch { }

                        try
                        {
                            // Decode base64
                            byte[] data = Convert.FromBase64String(base64Code);
                            string calcpadCode = Encoding.UTF8.GetString(data);

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] Decoded to: {calcpadCode}\n");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] Calling calcpadExecutor...\n");
                            }
                            catch { }

                            // Execute Calcpad code
                            string calcpadResult = calcpadExecutor(calcpadCode);

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] Got result: {calcpadResult.Substring(0, Math.Min(50, calcpadResult.Length))}...\n");
                            }
                            catch { }

                            // Append result
                            result.Append(calcpadResult);
                        }
                        catch (Exception ex)
                        {
                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] ERROR: {ex.Message}\n");
                            }
                            catch { }

                            // If decoding or execution fails, keep the marker
                            result.Append($"<!--CALCPAD_INLINE:{base64Code}-->");
                        }

                        i = endIndex + 3; // Skip -->
                    }
                    else
                    {
                        result.Append(htmlContent[i]);
                        i++;
                    }
                }
                else
                {
                    result.Append(htmlContent[i]);
                    i++;
                }
            }

            return result.ToString();
        }

        /// <summary>
        /// Processes MULTILANG_OUTPUT markers in HTML content
        /// Replaces <!--MULTILANG_OUTPUT:base64--> with the decoded HTML
        /// </summary>
        /// <param name="htmlContent">HTML content with MULTILANG_OUTPUT markers</param>
        /// <returns>HTML with markers replaced by decoded content</returns>
        public static string ProcessMultilangOutputMarkers(string htmlContent)
        {
            if (string.IsNullOrEmpty(htmlContent))
                return htmlContent;

            const string markerStart = "<!--MULTILANG_OUTPUT:";
            const string markerEnd = "-->";

            // Quick check: if no markers, return as-is
            if (!htmlContent.Contains(markerStart))
                return htmlContent;

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessMultilangOutputMarkers: Processing markers...\n");
            }
            catch { }

            var result = new StringBuilder();
            int i = 0;
            int markersProcessed = 0;

            while (i < htmlContent.Length)
            {
                // Look for marker: <!--MULTILANG_OUTPUT:
                if (i + markerStart.Length < htmlContent.Length &&
                    htmlContent.Substring(i, markerStart.Length) == markerStart)
                {
                    markersProcessed++;
                    int start = i + markerStart.Length;
                    int endIndex = htmlContent.IndexOf(markerEnd, start, StringComparison.Ordinal);

                    if (endIndex > start)
                    {
                        var base64Content = htmlContent.Substring(start, endIndex - start);

                        try
                        {
                            // Decode base64 to get the original HTML
                            var decodedBytes = Convert.FromBase64String(base64Content);
                            var decodedHtml = System.Text.Encoding.UTF8.GetString(decodedBytes);

                            // Insert the decoded HTML
                            result.Append(decodedHtml);

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] ProcessMultilangOutputMarkers: Decoded marker #{markersProcessed}, HTML length: {decodedHtml.Length}\n");
                            }
                            catch { }
                        }
                        catch (Exception ex)
                        {
                            // If decoding fails, keep the marker as-is
                            result.Append($"<!--MULTILANG_OUTPUT:{base64Content}-->");

                            try
                            {
                                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                                System.IO.File.AppendAllText(debugPath,
                                    $"[{DateTime.Now:HH:mm:ss}] ProcessMultilangOutputMarkers: Failed to decode marker #{markersProcessed}: {ex.Message}\n");
                            }
                            catch { }
                        }

                        i = endIndex + markerEnd.Length;
                    }
                    else
                    {
                        result.Append(htmlContent[i]);
                        i++;
                    }
                }
                else
                {
                    result.Append(htmlContent[i]);
                    i++;
                }
            }

            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessMultilangOutputMarkers: Processed {markersProcessed} markers, result length: {result.Length}\n");
            }
            catch { }

            return result.ToString();
        }

        /// <summary>
        /// Checks if the code starts with @{page markdown} directive
        /// </summary>
        /// <param name="code">Input code</param>
        /// <param name="markdownContent">Content after the directive (if found)</param>
        /// <returns>True if @{page markdown} was found</returns>
        private bool IsMarkdownPageMode(string code, out string markdownContent)
        {
            markdownContent = code;

            if (string.IsNullOrWhiteSpace(code))
                return false;

            var lines = code.Split('\n');
            foreach (var line in lines)
            {
                var trimmed = line.Trim().ToLower();

                // Skip empty lines and comments at the start
                if (string.IsNullOrWhiteSpace(trimmed))
                    continue;
                if (trimmed.StartsWith("'"))
                    continue;

                // Check for @{page markdown} directive
                if (trimmed == "@{page markdown}" || trimmed.StartsWith("@{page markdown}"))
                {
                    // Find where this line ends and get everything after
                    var idx = code.IndexOf(line) + line.Length;
                    markdownContent = idx < code.Length ? code.Substring(idx).TrimStart('\r', '\n') : "";
                    return true;
                }

                // If first non-empty, non-comment line is not @{page markdown}, stop checking
                break;
            }

            return false;
        }

        /// <summary>
        /// Processes entire page as Markdown with support for ALL parsers:
        /// - $$expression$$ = Calcpad block (evaluated and rendered as math)
        /// - $variable = Inline value substitution
        /// - @{table}...@{end table} = Table from matrix/vector
        /// - @{columns N}...@{column}...@{end columns} = Multi-column layout
        /// - @{python}...@{end python} = Python code
        /// - @{octave}...@{end octave} = Octave/MATLAB code
        /// - @{typescript}...@{end typescript} = TypeScript code
        /// - Any other @{language}...@{end language} = External code
        /// - Everything else = Markdown
        /// </summary>
        private string ProcessMarkdownPage(string content, Action<string>? progressCallback)
        {
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-debug.txt");
                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] ProcessMarkdownPage: Processing {content.Length} chars\n");
            }
            catch { }

            var variables = new System.Collections.Generic.Dictionary<string, object>();
            var result = new StringBuilder();

            // Process in segments: Calcpad blocks ($$...$$), @{lang}, @{table}, and Markdown
            int i = 0;
            var markdownBuffer = new StringBuilder();

            while (i < content.Length)
            {
                // Check for Calcpad block: $$...$$
                if (i + 2 < content.Length && content.Substring(i, 2) == "$$")
                {
                    // Flush markdown buffer first
                    if (markdownBuffer.Length > 0)
                    {
                        result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                        markdownBuffer.Clear();
                    }

                    i += 2; // Skip opening $$
                    int endCalcpad = content.IndexOf("$$", i);
                    if (endCalcpad > i)
                    {
                        var calcpadCode = content.Substring(i, endCalcpad - i).Trim();
                        // Mark for Calcpad processing
                        var base64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(calcpadCode));
                        result.Append($"<!--CALCPAD_INLINE:{base64}-->");
                        i = endCalcpad + 2;
                    }
                    else
                    {
                        markdownBuffer.Append("$$");
                    }
                }
                // Check for @{...} external code blocks (including @{table}, @{columns})
                else if (i + 2 < content.Length && content.Substring(i, 2) == "@{")
                {
                    // Find the closing } of the directive
                    int closeDirective = content.IndexOf('}', i + 2);
                    if (closeDirective > i + 2)
                    {
                        var directiveContent = content.Substring(i + 2, closeDirective - i - 2).Trim();
                        var langName = directiveContent.Split(' ')[0].ToLower();

                        // Special handling for @{columns N}
                        if (langName == "columns")
                        {
                            // Flush markdown buffer first
                            if (markdownBuffer.Length > 0)
                            {
                                result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                                markdownBuffer.Clear();
                            }

                            // Process columns block
                            var endColumnsDirective = "@{end columns}";
                            int endColumnsBlock = content.IndexOf(endColumnsDirective, closeDirective, StringComparison.OrdinalIgnoreCase);

                            if (endColumnsBlock > closeDirective)
                            {
                                var columnsContent = content.Substring(closeDirective + 1, endColumnsBlock - closeDirective - 1);
                                var columnsHtml = ProcessColumnsBlock(directiveContent, columnsContent, variables, progressCallback);
                                result.Append(columnsHtml);
                                i = endColumnsBlock + endColumnsDirective.Length;
                            }
                            else
                            {
                                // No end directive found, treat as regular text
                                markdownBuffer.Append("@{");
                                i += 2;
                            }
                        }
                        else
                        {
                            // Find the end directive
                            var endDirective = $"@{{end {langName}}}";
                            int endBlock = content.IndexOf(endDirective, closeDirective, StringComparison.OrdinalIgnoreCase);

                            if (endBlock > closeDirective)
                            {
                                // Flush markdown buffer
                                if (markdownBuffer.Length > 0)
                                {
                                    result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                                    markdownBuffer.Clear();
                                }

                                // Extract the code block
                                var codeStart = closeDirective + 1;
                                var codeContent = content.Substring(codeStart, endBlock - codeStart);

                                // Process based on language type
                                if (langName == "table")
                                {
                                    // Table is handled by MultLangProcessor
                                    result.Append(_multLangProcessor.ProcessTableBlockPublic(codeContent.Trim(), variables));
                                }
                                else
                                {
                                    // External language - process with MultLangProcessor
                                    var fullBlock = $"@{{{directiveContent}}}\n{codeContent}\n{endDirective}";
                                    var blockHtml = _multLangProcessor.Process(fullBlock, returnHtml: true, enableCollapse: false, progressCallback: progressCallback);

                                    // Extract variables from execution
                                    foreach (var kv in _multLangProcessor.ExportedVariables)
                                    {
                                        variables[kv.Key] = kv.Value;
                                    }

                                    result.Append(blockHtml);
                                }

                                i = endBlock + endDirective.Length;
                            }
                            else
                            {
                                // No end directive found, treat as regular text
                                markdownBuffer.Append("@{");
                                i += 2;
                            }
                        }
                    }
                    else
                    {
                        markdownBuffer.Append("@{");
                        i += 2;
                    }
                }
                else
                {
                    markdownBuffer.Append(content[i]);
                    i++;
                }
            }

            // Flush remaining markdown
            if (markdownBuffer.Length > 0)
            {
                result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
            }

            // Wrap in basic HTML structure
            var html = $@"<div class='markdown-page'>
{result}
</div>";

            return html;
        }

        /// <summary>
        /// Processes @{columns N}...@{column}...@{end columns} blocks
        /// </summary>
        /// <param name="directive">The full directive content (e.g., "columns 3")</param>
        /// <param name="content">Content between @{columns N} and @{end columns}</param>
        /// <param name="variables">Variables dictionary for substitution</param>
        /// <param name="progressCallback">Progress callback for external code</param>
        /// <returns>HTML with CSS grid layout</returns>
        private string ProcessColumnsBlock(string directive, string content, System.Collections.Generic.Dictionary<string, object> variables, Action<string>? progressCallback)
        {
            // Parse number of columns from directive "columns N"
            var parts = directive.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            int numColumns = 2; // Default
            if (parts.Length >= 2 && int.TryParse(parts[1], out int n) && n > 0)
            {
                numColumns = Math.Min(n, 12); // Max 12 columns
            }

            // Split content by @{column} separator
            var columnSeparator = "@{column}";
            var columnContents = new System.Collections.Generic.List<string>();

            int pos = 0;
            while (pos < content.Length)
            {
                int nextSep = content.IndexOf(columnSeparator, pos, StringComparison.OrdinalIgnoreCase);
                if (nextSep >= 0)
                {
                    columnContents.Add(content.Substring(pos, nextSep - pos));
                    pos = nextSep + columnSeparator.Length;
                }
                else
                {
                    columnContents.Add(content.Substring(pos));
                    break;
                }
            }

            // If no separators found, use numColumns to split evenly (or just use as single column)
            if (columnContents.Count == 0)
            {
                columnContents.Add(content);
            }

            // Build HTML with CSS Grid
            var html = new StringBuilder();
            html.AppendLine($"<div class=\"calcpad-columns\" style=\"display: grid; grid-template-columns: repeat({numColumns}, 1fr); gap: 1rem;\">");

            foreach (var colContent in columnContents)
            {
                html.AppendLine("<div class=\"calcpad-column\" style=\"padding: 0.5rem;\">");

                // Process the column content recursively (may contain Calcpad blocks, external code, etc.)
                var processedColumn = ProcessMarkdownPageContent(colContent.Trim(), variables, progressCallback);
                html.Append(processedColumn);

                html.AppendLine("</div>");
            }

            html.AppendLine("</div>");
            return html.ToString();
        }

        /// <summary>
        /// Processes content for Markdown page mode (reusable for columns, etc.)
        /// </summary>
        private string ProcessMarkdownPageContent(string content, System.Collections.Generic.Dictionary<string, object> variables, Action<string>? progressCallback)
        {
            var result = new StringBuilder();
            int i = 0;
            var markdownBuffer = new StringBuilder();

            while (i < content.Length)
            {
                // Check for Calcpad block: $$...$$
                if (i + 2 < content.Length && content.Substring(i, 2) == "$$")
                {
                    // Flush markdown buffer first
                    if (markdownBuffer.Length > 0)
                    {
                        result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                        markdownBuffer.Clear();
                    }

                    i += 2; // Skip opening $$
                    int endCalcpad = content.IndexOf("$$", i);
                    if (endCalcpad > i)
                    {
                        var calcpadCode = content.Substring(i, endCalcpad - i).Trim();
                        var base64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(calcpadCode));
                        result.Append($"<!--CALCPAD_INLINE:{base64}-->");
                        i = endCalcpad + 2;
                    }
                    else
                    {
                        markdownBuffer.Append("$$");
                    }
                }
                // Check for @{...} external code blocks
                else if (i + 2 < content.Length && content.Substring(i, 2) == "@{")
                {
                    int closeDirective = content.IndexOf('}', i + 2);
                    if (closeDirective > i + 2)
                    {
                        var directiveContent = content.Substring(i + 2, closeDirective - i - 2).Trim();
                        var langName = directiveContent.Split(' ')[0].ToLower();

                        // Skip @{column} - it's just a separator, handled by parent
                        if (langName == "column")
                        {
                            i = closeDirective + 1;
                            continue;
                        }

                        // Nested @{columns} support
                        if (langName == "columns")
                        {
                            if (markdownBuffer.Length > 0)
                            {
                                result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                                markdownBuffer.Clear();
                            }

                            var endColDir = "@{end columns}";
                            int endCol = content.IndexOf(endColDir, closeDirective, StringComparison.OrdinalIgnoreCase);
                            if (endCol > closeDirective)
                            {
                                var nestedContent = content.Substring(closeDirective + 1, endCol - closeDirective - 1);
                                result.Append(ProcessColumnsBlock(directiveContent, nestedContent, variables, progressCallback));
                                i = endCol + endColDir.Length;
                            }
                            else
                            {
                                markdownBuffer.Append("@{");
                                i += 2;
                            }
                        }
                        else
                        {
                            var endDirective = $"@{{end {langName}}}";
                            int endBlock = content.IndexOf(endDirective, closeDirective, StringComparison.OrdinalIgnoreCase);

                            if (endBlock > closeDirective)
                            {
                                if (markdownBuffer.Length > 0)
                                {
                                    result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
                                    markdownBuffer.Clear();
                                }

                                var codeStart = closeDirective + 1;
                                var codeContent = content.Substring(codeStart, endBlock - codeStart);

                                if (langName == "table")
                                {
                                    result.Append(_multLangProcessor.ProcessTableBlockPublic(codeContent.Trim(), variables));
                                }
                                else
                                {
                                    var fullBlock = $"@{{{directiveContent}}}\n{codeContent}\n{endDirective}";
                                    var blockHtml = _multLangProcessor.Process(fullBlock, returnHtml: true, enableCollapse: false, progressCallback: progressCallback);

                                    foreach (var kv in _multLangProcessor.ExportedVariables)
                                    {
                                        variables[kv.Key] = kv.Value;
                                    }

                                    result.Append(blockHtml);
                                }

                                i = endBlock + endDirective.Length;
                            }
                            else
                            {
                                markdownBuffer.Append("@{");
                                i += 2;
                            }
                        }
                    }
                    else
                    {
                        markdownBuffer.Append("@{");
                        i += 2;
                    }
                }
                else
                {
                    markdownBuffer.Append(content[i]);
                    i++;
                }
            }

            // Flush remaining markdown
            if (markdownBuffer.Length > 0)
            {
                result.Append(RenderMarkdownSegment(markdownBuffer.ToString(), variables));
            }

            return result.ToString();
        }

        /// <summary>
        /// Renders a segment of Markdown to HTML, with $variable substitution
        /// </summary>
        private string RenderMarkdownSegment(string markdown, System.Collections.Generic.Dictionary<string, object> variables)
        {
            // Process $variable substitution
            var processed = System.Text.RegularExpressions.Regex.Replace(
                markdown,
                @"(?<!\\)\$([a-zA-Z_][a-zA-Z0-9_]*)",
                m =>
                {
                    var varName = m.Groups[1].Value;
                    if (variables.TryGetValue(varName, out var value))
                    {
                        if (value is double d)
                            return d.ToString("G10", System.Globalization.CultureInfo.InvariantCulture);
                        return value?.ToString() ?? "";
                    }
                    // Variable not found - create marker for Calcpad to resolve
                    var base64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(varName));
                    return $"<!--CALCPAD_INLINE:{base64}-->";
                }
            );

            // Escape \$ to $
            processed = processed.Replace("\\$", "$");

            // Render Markdown to HTML using Markdig
            try
            {
                // Use basic pipeline (extensions are in separate package)
                return Markdig.Markdown.ToHtml(processed);
            }
            catch
            {
                // Fallback: basic HTML conversion
                return $"<p>{System.Web.HttpUtility.HtmlEncode(processed)}</p>";
            }
        }
    }
}
