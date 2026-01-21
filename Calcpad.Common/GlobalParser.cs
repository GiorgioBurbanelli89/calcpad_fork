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
    }
}
