using System;
using Calcpad.Common;

class TestMcdxConverter
{
    static void Main(string[] args)
    {
        var converter = new McdxConverter();

        if (args.Length == 0)
        {
            Console.WriteLine("Uso: test_mcdx_converter <archivo.mcdx>");
            return;
        }

        string mcdxPath = args[0];

        try
        {
            Console.WriteLine($"Convirtiendo: {mcdxPath}");
            string result = converter.Convert(mcdxPath);

            Console.WriteLine("\n=== RESULTADO ===\n");
            Console.WriteLine(result);

            Console.WriteLine("\n=== VERSION ===");
            Console.WriteLine($"Mathcad Version: {converter.MathcadVersion}");

            Console.WriteLine("\n=== ADVERTENCIAS ===");
            foreach (var warning in converter.Warnings)
            {
                Console.WriteLine($"  - {warning}");
            }

            // Guardar a archivo .cpd
            string outputPath = System.IO.Path.ChangeExtension(mcdxPath, ".cpd");
            System.IO.File.WriteAllText(outputPath, result);
            Console.WriteLine($"\nGuardado en: {outputPath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
