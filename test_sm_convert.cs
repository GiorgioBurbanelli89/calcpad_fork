using System;
using Calcpad.Common;

class Program
{
    static void Main()
    {
        var converter = new SMathConverter();
        string result = converter.Convert(@"C:\Users\j-b-j\Downloads\Imagen.sm");

        Console.WriteLine($"Result length: {result.Length}");
        Console.WriteLine($"Warnings: {converter.Warnings.Count}");
        foreach (var w in converter.Warnings)
            Console.WriteLine($"  - {w}");

        // Save result
        System.IO.File.WriteAllText(@"C:\Users\j-b-j\Documents\Calcpad-7.5.7\test_smath_image.cpd", result);

        // Show first 40 lines
        Console.WriteLine("\nFirst 40 lines:");
        var lines = result.Split('\n');
        for (int i = 0; i < Math.Min(40, lines.Length); i++)
        {
            var line = lines[i].Length > 80 ? lines[i].Substring(0, 80) + "..." : lines[i];
            Console.WriteLine($"{i+1}: {line}");
        }
    }
}
