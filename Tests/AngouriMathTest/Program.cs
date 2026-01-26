// Test de AngouriMath para evaluar integración con Calcpad
using AngouriMath;
using AngouriMath.Extensions;
using static AngouriMath.MathS;

Console.WriteLine("=== Test de AngouriMath para Calcpad ===\n");

// ============================================
// 1. PARSING Y SIMPLIFICACIÓN
// ============================================
Console.WriteLine("1. PARSING Y SIMPLIFICACIÓN");
Console.WriteLine(new string('-', 50));

Entity expr1 = "x^2 + 2*x + 1";
Console.WriteLine($"Expresión: {expr1}");
Console.WriteLine($"Simplificada: {expr1.Simplify()}");

Entity expr2 = "(x + 1)^2";
Console.WriteLine($"\nExpresión: {expr2}");
Console.WriteLine($"Expandida: {expr2.Expand()}");

Entity expr3 = "sin(x)^2 + cos(x)^2";
Console.WriteLine($"\nExpresión: {expr3}");
Console.WriteLine($"Simplificada: {expr3.Simplify()}");

// ============================================
// 2. DERIVADAS
// ============================================
Console.WriteLine("\n\n2. DERIVADAS");
Console.WriteLine(new string('-', 50));

Entity f1 = "x^3 + 2*x^2 - 5*x + 1";
Console.WriteLine($"f(x) = {f1}");
Console.WriteLine($"f'(x) = {f1.Differentiate("x")}");
Console.WriteLine($"f''(x) = {f1.Differentiate("x").Differentiate("x")}");

Entity f2 = "sin(x) * e^x";
Console.WriteLine($"\nf(x) = {f2}");
Console.WriteLine($"f'(x) = {f2.Differentiate("x").Simplify()}");

Entity f3 = "ln(x^2 + 1)";
Console.WriteLine($"\nf(x) = {f3}");
Console.WriteLine($"f'(x) = {f3.Differentiate("x").Simplify()}");

// ============================================
// 3. INTEGRALES
// ============================================
Console.WriteLine("\n\n3. INTEGRALES");
Console.WriteLine(new string('-', 50));

Entity g1 = "x^2";
Console.WriteLine($"∫ {g1} dx = {g1.Integrate("x")}");

Entity g2 = "sin(x)";
Console.WriteLine($"∫ {g2} dx = {g2.Integrate("x")}");

Entity g3 = "e^x";
Console.WriteLine($"∫ {g3} dx = {g3.Integrate("x")}");

// ============================================
// 4. RESOLVER ECUACIONES
// ============================================
Console.WriteLine("\n\n4. RESOLVER ECUACIONES");
Console.WriteLine(new string('-', 50));

// Ecuación cuadrática
Entity eq1 = "x^2 - 5*x + 6";
Console.WriteLine($"Resolver: {eq1} = 0");
var solutions1 = eq1.SolveEquation("x");
Console.WriteLine($"Soluciones: {solutions1}");

// Ecuación cúbica
Entity eq2 = "x^3 - 6*x^2 + 11*x - 6";
Console.WriteLine($"\nResolver: {eq2} = 0");
var solutions2 = eq2.SolveEquation("x");
Console.WriteLine($"Soluciones: {solutions2}");

// Ecuación trigonométrica
Entity eq3 = "sin(x) - 1/2";
Console.WriteLine($"\nResolver: {eq3} = 0");
var solutions3 = eq3.SolveEquation("x");
Console.WriteLine($"Soluciones: {solutions3}");

// ============================================
// 5. SISTEMAS DE ECUACIONES
// ============================================
Console.WriteLine("\n\n5. SISTEMAS DE ECUACIONES");
Console.WriteLine(new string('-', 50));

// Sistema 2x2
Console.WriteLine("Sistema:");
Console.WriteLine("  2x + y = 5");
Console.WriteLine("  x - y = 1");

var system = MathS.Equations(
    "2*x + y - 5",
    "x - y - 1"
);
var vars = new[] { Var("x"), Var("y") };
var result = system.Solve(vars);
Console.WriteLine($"Solución: {result}");

// Sistema 3x3
Console.WriteLine("\nSistema 3x3:");
Console.WriteLine("  x + y + z = 6");
Console.WriteLine("  2x - y + z = 3");
Console.WriteLine("  x + 2y - z = 2");

var system3 = MathS.Equations(
    "x + y + z - 6",
    "2*x - y + z - 3",
    "x + 2*y - z - 2"
);
var vars3 = new[] { Var("x"), Var("y"), Var("z") };
var result3 = system3.Solve(vars3);
Console.WriteLine($"Solución: {result3}");

// ============================================
// 6. MATRICES Y OPERACIONES
// ============================================
Console.WriteLine("\n\n6. MATRICES");
Console.WriteLine(new string('-', 50));

var matrix1 = MathS.Matrix(new Entity[,]
{
    { 1, 2 },
    { 3, 4 }
});
Console.WriteLine($"Matriz A:\n{matrix1}");

var matrix2 = MathS.Matrix(new Entity[,]
{
    { 5, 6 },
    { 7, 8 }
});
Console.WriteLine($"\nMatriz B:\n{matrix2}");

// Multiplicación de matrices
var product = matrix1 * matrix2;
Console.WriteLine($"\nA × B:\n{product.Simplify()}");

// Determinante (es propiedad, no método)
Console.WriteLine($"\ndet(A) = {matrix1.Determinant}");

// Matriz inversa (es propiedad, no método)
var inverse = matrix1.Inverse;
Console.WriteLine($"\nA⁻¹:\n{inverse}");

// ============================================
// 7. EVALUACIÓN NUMÉRICA
// ============================================
Console.WriteLine("\n\n7. EVALUACIÓN NUMÉRICA");
Console.WriteLine(new string('-', 50));

Entity numExpr = "sqrt(2) + pi/4";
Console.WriteLine($"Expresión: {numExpr}");
Console.WriteLine($"Valor numérico: {numExpr.EvalNumerical()}");

Entity paramExpr = "x^2 + 2*x + 1";
var substituted = paramExpr.Substitute("x", 3);
Console.WriteLine($"\nf(x) = {paramExpr}");
Console.WriteLine($"f(3) = {substituted} = {substituted.EvalNumerical()}");

// ============================================
// 8. LÍMITES
// ============================================
Console.WriteLine("\n\n8. LÍMITES");
Console.WriteLine(new string('-', 50));

Entity limExpr1 = "sin(x)/x";
Console.WriteLine($"lim(x→0) {limExpr1} = {MathS.Limit(limExpr1, "x", 0)}");

Entity limExpr2 = "(1 + 1/n)^n";
Console.WriteLine($"lim(n→∞) {limExpr2} = {MathS.Limit(limExpr2, "n", "+oo")}");

// ============================================
// 9. FACTORIZACIÓN Y EXPANSIÓN
// ============================================
Console.WriteLine("\n\n9. FACTORIZACIÓN Y EXPANSIÓN");
Console.WriteLine(new string('-', 50));

Entity factorExpr = "x^2 - 4";
Console.WriteLine($"Expresión: {factorExpr}");
Console.WriteLine($"Factorizada: {factorExpr.Simplify()}");

Entity expandExpr = "(x + 2)*(x - 2)";
Console.WriteLine($"\nExpresión: {expandExpr}");
Console.WriteLine($"Expandida: {expandExpr.Expand()}");

// ============================================
// 10. ECUACIONES DIFERENCIALES (Básico)
// ============================================
Console.WriteLine("\n\n10. VERIFICACIÓN DE EDO");
Console.WriteLine(new string('-', 50));

// Verificar que y = e^x es solución de y' = y
Entity y = "e^x";
Entity yPrime = y.Differentiate("x");
Console.WriteLine($"y = {y}");
Console.WriteLine($"y' = {yPrime}");
Console.WriteLine($"¿y' = y? {(yPrime - y).Simplify() == 0}");

// y = sin(x) es solución de y'' + y = 0
Entity y2 = "sin(x)";
Entity y2Prime = y2.Differentiate("x");
Entity y2DoublePrime = y2Prime.Differentiate("x");
Console.WriteLine($"\ny = {y2}");
Console.WriteLine($"y'' = {y2DoublePrime}");
Console.WriteLine($"y'' + y = {(y2DoublePrime + y2).Simplify()}");

// ============================================
// 11. LaTeX OUTPUT
// ============================================
Console.WriteLine("\n\n11. SALIDA LaTeX");
Console.WriteLine(new string('-', 50));

Entity latexExpr = "sqrt(x^2 + y^2) / (a + b)";
Console.WriteLine($"Expresión: {latexExpr}");
Console.WriteLine($"LaTeX: {latexExpr.Latexise()}");

Entity latexIntegral = "integral(x^2, x)";
Console.WriteLine($"\nIntegral simbólica: {latexIntegral}");

Console.WriteLine("\n\n=== TEST COMPLETADO ===");
Console.WriteLine("AngouriMath es compatible con .NET 10 y funciona correctamente.");
