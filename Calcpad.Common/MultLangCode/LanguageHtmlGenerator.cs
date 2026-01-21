using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Web;

namespace Calcpad.Common.MultLangCode
{
    /// <summary>
    /// Generates HTML output for language execution results
    /// Uses template files for each language
    /// </summary>
    public static class LanguageHtmlGenerator
    {
        // Language colors
        private static readonly Dictionary<string, string> _headerColors = new()
        {
            ["python"] = "#3776ab",
            ["octave"] = "#0790c0",
            ["cpp"] = "#00599c",
            ["julia"] = "#9558b2",
            ["r"] = "#276dc3",
            ["powershell"] = "#012456",
            ["bash"] = "#4eaa25",
            ["cmd"] = "#000000",
            ["markdown"] = "#083fa1",
            ["csharp"] = "#68217a",
            ["xaml"] = "#0c60a3",
            ["wpf"] = "#0c60a3",
            ["c"] = "#555555",
            ["fortran"] = "#734f96",
            ["opensees"] = "#e67e22",
            ["rust"] = "#dea584"
        };

        private static readonly Dictionary<string, string> _templateCache = new();
        private static string _templatesPath;

        /// <summary>
        /// Sets the path to the templates directory
        /// </summary>
        public static string TemplatesPath
        {
            get
            {
                if (string.IsNullOrEmpty(_templatesPath))
                    _templatesPath = FindTemplatesPath();
                return _templatesPath;
            }
            set => _templatesPath = value;
        }

        /// <summary>
        /// Finds the templates directory
        /// </summary>
        private static string FindTemplatesPath()
        {
            var possiblePaths = new List<string>();

            // 1. Next to the Calcpad.Common.dll
            var assemblyDir = Path.GetDirectoryName(typeof(LanguageHtmlGenerator).Assembly.Location);
            if (!string.IsNullOrEmpty(assemblyDir))
            {
                possiblePaths.Add(Path.Combine(assemblyDir, "MultLangCode", "Templates"));
                possiblePaths.Add(Path.Combine(assemblyDir, "Templates"));
            }

            // 2. Current working directory
            possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangCode", "Templates"));
            possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "Templates"));

            foreach (var path in possiblePaths)
            {
                if (Directory.Exists(path))
                    return path;
            }

            return possiblePaths.Count > 0 ? possiblePaths[0] : "Templates";
        }

        /// <summary>
        /// Generates HTML output for an execution result using inline styles (no templates)
        /// Returns HTML fragment (not full document) that can be embedded in parent HTML
        /// </summary>
        public static string GenerateHtml(string language, ExecutionResult result, bool enableCollapse = true)
        {
            // Always use simple inline HTML (no templates) for embedding
            return GenerateSimpleHtml(language, result, enableCollapse);
        }

        // Counter for unique IDs
        private static int _outputCounter = 0;

        /// <summary>
        /// Fallback: generates simple inline HTML when template is not found
        /// </summary>
        private static string GenerateSimpleHtml(string language, ExecutionResult result, bool enableCollapse = true)
        {
            var displayName = GetDisplayName(language);
            var output = result.Output;
            var error = result.Error;

            var color = _headerColors.ContainsKey(language.ToLower())
                ? _headerColors[language.ToLower()]
                : "#4A90E2";

            var sb = new StringBuilder();
            sb.AppendLine($"<div class='language-output' style='margin: 10px 0; border-left: 3px solid {color}; padding-left: 10px;'>");

            if (enableCollapse)
            {
                // Header with collapse/expand button
                var uniqueId = $"lang-output-{_outputCounter++}";
                sb.AppendLine($"<div class='language-header' onclick='toggleLangOutput(\"{uniqueId}\")' style='font-weight: bold; color: {color}; margin-bottom: 5px; cursor: pointer; user-select: none;'>");
                sb.AppendLine($"<span id='{uniqueId}-icon' style='display: inline-block; width: 16px;'>▼</span> {displayName}:");
                sb.AppendLine("</div>");

                // Collapsible content
                sb.AppendLine($"<div id='{uniqueId}' class='language-content'>");
            }
            else
            {
                // Simple header without collapse button
                sb.AppendLine($"<div class='language-header' style='font-weight: bold; color: {color}; margin-bottom: 5px;'>{displayName}:</div>");
                sb.AppendLine("<div class='language-content'>");
            }

            if (!result.Success)
            {
                sb.AppendLine($"<div class='language-error' style='color: #d32f2f; padding: 5px 0; font-family: monospace; white-space: pre-wrap;'>");
                sb.AppendLine(HttpUtility.HtmlEncode($"ERROR:\n{error}"));
                sb.AppendLine("</div>");
            }
            else if (!string.IsNullOrWhiteSpace(output))
            {
                sb.AppendLine($"<div class='language-output-text' style='color: #333; padding: 5px 0; font-family: monospace; white-space: pre-wrap;'>");
                // Check if output contains HTML tags (like <img>) - don't escape those
                if (ContainsHtmlTags(output))
                {
                    sb.AppendLine(ProcessOutputWithHtml(output));
                }
                else
                {
                    sb.AppendLine(HttpUtility.HtmlEncode(output));
                }
                sb.AppendLine("</div>");
            }
            else
            {
                if (IsGuiLanguage(language))
                {
                    sb.AppendLine($"<div class='language-success' style='color: #388e3c; padding: 5px 0; font-style: italic;'>");
                    sb.AppendLine($"✓ {displayName} ejecutado correctamente (ventana GUI mostrada)");
                    sb.AppendLine("</div>");
                }
                else
                {
                    sb.AppendLine("<div class='language-no-output' style='color: #757575; font-style: italic; padding: 5px 0;'>(sin salida)</div>");
                }
            }

            sb.AppendLine("</div>"); // Close language-content
            sb.AppendLine("</div>"); // Close language-output

            return sb.ToString();
        }

        /// <summary>
        /// Checks if a language is a GUI framework
        /// </summary>
        private static bool IsGuiLanguage(string language)
        {
            return language.ToLower() switch
            {
                "qt" => true,
                "gtk" => true,
                "wpf" => true,
                "xaml" => true,
                "avalonia" => true,
                _ => false
            };
        }

        /// <summary>
        /// Loads a template file for a language
        /// </summary>
        private static string LoadTemplate(string language)
        {
            if (_templateCache.TryGetValue(language, out var cached))
                return cached;

            var templatePath = Path.Combine(TemplatesPath, $"{language}.html");
            if (!File.Exists(templatePath))
            {
                // Try base template
                templatePath = Path.Combine(TemplatesPath, "base.html");
            }

            if (File.Exists(templatePath))
            {
                try
                {
                    var template = File.ReadAllText(templatePath);
                    _templateCache[language] = template;
                    return template;
                }
                catch
                {
                    // Fall through to return null
                }
            }

            return null;
        }

        /// <summary>
        /// Generates inline HTML (fallback when templates not available)
        /// </summary>
        private static string GenerateInlineHtml(string displayName, string headerColor, string outputColor, string output)
        {
            var sb = new StringBuilder();
            sb.Append($"<div style=\"margin:10px 0;font-family:Consolas,Monaco,monospace;\">");
            sb.Append($"<div style=\"padding:6px 12px;border-radius:4px 4px 0 0;font-weight:bold;font-size:12px;color:white;background-color:{headerColor};\">{displayName}</div>");
            sb.Append($"<div style=\"background-color:#1e1e1e;color:{outputColor};border:1px solid #3c3c3c;border-top:none;padding:10px;white-space:pre-wrap;font-size:13px;line-height:1.4;border-radius:0 0 4px 4px;max-height:400px;overflow-y:auto;\">{output}</div>");
            sb.Append("</div>");
            return sb.ToString();
        }

        /// <summary>
        /// Gets display name for a language
        /// </summary>
        private static string GetDisplayName(string language)
        {
            return language.ToLower() switch
            {
                "python" => "Python",
                "octave" => "GNU Octave",
                "cpp" => "C++",
                "julia" => "Julia",
                "r" => "R",
                "powershell" => "PowerShell",
                "bash" => "Bash",
                "cmd" => "Command Prompt",
                "markdown" => "Markdown",
                "csharp" => "C#",
                "xaml" => "XAML",
                "wpf" => "WPF",
                "opensees" => "OpenSees",
                "rust" => "Rust",
                _ => language
            };
        }

        /// <summary>
        /// Resets the template cache
        /// </summary>
        public static void ResetStyles()
        {
            _templateCache.Clear();
        }

        /// <summary>
        /// Generates HTML for multiple execution results
        /// </summary>
        public static string GenerateHtml(Dictionary<string, List<(CodeBlock block, ExecutionResult result)>> results)
        {
            var sb = new StringBuilder();

            foreach (var (language, blocks) in results)
            {
                foreach (var (block, result) in blocks)
                {
                    sb.AppendLine(GenerateHtml(language, result));
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Generates HTML output for a code block execution
        /// </summary>
        public static string GenerateOutput(string language, string code, ExecutionResult result, bool enableCollapse = true)
        {
            return GenerateHtml(language, result, enableCollapse);
        }

        /// <summary>
        /// Generates HTML for when a language is not available
        /// </summary>
        public static string GenerateNotAvailable(string language, string code)
        {
            var result = new ExecutionResult
            {
                Success = false,
                Error = $"Language '{language}' is not installed or not found in PATH.\nPlease install it and add to system PATH."
            };
            return GenerateHtml(language, result);
        }

        /// <summary>
        /// Checks if output contains HTML tags that should be preserved
        /// </summary>
        private static bool ContainsHtmlTags(string output)
        {
            if (string.IsNullOrEmpty(output))
                return false;

            // Check for common HTML tags that should be preserved
            return output.Contains("<img ", StringComparison.OrdinalIgnoreCase) ||
                   output.Contains("<img>", StringComparison.OrdinalIgnoreCase) ||
                   output.Contains("<a ", StringComparison.OrdinalIgnoreCase) ||
                   output.Contains("<div ", StringComparison.OrdinalIgnoreCase) ||
                   output.Contains("<span ", StringComparison.OrdinalIgnoreCase) ||
                   output.Contains("<table", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Processes output that contains HTML tags - preserves HTML, escapes plain text
        /// </summary>
        private static string ProcessOutputWithHtml(string output)
        {
            var sb = new StringBuilder();
            var lines = output.Split('\n');

            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                // If line starts with HTML tag, don't escape it
                // Support common HTML tags: img, a, div, span, table, p, ul, ol, li, h1-h6, strong, em, br, hr
                if (trimmed.StartsWith("<") && IsHtmlTag(trimmed))
                {
                    sb.AppendLine(line);
                }
                else
                {
                    sb.AppendLine(HttpUtility.HtmlEncode(line));
                }
            }

            return sb.ToString().TrimEnd();
        }

        /// <summary>
        /// Checks if a line contains a recognized HTML tag
        /// </summary>
        private static bool IsHtmlTag(string trimmed)
        {
            // Common HTML tags to preserve
            return trimmed.StartsWith("<img", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<a ", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<div", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<span", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<table", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<p>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<p ", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</p>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<ul>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<ul ", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</ul>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<ol>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<ol ", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</ol>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<li>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<li ", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</li>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<strong>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</strong>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<em>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</em>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<br", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<hr", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h1", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h2", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h3", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h4", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h5", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<h6", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</h", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</div>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</span>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</table>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<tr", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</tr>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<td", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</td>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<th", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</th>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<thead", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</thead>", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("<tbody", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.StartsWith("</tbody>", StringComparison.OrdinalIgnoreCase);
        }
    }
}
