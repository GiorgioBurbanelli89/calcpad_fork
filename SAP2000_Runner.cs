using System;
using SAP2000v1;

namespace SAP2000Runner
{
    class Program
    {
        static void Main(string[] args)
        {
            // Crear instancia de SAP2000
            SAP2000v25.SapObject mySapObject = null;
            SAP2000v25.cSapModel mySapModel = null;
            SAP2000v25.cHelper myHelper = null;

            try
            {
                Console.WriteLine("Iniciando SAP2000...");

                // Crear objeto helper
                myHelper = new SAP2000v25.Helper();

                // Crear instancia de SAP2000
                mySapObject = myHelper.CreateObjectProgID("CSI.SAP2000.API.SapObject");

                // Iniciar SAP2000 (invisible y sin alertas)
                mySapObject.ApplicationStart(Units: SAP2000v25.eUnits.kN_m_C, Visible: false, FileName: "");

                // Obtener modelo
                mySapModel = mySapObject.SapModel;

                // IMPORTANTE: Desactivar TODAS las alertas y mensajes
                int ret = mySapModel.SetModelIsLocked(false);

                // Abrir el archivo del modelo
                string modelPath = @"C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\SAP 2000\Plate-6x4.s2k";
                Console.WriteLine($"Abriendo modelo: {modelPath}");
                ret = mySapModel.File.OpenFile(modelPath);

                if (ret != 0)
                {
                    Console.WriteLine("Error al abrir el archivo");
                    return;
                }

                Console.WriteLine("Modelo abierto exitosamente");

                // Desbloquear el modelo para modificaciones
                ret = mySapModel.SetModelIsLocked(false);

                // Ejecutar análisis
                Console.WriteLine("Ejecutando análisis...");
                ret = mySapModel.Analyze.RunAnalysis();

                if (ret != 0)
                {
                    Console.WriteLine("Error en el análisis");
                }
                else
                {
                    Console.WriteLine("Análisis completado exitosamente");
                }

                // Guardar el modelo
                string savePath = @"C:\Users\j-b-j\Documents\Calcpad-7.5.7\Plate-6x4_Analizado.s2k";
                Console.WriteLine($"Guardando modelo en: {savePath}");
                ret = mySapModel.File.Save(savePath);

                if (ret == 0)
                {
                    Console.WriteLine("Modelo guardado exitosamente");
                }

                // Obtener resultados del nodo central (nodo 18: x=0, y=0)
                int numberResults = 0;
                string[] obj = null;
                string[] elm = null;
                string[] loadCase = null;
                string[] stepType = null;
                double[] stepNum = null;
                double[] U1 = null, U2 = null, U3 = null;
                double[] R1 = null, R2 = null, R3 = null;

                Console.WriteLine("\nObteniendo resultados del nodo central (nodo 18)...");
                ret = mySapModel.Results.JointDispl(
                    "18",
                    SAP2000v25.eItemTypeElm.ObjectElm,
                    ref numberResults,
                    ref obj,
                    ref elm,
                    ref loadCase,
                    ref stepType,
                    ref stepNum,
                    ref U1,
                    ref U2,
                    ref U3,
                    ref R1,
                    ref R2,
                    ref R3
                );

                if (ret == 0 && numberResults > 0)
                {
                    Console.WriteLine($"\nResultados para el nodo 18 (centro de la losa):");
                    Console.WriteLine($"Número de resultados: {numberResults}");
                    for (int i = 0; i < numberResults; i++)
                    {
                        Console.WriteLine($"\nCaso de carga: {loadCase[i]}");
                        Console.WriteLine($"  Desplazamiento UZ (vertical): {U3[i] * 1000:F4} mm");
                        Console.WriteLine($"  Rotación RX: {R1[i]:F6} rad");
                        Console.WriteLine($"  Rotación RY: {R2[i]:F6} rad");
                    }
                }

                // Obtener momentos en el elemento central
                int numberResultsShell = 0;
                string[] objShell = null;
                string[] elmShell = null;
                string[] pointElmShell = null;
                string[] loadCaseShell = null;
                string[] stepTypeShell = null;
                double[] stepNumShell = null;
                double[] F11 = null, F22 = null, F12 = null;
                double[] FMax = null, FMin = null, FAngle = null;
                double[] FVM = null;
                double[] M11 = null, M22 = null, M12 = null;
                double[] MMax = null, MMin = null, MAngle = null;
                double[] V13 = null, V23 = null, VMax = null, VAngle2 = null;

                Console.WriteLine("\nObteniendo momentos del elemento central...");
                ret = mySapModel.Results.AreaStressShell(
                    "10", // Elemento central
                    SAP2000v25.eItemTypeElm.Element,
                    ref numberResultsShell,
                    ref objShell,
                    ref elmShell,
                    ref pointElmShell,
                    ref loadCaseShell,
                    ref stepTypeShell,
                    ref stepNumShell,
                    ref F11, ref F22, ref F12,
                    ref FMax, ref FMin, ref FAngle,
                    ref FVM,
                    ref M11, ref M22, ref M12,
                    ref MMax, ref MMin, ref MAngle,
                    ref V13, ref V23, ref VMax, ref VAngle2
                );

                if (ret == 0 && numberResultsShell > 0)
                {
                    Console.WriteLine($"\nMomentos en el elemento central:");
                    for (int i = 0; i < numberResultsShell; i++)
                    {
                        Console.WriteLine($"\nCaso de carga: {loadCaseShell[i]}");
                        Console.WriteLine($"  Punto: {pointElmShell[i]}");
                        Console.WriteLine($"  Momento M11 (Mx): {M11[i]:F4} kN·m/m");
                        Console.WriteLine($"  Momento M22 (My): {M22[i]:F4} kN·m/m");
                        Console.WriteLine($"  Momento M12 (Mxy): {M12[i]:F4} kN·m/m");
                    }
                }

                Console.WriteLine("\n=== COMPARACIÓN CON CALCPAD ===");
                Console.WriteLine("Según el ejemplo de Calcpad 'Rectangular Slab FEA.cpd':");
                Console.WriteLine("- Losa: 6m x 4m, espesor 0.1m");
                Console.WriteLine("- Carga: q = 10 kN/m²");
                Console.WriteLine("- Material: E = 35000 MPa, ν = 0.15");
                Console.WriteLine("- Malla: 6x4 elementos");
                Console.WriteLine("\nCalcular los resultados de Calcpad y compararlos aquí.");

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
            }
            finally
            {
                // Cerrar SAP2000
                if (mySapObject != null)
                {
                    Console.WriteLine("\nCerrando SAP2000...");
                    mySapObject.ApplicationExit(false);
                }

                // Liberar objetos COM
                if (mySapModel != null)
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(mySapModel);
                if (mySapObject != null)
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(mySapObject);
                if (myHelper != null)
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(myHelper);

                Console.WriteLine("Proceso completado. Presiona Enter para salir...");
                Console.ReadLine();
            }
        }
    }
}
