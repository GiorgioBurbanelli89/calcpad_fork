using System.Windows;

namespace Calcpad.Wpf.MathEditor
{
    public partial class MathEditorTestWindow : Window
    {
        public MathEditorTestWindow()
        {
            InitializeComponent();
        }

        private void BtnGetCode_Click(object sender, RoutedEventArgs e)
        {
            var code = MathEditor.ToCalcpad();
            OutputText.Text = $"Código Calcpad:\n{code}";
        }

        private void BtnClear_Click(object sender, RoutedEventArgs e)
        {
            MathEditor.FromCalcpad("");
            OutputText.Text = "";
        }
    }
}
