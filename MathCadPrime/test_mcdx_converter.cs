// Test simple para McdxConverter
using System;
using Calcpad.Common;

class Program
{
    static void Main(string[] args)
    {
        string mcdxPath = @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\MathCadPrime\Grafica.mcdx";
        string outputPath = @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\MathCadPrime\Grafica_Convertido.cpd";

        try
        {
            var converter = new McdxConverter();
            string result = converter.Convert(mcdxPath);

            Console.WriteLine("=== RESULTADO DE LA CONVERSIÓN ===");
            Console.WriteLine(result);
            Console.WriteLine("\n=== ADVERTENCIAS ===");
            foreach (var warning in converter.Warnings)
            {
                Console.WriteLine($"  - {warning}");
            }

            // Guardar archivo
            System.IO.File.WriteAllText(outputPath, result);
            Console.WriteLine($"\nArchivo guardado en: {outputPath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
