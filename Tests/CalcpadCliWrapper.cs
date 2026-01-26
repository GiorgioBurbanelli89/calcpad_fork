using Calcpad.Core;
using Calcpad.Common;
using Calcpad.Common.MultLangCode;
using System;
using System.IO;

namespace CalcpadCliWrapper
{
    /// <summary>
    /// CLI Wrapper para ejecutar Calcpad y generar HTML
    /// Usa las mismas bibliotecas que Calcpad.Wpf
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Uso: CalcpadCliWrapper <archivo.cpd> [salida.html] [-s]");
                Console.WriteLine();
                Console.WriteLine("Opciones:");
                Console.WriteLine("  -s  Modo silencioso (sin mensajes de progreso)");
                Console.WriteLine();
                Console.WriteLine("Ejemplos:");
                Console.WriteLine("  CalcpadCliWrapper test.cpd");
                Console.WriteLine("  CalcpadCliWrapper test.cpd resultado.html");
                Console.WriteLine("  CalcpadCliWrapper test.cpd resultado.html -s");
                return;
            }

            var inputFile = args[0];
            var outputFile = args.Length > 1 && !args[1].StartsWith("-") ? args[1] : Path.ChangeExtension(inputFile, ".html");
            var silent = Array.Exists(args, arg => arg == "-s");

            try
            {
                if (!silent) Console.WriteLine($"Leyendo archivo: {inputFile}");

                // Cambiar al directorio del archivo de entrada
                var dir = Path.GetDirectoryName(Path.GetFullPath(inputFile));
                if (!string.IsNullOrEmpty(dir))
                    Directory.SetCurrentDirectory(dir);

                // Leer código
                var code = CalcpadReader.Read(inputFile);
                if (!silent) Console.WriteLine($"Código leído: {code.Length} caracteres");

                // Procesar con MultLangProcessor (igual que Calcpad.Cli)
                var processor = new CalcpadProcessor(CalcpadReader.Include);
                var result = processor.ProcessCode(code, addLineNumbers: true);

                if (!result.Success)
                {
                    Console.Error.WriteLine($"Error de procesamiento: {result.ErrorMessage}");
                    Environment.Exit(1);
                }

                var unwrappedCode = result.ProcessedCode;
                var hasMacroErrors = result.HasMacroErrors;

                string htmlResult;

                if (hasMacroErrors)
                {
                    htmlResult = CalcpadReader.CodeToHtml(unwrappedCode);
                }
                else if (result.MultilangProcessed)
                {
                    // Si MultLang procesó código externo, el resultado ya es HTML
                    htmlResult = unwrappedCode;
                }
                else
                {
                    // Parsear con ExpressionParser
                    if (!silent) Console.WriteLine("Parseando expresiones...");

                    var settings = new Settings();
                    settings.Math.Decimals = 6;

                    ExpressionParser parser = new()
                    {
                        Settings = settings
                    };

                    parser.Parse(unwrappedCode, true, false);
                    htmlResult = parser.HtmlResult;
                }

                // Convertir a HTML
                if (!silent) Console.WriteLine($"Generando HTML: {outputFile}");

                Converter converter = new(silent);
                converter.ToHtml(htmlResult, outputFile);

                if (!silent)
                {
                    Console.WriteLine();
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine("✓ Archivo generado exitosamente");
                    Console.ResetColor();
                    Console.WriteLine($"  Output: {Path.GetFullPath(outputFile)}");
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.Error.WriteLine($"ERROR: {ex.Message}");
                Console.ResetColor();
                if (!silent)
                {
                    Console.Error.WriteLine();
                    Console.Error.WriteLine("Stack trace:");
                    Console.Error.WriteLine(ex.StackTrace);
                }
                Environment.Exit(1);
            }
        }
    }
}
