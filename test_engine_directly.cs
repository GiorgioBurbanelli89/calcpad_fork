using System;
using System.Threading.Tasks;
using GenericDebugger.Engines.Roslyn;

class Program
{
    static async Task Main()
    {
        Console.WriteLine("=== Test del CSharpScriptEngine ===\n");

        var engine = new CSharpScriptEngine();

        // Crear un script de prueba
        var scriptPath = System.IO.Path.GetTempFileName() + ".cs";
        System.IO.File.WriteAllText(scriptPath, @"
int x = 10;
int y = 20;
int z = x + y;
Console.WriteLine($""La suma es: {z}"");
");

        Console.WriteLine($"Script creado: {scriptPath}\n");

        // Inicializar engine
        var success = await engine.InitializeAsync(scriptPath);
        Console.WriteLine($"✓ Engine inicializado: {success}");
        Console.WriteLine($"  Motor: {engine.Name}");
        Console.WriteLine($"  Líneas totales: {engine.TotalLines}\n");

        // Agregar breakpoint en línea 3
        engine.BreakpointManager.AddBreakpoint(3);
        Console.WriteLine("✓ Breakpoint agregado en línea 3\n");

        // Suscribirse a eventos
        engine.OnExecutionStep += (sender, e) =>
        {
            Console.WriteLine($"▶ Línea {e.LineNumber}: {e.LineContent.Trim()}");
            if (!string.IsNullOrEmpty(e.Output))
            {
                Console.WriteLine($"  Output: {e.Output}");
            }
        };

        engine.BreakpointManager.OnBreakpointHit += (sender, e) =>
        {
            Console.WriteLine($"\n⏸ BREAKPOINT en línea {e.Breakpoint.LineNumber}\n");
        };

        // Ejecutar línea por línea
        Console.WriteLine("=== Ejecutando línea por línea ===\n");

        for (int i = 0; i < engine.TotalLines; i++)
        {
            var result = await engine.ExecuteLineAsync(i);

            if (!result.Success)
            {
                Console.WriteLine($"✗ Error: {result.Error?.Message}");
                break;
            }

            // Mostrar variables después de cada línea
            var vars = engine.VariableInspector.GetAllVariables();
            if (vars.Count > 0)
            {
                Console.WriteLine("  Variables:");
                foreach (var v in vars)
                {
                    Console.WriteLine($"    {v.Name} = {v.ValueString} ({v.TypeName})");
                }
            }
            Console.WriteLine();
        }

        Console.WriteLine("\n=== Test completado ===");

        // Limpiar
        System.IO.File.Delete(scriptPath);
    }
}
