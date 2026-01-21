namespace Calcpad.Common
{
    /// <summary>
    /// Specifies the environment in which Calcpad is running.
    /// Used to conditionally execute environment-specific logic.
    /// </summary>
    public enum CalcpadEnvironment
    {
        /// <summary>
        /// Command-line interface environment
        /// </summary>
        Cli,

        /// <summary>
        /// Windows Presentation Foundation (GUI) environment
        /// </summary>
        Wpf,

        /// <summary>
        /// Python API environment
        /// </summary>
        Api
    }
}
