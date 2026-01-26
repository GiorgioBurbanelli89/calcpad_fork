using System;
using System.Windows;

namespace Calcpad.Wpf.MiniWord
{
    /// <summary>
    /// Ventana contenedora para el visor MiniWord
    /// </summary>
    public partial class MiniWordWindow : Window
    {
        /// <summary>
        /// Evento que se dispara cuando el usuario quiere importar contenido a Calcpad
        /// </summary>
        public event EventHandler<ImportToCalcpadEventArgs> ImportToCalcpad;

        public MiniWordWindow()
        {
            InitializeComponent();
            WordViewer.ImportToCalcpad += WordViewer_ImportToCalcpad;
        }

        public MiniWordWindow(string filePath) : this()
        {
            if (!string.IsNullOrEmpty(filePath))
            {
                WordViewer.OpenDocument(filePath);
                Title = $"MiniWord - {System.IO.Path.GetFileName(filePath)}";
            }
        }

        private void WordViewer_ImportToCalcpad(object sender, ImportToCalcpadEventArgs e)
        {
            ImportToCalcpad?.Invoke(this, e);
        }

        /// <summary>
        /// Abre un documento en el visor
        /// </summary>
        public void OpenDocument(string filePath)
        {
            WordViewer.OpenDocument(filePath);
            Title = $"MiniWord - {System.IO.Path.GetFileName(filePath)}";
        }
    }
}
