// Test script para verificar la conversión de chartComponent
using System;
using System.IO;
using Calcpad.Common;

class Program
{
    static void Main(string[] args)
    {
        string mcdxPath = args.Length > 0
            ? args[0]
            : @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\MathCadPrime\Solucion de una ecuacion diferencial.mcdx";

        if (!File.Exists(mcdxPath))
        {
            Console.WriteLine($"Archivo no encontrado: {mcdxPath}");
            return;
        }

        Console.WriteLine($"Convirtiendo: {Path.GetFileName(mcdxPath)}");
        Console.WriteLine(new string('=', 60));

        try
        {
            var converter = new McdxConverter();
            string result = converter.Convert(mcdxPath);

            // Mostrar versión detectada
            Console.WriteLine($"Versión Mathcad: {converter.MathcadVersion}");
            Console.WriteLine();

            // Mostrar advertencias
            if (converter.Warnings.Count > 0)
            {
                Console.WriteLine("Advertencias:");
                foreach (var warning in converter.Warnings)
                {
                    Console.WriteLine($"  - {warning}");
                }
                Console.WriteLine();
            }

            // Guardar resultado
            string outputPath = Path.ChangeExtension(mcdxPath, "_converted.cpd");
            File.WriteAllText(outputPath, result);
            Console.WriteLine($"Resultado guardado en: {outputPath}");
            Console.WriteLine();

            // Mostrar fragmento del resultado (primeras 150 líneas)
            var lines = result.Split('\n');
            int maxLines = Math.Min(lines.Length, 150);

            Console.WriteLine($"Contenido (primeras {maxLines} líneas):");
            Console.WriteLine(new string('-', 60));
            for (int i = 0; i < maxLines; i++)
            {
                Console.WriteLine(lines[i].TrimEnd('\r'));
            }

            if (lines.Length > maxLines)
            {
                Console.WriteLine($"... ({lines.Length - maxLines} líneas más)");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
