/*
 * Test SAP2000 API - C#
 *
 * Para compilar:
 * csc /reference:"C:\Program Files\Computers and Structures\SAP2000 24\SAP2000v1.dll" TestSAP2000API.cs
 *
 * O usar el script compile_sap2000_test.bat
 */

using System;
using SAP2000v1;

namespace TestSAP2000
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=".PadRight(70, '='));
            Console.WriteLine("TEST SAP2000 API - C#");
            Console.WriteLine("=".PadRight(70, '='));

            Helper helper = null;
            cOAPI mySapObject = null;
            cSapModel SapModel = null;

            try
            {
                // Crear helper
                Console.WriteLine("\n--- Creando Helper ---");
                helper = new Helper();
                Console.WriteLine("✓ Helper creado");

                // Opción 1: Conectar a instancia existente
                Console.WriteLine("\n--- Intentando conectar a SAP2000 existente ---");
                try
                {
                    mySapObject = helper.GetObject("CSI.SAP2000.API.SAPObject");
                    Console.WriteLine("✓ Conectado a SAP2000 existente");
                }
                catch
                {
                    // Opción 2: Crear nueva instancia
                    Console.WriteLine("No hay instancia activa. Creando nueva...");
                    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject");
                    mySapObject.ApplicationStart();
                    Console.WriteLine("✓ Nueva instancia de SAP2000 creada");
                }

                // Obtener modelo
                SapModel = mySapObject.SapModel;
                Console.WriteLine("✓ SapModel obtenido");

                // Obtener versión
                string[] version = new string[1];
                SapModel.GetVersion(ref version[0]);
                Console.WriteLine($"✓ SAP2000 Versión: {version[0]}");

                // Obtener archivo actual
                string filePath = "";
                SapModel.GetModelFilename(ref filePath);
                if (!string.IsNullOrEmpty(filePath))
                {
                    Console.WriteLine($"✓ Archivo actual: {filePath}");
                }
                else
                {
                    Console.WriteLine("  No hay archivo abierto");
                }

                // Crear modelo de prueba simple
                Console.WriteLine("\n--- Creando modelo de prueba ---");

                // Inicializar nuevo modelo (kN, m, C)
                SapModel.InitializeNewModel(eUnits.kN_m_C);
                Console.WriteLine("✓ Modelo inicializado (kN, m, C)");

                // Crear archivo nuevo
                SapModel.File.NewBlank();
                Console.WriteLine("✓ Archivo nuevo creado");

                // Agregar un punto
                string pointName = "";
                SapModel.PointObj.AddCartesian(0, 0, 0, ref pointName);
                Console.WriteLine($"✓ Punto creado: {pointName}");

                // Contar puntos
                int numPoints = 0;
                numPoints = SapModel.PointObj.Count();
                Console.WriteLine($"✓ Total de puntos: {numPoints}");

                // Definir material
                SapModel.PropMaterial.SetMaterial("CONC", eMatType.Concrete);
                Console.WriteLine("✓ Material 'CONC' definido");

                // Propiedades isotrópicas
                SapModel.PropMaterial.SetMPIsotropic("CONC", 3600, 0.2, 0.0000055);
                Console.WriteLine("✓ Propiedades isotrópicas asignadas");

                // Guardar modelo
                string savePath = @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_SAP2000_API.sdb";
                SapModel.File.Save(savePath);
                Console.WriteLine($"✓ Modelo guardado: {savePath}");

                Console.WriteLine("\n" + "=".PadRight(70, '='));
                Console.WriteLine("✓✓✓ API DE SAP2000 FUNCIONANDO CORRECTAMENTE ✓✓✓");
                Console.WriteLine("=".PadRight(70, '='));
                Console.WriteLine($"\nModelo de prueba creado: {savePath}");
                Console.WriteLine("Puedes abrirlo en SAP2000 para verificar.");

                // Preguntar si cerrar
                Console.Write("\n¿Cerrar SAP2000? (S/N): ");
                string response = Console.ReadLine();
                if (response.ToUpper() == "S")
                {
                    mySapObject.ApplicationExit(false);
                    Console.WriteLine("✓ SAP2000 cerrado");
                }
                else
                {
                    Console.WriteLine("SAP2000 dejado abierto para inspección");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n✗ ERROR: {ex.Message}");
                Console.WriteLine($"\nStack Trace:\n{ex.StackTrace}");

                Console.WriteLine("\n" + "=".PadRight(70, '='));
                Console.WriteLine("RAZONES POSIBLES DEL ERROR:");
                Console.WriteLine("=".PadRight(70, '='));
                Console.WriteLine("1. SAP2000 no está instalado correctamente");
                Console.WriteLine("2. SAP2000v1.dll no se encuentra");
                Console.WriteLine("3. Permisos insuficientes (ejecutar como administrador)");
                Console.WriteLine("4. Versión incompatible de SAP2000");
                Console.WriteLine("=".PadRight(70, '='));

                Environment.Exit(1);
            }

            Console.WriteLine("\nPresiona cualquier tecla para salir...");
            Console.ReadKey();
        }
    }
}
