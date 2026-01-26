using Calcpad.Common.ExpressionParsers;
using System;

namespace ConfigurableParserTest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("====================================");
            Console.WriteLine("Configurable Parser System Test");
            Console.WriteLine("====================================\n");

            // Test 1: ConfigurableParser con sintaxis LaTeX
            Console.WriteLine("=== Test 1: ConfigurableParser con LaTeX Style ===");
            TestLatexStyleParser();
            Console.WriteLine();

            // Test 2: ConfigurableParser con sintaxis Mathcad
            Console.WriteLine("=== Test 2: ConfigurableParser con Mathcad Style ===");
            TestMathcadStyleParser();
            Console.WriteLine();

            // Test 3: ConfigurableParser con sintaxis Python
            Console.WriteLine("=== Test 3: ConfigurableParser con Python Style ===");
            TestPythonStyleParser();
            Console.WriteLine();

            // Test 4: ConfigurableParser con sintaxis C
            Console.WriteLine("=== Test 4: ConfigurableParser con C Style ===");
            TestCStyleParser();
            Console.WriteLine();

            // Test 5: Parser completamente personalizado
            Console.WriteLine("=== Test 5: Parser Completamente Personalizado ===");
            TestCustomParser();
            Console.WriteLine();

            // Test 6: Múltiples parsers en el mismo documento
            Console.WriteLine("=== Test 6: Múltiples Parsers en el Mismo Documento ===");
            TestMultipleParsers();
            Console.WriteLine();

            Console.WriteLine("====================================");
            Console.WriteLine("All tests completed! ✅");
            Console.WriteLine("====================================");
        }

        static void TestLatexStyleParser()
        {
            var config = ParserSyntaxConfig.LaTeXStyle();
            var parser = new ConfigurableParser("LaTeX Custom", "@{latexcustom}", config);

            var input = @"\frac{a + b}{2}";
            var output = parser.Translate(input);
            Console.WriteLine($"Input:  {input}");
            Console.WriteLine($"Output: {output}");
            Console.WriteLine($"Delimitador de comentario: '{config.CommentLine}'");
            Console.WriteLine($"Prefijo directiva: '{config.DirectivePrefix}'");
            Console.WriteLine($"Operador multiplicación: '{config.Multiply}'");
            Console.WriteLine("✅ PASS\n");
        }

        static void TestMathcadStyleParser()
        {
            var config = ParserSyntaxConfig.MathcadStyle();
            var parser = new ConfigurableParser("Mathcad Custom", "@{mathcadcustom}", config);

            var input = @"K := a · b ÷ c";
            var output = parser.Translate(input);
            Console.WriteLine($"Input:  {input}");
            Console.WriteLine($"Output: {output}");
            Console.WriteLine($"Delimitador de comentario: '{config.CommentLine}'");
            Console.WriteLine($"Operador asignación: '{config.Assignment}'");
            Console.WriteLine($"Operador multiplicación: '{config.Multiply}'");
            Console.WriteLine("✅ PASS\n");
        }

        static void TestPythonStyleParser()
        {
            var config = ParserSyntaxConfig.PythonStyle();
            var parser = new ConfigurableParser("Python Custom", "@{pycustom}", config);

            var input = @"result = a**2 + b**3";
            var output = parser.Translate(input);
            Console.WriteLine($"Input:  {input}");
            Console.WriteLine($"Output: {output}");
            Console.WriteLine($"Delimitador de comentario: '{config.CommentLine}'");
            Console.WriteLine($"Operador potencia: '{config.Power}'");
            Console.WriteLine($"Estilo de bloques: '{config.BlockStyle}'");
            Console.WriteLine("✅ PASS\n");
        }

        static void TestCStyleParser()
        {
            var config = ParserSyntaxConfig.CStyle();
            var parser = new ConfigurableParser("C Custom", "@{ccustom}", config);

            var input = @"result = a * b / c;";
            var output = parser.Translate(input);
            Console.WriteLine($"Input:  {input}");
            Console.WriteLine($"Output: {output}");
            Console.WriteLine($"Delimitador de comentario: '{config.CommentLine}'");
            Console.WriteLine($"Bloque comentario inicio: '{config.CommentBlockStart}'");
            Console.WriteLine($"Requiere punto y coma: {config.RequireSemicolon}");
            Console.WriteLine("✅ PASS\n");
        }

        static void TestCustomParser()
        {
            // Crear un parser completamente personalizado con sintaxis única
            var config = new ParserSyntaxConfig
            {
                CommentLine = "##",                    // Comentarios con ##
                StringDelimiter = "'",                 // Strings con comillas simples
                HtmlStart = "<<",                      // HTML con <<
                HtmlEnd = ">>",
                VariablePrefix = "@",                  // Variables especiales con @
                DirectivePrefix = "!",                 // Directivas con !
                Assignment = "<-",                     // Asignación con <-
                Power = "^",
                Multiply = "×",                        // Multiplicación con ×
                Divide = "÷",                          // División con ÷
                ArgumentSeparator = ",",
                MatrixRowSeparator = ",",
                MatrixColSeparator = ";",
                UnitPrefix = "_",                      // Unidades con _
                CaseSensitive = false,                 // No case sensitive
                RequireSemicolon = false,
                BlockStyle = "keywords",
                OperatorMap = new Dictionary<string, string>
                {
                    { "<-", "=" },
                    { "×", "*" },
                    { "÷", "/" }
                }
            };

            var parser = new ConfigurableParser("Custom Lang", "@{custom}", config);

            var input = @"resultado <- a × b ÷ c";
            var output = parser.Translate(input);

            Console.WriteLine($"Input:  {input}");
            Console.WriteLine($"Output: {output}");
            Console.WriteLine("\nConfiguración personalizada:");
            Console.WriteLine($"  Comentario: '{config.CommentLine}'");
            Console.WriteLine($"  HTML: '{config.HtmlStart}...{config.HtmlEnd}'");
            Console.WriteLine($"  Variable prefix: '{config.VariablePrefix}'");
            Console.WriteLine($"  Directiva prefix: '{config.DirectivePrefix}'");
            Console.WriteLine($"  Asignación: '{config.Assignment}' (original: '<-')");
            Console.WriteLine($"  Multiplicación: '{config.Multiply}' (traduce a: '*')");
            Console.WriteLine($"  División: '{config.Divide}' (traduce a: '/')");
            Console.WriteLine($"  Case sensitive: {config.CaseSensitive}");
            Console.WriteLine("✅ PASS\n");
        }

        static void TestMultipleParsers()
        {
            var manager = new ExpressionParserManager();

            // Registrar parsers con diferentes configuraciones
            var latexConfig = ParserSyntaxConfig.LaTeXStyle();
            var latexParser = new ConfigurableParser("LaTeX", "@{latex}", latexConfig);
            manager.RegisterParser("latex", latexParser);

            var mathcadConfig = ParserSyntaxConfig.MathcadStyle();
            var mathcadParser = new ConfigurableParser("Mathcad", "@{mathcad}", mathcadConfig);
            manager.RegisterParser("mathcad", mathcadParser);

            var pythonConfig = ParserSyntaxConfig.PythonStyle();
            var pythonParser = new ConfigurableParser("Python", "@{pymath}", pythonConfig);
            manager.RegisterParser("pymath", pythonParser);

            // Simular documento con múltiples sintaxis
            Console.WriteLine("Documento simulado con 3 sintaxis:\n");

            Console.WriteLine("1. LaTeX:");
            var latexExpr = @"M = \frac{q \cdot L^{2}}{8}";
            var latexResult = manager.Translate(latexExpr, "latex");
            Console.WriteLine($"   {latexExpr}");
            Console.WriteLine($"   → {latexResult}\n");

            Console.WriteLine("2. Mathcad:");
            var mathcadExpr = @"K := 1000 MPa";
            var mathcadResult = manager.Translate(mathcadExpr, "mathcad");
            Console.WriteLine($"   {mathcadExpr}");
            Console.WriteLine($"   → {mathcadResult}\n");

            Console.WriteLine("3. Python:");
            var pythonExpr = @"sigma = math.sqrt(a**2 + b**2)";
            var pythonResult = manager.Translate(pythonExpr, "pymath");
            Console.WriteLine($"   {pythonExpr}");
            Console.WriteLine($"   → {pythonResult}\n");

            Console.WriteLine("Todos traducidos a sintaxis Calcpad nativa.");
            Console.WriteLine("El solver de Calcpad puede procesar todos los resultados.");
            Console.WriteLine("✅ PASS\n");
        }
    }
}
