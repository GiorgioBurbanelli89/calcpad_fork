// SMathConverter.cs - Conversor de SMath Studio (.sm) a Calcpad (.cpd)
// El formato .sm es XML plano (no ZIP como .mcdx)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace Calcpad.Common
{
    /// <summary>
    /// Conversor de archivos SMath Studio (.sm) a Calcpad (.cpd)
    /// </summary>
    public class SMathConverter
    {
        private readonly StringBuilder _output = new StringBuilder();
        private readonly List<string> _warnings = new List<string>();
        private string _smathVersion = "Desconocida";

        /// <summary>
        /// Lista de advertencias generadas durante la conversión
        /// </summary>
        public IReadOnlyList<string> Warnings => _warnings.AsReadOnly();

        /// <summary>
        /// Versión de SMath Studio detectada en el archivo
        /// </summary>
        public string SMathVersion => _smathVersion;

        /// <summary>
        /// Convierte un archivo .sm a formato .cpd (string)
        /// </summary>
        /// <param name="smPath">Ruta al archivo .sm</param>
        /// <returns>Contenido en formato Calcpad</returns>
        public string Convert(string smPath)
        {
            if (!File.Exists(smPath))
                throw new FileNotFoundException($"Archivo no encontrado: {smPath}");

            _output.Clear();
            _warnings.Clear();
            _smathVersion = "Desconocida";

            try
            {
                // SMath files are plain XML
                var doc = XDocument.Load(smPath);
                var root = doc.Root;

                if (root == null)
                    throw new Exception("El archivo .sm no tiene un elemento raíz válido");

                // Extract version info
                ExtractSMathVersion(root);

                // Write header
                _output.AppendLine("' ============================================");
                _output.AppendLine($"' Importado de SMath Studio (.sm)");
                _output.AppendLine($"' Versión SMath: {_smathVersion}");
                _output.AppendLine($"' Archivo: {Path.GetFileName(smPath)}");
                _output.AppendLine($"' Fecha: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
                _output.AppendLine("' ============================================");
                _output.AppendLine();

                // Process the worksheet
                ProcessWorksheet(root);

                return _output.ToString();
            }
            catch (Exception ex)
            {
                throw new Exception($"Error al procesar archivo SMath: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Convierte y guarda a archivo
        /// </summary>
        public string ConvertAndSave(string smPath, string outputPath = null)
        {
            if (string.IsNullOrEmpty(outputPath))
                outputPath = Path.ChangeExtension(smPath, ".cpd");

            string content = Convert(smPath);
            File.WriteAllText(outputPath, content, Encoding.UTF8);
            return outputPath;
        }

        /// <summary>
        /// Extrae la versión de SMath Studio
        /// </summary>
        private void ExtractSMathVersion(XElement root)
        {
            try
            {
                // Look for version attribute in root or metadata
                var versionAttr = root.Attribute("version");
                if (versionAttr != null)
                {
                    _smathVersion = versionAttr.Value;
                    return;
                }

                // Try to find in settings or metadata elements
                var settings = root.Element("settings");
                if (settings != null)
                {
                    var ver = settings.Element("version")?.Value;
                    if (!string.IsNullOrEmpty(ver))
                    {
                        _smathVersion = ver;
                        return;
                    }
                }

                // Check for "generator" or similar attributes
                var generator = root.Attribute("generator")?.Value;
                if (!string.IsNullOrEmpty(generator))
                {
                    _smathVersion = generator;
                    return;
                }

                _smathVersion = "SMath Studio";
            }
            catch
            {
                _smathVersion = "Desconocida";
            }
        }

        /// <summary>
        /// Procesa el documento XML del worksheet
        /// </summary>
        private void ProcessWorksheet(XElement root)
        {
            // SMath structure varies, but typically has regions or math elements
            // Common structures:
            // <worksheet><regions><region>...</region></regions></worksheet>
            // or <math><region>...</region></math>

            var regions = root.Descendants("region").ToList();
            if (regions.Count == 0)
            {
                // Try alternative structures
                regions = root.Descendants("math").ToList();
            }
            if (regions.Count == 0)
            {
                // Try to find any element with math content
                regions = root.Elements().ToList();
            }

            foreach (var region in regions)
            {
                ProcessRegion(region);
            }

            if (_output.Length == 0 || _output.ToString().Trim().Split('\n').Length <= 7)
            {
                _warnings.Add("El archivo parece estar vacío o no contiene expresiones matemáticas reconocibles");
            }
        }

        /// <summary>
        /// Procesa una región del documento
        /// </summary>
        private void ProcessRegion(XElement region)
        {
            var regionType = region.Attribute("type")?.Value ?? region.Name.LocalName;

            switch (regionType.ToLowerInvariant())
            {
                case "math":
                case "expression":
                case "formula":
                    ProcessMathRegion(region);
                    break;
                case "text":
                case "comment":
                    ProcessTextRegion(region);
                    break;
                case "plot":
                case "graph":
                    _warnings.Add("Gráfico no soportado - se omitió");
                    _output.AppendLine("' [Gráfico de SMath - no soportado]");
                    break;
                case "region":
                    // Generic region - try to detect content type
                    var mathContent = region.Descendants("math").FirstOrDefault() ??
                                     region.Descendants("e").FirstOrDefault() ??
                                     region.Descendants("expr").FirstOrDefault();
                    if (mathContent != null)
                        ProcessMathRegion(region);
                    else
                        ProcessTextRegion(region);
                    break;
                default:
                    // Try to extract any math-like content
                    var content = region.Value?.Trim();
                    if (!string.IsNullOrEmpty(content))
                    {
                        if (content.Contains("=") || content.Contains(":="))
                            _output.AppendLine(CleanExpression(content));
                        else
                            _output.AppendLine($"' {content}");
                    }
                    break;
            }
        }

        /// <summary>
        /// Procesa una región matemática
        /// </summary>
        private void ProcessMathRegion(XElement region)
        {
            try
            {
                // SMath uses different XML structures for math
                // Try to find the expression content
                var expr = ExtractExpression(region);

                if (!string.IsNullOrWhiteSpace(expr))
                {
                    _output.AppendLine(CleanExpression(expr));
                }
            }
            catch (Exception ex)
            {
                _warnings.Add($"Error procesando expresión matemática: {ex.Message}");
            }
        }

        /// <summary>
        /// Extrae una expresión del elemento
        /// </summary>
        private string ExtractExpression(XElement elem)
        {
            // SMath stores expressions in various ways
            // Try different approaches

            // 1. Direct value
            var directValue = elem.Value?.Trim();
            if (!string.IsNullOrEmpty(directValue) &&
                (directValue.Contains("=") || directValue.Contains(":=")))
            {
                return directValue;
            }

            // 2. Look for specific SMath elements
            var eElement = elem.Descendants("e").FirstOrDefault();
            if (eElement != null)
            {
                return ProcessSMathExpression(eElement);
            }

            // 3. Look for "math" child
            var mathElement = elem.Descendants("math").FirstOrDefault();
            if (mathElement != null)
            {
                return ProcessSMathExpression(mathElement);
            }

            // 4. Look for assignment patterns in child elements
            var children = elem.Elements().ToList();
            if (children.Count > 0)
            {
                var sb = new StringBuilder();
                foreach (var child in children)
                {
                    var childExpr = ExtractExpression(child);
                    if (!string.IsNullOrWhiteSpace(childExpr))
                        sb.AppendLine(childExpr);
                }
                return sb.ToString().Trim();
            }

            return directValue ?? "";
        }

        /// <summary>
        /// Procesa una expresión SMath específica
        /// </summary>
        private string ProcessSMathExpression(XElement expr)
        {
            var sb = new StringBuilder();

            // SMath uses operators like ≔ for assignment
            // We need to convert to Calcpad syntax

            foreach (var node in expr.Nodes())
            {
                if (node is XElement el)
                {
                    var localName = el.Name.LocalName.ToLowerInvariant();
                    switch (localName)
                    {
                        case "v": // Variable
                        case "var":
                        case "id":
                            sb.Append(CleanIdentifier(el.Value));
                            break;
                        case "n": // Number
                        case "num":
                        case "real":
                            sb.Append(el.Value);
                            break;
                        case "o": // Operator
                        case "op":
                            var op = el.Value?.Trim();
                            sb.Append(ConvertOperator(op));
                            break;
                        case "f": // Function
                        case "func":
                            sb.Append(ConvertFunction(el));
                            break;
                        case "mat": // Matrix
                        case "matrix":
                            sb.Append(ProcessMatrix(el));
                            break;
                        case "vec": // Vector
                        case "vector":
                            sb.Append(ProcessVector(el));
                            break;
                        default:
                            // Recurse into unknown elements
                            sb.Append(ProcessSMathExpression(el));
                            break;
                    }
                }
                else if (node is XText text)
                {
                    sb.Append(text.Value);
                }
            }

            return sb.ToString();
        }

        /// <summary>
        /// Convierte operadores de SMath a Calcpad
        /// </summary>
        private string ConvertOperator(string op)
        {
            return op switch
            {
                "≔" => " = ",      // Assignment
                ":=" => " = ",     // Assignment
                "→" => " = ",      // Evaluation
                "·" => "*",        // Multiplication
                "×" => "*",        // Multiplication
                "÷" => "/",        // Division
                "²" => "^2",       // Square
                "³" => "^3",       // Cube
                "√" => "sqrt",     // Square root
                "∑" => "sum",      // Sum
                "∏" => "product",  // Product
                "∫" => "integral", // Integral
                "π" => "π",        // Pi
                "∞" => "∞",        // Infinity
                _ => op ?? ""
            };
        }

        /// <summary>
        /// Convierte funciones de SMath a Calcpad
        /// </summary>
        private string ConvertFunction(XElement func)
        {
            var funcName = func.Attribute("name")?.Value ?? func.Value;
            var args = func.Elements().Select(e => ProcessSMathExpression(e));

            // Map SMath function names to Calcpad
            var calcpadFunc = funcName?.ToLowerInvariant() switch
            {
                "sqrt" => "sqrt",
                "sin" => "sin",
                "cos" => "cos",
                "tan" => "tan",
                "asin" => "asin",
                "acos" => "acos",
                "atan" => "atan",
                "log" => "log",
                "ln" => "ln",
                "exp" => "exp",
                "abs" => "abs",
                "floor" => "floor",
                "ceil" => "ceiling",
                "round" => "round",
                "max" => "max",
                "min" => "min",
                "sum" => "sum",
                "det" => "det",
                "transpose" => "transp",
                "inverse" => "inv",
                _ => funcName
            };

            return $"{calcpadFunc}({string.Join("; ", args)})";
        }

        /// <summary>
        /// Procesa una matriz de SMath
        /// </summary>
        private string ProcessMatrix(XElement matrix)
        {
            var rows = matrix.Elements("row").ToList();
            if (rows.Count == 0)
            {
                rows = matrix.Elements("r").ToList();
            }
            if (rows.Count == 0)
            {
                // Try to parse inline
                return $"[{matrix.Value}]";
            }

            var sb = new StringBuilder("[");
            for (int r = 0; r < rows.Count; r++)
            {
                if (r > 0) sb.Append(" | ");

                var cells = rows[r].Elements().ToList();
                for (int c = 0; c < cells.Count; c++)
                {
                    if (c > 0) sb.Append("; ");
                    sb.Append(ProcessSMathExpression(cells[c]));
                }
            }
            sb.Append("]");
            return sb.ToString();
        }

        /// <summary>
        /// Procesa un vector de SMath
        /// </summary>
        private string ProcessVector(XElement vector)
        {
            var elements = vector.Elements().ToList();
            if (elements.Count == 0)
            {
                return $"[{vector.Value}]";
            }

            var values = elements.Select(e => ProcessSMathExpression(e));
            return $"[{string.Join("; ", values)}]";
        }

        /// <summary>
        /// Procesa una región de texto
        /// </summary>
        private void ProcessTextRegion(XElement region)
        {
            var content = region.Value?.Trim();
            if (!string.IsNullOrEmpty(content))
            {
                // Convert to Calcpad comment
                foreach (var line in content.Split('\n'))
                {
                    _output.AppendLine($"' {line.Trim()}");
                }
            }
        }

        /// <summary>
        /// Limpia un identificador
        /// </summary>
        private string CleanIdentifier(string id)
        {
            if (string.IsNullOrEmpty(id))
                return "";

            // Remove subscript markers
            id = Regex.Replace(id, @"_(\d+)", "$1");

            // Convert common Greek letters
            id = id.Replace("alpha", "α")
                   .Replace("beta", "β")
                   .Replace("gamma", "γ")
                   .Replace("delta", "δ")
                   .Replace("epsilon", "ε")
                   .Replace("theta", "θ")
                   .Replace("lambda", "λ")
                   .Replace("mu", "μ")
                   .Replace("pi", "π")
                   .Replace("sigma", "σ")
                   .Replace("omega", "ω");

            return id.Trim();
        }

        /// <summary>
        /// Limpia una expresión para Calcpad
        /// </summary>
        private string CleanExpression(string expr)
        {
            if (string.IsNullOrEmpty(expr))
                return "";

            // Convert assignment operators
            expr = expr.Replace("≔", "=")
                       .Replace(":=", "=")
                       .Replace("→", "=");

            // Convert multiplication
            expr = expr.Replace("·", "*")
                       .Replace("×", "*");

            // Convert division
            expr = expr.Replace("÷", "/");

            // Convert powers
            expr = expr.Replace("²", "^2")
                       .Replace("³", "^3");

            // Clean up whitespace
            expr = Regex.Replace(expr, @"\s+", " ").Trim();

            return expr;
        }
    }
}
