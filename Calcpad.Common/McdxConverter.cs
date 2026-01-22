// McdxConverter.cs - Conversor de Mathcad Prime (.mcdx) a Calcpad (.cpd)
// El formato .mcdx es un archivo ZIP (Open Packaging Conventions) que contiene XML
// Usado por: Botón "Importar Mathcad" y directiva @{mcdx}

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace Calcpad.Common
{
    /// <summary>
    /// Conversor de archivos Mathcad Prime (.mcdx) a Calcpad (.cpd)
    /// </summary>
    public class McdxConverter
    {
        private readonly StringBuilder _output = new StringBuilder();
        private readonly List<string> _warnings = new List<string>();
        private readonly XNamespace _mlNs = "http://schemas.mathsoft.com/math50";
        private readonly XNamespace _wsNs = "http://schemas.mathsoft.com/worksheet50";
        private string _mathcadVersion = "Desconocida";

        /// <summary>
        /// Lista de advertencias generadas durante la conversión
        /// </summary>
        public IReadOnlyList<string> Warnings => _warnings.AsReadOnly();

        /// <summary>
        /// Versión de Mathcad Prime detectada en el archivo
        /// </summary>
        public string MathcadVersion => _mathcadVersion;

        /// <summary>
        /// Convierte un archivo .mcdx a formato .cpd (string)
        /// </summary>
        /// <param name="mcdxPath">Ruta al archivo .mcdx</param>
        /// <returns>Contenido en formato Calcpad</returns>
        public string Convert(string mcdxPath)
        {
            if (!File.Exists(mcdxPath))
                throw new FileNotFoundException($"Archivo no encontrado: {mcdxPath}");

            _output.Clear();
            _warnings.Clear();
            _mathcadVersion = "Desconocida";

            try
            {
                // Copiar a archivo temporal para evitar bloqueo si Mathcad tiene el archivo abierto
                string tempPath = Path.Combine(Path.GetTempPath(), "calcpad_mcdx_" + Guid.NewGuid().ToString("N") + ".mcdx");
                try
                {
                    File.Copy(mcdxPath, tempPath, true);
                }
                catch (IOException)
                {
                    // Si no se puede copiar, intentar leer directamente
                    tempPath = mcdxPath;
                }

                using (var archive = ZipFile.OpenRead(tempPath))
                {
                    // Buscar y extraer versión de Mathcad de los metadatos
                    ExtractMathcadVersion(archive);

                    // Ahora escribir el encabezado con la versión
                    _output.AppendLine("' ============================================");
                    _output.AppendLine($"' Importado de Mathcad Prime (.mcdx)");
                    _output.AppendLine($"' Versión Mathcad: {_mathcadVersion}");
                    _output.AppendLine($"' Archivo: {Path.GetFileName(mcdxPath)}");
                    _output.AppendLine($"' Fecha: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
                    _output.AppendLine("' ============================================");
                    _output.AppendLine();

                    // Buscar worksheet.xml
                    ZipArchiveEntry worksheetEntry = null;
                    foreach (var entry in archive.Entries)
                    {
                        if (entry.FullName.EndsWith("worksheet.xml", StringComparison.OrdinalIgnoreCase))
                        {
                            worksheetEntry = entry;
                            break;
                        }
                    }

                    if (worksheetEntry == null)
                        throw new Exception("No se encontró worksheet.xml en el archivo .mcdx");

                    using (var stream = worksheetEntry.Open())
                    {
                        var doc = XDocument.Load(stream);
                        ProcessWorksheet(doc);
                    }
                }

                // Limpiar archivo temporal
                if (tempPath != mcdxPath && File.Exists(tempPath))
                {
                    try { File.Delete(tempPath); } catch { }
                }
            }
            catch (InvalidDataException)
            {
                throw new Exception("El archivo no es un archivo .mcdx válido (debe ser un archivo ZIP)");
            }

            // Agregar advertencias al final si las hay
            if (_warnings.Count > 0)
            {
                _output.AppendLine();
                _output.AppendLine("' === ADVERTENCIAS ===");
                foreach (var warning in _warnings)
                {
                    _output.AppendLine($"' {warning}");
                }
            }

            return _output.ToString();
        }

        /// <summary>
        /// Convierte y guarda el archivo .cpd
        /// </summary>
        public string ConvertAndSave(string mcdxPath, string outputPath = null)
        {
            if (string.IsNullOrEmpty(outputPath))
                outputPath = Path.ChangeExtension(mcdxPath, ".cpd");

            string content = Convert(mcdxPath);
            File.WriteAllText(outputPath, content, Encoding.UTF8);
            return outputPath;
        }

        /// <summary>
        /// Extrae la versión de Mathcad Prime de los metadatos del archivo .mcdx
        /// </summary>
        private void ExtractMathcadVersion(ZipArchive archive)
        {
            _mathcadVersion = "Desconocida";

            try
            {
                // Buscar en docProps/app.xml (donde está Application y AppVersion)
                var appEntry = archive.Entries.FirstOrDefault(e =>
                    e.FullName.Equals("docProps/app.xml", StringComparison.OrdinalIgnoreCase));

                if (appEntry != null)
                {
                    using (var stream = appEntry.Open())
                    {
                        var doc = XDocument.Load(stream);
                        var root = doc.Root;
                        if (root != null)
                        {
                            // Namespace típico de Open Packaging Conventions
                            XNamespace ns = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties";

                            // Buscar Application y AppVersion
                            var appName = root.Element(ns + "Application")?.Value
                                       ?? root.Descendants().FirstOrDefault(e => e.Name.LocalName == "Application")?.Value;

                            var appVersion = root.Element(ns + "AppVersion")?.Value
                                          ?? root.Descendants().FirstOrDefault(e => e.Name.LocalName == "AppVersion")?.Value;

                            if (!string.IsNullOrEmpty(appName) || !string.IsNullOrEmpty(appVersion))
                            {
                                if (!string.IsNullOrEmpty(appName) && !string.IsNullOrEmpty(appVersion))
                                    _mathcadVersion = $"{appName} {appVersion}";
                                else if (!string.IsNullOrEmpty(appVersion))
                                    _mathcadVersion = $"Prime {appVersion}";
                                else
                                    _mathcadVersion = appName;
                            }
                        }
                    }
                }

                // Si no se encontró en app.xml, buscar en el worksheet.xml
                if (_mathcadVersion == "Desconocida")
                {
                    var worksheetEntry = archive.Entries.FirstOrDefault(e =>
                        e.FullName.EndsWith("worksheet.xml", StringComparison.OrdinalIgnoreCase));

                    if (worksheetEntry != null)
                    {
                        using (var stream = worksheetEntry.Open())
                        {
                            var doc = XDocument.Load(stream);
                            var root = doc.Root;
                            if (root != null)
                            {
                                // Buscar atributo version en el elemento raíz
                                var versionAttr = root.Attribute("version");
                                if (versionAttr != null)
                                    _mathcadVersion = $"Prime (worksheet v{versionAttr.Value})";

                                // También buscar en el namespace del schema
                                var schemaVersion = root.Name.NamespaceName;
                                if (!string.IsNullOrEmpty(schemaVersion))
                                {
                                    // Extraer versión del namespace (ej: http://schemas.mathsoft.com/worksheet50)
                                    var match = Regex.Match(schemaVersion, @"(\d+)$");
                                    if (match.Success)
                                    {
                                        string wsVersion = match.Value;
                                        if (_mathcadVersion == "Desconocida")
                                            _mathcadVersion = $"Prime (schema v{wsVersion})";
                                    }
                                }
                            }
                        }
                    }
                }

                // Buscar también en Content_Types.xml o rels/.rels para más info
                if (_mathcadVersion == "Desconocida")
                {
                    var coreEntry = archive.Entries.FirstOrDefault(e =>
                        e.FullName.Equals("docProps/core.xml", StringComparison.OrdinalIgnoreCase));

                    if (coreEntry != null)
                    {
                        using (var stream = coreEntry.Open())
                        {
                            var doc = XDocument.Load(stream);
                            // Dublin Core namespace
                            XNamespace dcNs = "http://purl.org/dc/elements/1.1/";
                            var creator = doc.Descendants(dcNs + "creator").FirstOrDefault()?.Value;
                            if (!string.IsNullOrEmpty(creator) && creator.Contains("Mathcad"))
                                _mathcadVersion = creator;
                        }
                    }
                }
            }
            catch
            {
                // Si hay error leyendo metadatos, continuar con versión desconocida
                _mathcadVersion = "Desconocida";
            }
        }

        /// <summary>
        /// Procesa el documento XML del worksheet
        /// </summary>
        private void ProcessWorksheet(XDocument doc)
        {
            var root = doc.Root;
            if (root == null) return;

            // Obtener namespace
            XNamespace ns = root.GetDefaultNamespace();
            if (string.IsNullOrEmpty(ns.NamespaceName))
                ns = _wsNs;

            // Buscar todas las regiones
            var regions = root.Descendants(ns + "region");
            if (!regions.Any())
                regions = root.Descendants("region");

            foreach (var region in regions)
            {
                ProcessRegion(region, ns);
            }
        }

        /// <summary>
        /// Procesa una región individual
        /// </summary>
        private void ProcessRegion(XElement region, XNamespace ns)
        {
            // Buscar elemento math
            var math = region.Descendants().FirstOrDefault(e =>
                e.Name.LocalName == "math" ||
                e.Name == ns + "math");

            if (math != null)
            {
                ProcessMathRegion(math);
                return;
            }

            // Buscar elemento text
            var text = region.Descendants().FirstOrDefault(e =>
                e.Name.LocalName == "text" ||
                e.Name == ns + "text");

            if (text != null)
            {
                ProcessTextRegion(text);
                return;
            }

            // Buscar plot (gráfico)
            var plot = region.Descendants().FirstOrDefault(e =>
                e.Name.LocalName == "plot" ||
                e.Name == ns + "plot");

            if (plot != null)
            {
                _warnings.Add("Gráfico omitido (no soportado)");
            }
        }

        /// <summary>
        /// Procesa una región matemática
        /// </summary>
        private void ProcessMathRegion(XElement math)
        {
            try
            {
                // Buscar define (asignación) o eval (evaluación)
                var define = math.Descendants().FirstOrDefault(e => e.Name.LocalName == "define");
                var eval = math.Descendants().FirstOrDefault(e => e.Name.LocalName == "eval");

                if (define != null)
                {
                    string expr = ProcessDefine(define);
                    if (!string.IsNullOrWhiteSpace(expr))
                        _output.AppendLine(expr);
                }
                else if (eval != null)
                {
                    string expr = ProcessEval(eval);
                    if (!string.IsNullOrWhiteSpace(expr))
                        _output.AppendLine(expr);
                }
            }
            catch (Exception ex)
            {
                _warnings.Add($"Error procesando expresión: {ex.Message}");
            }
        }

        /// <summary>
        /// Procesa una definición (variable = valor)
        /// </summary>
        private string ProcessDefine(XElement define)
        {
            var children = define.Elements().ToList();
            if (children.Count < 2) return null;

            // Primer hijo: nombre de la variable
            string varName = ExtractValue(children[0]);

            // Segundo hijo: valor/expresión
            string value = ExtractExpression(children[1]);

            if (string.IsNullOrWhiteSpace(varName) || string.IsNullOrWhiteSpace(value))
                return null;

            return $"{varName} = {value}";
        }

        /// <summary>
        /// Procesa una evaluación (mostrar resultado)
        /// </summary>
        private string ProcessEval(XElement eval)
        {
            var children = eval.Elements().ToList();
            if (children.Count == 0) return null;

            string expr = ExtractExpression(children[0]);
            if (string.IsNullOrWhiteSpace(expr))
                return null;

            // En Calcpad, simplemente ponemos la expresión para que se evalúe
            return expr;
        }

        /// <summary>
        /// Extrae el valor de un elemento (id, real, str)
        /// </summary>
        private string ExtractValue(XElement elem)
        {
            string localName = elem.Name.LocalName;

            switch (localName)
            {
                case "id":
                    return CleanIdentifier(elem.Value);
                case "real":
                    return elem.Value;
                case "str":
                    return $"\"{elem.Value}\"";
                default:
                    return ExtractExpression(elem);
            }
        }

        /// <summary>
        /// Extrae una expresión completa (recursivo)
        /// </summary>
        private string ExtractExpression(XElement elem)
        {
            string localName = elem.Name.LocalName;
            var children = elem.Elements().ToList();

            switch (localName)
            {
                case "id":
                    return CleanIdentifier(elem.Value);

                case "real":
                    return elem.Value;

                case "str":
                    return $"\"{elem.Value}\"";

                case "matrix":
                    return ProcessMatrix(elem);

                case "vector":
                    return ProcessVector(elem);

                case "apply":
                    return ProcessApply(elem);

                case "eval":
                    if (children.Count > 0)
                        return ExtractExpression(children[0]);
                    return "";

                case "parens":
                    if (children.Count > 0)
                        return $"({ExtractExpression(children[0])})";
                    return "()";

                case "sequence":
                    // Lista de argumentos
                    var args = children.Select(c => ExtractExpression(c));
                    return string.Join("; ", args);

                default:
                    // Si tiene hijos, procesar el primero
                    if (children.Count > 0)
                        return ExtractExpression(children[0]);
                    return elem.Value ?? "";
            }
        }

        /// <summary>
        /// Procesa un vector de Mathcad
        /// En Calcpad: vector columna = [v1; v2; v3], vector fila = [v1, v2, v3]
        /// </summary>
        private string ProcessVector(XElement vector)
        {
            var values = vector.Elements()
                .Where(e => e.Name.LocalName == "real" || e.Name.LocalName == "id" ||
                           e.Name.LocalName == "apply" || e.Name.LocalName == "matrix")
                .Select(e => ExtractExpression(e))
                .ToList();

            if (values.Count == 0)
                return "[]";

            // Vector columna en Calcpad: [v1; v2; v3] (punto y coma separa filas)
            var sb = new StringBuilder();
            sb.Append("[");
            sb.Append(string.Join("; ", values));
            sb.Append("]");
            return sb.ToString();
        }

        /// <summary>
        /// Procesa una matriz de Mathcad
        /// Mathcad almacena matrices en orden column-major
        /// En Calcpad: [fila1 | fila2 | fila3] donde cada fila usa punto y coma
        /// Ejemplo: [2; 2; 3 | 5; 4; 2] para matriz 2x3
        /// </summary>
        private string ProcessMatrix(XElement matrix)
        {
            // Obtener dimensiones
            var rowsAttr = matrix.Attribute("rows");
            var colsAttr = matrix.Attribute("cols");

            if (rowsAttr == null || colsAttr == null)
            {
                _warnings.Add("Matriz sin dimensiones especificadas");
                return "[]";
            }

            int rows = int.Parse(rowsAttr.Value);
            int cols = int.Parse(colsAttr.Value);

            // Obtener todos los valores
            var values = matrix.Elements()
                .Where(e => e.Name.LocalName == "real" || e.Name.LocalName == "id" || e.Name.LocalName == "apply")
                .Select(e => ExtractExpression(e))
                .ToList();

            if (values.Count != rows * cols)
            {
                _warnings.Add($"Matriz con valores incompletos: esperados {rows * cols}, encontrados {values.Count}");
            }

            // Mathcad almacena en column-major order:
            // Para matriz 2x3: [0,0], [1,0], [0,1], [1,1], [0,2], [1,2]
            // Necesitamos convertir a row-major para Calcpad:
            // Fila 0: [0,0], [0,1], [0,2]
            // Fila 1: [1,0], [1,1], [1,2]
            // Formato Calcpad: [fila0_col0, fila0_col1, fila0_col2 | fila1_col0, fila1_col1, fila1_col2]

            var sb = new StringBuilder();
            sb.Append("[");

            for (int r = 0; r < rows; r++)
            {
                if (r > 0) sb.Append(" | ");  // Separador de filas en Calcpad

                for (int c = 0; c < cols; c++)
                {
                    if (c > 0) sb.Append("; ");  // Separador de columnas en Calcpad (;)

                    // Índice en column-major: c * rows + r
                    int idx = c * rows + r;
                    if (idx < values.Count)
                        sb.Append(values[idx]);
                    else
                        sb.Append("0");
                }
            }

            sb.Append("]");
            return sb.ToString();
        }

        /// <summary>
        /// Procesa un elemento apply (operación o función)
        /// </summary>
        private string ProcessApply(XElement apply)
        {
            var children = apply.Elements().ToList();
            if (children.Count == 0) return "";

            string op = children[0].Name.LocalName;

            switch (op)
            {
                // Operadores aritméticos
                case "plus":
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])} + {ExtractExpression(children[2])}";
                    break;

                case "minus":
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])} - {ExtractExpression(children[2])}";
                    else if (children.Count >= 2)
                        return $"-{ExtractExpression(children[1])}";
                    break;

                case "mult":
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])}*{ExtractExpression(children[2])}";
                    break;

                case "div":
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])}/{ExtractExpression(children[2])}";
                    break;

                case "pow":
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])}^{ExtractExpression(children[2])}";
                    break;

                case "scale":
                    // Multiplicación con unidad: 210*GPa
                    if (children.Count >= 3)
                        return $"{ExtractExpression(children[1])}*{ExtractExpression(children[2])}";
                    break;

                // Funciones matemáticas
                case "sqrt":
                    if (children.Count >= 2)
                        return $"sqr({ExtractExpression(children[1])})";
                    break;

                case "sin":
                case "cos":
                case "tan":
                case "asin":
                case "acos":
                case "atan":
                case "sinh":
                case "cosh":
                case "tanh":
                case "ln":
                case "log":
                case "exp":
                case "abs":
                    if (children.Count >= 2)
                        return $"{op}({ExtractExpression(children[1])})";
                    break;

                case "id":
                    // Llamada a función: fem_beam_K(E, A, I, L)
                    string funcName = CleanIdentifier(children[0].Value);
                    if (children.Count >= 2)
                    {
                        var funcArgs = new List<string>();
                        for (int i = 1; i < children.Count; i++)
                        {
                            string arg = ExtractExpression(children[i]);
                            // Si es una secuencia, separar los argumentos
                            if (children[i].Name.LocalName == "sequence")
                            {
                                var seqArgs = children[i].Elements().Select(e => ExtractExpression(e));
                                funcArgs.AddRange(seqArgs);
                            }
                            else if (!string.IsNullOrWhiteSpace(arg))
                            {
                                funcArgs.Add(arg);
                            }
                        }
                        return $"{funcName}({string.Join("; ", funcArgs)})";
                    }
                    return funcName;

                default:
                    // Operador desconocido - intentar procesar hijos
                    if (children.Count >= 2)
                    {
                        var parts = children.Skip(1).Select(c => ExtractExpression(c));
                        return string.Join(" ", parts);
                    }
                    break;
            }

            return "";
        }

        /// <summary>
        /// Limpia un identificador (quita espacios, etc.)
        /// </summary>
        private string CleanIdentifier(string id)
        {
            if (string.IsNullOrWhiteSpace(id)) return "";

            // Quitar espacios en blanco
            id = id.Trim();

            // Reemplazar caracteres griegos comunes
            var greekMap = new Dictionary<string, string>
            {
                { "α", "alpha" }, { "β", "beta" }, { "γ", "gamma" },
                { "δ", "delta" }, { "ε", "epsilon" }, { "θ", "theta" },
                { "λ", "lambda" }, { "μ", "mu" }, { "ν", "nu" },
                { "π", "pi" }, { "ρ", "rho" }, { "σ", "sigma" },
                { "τ", "tau" }, { "φ", "phi" }, { "ω", "omega" }
            };

            foreach (var kv in greekMap)
            {
                id = id.Replace(kv.Key, kv.Value);
            }

            return id;
        }

        /// <summary>
        /// Procesa una región de texto
        /// </summary>
        private void ProcessTextRegion(XElement text)
        {
            string content = text.Value?.Trim();
            if (!string.IsNullOrWhiteSpace(content))
            {
                // Convertir a comentario de Calcpad
                foreach (var line in content.Split('\n'))
                {
                    _output.AppendLine($"' {line.Trim()}");
                }
            }
        }
    }
}
