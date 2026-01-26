// McdxConverter.cs - Conversor de Mathcad Prime (.mcdx) a Calcpad (.cpd)
// El formato .mcdx es un archivo ZIP que contiene XML

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace McdxToCpd
{
    /// <summary>
    /// Conversor de archivos Mathcad Prime (.mcdx) a Calcpad (.cpd)
    /// </summary>
    public class McdxConverter
    {
        private readonly StringBuilder _output = new StringBuilder();
        private readonly List<string> _warnings = new List<string>();

        /// <summary>
        /// Convierte un archivo .mcdx a formato .cpd
        /// </summary>
        public string Convert(string mcdxPath)
        {
            if (!File.Exists(mcdxPath))
                throw new FileNotFoundException($"Archivo no encontrado: {mcdxPath}");

            _output.Clear();
            _warnings.Clear();

            // Agregar encabezado
            _output.AppendLine("' Archivo convertido de Mathcad Prime (.mcdx) a Calcpad (.cpd)");
            _output.AppendLine($"' Archivo original: {Path.GetFileName(mcdxPath)}");
            _output.AppendLine($"' Fecha de conversion: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            _output.AppendLine();

            try
            {
                // Abrir el archivo .mcdx como ZIP
                using (var archive = ZipFile.OpenRead(mcdxPath))
                {
                    // Buscar el archivo worksheet.xml principal
                    var worksheetEntry = archive.GetEntry("worksheet/worksheet.xml");

                    if (worksheetEntry == null)
                    {
                        // Intentar otros nombres posibles
                        foreach (var entry in archive.Entries)
                        {
                            if (entry.Name.EndsWith(".xml", StringComparison.OrdinalIgnoreCase))
                            {
                                Console.WriteLine($"  Encontrado: {entry.FullName}");
                            }
                        }
                        throw new Exception("No se encontro worksheet.xml en el archivo .mcdx");
                    }

                    // Leer y parsear el XML
                    using (var stream = worksheetEntry.Open())
                    {
                        var doc = XDocument.Load(stream);
                        ProcessWorksheet(doc);
                    }
                }
            }
            catch (InvalidDataException)
            {
                throw new Exception("El archivo no es un archivo ZIP valido (.mcdx debe ser un archivo ZIP)");
            }

            // Agregar advertencias al final
            if (_warnings.Count > 0)
            {
                _output.AppendLine();
                _output.AppendLine("' === ADVERTENCIAS DE CONVERSION ===");
                foreach (var warning in _warnings)
                {
                    _output.AppendLine($"' {warning}");
                }
            }

            return _output.ToString();
        }

        /// <summary>
        /// Procesa el documento XML del worksheet
        /// </summary>
        private void ProcessWorksheet(XDocument doc)
        {
            var root = doc.Root;
            if (root == null) return;

            // Namespace de Mathcad
            XNamespace ns = root.GetDefaultNamespace();

            // Buscar regiones (regions)
            var regions = root.Descendants(ns + "region");

            foreach (var region in regions)
            {
                ProcessRegion(region, ns);
            }
        }

        /// <summary>
        /// Procesa una region individual
        /// </summary>
        private void ProcessRegion(XElement region, XNamespace ns)
        {
            // Determinar tipo de region
            var math = region.Element(ns + "math");
            var text = region.Element(ns + "text");
            var plot = region.Element(ns + "plot");

            if (math != null)
            {
                ProcessMathRegion(math, ns);
            }
            else if (text != null)
            {
                ProcessTextRegion(text);
            }
            else if (plot != null)
            {
                _warnings.Add("Graficos (plot) no soportados - se omitio una region de grafico");
            }
        }

        /// <summary>
        /// Procesa una region matematica
        /// </summary>
        private void ProcessMathRegion(XElement math, XNamespace ns)
        {
            try
            {
                // Extraer la expresion
                string expression = ExtractExpression(math, ns);

                if (!string.IsNullOrWhiteSpace(expression))
                {
                    // Convertir sintaxis de Mathcad a Calcpad
                    string converted = ConvertSyntax(expression);
                    _output.AppendLine(converted);
                }
            }
            catch (Exception ex)
            {
                _warnings.Add($"Error procesando expresion: {ex.Message}");
            }
        }

        /// <summary>
        /// Extrae la expresion matematica del XML
        /// </summary>
        private string ExtractExpression(XElement math, XNamespace ns)
        {
            var sb = new StringBuilder();

            // Recorrer elementos hijos
            foreach (var elem in math.Descendants())
            {
                string localName = elem.Name.LocalName;

                switch (localName)
                {
                    case "id":      // Identificador/variable
                        sb.Append(elem.Value);
                        break;
                    case "real":    // Numero real
                        sb.Append(elem.Value);
                        break;
                    case "str":     // String
                        sb.Append($"\"{elem.Value}\"");
                        break;
                    case "apply":   // Aplicacion de operador
                        // El operador esta en el atributo
                        break;
                    case "define":  // Definicion (=)
                        sb.Append(" = ");
                        break;
                    case "eval":    // Evaluacion (resultado)
                        sb.Append(" = ?");
                        break;
                    case "plus":
                        sb.Append(" + ");
                        break;
                    case "minus":
                        sb.Append(" - ");
                        break;
                    case "mult":
                        sb.Append("*");
                        break;
                    case "div":
                        sb.Append("/");
                        break;
                    case "pow":
                        sb.Append("^");
                        break;
                    case "sqrt":
                        sb.Append("sqrt(");
                        break;
                    case "parens":
                        sb.Append("(");
                        break;
                }
            }

            return sb.ToString().Trim();
        }

        /// <summary>
        /// Convierte la sintaxis de Mathcad a Calcpad
        /// </summary>
        private string ConvertSyntax(string expr)
        {
            string result = expr;

            // Conversiones de sintaxis
            var conversions = new Dictionary<string, string>
            {
                // Funciones matematicas
                { @"\bsin\(", "sin(" },
                { @"\bcos\(", "cos(" },
                { @"\btan\(", "tan(" },
                { @"\bsqrt\(", "sqr(" },    // Calcpad usa sqr() para raiz cuadrada
                { @"\babs\(", "abs(" },
                { @"\bln\(", "ln(" },
                { @"\blog\(", "log(" },
                { @"\bexp\(", "exp(" },

                // Constantes
                { @"\bpi\b", "pi" },
                { @"\be\b", "e" },

                // Operadores
                { ":=", " = " },            // Definicion en Mathcad
                { "==", " = " },

                // Unidades comunes (Mathcad -> Calcpad)
                { @"\bkN\b", "kN" },
                { @"\bMPa\b", "MPa" },
                { @"\bGPa\b", "GPa" },
                { @"\bmm\b", "mm" },
                { @"\bcm\b", "cm" },
                { @"\bm\b", "m" },
            };

            foreach (var conv in conversions)
            {
                result = Regex.Replace(result, conv.Key, conv.Value);
            }

            // Limpiar espacios multiples
            result = Regex.Replace(result, @"\s+", " ");

            return result.Trim();
        }

        /// <summary>
        /// Procesa una region de texto
        /// </summary>
        private void ProcessTextRegion(XElement text)
        {
            string content = text.Value;

            if (!string.IsNullOrWhiteSpace(content))
            {
                // Convertir a comentario de Calcpad
                _output.AppendLine($"' {content}");
            }
        }

        /// <summary>
        /// Lista de advertencias generadas durante la conversion
        /// </summary>
        public IReadOnlyList<string> Warnings => _warnings.AsReadOnly();
    }
}
