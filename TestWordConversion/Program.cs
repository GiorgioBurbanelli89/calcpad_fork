using System;
using System.IO;
using Calcpad.OpenXml;

class Program
{
    static void Main()
    {
        var docxPath = @"C:\Users\j-b-j\Downloads\calculo_estructural_escalera_metalica.docx";
        var outputPath = "word_output.html";

        Console.WriteLine("======================================");
        Console.WriteLine("Conversión Word → HTML con DocxReader");
        Console.WriteLine("======================================");
        Console.WriteLine($"Documento: {docxPath}");
        Console.WriteLine();

        try
        {
            var reader = new DocxReader();
            Console.WriteLine("Leyendo documento...");

            var html = reader.ReadToHtml(docxPath);

            File.WriteAllText(outputPath, html);

            Console.WriteLine();
            Console.WriteLine("======================================");
            Console.WriteLine("Información del documento:");
            Console.WriteLine("======================================");
            Console.WriteLine($"Título: {reader.Title}");
            Console.WriteLine($"Versión Word: {reader.WordVersion}");
            Console.WriteLine($"Imágenes: {reader.Images.Count}");
            Console.WriteLine($"Advertencias: {reader.Warnings.Count}");

            if (reader.Warnings.Count > 0)
            {
                Console.WriteLine();
                Console.WriteLine("Advertencias:");
                foreach (var warning in reader.Warnings)
                    Console.WriteLine($"  - {warning}");
            }

            Console.WriteLine();
            Console.WriteLine($"HTML guardado en: {outputPath}");
            Console.WriteLine($"Tamaño: {html.Length} caracteres");

            // Mostrar primeras líneas del HTML
            Console.WriteLine();
            Console.WriteLine("Primeras líneas del HTML:");
            var lines = html.Split('\n');
            for (int i = 0; i < Math.Min(30, lines.Length); i++)
            {
                Console.WriteLine(lines[i]);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"ERROR: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
