# SMath Studio - Gráficas Custom, AI y Python

## 🎯 Respuesta Directa

**SÍ, puedes hacer las 3 cosas:**

1. ✅ **Crear tus propias gráficas** (no usar las de SMath)
2. ✅ **Agregar AI/Machine Learning**
3. ✅ **Integrar Python**

---

## 📊 1. Gráficas Personalizadas (Custom Charts)

### Concepto

Crear una **región personalizada** que dibuja gráficas a tu medida usando GDI+ o WPF.

### Método 1: Región con GDI+ (Más Simple)

#### Código del Plugin

**CustomChartPlugin.cs**
```csharp
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using SMath.Controls;
using SMath.Manager;
using SMath.Math.Numeric;

namespace CustomChartPlugin
{
    // ================================================================
    // PLUGIN PRINCIPAL
    // ================================================================
    public class CustomChartPlugin : IPluginCustomRegion
    {
        public RegionBase CreateRegion()
        {
            return new CustomChartRegion();
        }

        public string RegionTypeName => "Custom Chart";
    }

    // ================================================================
    // REGIÓN DE GRÁFICA PERSONALIZADA
    // ================================================================
    public class CustomChartRegion : RegionBase
    {
        private double[] xData;
        private double[] yData;
        private string chartType = "line"; // line, bar, scatter, heatmap, 3d

        public CustomChartRegion()
        {
            // Datos de ejemplo
            xData = new double[] { 0, 1, 2, 3, 4, 5 };
            yData = new double[] { 0, 1, 4, 9, 16, 25 };
        }

        // Establecer datos desde SMath
        public void SetData(double[] x, double[] y, string type = "line")
        {
            xData = x;
            yData = y;
            chartType = type;
        }

        // ================================================================
        // DIBUJAR LA GRÁFICA
        // ================================================================
        public override void Draw(Graphics g, Rectangle bounds)
        {
            // Fondo
            g.FillRectangle(new SolidBrush(Color.White), bounds);

            switch (chartType)
            {
                case "line":
                    DrawLineChart(g, bounds);
                    break;
                case "bar":
                    DrawBarChart(g, bounds);
                    break;
                case "scatter":
                    DrawScatterChart(g, bounds);
                    break;
                case "heatmap":
                    DrawHeatmap(g, bounds);
                    break;
                case "polar":
                    DrawPolarChart(g, bounds);
                    break;
                case "3d":
                    Draw3DChart(g, bounds);
                    break;
            }

            // Título y leyenda
            DrawTitle(g, bounds);
            DrawAxes(g, bounds);
            DrawLegend(g, bounds);
        }

        // ================================================================
        // GRÁFICA DE LÍNEA PERSONALIZADA
        // ================================================================
        private void DrawLineChart(Graphics g, Rectangle bounds)
        {
            if (xData == null || yData == null || xData.Length == 0) return;

            // Configurar anti-aliasing
            g.SmoothingMode = SmoothingMode.AntiAlias;

            // Calcular escalas
            float xMin = (float)xData.Min();
            float xMax = (float)xData.Max();
            float yMin = (float)yData.Min();
            float yMax = (float)yData.Max();

            float margin = 50;
            float plotWidth = bounds.Width - 2 * margin;
            float plotHeight = bounds.Height - 2 * margin;

            // Función para transformar coordenadas
            PointF Transform(double x, double y)
            {
                float px = margin + plotWidth * (float)((x - xMin) / (xMax - xMin));
                float py = bounds.Height - margin - plotHeight * (float)((y - yMin) / (yMax - yMin));
                return new PointF(px, py);
            }

            // Dibujar grid (opcional)
            DrawGrid(g, bounds, margin, xMin, xMax, yMin, yMax);

            // Dibujar línea con gradiente
            Pen linePen = new Pen(Color.FromArgb(100, 50, 150, 255), 3);
            linePen.StartCap = LineCap.Round;
            linePen.EndCap = LineCap.Round;

            for (int i = 0; i < xData.Length - 1; i++)
            {
                PointF p1 = Transform(xData[i], yData[i]);
                PointF p2 = Transform(xData[i + 1], yData[i + 1]);

                // Línea con gradiente de color según altura
                Color c1 = GetGradientColor(yData[i], yMin, yMax);
                Color c2 = GetGradientColor(yData[i + 1], yMin, yMax);

                using (LinearGradientBrush brush = new LinearGradientBrush(p1, p2, c1, c2))
                {
                    Pen gradPen = new Pen(brush, 3);
                    g.DrawLine(gradPen, p1, p2);
                }
            }

            // Dibujar puntos
            for (int i = 0; i < xData.Length; i++)
            {
                PointF p = Transform(xData[i], yData[i]);
                g.FillEllipse(Brushes.White, p.X - 5, p.Y - 5, 10, 10);
                g.DrawEllipse(new Pen(Color.FromArgb(50, 100, 200), 2), p.X - 5, p.Y - 5, 10, 10);

                // Etiqueta del valor
                string label = $"{yData[i]:F2}";
                SizeF labelSize = g.MeasureString(label, SystemFonts.DefaultFont);
                g.DrawString(label, SystemFonts.DefaultFont, Brushes.Black,
                             p.X - labelSize.Width / 2, p.Y - 20);
            }
        }

        // ================================================================
        // GRÁFICA DE BARRAS PERSONALIZADA
        // ================================================================
        private void DrawBarChart(Graphics g, Rectangle bounds)
        {
            if (yData == null || yData.Length == 0) return;

            float margin = 50;
            float plotWidth = bounds.Width - 2 * margin;
            float plotHeight = bounds.Height - 2 * margin;

            float yMax = (float)yData.Max();
            float barWidth = plotWidth / yData.Length * 0.8f;
            float spacing = plotWidth / yData.Length * 0.2f;

            for (int i = 0; i < yData.Length; i++)
            {
                float x = margin + i * (barWidth + spacing);
                float height = plotHeight * (float)(yData[i] / yMax);
                float y = bounds.Height - margin - height;

                // Barra con gradiente vertical
                using (LinearGradientBrush brush = new LinearGradientBrush(
                    new PointF(x, y),
                    new PointF(x, y + height),
                    Color.FromArgb(100, 50, 200, 255),
                    Color.FromArgb(255, 100, 150, 255)))
                {
                    g.FillRectangle(brush, x, y, barWidth, height);
                }

                // Borde
                g.DrawRectangle(new Pen(Color.FromArgb(30, 50, 150), 2), x, y, barWidth, height);

                // Etiqueta
                string label = $"{yData[i]:F1}";
                SizeF labelSize = g.MeasureString(label, SystemFonts.DefaultFont);
                g.DrawString(label, SystemFonts.DefaultFont, Brushes.Black,
                             x + barWidth / 2 - labelSize.Width / 2, y - 20);
            }
        }

        // ================================================================
        // GRÁFICA DE DISPERSIÓN (SCATTER)
        // ================================================================
        private void DrawScatterChart(Graphics g, Rectangle bounds)
        {
            if (xData == null || yData == null) return;

            float margin = 50;
            float plotWidth = bounds.Width - 2 * margin;
            float plotHeight = bounds.Height - 2 * margin;

            float xMin = (float)xData.Min();
            float xMax = (float)xData.Max();
            float yMin = (float)yData.Min();
            float yMax = (float)yData.Max();

            for (int i = 0; i < xData.Length; i++)
            {
                float x = margin + plotWidth * (float)((xData[i] - xMin) / (xMax - xMin));
                float y = bounds.Height - margin - plotHeight * (float)((yData[i] - yMin) / (yMax - yMin));

                // Tamaño del punto proporcional al valor
                float size = 5 + 10 * (float)(yData[i] / yMax);

                // Color según valor
                Color color = GetGradientColor(yData[i], yMin, yMax);

                // Dibujar punto con halo
                using (GraphicsPath path = new GraphicsPath())
                {
                    path.AddEllipse(x - size, y - size, size * 2, size * 2);

                    using (PathGradientBrush brush = new PathGradientBrush(path))
                    {
                        brush.CenterColor = color;
                        brush.SurroundColors = new Color[] { Color.FromArgb(50, color) };

                        g.FillEllipse(brush, x - size, y - size, size * 2, size * 2);
                    }
                }

                g.DrawEllipse(new Pen(Color.White, 2), x - size, y - size, size * 2, size * 2);
            }
        }

        // ================================================================
        // MAPA DE CALOR (HEATMAP)
        // ================================================================
        private void DrawHeatmap(Graphics g, Rectangle bounds)
        {
            // Asumiendo que yData es una matriz aplanada
            int rows = (int)Math.Sqrt(yData.Length);
            int cols = rows;

            float cellWidth = (float)bounds.Width / cols;
            float cellHeight = (float)bounds.Height / rows;

            double min = yData.Min();
            double max = yData.Max();

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    int idx = i * cols + j;
                    if (idx >= yData.Length) continue;

                    float x = j * cellWidth;
                    float y = i * cellHeight;

                    Color color = GetHeatmapColor(yData[idx], min, max);
                    g.FillRectangle(new SolidBrush(color), x, y, cellWidth, cellHeight);
                }
            }

            // Dibujar escala de colores
            DrawColorScale(g, bounds, min, max);
        }

        // ================================================================
        // GRÁFICA POLAR
        // ================================================================
        private void DrawPolarChart(Graphics g, Rectangle bounds)
        {
            if (xData == null || yData == null) return;

            float centerX = bounds.Width / 2f;
            float centerY = bounds.Height / 2f;
            float radius = Math.Min(bounds.Width, bounds.Height) / 2f - 50;

            // Dibujar círculos concéntricos
            for (int i = 1; i <= 5; i++)
            {
                float r = radius * i / 5f;
                g.DrawEllipse(new Pen(Color.LightGray, 1),
                              centerX - r, centerY - r, r * 2, r * 2);
            }

            // Dibujar radios
            for (int angle = 0; angle < 360; angle += 30)
            {
                double rad = angle * Math.PI / 180;
                float x = centerX + radius * (float)Math.Cos(rad);
                float y = centerY + radius * (float)Math.Sin(rad);
                g.DrawLine(new Pen(Color.LightGray, 1), centerX, centerY, x, y);
            }

            // Dibujar datos
            double maxR = yData.Max();
            PointF[] points = new PointF[xData.Length + 1];

            for (int i = 0; i < xData.Length; i++)
            {
                double angle = xData[i];
                double r = yData[i] / maxR * radius;

                float x = centerX + (float)(r * Math.Cos(angle));
                float y = centerY + (float)(r * Math.Sin(angle));

                points[i] = new PointF(x, y);
            }
            points[xData.Length] = points[0]; // Cerrar

            // Llenar área
            using (SolidBrush fillBrush = new SolidBrush(Color.FromArgb(100, 100, 150, 255)))
            {
                g.FillPolygon(fillBrush, points);
            }

            // Dibujar línea
            g.DrawLines(new Pen(Color.FromArgb(50, 100, 200), 3), points);
        }

        // ================================================================
        // PSEUDO-3D (ISOMÉTRICO)
        // ================================================================
        private void Draw3DChart(Graphics g, Rectangle bounds)
        {
            // Proyección isométrica simple
            int rows = 10;
            int cols = 10;

            float cellSize = 20;
            float offsetX = bounds.Width / 2f;
            float offsetY = bounds.Height / 2f;

            // Ángulos isométricos
            double angleX = Math.PI / 6;  // 30 grados
            double angleY = -Math.PI / 6;

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    int idx = i * cols + j;
                    if (idx >= yData.Length) continue;

                    float height = (float)yData[idx] * 5;

                    // Transformar a coordenadas isométricas
                    float x = offsetX + (float)(j * cellSize * Math.Cos(angleX) + i * cellSize * Math.Cos(angleY));
                    float y = offsetY + (float)(j * cellSize * Math.Sin(angleX) + i * cellSize * Math.Sin(angleY)) - height;

                    // Dibujar barra 3D
                    Draw3DBar(g, x, y, cellSize, height, GetGradientColor(yData[idx], yData.Min(), yData.Max()));
                }
            }
        }

        private void Draw3DBar(Graphics g, float x, float y, float size, float height, Color color)
        {
            // Top face
            PointF[] top = new PointF[]
            {
                new PointF(x, y),
                new PointF(x + size * 0.5f, y - size * 0.25f),
                new PointF(x + size, y),
                new PointF(x + size * 0.5f, y + size * 0.25f)
            };
            g.FillPolygon(new SolidBrush(Color.FromArgb(color.A,
                Math.Min(color.R + 50, 255),
                Math.Min(color.G + 50, 255),
                Math.Min(color.B + 50, 255))), top);

            // Right face
            PointF[] right = new PointF[]
            {
                new PointF(x + size, y),
                new PointF(x + size, y + height),
                new PointF(x + size * 0.5f, y + height + size * 0.25f),
                new PointF(x + size * 0.5f, y + size * 0.25f)
            };
            g.FillPolygon(new SolidBrush(color), right);

            // Left face
            PointF[] left = new PointF[]
            {
                new PointF(x, y),
                new PointF(x, y + height),
                new PointF(x + size * 0.5f, y + height + size * 0.25f),
                new PointF(x + size * 0.5f, y + size * 0.25f)
            };
            g.FillPolygon(new SolidBrush(Color.FromArgb(color.A,
                Math.Max(color.R - 50, 0),
                Math.Max(color.G - 50, 0),
                Math.Max(color.B - 50, 0))), left);
        }

        // ================================================================
        // FUNCIONES AUXILIARES
        // ================================================================
        private void DrawGrid(Graphics g, Rectangle bounds, float margin,
                              float xMin, float xMax, float yMin, float yMax)
        {
            Pen gridPen = new Pen(Color.FromArgb(50, 200, 200, 200), 1);
            gridPen.DashStyle = DashStyle.Dot;

            // Líneas verticales
            for (int i = 0; i <= 10; i++)
            {
                float x = margin + (bounds.Width - 2 * margin) * i / 10f;
                g.DrawLine(gridPen, x, margin, x, bounds.Height - margin);
            }

            // Líneas horizontales
            for (int i = 0; i <= 10; i++)
            {
                float y = margin + (bounds.Height - 2 * margin) * i / 10f;
                g.DrawLine(gridPen, margin, y, bounds.Width - margin, y);
            }
        }

        private void DrawAxes(Graphics g, Rectangle bounds)
        {
            float margin = 50;
            Pen axisPen = new Pen(Color.Black, 2);

            // Eje X
            g.DrawLine(axisPen, margin, bounds.Height - margin,
                       bounds.Width - margin, bounds.Height - margin);

            // Eje Y
            g.DrawLine(axisPen, margin, margin,
                       margin, bounds.Height - margin);

            // Etiquetas de ejes
            g.DrawString("X", SystemFonts.DefaultFont, Brushes.Black,
                         bounds.Width - margin + 10, bounds.Height - margin - 10);
            g.DrawString("Y", SystemFonts.DefaultFont, Brushes.Black,
                         margin - 20, margin - 20);
        }

        private void DrawTitle(Graphics g, Rectangle bounds)
        {
            Font titleFont = new Font("Arial", 14, FontStyle.Bold);
            string title = $"Custom {chartType.ToUpper()} Chart";
            SizeF titleSize = g.MeasureString(title, titleFont);

            g.DrawString(title, titleFont, Brushes.Black,
                         bounds.Width / 2 - titleSize.Width / 2, 10);
        }

        private void DrawLegend(Graphics g, Rectangle bounds)
        {
            // Leyenda simple
            float x = bounds.Width - 150;
            float y = 50;

            g.FillRectangle(new SolidBrush(Color.FromArgb(200, 255, 255, 255)),
                            x - 10, y - 10, 140, 60);
            g.DrawRectangle(new Pen(Color.Gray, 1), x - 10, y - 10, 140, 60);

            g.DrawString("Data Series 1", SystemFonts.DefaultFont, Brushes.Black, x, y);
            g.DrawLine(new Pen(Color.FromArgb(50, 100, 200), 3), x, y + 20, x + 30, y + 20);
        }

        private void DrawColorScale(Graphics g, Rectangle bounds, double min, double max)
        {
            float x = bounds.Width - 50;
            float y = 50;
            float width = 30;
            float height = bounds.Height - 100;

            for (int i = 0; i < height; i++)
            {
                double value = max - (max - min) * i / height;
                Color color = GetHeatmapColor(value, min, max);
                g.DrawLine(new Pen(color, 1), x, y + i, x + width, y + i);
            }

            g.DrawRectangle(Pens.Black, x, y, width, height);
            g.DrawString($"{max:F1}", SystemFonts.DefaultFont, Brushes.Black, x + width + 5, y);
            g.DrawString($"{min:F1}", SystemFonts.DefaultFont, Brushes.Black, x + width + 5, y + height - 10);
        }

        private Color GetGradientColor(double value, double min, double max)
        {
            double normalized = (value - min) / (max - min);
            normalized = Math.Max(0, Math.Min(1, normalized));

            // Gradiente azul -> verde -> amarillo -> rojo
            if (normalized < 0.33)
            {
                // Azul -> Verde
                float t = (float)(normalized / 0.33);
                return Color.FromArgb(
                    (int)(0 + 0 * t),
                    (int)(100 + 155 * t),
                    (int)(255 - 255 * t)
                );
            }
            else if (normalized < 0.66)
            {
                // Verde -> Amarillo
                float t = (float)((normalized - 0.33) / 0.33);
                return Color.FromArgb(
                    (int)(0 + 255 * t),
                    (int)(255),
                    (int)(0)
                );
            }
            else
            {
                // Amarillo -> Rojo
                float t = (float)((normalized - 0.66) / 0.34);
                return Color.FromArgb(
                    (int)(255),
                    (int)(255 - 255 * t),
                    (int)(0)
                );
            }
        }

        private Color GetHeatmapColor(double value, double min, double max)
        {
            double normalized = (value - min) / (max - min);
            normalized = Math.Max(0, Math.Min(1, normalized));

            // Paleta tipo "jet"
            byte r, g, b;

            if (normalized < 0.25)
            {
                r = 0;
                g = (byte)(255 * normalized / 0.25);
                b = 255;
            }
            else if (normalized < 0.5)
            {
                r = 0;
                g = 255;
                b = (byte)(255 * (0.5 - normalized) / 0.25);
            }
            else if (normalized < 0.75)
            {
                r = (byte)(255 * (normalized - 0.5) / 0.25);
                g = 255;
                b = 0;
            }
            else
            {
                r = 255;
                g = (byte)(255 * (1.0 - normalized) / 0.25);
                b = 0;
            }

            return Color.FromArgb(r, g, b);
        }
    }
}
```

#### Usar en SMath Studio

```
# Datos
x := 0,0.1..2π
y := sin(x)

# Crear gráfica personalizada
Insertar → Custom Chart

[Widget interactivo aparece]

# Configurar datos
chart.SetData(x, y, "line")  # O "bar", "scatter", "polar", "3d"

[Gráfica personalizada se dibuja con tu estilo]
```

---

## 🤖 2. Integrar AI / Machine Learning

### Método 1: ML.NET (Microsoft)

**AIPlugin.cs**
```csharp
using System;
using Microsoft.ML;
using Microsoft.ML.Data;
using SMath.Manager;

namespace AIPlugin
{
    public class MLPlugin : IPluginLowLevelEvaluationFast
    {
        private static MLContext mlContext = new MLContext();

        public void Initialize()
        {
            GlobalFunctions.RegisterFunction("train_model", TrainModel);
            GlobalFunctions.RegisterFunction("predict", Predict);
            GlobalFunctions.RegisterFunction("classify", Classify);
        }

        // ================================================================
        // REGRESIÓN LINEAL
        // ================================================================
        private static Term TrainModel(Term[] args)
        {
            // args[0] = matriz X (features)
            // args[1] = vector y (targets)

            Matrix X = args[0].obj.ToMatrix();
            Matrix y = args[1].obj.ToMatrix();

            // Preparar datos
            var data = new List<RegressionData>();
            for (int i = 0; i < X.Rows; i++)
            {
                data.Add(new RegressionData
                {
                    Feature1 = (float)X[i, 0].ToDouble(),
                    Feature2 = (float)X[i, 1].ToDouble(),
                    Label = (float)y[i, 0].ToDouble()
                });
            }

            IDataView trainingData = mlContext.Data.LoadFromEnumerable(data);

            // Definir pipeline
            var pipeline = mlContext.Transforms.Concatenate("Features", "Feature1", "Feature2")
                .Append(mlContext.Regression.Trainers.Sdca(labelColumnName: "Label"));

            // Entrenar modelo
            var model = pipeline.Fit(trainingData);

            // Guardar modelo
            mlContext.Model.Save(model, trainingData.Schema, "model.zip");

            return new Term("Model trained successfully");
        }

        private static Term Predict(Term[] args)
        {
            // Cargar modelo
            DataViewSchema modelSchema;
            ITransformer model = mlContext.Model.Load("model.zip", out modelSchema);

            var predictionEngine = mlContext.Model.CreatePredictionEngine<RegressionData, RegressionPrediction>(model);

            // Predecir
            var input = new RegressionData
            {
                Feature1 = (float)args[0].obj.ToDouble(),
                Feature2 = (float)args[1].obj.ToDouble()
            };

            var prediction = predictionEngine.Predict(input);

            return new Term(prediction.Score);
        }

        // ================================================================
        // CLASIFICACIÓN
        // ================================================================
        private static Term Classify(Term[] args)
        {
            // Clasificador simple de k-nearest neighbors
            Matrix trainingX = args[0].obj.ToMatrix();
            Matrix trainingY = args[1].obj.ToMatrix();
            Matrix testPoint = args[2].obj.ToMatrix();
            int k = (int)args[3].obj.ToDouble();

            // Calcular distancias
            double[] distances = new double[trainingX.Rows];
            for (int i = 0; i < trainingX.Rows; i++)
            {
                double dist = 0;
                for (int j = 0; j < trainingX.Cols; j++)
                {
                    double diff = trainingX[i, j].ToDouble() - testPoint[0, j].ToDouble();
                    dist += diff * diff;
                }
                distances[i] = Math.Sqrt(dist);
            }

            // Encontrar k vecinos más cercanos
            var neighbors = distances
                .Select((dist, idx) => new { Distance = dist, Index = idx })
                .OrderBy(x => x.Distance)
                .Take(k)
                .ToList();

            // Votación mayoritaria
            var votes = neighbors
                .GroupBy(n => trainingY[n.Index, 0].ToDouble())
                .OrderByDescending(g => g.Count())
                .First();

            return new Term(votes.Key);
        }
    }

    // Clases de datos
    public class RegressionData
    {
        public float Feature1 { get; set; }
        public float Feature2 { get; set; }
        public float Label { get; set; }
    }

    public class RegressionPrediction
    {
        [ColumnName("Score")]
        public float Score { get; set; }
    }
}
```

**Usar en SMath:**
```
# Datos de entrenamiento
X_train := [[1, 2],
            [2, 3],
            [3, 4],
            [4, 5]]

y_train := [[3],
            [5],
            [7],
            [9]]

# Entrenar modelo de AI
train_model(X_train, y_train)

# Predecir nuevos valores
y_pred := predict(5, 6)  # → 11 (aproximadamente)

# Clasificación
X_iris := [[5.1, 3.5],
           [4.9, 3.0],
           [6.7, 3.1],
           ...]

y_iris := [[0], [0], [1], ...]  # Clases

# Clasificar nuevo punto
class := classify(X_iris, y_iris, [[5.5, 3.2]], 5)
```

### Método 2: TensorFlow.NET

**TensorFlowPlugin.cs**
```csharp
using System;
using Tensorflow;
using SMath.Manager;
using static Tensorflow.Binding;

namespace TensorFlowPlugin
{
    public class TFPlugin : IPluginLowLevelEvaluationFast
    {
        public void Initialize()
        {
            GlobalFunctions.RegisterFunction("train_neural_network", TrainNN);
            GlobalFunctions.RegisterFunction("nn_predict", PredictNN);
        }

        private static Term TrainNN(Term[] args)
        {
            // Crear red neuronal simple
            var X = args[0].obj.ToMatrix();
            var y = args[1].obj.ToMatrix();

            // Convertir a tensores
            var X_tensor = tf.constant(MatrixToArray(X));
            var y_tensor = tf.constant(MatrixToArray(y));

            // Definir modelo
            var model = tf.keras.Sequential(new Layer[]
            {
                tf.keras.layers.Dense(64, activation: "relu"),
                tf.keras.layers.Dense(32, activation: "relu"),
                tf.keras.layers.Dense(1)
            });

            // Compilar
            model.compile(
                optimizer: tf.keras.optimizers.Adam(0.001f),
                loss: "mse"
            );

            // Entrenar
            model.fit(X_tensor, y_tensor, epochs: 100);

            // Guardar
            model.save("neural_model.h5");

            return new Term("Neural network trained");
        }

        private static float[,] MatrixToArray(Matrix m)
        {
            float[,] result = new float[m.Rows, m.Cols];
            for (int i = 0; i < m.Rows; i++)
                for (int j = 0; j < m.Cols; j++)
                    result[i, j] = (float)m[i, j].ToDouble();
            return result;
        }
    }
}
```

---

## 🐍 3. Integrar Python

### Método 1: Python.NET (IronPython)

**PythonPlugin.cs**
```csharp
using System;
using Python.Runtime;
using SMath.Manager;
using SMath.Math.Numeric;

namespace PythonIntegrationPlugin
{
    public class PythonPlugin : IPluginLowLevelEvaluationFast
    {
        public void Initialize()
        {
            // Inicializar Python
            Runtime.PythonDLL = @"C:\Python39\python39.dll";
            PythonEngine.Initialize();

            GlobalFunctions.RegisterFunction("py_exec", ExecutePython);
            GlobalFunctions.RegisterFunction("py_numpy", UseNumPy);
            GlobalFunctions.RegisterFunction("py_matplotlib", PlotMatplotlib);
        }

        // ================================================================
        // EJECUTAR CÓDIGO PYTHON
        // ================================================================
        private static Term ExecutePython(Term[] args)
        {
            string code = args[0].obj.ToString();

            using (Py.GIL())
            {
                dynamic py = PythonEngine.ModuleFromString("script", code);
                var result = py.result;

                return new Term((double)result);
            }
        }

        // ================================================================
        // USAR NUMPY
        // ================================================================
        private static Term UseNumPy(Term[] args)
        {
            Matrix data = args[0].obj.ToMatrix();

            using (Py.GIL())
            {
                dynamic np = Py.Import("numpy");

                // Convertir matriz de SMath a NumPy array
                double[,] arr = new double[data.Rows, data.Cols];
                for (int i = 0; i < data.Rows; i++)
                    for (int j = 0; j < data.Cols; j++)
                        arr[i, j] = data[i, j].ToDouble();

                dynamic npArray = np.array(arr);

                // Operaciones NumPy
                dynamic mean = np.mean(npArray);
                dynamic std = np.std(npArray);
                dynamic eigenvalues = np.linalg.eigvals(npArray);

                // Retornar resultados
                Matrix result = new Matrix(1, 3);
                result[0, 0] = new Term((double)mean);
                result[0, 1] = new Term((double)std);
                result[0, 2] = new Term((double)eigenvalues[0]);

                return new Term(result);
            }
        }

        // ================================================================
        // MATPLOTLIB
        // ================================================================
        private static Term PlotMatplotlib(Term[] args)
        {
            Matrix x = args[0].obj.ToMatrix();
            Matrix y = args[1].obj.ToMatrix();

            using (Py.GIL())
            {
                dynamic plt = Py.Import("matplotlib.pyplot");

                // Convertir datos
                double[] xArr = new double[x.Rows];
                double[] yArr = new double[y.Rows];

                for (int i = 0; i < x.Rows; i++)
                {
                    xArr[i] = x[i, 0].ToDouble();
                    yArr[i] = y[i, 0].ToDouble();
                }

                // Graficar
                plt.figure(figsize: new int[] { 10, 6 });
                plt.plot(xArr, yArr, "b-", linewidth: 2);
                plt.xlabel("X");
                plt.ylabel("Y");
                plt.title("Plot from SMath Studio");
                plt.grid(true);
                plt.savefig("plot.png");
                plt.show();
            }

            return new Term("Plot saved as plot.png");
        }
    }
}
```

**Usar en SMath:**
```
# Ejecutar código Python
result := py_exec("
import numpy as np
result = np.sin(0.5) * 2
")

# Usar NumPy
A := [[1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]]

stats := py_numpy(A)  # → [mean, std, eigenvalue]

# Graficar con Matplotlib
x := 0,0.1..2π
y := sin(x)

py_matplotlib(x, y)  # Crea plot.png con Matplotlib
```

### Método 2: Subprocess (Ejecutar Python Externo)

**PythonSubprocessPlugin.cs**
```csharp
using System;
using System.Diagnostics;
using System.IO;
using SMath.Manager;

namespace PythonSubprocessPlugin
{
    public class PySubprocessPlugin : IPluginLowLevelEvaluationFast
    {
        public void Initialize()
        {
            GlobalFunctions.RegisterFunction("python", RunPythonScript);
            GlobalFunctions.RegisterFunction("python_ml", RunMLScript);
        }

        private static Term RunPythonScript(Term[] args)
        {
            // args[0] = script Python como string
            string script = args[0].obj.ToString();

            // Escribir script a archivo
            File.WriteAllText("temp_script.py", script);

            // Ejecutar Python
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "temp_script.py",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            Process process = Process.Start(psi);
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (!string.IsNullOrEmpty(error))
                return new Term($"Error: {error}");

            // Parsear resultado
            if (double.TryParse(output.Trim(), out double result))
                return new Term(result);

            return new Term(output.Trim());
        }

        private static Term RunMLScript(Term[] args)
        {
            Matrix X = args[0].obj.ToMatrix();
            Matrix y = args[1].obj.ToMatrix();

            // Generar script Python con machine learning
            string script = $@"
import numpy as np
from sklearn.linear_model import LinearRegression

# Datos
X = np.array({MatrixToPythonList(X)})
y = np.array({MatrixToPythonList(y)})

# Entrenar modelo
model = LinearRegression()
model.fit(X, y)

# Predecir
X_test = np.array([[5, 6]])
y_pred = model.predict(X_test)

print(y_pred[0])
";

            File.WriteAllText("ml_script.py", script);

            // Ejecutar
            Process process = Process.Start(new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "ml_script.py",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                CreateNoWindow = true
            });

            string output = process.StandardOutput.ReadToEnd();
            process.WaitForExit();

            return new Term(double.Parse(output.Trim()));
        }

        private static string MatrixToPythonList(Matrix m)
        {
            string result = "[";
            for (int i = 0; i < m.Rows; i++)
            {
                result += "[";
                for (int j = 0; j < m.Cols; j++)
                {
                    result += m[i, j].ToDouble().ToString();
                    if (j < m.Cols - 1) result += ", ";
                }
                result += "]";
                if (i < m.Rows - 1) result += ", ";
            }
            result += "]";
            return result;
        }
    }
}
```

**Usar en SMath:**
```
# Ejecutar script Python simple
result := python("
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.savefig('output.png')

print(np.max(y))
")

# Machine learning con scikit-learn
X_train := [[1, 2], [2, 3], [3, 4]]
y_train := [[3], [5], [7]]

prediction := python_ml(X_train, y_train)
```

---

## 📊 Resumen de Capacidades

| Característica | ¿Posible? | Dificultad | Método |
|----------------|-----------|------------|--------|
| **Gráficas Personalizadas** | ✅ Sí | ⭐⭐⭐ Media-Alta | IPluginCustomRegion + GDI+ |
| **Gráficas 3D Custom** | ✅ Sí | ⭐⭐⭐⭐ Alta | GDI+ isométrico o WPF 3D |
| **Gráficas Interactivas** | ✅ Sí | ⭐⭐⭐⭐ Alta | WPF Controls |
| **AI/ML (ML.NET)** | ✅ Sí | ⭐⭐⭐ Media-Alta | NuGet ML.NET |
| **AI/ML (TensorFlow)** | ✅ Sí | ⭐⭐⭐⭐ Alta | TensorFlow.NET |
| **Python Integration** | ✅ Sí | ⭐⭐ Media | Python.NET o subprocess |
| **Matplotlib desde SMath** | ✅ Sí | ⭐⭐⭐ Media-Alta | Python.NET |
| **NumPy/SciPy** | ✅ Sí | ⭐⭐⭐ Media-Alta | Python.NET |
| **Scikit-learn** | ✅ Sí | ⭐⭐⭐ Media-Alta | Subprocess |

---

## ✅ Conclusión

### Pregunta Original:
> "Es decir, ¿puedo crear mi propio formato de gráfica, agregar AI, y agregar Python?"

### Respuesta:
**¡SÍ a todo!**

1. ✅ **Gráficas personalizadas:** Usa `IPluginCustomRegion` + GDI+/WPF
2. ✅ **AI/Machine Learning:** Usa ML.NET o TensorFlow.NET
3. ✅ **Python:** Usa Python.NET o subprocess

**No hay límites reales** - puedes extender SMath Studio como quieras.

### Tu caso de uso:
- Gráficas FEM personalizadas (mallas, deformadas)
- AI para optimización de estructuras
- Python para cálculos científicos

**Todo es posible con plugins de SMath Studio.**
