using System;
using System.Windows;

namespace Calcpad.Wpf.MiniExcel
{
    /// <summary>
    /// Ventana contenedora para el visor MiniExcel
    /// </summary>
    public partial class MiniExcelWindow : Window
    {
        /// <summary>
        /// Evento que se dispara cuando el usuario quiere importar contenido a Calcpad
        /// </summary>
        public event EventHandler<ExcelImportEventArgs> ImportToCalcpad;

        public MiniExcelWindow()
        {
            InitializeComponent();
            ExcelViewer.ImportToCalcpad += ExcelViewer_ImportToCalcpad;
        }

        public MiniExcelWindow(string filePath) : this()
        {
            if (!string.IsNullOrEmpty(filePath))
            {
                ExcelViewer.OpenDocument(filePath);
                Title = $"MiniExcel - {System.IO.Path.GetFileName(filePath)}";
            }
        }

        private void ExcelViewer_ImportToCalcpad(object sender, ExcelImportEventArgs e)
        {
            ImportToCalcpad?.Invoke(this, e);
        }

        /// <summary>
        /// Abre un documento en el visor
        /// </summary>
        public void OpenDocument(string filePath)
        {
            ExcelViewer.OpenDocument(filePath);
            Title = $"MiniExcel - {System.IO.Path.GetFileName(filePath)}";
        }
    }
}
