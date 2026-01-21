using Calcpad.Core;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;

namespace Calcpad.Common
{
    /// <summary>
    /// Unified file reader for Calcpad files (.cpd, .cpdz, .txt)
    /// Combines functionality from Calcpad.Cli and Calcpad.Wpf
    /// </summary>
    public static class CalcpadReader
    {
        private static readonly StringBuilder _stringBuilder = new();

        /// <summary>
        /// TEST FUNCTION: Simple suma function to verify Calcpad.Common works in both CLI and WPF
        /// suma(x) = x + 1
        /// </summary>
        /// <param name="x">Input value</param>
        /// <returns>x + 1</returns>
        public static double Suma(double x)
        {
            return x + 1;
        }

        /// <summary>
        /// Returns a test message to verify the Common library is loaded
        /// </summary>
        public static string GetTestMessage()
        {
            return "[Calcpad.Common] Library loaded successfully!";
        }

        /// <summary>
        /// Reads and processes a Calcpad file
        /// </summary>
        /// <param name="fileName">Path to the file</param>
        /// <param name="environment">The environment calling this method (Cli, Wpf, Api)</param>
        /// <returns>Processed file content as string</returns>
        public static string Read(string fileName, CalcpadEnvironment environment = CalcpadEnvironment.Cli)
        {
            var content = ReadFileContent(fileName, environment);
            var inputLines = content.EnumerateLines();
            var outputLines = new List<string>();
            var hasForm = false;
            var insideLanguageBlock = false;

            foreach (var line in inputLines)
            {
                var lineStr = line.ToString();
                var trimmedLine = lineStr.Trim();

                // Check if we're entering or exiting a language block
                // MultLang directives use @{language} and @{end language} format
                if (trimmedLine.StartsWith("@{"))
                {
                    if (trimmedLine.StartsWith("@{end "))
                    {
                        insideLanguageBlock = false;
                    }
                    else
                    {
                        // @{python}, @{octave}, @{csharp}, etc.
                        insideLanguageBlock = true;
                    }
                }
                // Also check old-style directives starting with #
                else if (trimmedLine.StartsWith("#") && !trimmedLine.StartsWith("#hide") &&
                    !trimmedLine.StartsWith("#show") && !trimmedLine.StartsWith("#pre") &&
                    !trimmedLine.StartsWith("#post") && !trimmedLine.StartsWith("#val") &&
                    !trimmedLine.StartsWith("#equ") && !trimmedLine.StartsWith("#noc"))
                {
                    // Could be a language directive like #python, #csharp, etc.
                    if (trimmedLine.Contains("end"))
                    {
                        insideLanguageBlock = false;
                    }
                    else
                    {
                        insideLanguageBlock = true;
                    }
                }

                ReadOnlySpan<char> s;
                if (line.Contains('\v'))
                {
                    hasForm = true;
                    var n = line.IndexOf('\v');
                    if (n == 0)
                    {
                        InputFieldProcessor.SetInputFieldsFromFile(line[1..].EnumerateSplits('\t'), outputLines);
                        break;
                    }
                    else
                    {
                        InputFieldProcessor.SetInputFieldsFromFile(line[(n + 1)..].EnumerateSplits('\t'), outputLines);
                        s = line[..n];
                    }
                }
                else
                {
                    // Don't process operators inside language blocks
                    if (insideLanguageBlock)
                    {
                        s = line.TrimStart('\t');
                    }
                    else
                    {
                        s = OperatorConverter.ReplaceCStyleOperators(line.TrimStart('\t'));
                    }

                    if (!hasForm)
                        hasForm = MacroParser.HasInputFields(s);
                }
                outputLines.Add(s.ToString());
            }
            return string.Join(Environment.NewLine, outputLines);
        }

        /// <summary>
        /// Reads text content from a Calcpad file, handling compression if needed
        /// Use .EnumerateLines() from Calcpad.Core to iterate over lines
        /// </summary>
        /// <param name="fileName">Path to the file</param>
        /// <param name="environment">The environment calling this method</param>
        /// <returns>File content as string</returns>
        public static string ReadFileContent(string fileName, CalcpadEnvironment environment = CalcpadEnvironment.Cli)
        {
            if (Path.GetExtension(fileName).Equals(".cpdz", StringComparison.InvariantCultureIgnoreCase))
            {
                // Check if it's a ZIP archive (composite with images) or simple deflate
                if (Zip.IsComposite(fileName))
                {
                    // WPF uses DecompressWithImages to extract images alongside code
                    // CLI can also benefit from this for full compatibility
                    return Zip.DecompressWithImages(fileName);
                }
                else
                {
                    var f = new FileInfo(fileName)
                    {
                        IsReadOnly = false
                    };
                    using var fs = f.OpenRead();
                    return Zip.Decompress(fs);
                }
            }
            return File.ReadAllText(fileName);
        }

        /// <summary>
        /// Reads text content from a file, handling compression
        /// Alias for ReadFileContent for backward compatibility
        /// </summary>
        /// <param name="fileName">Path to the file</param>
        /// <returns>File content as string</returns>
        public static string ReadText(string fileName) => ReadFileContent(fileName);

        /// <summary>
        /// Processes an #include directive, reading and merging the included file
        /// </summary>
        /// <param name="fileName">Path to the included file</param>
        /// <param name="fields">Queue of field values for form processing</param>
        /// <returns>Processed content from the included file</returns>
        public static string Include(string fileName, Queue<string> fields)
        {
            var isLocal = false;
            var insideLanguageBlock = false;
            var s = File.ReadAllText(fileName);
            var j = s.IndexOf('\v');
            var hasForm = j > 0;
            var lines = (hasForm ? s[..j] : s).EnumerateLines();
            var getLines = new List<string>();
            var sf = hasForm ? s[(j + 1)..] : default;
            Queue<string> getFields = InputFieldProcessor.GetFields(sf, fields);
            foreach (var line in lines)
            {
                var lineStr = line.ToString();
                var trimmedLine = lineStr.Trim();

                // Check if we're entering or exiting a language block
                if (trimmedLine.StartsWith("#") && !trimmedLine.StartsWith("#hide") &&
                    !trimmedLine.StartsWith("#show") && !trimmedLine.StartsWith("#pre") &&
                    !trimmedLine.StartsWith("#post") && !trimmedLine.StartsWith("#val") &&
                    !trimmedLine.StartsWith("#equ") && !trimmedLine.StartsWith("#noc") &&
                    !trimmedLine.StartsWith("#local") && !trimmedLine.StartsWith("#global") &&
                    !trimmedLine.StartsWith("#include"))
                {
                    // Could be a language directive like #python, #csharp, #c, etc.
                    if (trimmedLine.Contains("end"))
                    {
                        insideLanguageBlock = false;
                    }
                    else
                    {
                        insideLanguageBlock = true;
                    }
                }

                if (Validator.IsKeyword(line, "#local"))
                    isLocal = true;
                else if (Validator.IsKeyword(line, "#global"))
                    isLocal = false;
                else
                {
                    if (!isLocal)
                    {
                        // Only process #include if we're NOT inside a language block
                        if (!insideLanguageBlock && Validator.IsKeyword(line, "#include"))
                        {
                            var includeFileName = GetModuleName(line);
                            getLines.Add(fields is null
                                ? Include(includeFileName, null)
                                : Include(includeFileName, new()));
                        }
                        else
                            getLines.Add(lineStr);
                    }
                }
            }
            if (hasForm && string.IsNullOrWhiteSpace(getLines[^1]))
                getLines.RemoveAt(getLines.Count - 1);

            var len = getLines.Count;
            if (len > 0)
            {
                _stringBuilder.Clear();
                for (int i = 0; i < len; ++i)
                {
                    if (getFields is not null && getFields.Count > 0)
                    {
                        if (MacroParser.SetLineInputFields(getLines[i].TrimEnd(), _stringBuilder, getFields, false))
                            getLines[i] = _stringBuilder.ToString();

                        _stringBuilder.Clear();
                    }
                }
            }
            return string.Join(Environment.NewLine, getLines);
        }

        /// <summary>
        /// Extracts the module name from an #include directive
        /// </summary>
        private static string GetModuleName(ReadOnlySpan<char> s)
        {
            var n = s.Length;
            if (n < 9)
                return null;

            n = s.IndexOfAny('\'', '"');
            var n1 = s.LastIndexOf('#');
            if (n < 9 || n1 > 0 && n1 < n)
                n = n1;

            if (n < 9)
                n = s.Length;

            return s[8..n].Trim().ToString();
        }

        private const string ErrorString = "#Error";

        /// <summary>
        /// Converts code to HTML with line numbers and error highlighting
        /// </summary>
        /// <param name="code">Source code to convert</param>
        /// <returns>HTML representation of the code</returns>
        public static string CodeToHtml(string code)
        {
            const string spaces = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
            var errors = new Queue<int>();
            _stringBuilder.Clear();
            var lines = code.EnumerateLines();
            _stringBuilder.AppendLine("<pre class=\"code\">");
            var lineNumber = 0;
            foreach (var line in lines)
            {
                ++lineNumber;
                var i = line.IndexOf('\v');
                var lineText = i < 0 ? line : line[..i];
                var sourceLine = i < 0 ? lineNumber.ToString() : line[(i + 1)..];
                var lineNumText = lineNumber.ToString(CultureInfo.InvariantCulture);
                var n = lineNumText.Length;
                _stringBuilder.Append($"<p class=\"line-text\" id=\"line-{lineNumber}\"><span title=\"Source line {sourceLine}\">{spaces[(6 * n)..]}{lineNumber}</span>&emsp;│&emsp;");
                if (line.StartsWith(ErrorString))
                {
                    errors.Enqueue(lineNumber);
                    _stringBuilder.Append($"<span class=\"err\">{lineText[1..]}</span>");
                }
                else
                {
                    _stringBuilder.Append(lineText);
                }
                _stringBuilder.Append("</p>");
            }
            _stringBuilder.Append("</pre>");
            if (errors.Count != 0 && lineNumber > 30)
            {
                _stringBuilder.AppendLine($"<div class=\"errorHeader\">Found <b>{errors.Count}</b> errors in modules and macros:");
                var count = 0;
                while (errors.Count != 0 && ++count < 20)
                {
                    var errorLine = errors.Dequeue();
                    _stringBuilder.Append($" <span class=\"roundBox\" data-line=\"{errorLine}\">{errorLine}</span>");
                }
                if (errors.Count > 0)
                    _stringBuilder.Append(" ...");

                _stringBuilder.Append("</div>");
                _stringBuilder.AppendLine("<style>body {padding-top:0.5em;} p {margin:0; line-height:1.15em;}</style>");
            }
            else
                _stringBuilder.AppendLine("<style>p {margin:0; line-height:1.15em;}</style>");
            return _stringBuilder.ToString();
        }
    }
}
