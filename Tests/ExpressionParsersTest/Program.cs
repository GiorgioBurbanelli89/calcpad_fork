using System;
using Calcpad.Common.ExpressionParsers;
using Calcpad.Common.MultLangCode;

namespace ExpressionParsersTest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("====================================");
            Console.WriteLine("Expression Parsers Test");
            Console.WriteLine("====================================\n");

            // Test 1: LaTeX Parser
            TestLaTeXParser();

            // Test 2: Mathcad Parser
            TestMathcadParser();

            // Test 3: Python Math Parser
            TestPythonMathParser();

            // Test 4: Expression Parser Manager
            TestExpressionParserManager();

            // Test 5: MultLangProcessor Integration
            TestMultLangProcessorIntegration();

            Console.WriteLine("\n====================================");
            Console.WriteLine("All tests completed!");
            Console.WriteLine("====================================");
        }

        static void TestLaTeXParser()
        {
            Console.WriteLine("=== Test 1: LaTeX Parser ===\n");

            var parser = new LaTeXParser();

            // Test fracciones
            var latex1 = @"\frac{a + b}{2}";
            var result1 = parser.Translate(latex1);
            Console.WriteLine($"LaTeX:    {latex1}");
            Console.WriteLine($"Calcpad:  {result1}");
            Console.WriteLine();

            // Test raíces
            var latex2 = @"\sqrt{x^2 + y^2}";
            var result2 = parser.Translate(latex2);
            Console.WriteLine($"LaTeX:    {latex2}");
            Console.WriteLine($"Calcpad:  {result2}");
            Console.WriteLine();

            // Test funciones trigonométricas
            var latex3 = @"\sin(x) + \cos(y)";
            var result3 = parser.Translate(latex3);
            Console.WriteLine($"LaTeX:    {latex3}");
            Console.WriteLine($"Calcpad:  {result3}");
            Console.WriteLine();

            // Test ecuación completa
            var latex4 = @"M_{max} = \frac{q \cdot L^{2}}{8}";
            var result4 = parser.TranslateEquation(latex4);
            Console.WriteLine($"LaTeX:    {latex4}");
            Console.WriteLine($"Calcpad:  {result4}");
            Console.WriteLine();
        }

        static void TestMathcadParser()
        {
            Console.WriteLine("=== Test 2: Mathcad Parser ===\n");

            var parser = new MathcadParser();

            // Test asignación
            var mathcad1 = "K := 1766.568";
            var result1 = parser.Translate(mathcad1);
            Console.WriteLine($"Mathcad:  {mathcad1}");
            Console.WriteLine($"Calcpad:  {result1}");
            Console.WriteLine();

            // Test operadores
            var mathcad2 = "F := a · b + c ÷ d";
            var result2 = parser.Translate(mathcad2);
            Console.WriteLine($"Mathcad:  {mathcad2}");
            Console.WriteLine($"Calcpad:  {result2}");
            Console.WriteLine();

            // Test función
            var mathcad3 = "f(x) := x^2 + 1";
            var result3 = parser.TranslateFunctionDefinition(mathcad3);
            Console.WriteLine($"Mathcad:  {mathcad3}");
            Console.WriteLine($"Calcpad:  {result3}");
            Console.WriteLine();
        }

        static void TestPythonMathParser()
        {
            Console.WriteLine("=== Test 3: Python Math Parser ===\n");

            var parser = new PythonMathParser();

            // Test potencia
            var python1 = "a**2 + b**3";
            var result1 = parser.Translate(python1);
            Console.WriteLine($"Python:   {python1}");
            Console.WriteLine($"Calcpad:  {result1}");
            Console.WriteLine();

            // Test funciones math
            var python2 = "math.sqrt(x) + math.sin(y)";
            var result2 = parser.Translate(python2);
            Console.WriteLine($"Python:   {python2}");
            Console.WriteLine($"Calcpad:  {result2}");
            Console.WriteLine();

            // Test constantes
            var python3 = "area = math.pi * r**2";
            var result3 = parser.Translate(python3);
            Console.WriteLine($"Python:   {python3}");
            Console.WriteLine($"Calcpad:  {result3}");
            Console.WriteLine();
        }

        static void TestExpressionParserManager()
        {
            Console.WriteLine("=== Test 4: Expression Parser Manager ===\n");

            var manager = new ExpressionParserManager();

            // Listar parsers disponibles
            Console.WriteLine("Parsers disponibles:");
            foreach (var (key, name, directive, mode) in manager.ListParsers())
            {
                Console.WriteLine($"  - {key}: {name} ({directive}) [Mode: {mode}]");
            }
            Console.WriteLine();

            // Test traducción con manager
            var latexExpr = @"\frac{a}{b} + \sqrt{c}";
            var translated = manager.Translate(latexExpr, "latex");
            Console.WriteLine($"Expresión LaTeX: {latexExpr}");
            Console.WriteLine($"Traducida:       {translated}");
            Console.WriteLine();
        }

        static void TestMultLangProcessorIntegration()
        {
            Console.WriteLine("=== Test 5: MultLangProcessor Integration ===\n");

            var processor = new MultLangProcessor();

            // Test bloque LaTeX
            var codeWithLatex = @"
' Variables Calcpad nativas
a = 5
b = 3

@{latex}
c = \frac{a + b}{2}
d = \sqrt{a^{2} + b^{2}}
@{end latex}

' Resultado
resultado = c + d
";

            Console.WriteLine("Código con bloque LaTeX:");
            Console.WriteLine(codeWithLatex);
            Console.WriteLine("\nProcesando...\n");

            var processed = processor.ProcessExpressionBlocks(codeWithLatex);
            Console.WriteLine("Código procesado:");
            Console.WriteLine(processed);
            Console.WriteLine();

            // Test bloque Mathcad
            var codeWithMathcad = @"
L := 6
q := 10

@{mathcad}
M_max := q · L^2 ÷ 8
@{end mathcad}
";

            Console.WriteLine("Código con bloque Mathcad:");
            Console.WriteLine(codeWithMathcad);
            Console.WriteLine("\nProcesando...\n");

            processed = processor.ProcessExpressionBlocks(codeWithMathcad);
            Console.WriteLine("Código procesado:");
            Console.WriteLine(processed);
            Console.WriteLine();
        }
    }
}
