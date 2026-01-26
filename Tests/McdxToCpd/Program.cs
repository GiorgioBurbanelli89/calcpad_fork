// Program.cs - Herramienta de linea de comandos para convertir .mcdx a .cpd

using System;
using System.IO;

namespace McdxToCpd
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("============================================");
            Console.WriteLine("  Conversor Mathcad Prime (.mcdx) a Calcpad (.cpd)");
            Console.WriteLine("============================================");
            Console.WriteLine();

            if (args.Length == 0)
            {
                ShowUsage();
                return;
            }

            string inputPath = args[0];
            string outputPath = args.Length > 1
                ? args[1]
                : Path.ChangeExtension(inputPath, ".cpd");

            Console.WriteLine($"Archivo de entrada: {inputPath}");
            Console.WriteLine($"Archivo de salida:  {outputPath}");
            Console.WriteLine();

            try
            {
                var converter = new McdxConverter();
                string result = converter.Convert(inputPath);

                File.WriteAllText(outputPath, result);

                Console.WriteLine("Conversion exitosa!");
                Console.WriteLine();

                if (converter.Warnings.Count > 0)
                {
                    Console.WriteLine($"Advertencias ({converter.Warnings.Count}):");
                    foreach (var warning in converter.Warnings)
                    {
                        Console.WriteLine($"  - {warning}");
                    }
                }

                Console.WriteLine();
                Console.WriteLine($"Archivo guardado: {outputPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex.Message}");
                Environment.Exit(1);
            }
        }

        static void ShowUsage()
        {
            Console.WriteLine("Uso: McdxToCpd <archivo.mcdx> [archivo.cpd]");
            Console.WriteLine();
            Console.WriteLine("Ejemplos:");
            Console.WriteLine("  McdxToCpd mi_calculo.mcdx");
            Console.WriteLine("  McdxToCpd mi_calculo.mcdx salida.cpd");
            Console.WriteLine();
            Console.WriteLine("Si no se especifica archivo de salida, se usa el mismo");
            Console.WriteLine("nombre con extension .cpd");
        }
    }
}
