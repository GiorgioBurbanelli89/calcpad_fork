using System;
using System.Windows;
using System.Windows.Input;
using ICSharpCode.AvalonEdit.Folding;
using System.Linq;
using System.Collections.Generic;
using Calcpad.Common.MultLangCode;
using ICSharpCode.AvalonEdit.CodeCompletion;
using ICSharpCode.AvalonEdit.Document;
using ICSharpCode.AvalonEdit.Editing;

namespace Calcpad.Wpf
{
    /// <summary>
    /// AvalonEdit integration for Calcpad - Code Folding support
    /// </summary>
    public partial class MainWindow
    {
        private FoldingManager? _foldingManager;
        private CalcpadFoldingStrategy? _foldingStrategy;
        private CompletionWindow? _completionWindow;
        private System.Windows.Threading.DispatcherTimer? _foldingUpdateTimer;
        private bool _foldingUpdatePending;

        /// <summary>
        /// Initialize AvalonEdit with code folding and syntax highlighting
        /// </summary>
        private void InitializeAvalonEdit()
        {
            if (TextEditor == null) return;

            // Install folding manager
            _foldingManager = FoldingManager.Install(TextEditor.TextArea);
            _foldingStrategy = new CalcpadFoldingStrategy();

            // Install syntax highlighting
            TextEditor.TextArea.TextView.LineTransformers.Add(new CalcpadHighlighter());

            // Setup debounced folding updates (300ms delay to prevent UI freeze)
            _foldingUpdateTimer = new System.Windows.Threading.DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(300)
            };
            _foldingUpdateTimer.Tick += (s, e) =>
            {
                _foldingUpdateTimer.Stop();
                if (_foldingUpdatePending)
                {
                    _foldingUpdatePending = false;
                    UpdateFoldingsInternal();
                }
            };

            // Update foldings when text changes (debounced)
            TextEditor.TextChanged += (s, e) => ScheduleFoldingUpdate();

            // Install autocomplete for @{calcpad:}
            TextEditor.TextArea.TextEntering += TextEditor_TextEntering;
            TextEditor.TextArea.TextEntered += TextEditor_TextEntered;

            // Initial update (delayed to not block startup)
            Dispatcher.InvokeAsync(() => UpdateFoldingsInternal(),
                System.Windows.Threading.DispatcherPriority.Background);
        }

        /// <summary>
        /// Schedule a debounced folding update
        /// </summary>
        private void ScheduleFoldingUpdate()
        {
            _foldingUpdatePending = true;
            _foldingUpdateTimer?.Stop();
            _foldingUpdateTimer?.Start();
        }

        private void TextEditor_TextEntering(object? sender, TextCompositionEventArgs e)
        {
            if (e.Text.Length > 0 && _completionWindow != null)
            {
                if (!char.IsLetterOrDigit(e.Text[0]))
                {
                    // Whenever a non-letter is typed while the completion window is open,
                    // insert the currently selected element.
                    _completionWindow.CompletionList.RequestInsertion(e);
                }
            }
            // Do not set e.Handled=true.
            // We still want to insert the character that was typed.
        }

        private void TextEditor_TextEntered(object? sender, TextCompositionEventArgs e)
        {
            if (TextEditor == null) return;

            // Check if we're inside @{html} or @{markdown} block
            if (!IsInsideExternalBlock())
                return;

            // Get the word before cursor
            string wordBeforeCursor = GetWordBeforeCursor();

            // If user typed "Calcpad", show autocomplete
            if (wordBeforeCursor.Equals("Calcpad", StringComparison.OrdinalIgnoreCase))
            {
                ShowCalcpadAutocomplete();
            }
        }

        private bool IsInsideExternalBlock()
        {
            if (TextEditor == null) return false;

            var textUpToCursor = TextEditor.Document.GetText(0, TextEditor.CaretOffset);

            // Count @{html}, @{markdown} vs @{end html}, @{end markdown}
            int htmlCount = 0;
            int markdownCount = 0;

            var lines = textUpToCursor.Split('\n');
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (trimmed.StartsWith("@{html}"))
                    htmlCount++;
                else if (trimmed.StartsWith("@{end html}"))
                    htmlCount--;
                else if (trimmed.StartsWith("@{markdown}"))
                    markdownCount++;
                else if (trimmed.StartsWith("@{end markdown}"))
                    markdownCount--;
            }

            return htmlCount > 0 || markdownCount > 0;
        }

        private string GetWordBeforeCursor()
        {
            if (TextEditor == null) return string.Empty;

            int offset = TextEditor.CaretOffset;
            if (offset == 0) return string.Empty;

            var document = TextEditor.Document;
            int startOffset = offset;

            // Go back to find start of word
            while (startOffset > 0 && char.IsLetterOrDigit(document.GetCharAt(startOffset - 1)))
            {
                startOffset--;
            }

            if (startOffset < offset)
            {
                return document.GetText(startOffset, offset - startOffset);
            }

            return string.Empty;
        }

        private void ShowCalcpadAutocomplete()
        {
            if (TextEditor == null) return;

            _completionWindow = new CompletionWindow(TextEditor.TextArea);
            var data = _completionWindow.CompletionList.CompletionData;

            // Add completion for @{calcpad:}
            data.Add(new CalcpadCompletionData());

            _completionWindow.Show();
            _completionWindow.Closed += delegate {
                _completionWindow = null;
            };
        }

        /// <summary>
        /// Update code foldings for @{language} blocks (debounced - schedules update)
        /// </summary>
        private void UpdateFoldings()
        {
            ScheduleFoldingUpdate();
        }

        /// <summary>
        /// Internal method that actually updates foldings
        /// </summary>
        private void UpdateFoldingsInternal()
        {
            if (_foldingManager != null && _foldingStrategy != null && TextEditor != null)
            {
                try
                {
                    _foldingStrategy.UpdateFoldings(_foldingManager, TextEditor.Document);
                }
                catch
                {
                    // Ignore folding errors
                }
            }
        }

        // ============================================
        // Event Handlers for TextEditor
        // ============================================

        private void TextEditor_TextChanged(object sender, EventArgs e)
        {
            // Delegate to existing RichTextBox logic if needed
            // Folding is now handled by TextChanged event in InitializeAvalonEdit
        }

        private void TextEditor_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            IsWebView2Focused = false;

            // F5: Toggle between Calculate and Show Help
            if (e.Key == Key.F5)
            {
                Calculate();
                e.Handled = true;
                return;
            }

            // Delegate other keys to RichTextBox_PreviewKeyDown for compatibility
            RichTextBox_PreviewKeyDown(sender, e);
        }

        private void TextEditor_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
        {
            // Delegate to existing RichTextBox_PreviewMouseWheel if it exists
        }

        private void TextEditor_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            // Delegate to existing RichTextBox_SizeChanged if it exists
        }

        private void TextEditor_GotKeyboardFocus(object sender, KeyboardFocusChangedEventArgs e)
        {
            // Delegate to existing RichTextBox_GotKeyboardFocus if it exists
        }

        /// <summary>
        /// Get current editor text (compatibility layer)
        /// </summary>
        public string GetEditorText()
        {
            return TextEditor?.Text ?? string.Empty;
        }

        /// <summary>
        /// Set editor text (compatibility layer)
        /// </summary>
        public void SetEditorText(string text)
        {
            if (TextEditor != null)
            {
                TextEditor.Text = text;
                UpdateFoldings();
            }
        }
    }

    /// <summary>
    /// Folding strategy for Calcpad code blocks
    /// Handles:
    /// - @{language} ... @{end language} (external languages)
    /// - #if ... #end if (conditionals)
    /// - #for ... #next (for loops)
    /// - #while ... #loop (while loops)
    /// - $svg ... $end (Calcpad SVG blocks)
    /// - <svg> ... </svg> (HTML SVG blocks)
    /// - <div> ... </div> (HTML blocks)
    /// - <!-- #region --> ... <!-- #endregion --> (HTML regions)
    /// - <head> ... </head>, <body> ... </body>, <script> ... </script>, <style> ... </style>
    /// </summary>
    public class CalcpadFoldingStrategy
    {
        public void UpdateFoldings(FoldingManager manager, ICSharpCode.AvalonEdit.Document.TextDocument document)
        {
            var foldings = CreateNewFoldings(document);
            manager.UpdateFoldings(foldings, -1);
        }

        private IEnumerable<NewFolding> CreateNewFoldings(ICSharpCode.AvalonEdit.Document.TextDocument document)
        {
            var foldings = new List<NewFolding>();

            try
            {
                // Stacks for different block types
                var externalLangStack = new Stack<(int line, string language)>();
                var ifStack = new Stack<int>();
                // Single stack for all loop types (#for, #repeat, #while) that end with #loop
                var loopStack = new Stack<(int line, string type)>();
                var svgStack = new Stack<int>();
                var divStack = new Stack<int>();
                // Stack for #def ... #end def
                var defStack = new Stack<int>();
                // Stack for HTML regions: <!-- #region NAME --> ... <!-- #endregion -->
                var regionStack = new Stack<(int line, string name)>();
                // Stacks for HTML tags
                var headStack = new Stack<int>();
                var bodyStack = new Stack<int>();
                var scriptStack = new Stack<int>();
                var styleStack = new Stack<int>();

                // Iterate through document lines using AvalonEdit's line system
                for (int lineNumber = 1; lineNumber <= document.LineCount; lineNumber++)
                {
                    var documentLine = document.GetLineByNumber(lineNumber);
                    var lineText = document.GetText(documentLine.Offset, documentLine.Length).TrimStart();

                    // External language blocks: @{language} ... @{end language}
                    if (lineText.StartsWith("@{") && !lineText.StartsWith("@{end"))
                    {
                        var endIdx = lineText.IndexOf('}');
                        if (endIdx > 2)
                        {
                            var language = lineText.Substring(2, endIdx - 2).Trim();
                            externalLangStack.Push((lineNumber, language));
                        }
                    }
                    else if (lineText.StartsWith("@{end"))
                    {
                        if (externalLangStack.Count > 0)
                        {
                            var (startLine, language) = externalLangStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            var endDocLine = documentLine;
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = endDocLine.EndOffset,
                                Name = $"▼ @{{{language}}} ..."
                            });
                        }
                    }
                    // Macro definitions: #def ... #end def
                    else if (lineText.StartsWith("#def "))
                    {
                        defStack.Push(lineNumber);
                    }
                    else if (lineText.StartsWith("#end def"))
                    {
                        if (defStack.Count > 0)
                        {
                            var startLine = defStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ #def ..."
                            });
                        }
                    }
                    // Conditional blocks: #if ... #end if
                    else if (lineText.StartsWith("#if ") || lineText.StartsWith("#if\t"))
                    {
                        ifStack.Push(lineNumber);
                    }
                    else if (lineText.StartsWith("#end if"))
                    {
                        if (ifStack.Count > 0)
                        {
                            var startLine = ifStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ #if ..."
                            });
                        }
                    }
                    // Loop blocks: #for, #repeat, #while all end with #loop
                    else if (lineText.StartsWith("#for ") || lineText.StartsWith("#for\t"))
                    {
                        loopStack.Push((lineNumber, "#for"));
                    }
                    else if (lineText.StartsWith("#repeat"))
                    {
                        loopStack.Push((lineNumber, "#repeat"));
                    }
                    else if (lineText.StartsWith("#while ") || lineText.StartsWith("#while\t"))
                    {
                        loopStack.Push((lineNumber, "#while"));
                    }
                    else if (lineText.StartsWith("#loop"))
                    {
                        if (loopStack.Count > 0)
                        {
                            var (startLine, loopType) = loopStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = $"▼ {loopType} ..."
                            });
                        }
                    }
                    // SVG blocks: <svg> ... </svg> OR $svg ... $end
                    else if (lineText.Contains("<svg") || lineText.StartsWith("$svg"))
                    {
                        svgStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</svg>") || lineText.StartsWith("$end"))
                    {
                        if (svgStack.Count > 0)
                        {
                            var startLine = svgStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ $svg ..."
                            });
                        }
                    }
                    // HTML div blocks: <div> ... </div>
                    else if (lineText.Contains("<div"))
                    {
                        divStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</div>"))
                    {
                        if (divStack.Count > 0)
                        {
                            var startLine = divStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ <div> ..."
                            });
                        }
                    }
                    // HTML regions: <!-- #region NAME --> ... <!-- #endregion -->
                    else if (lineText.Contains("<!-- #region"))
                    {
                        // Extract region name
                        var regionStartIdx = lineText.IndexOf("<!-- #region");
                        var regionNameStart = regionStartIdx + 12; // Length of "<!-- #region"
                        var regionNameEnd = lineText.IndexOf("-->", regionNameStart);
                        var regionName = regionNameEnd > regionNameStart
                            ? lineText.Substring(regionNameStart, regionNameEnd - regionNameStart).Trim()
                            : "region";
                        regionStack.Push((lineNumber, regionName));
                    }
                    else if (lineText.Contains("<!-- #endregion"))
                    {
                        if (regionStack.Count > 0)
                        {
                            var (startLine, regionName) = regionStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = $"▼ {regionName}"
                            });
                        }
                    }
                    // HTML <head> ... </head>
                    else if (lineText.Contains("<head"))
                    {
                        headStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</head>"))
                    {
                        if (headStack.Count > 0)
                        {
                            var startLine = headStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ <head> ..."
                            });
                        }
                    }
                    // HTML <body> ... </body>
                    else if (lineText.Contains("<body"))
                    {
                        bodyStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</body>"))
                    {
                        if (bodyStack.Count > 0)
                        {
                            var startLine = bodyStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ <body> ..."
                            });
                        }
                    }
                    // HTML <script> ... </script>
                    else if (lineText.Contains("<script"))
                    {
                        scriptStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</script>"))
                    {
                        if (scriptStack.Count > 0)
                        {
                            var startLine = scriptStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ <script> ..."
                            });
                        }
                    }
                    // HTML <style> ... </style>
                    else if (lineText.Contains("<style"))
                    {
                        styleStack.Push(lineNumber);
                    }
                    else if (lineText.Contains("</style>"))
                    {
                        if (styleStack.Count > 0)
                        {
                            var startLine = styleStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = "▼ <style> ..."
                            });
                        }
                    }
                }

                return foldings.OrderBy(f => f.StartOffset);
            }
            catch
            {
                // If folding fails, return empty list to prevent crashes
                return new List<NewFolding>();
            }
        }
    }

    /// <summary>
    /// Completion data for @{calcpad:} autocomplete
    /// </summary>
    public class CalcpadCompletionData : ICompletionData
    {
        public CalcpadCompletionData()
        {
            Text = "@{calcpad:}";
        }

        public System.Windows.Media.ImageSource? Image => null;

        public string Text { get; private set; }

        public object Content => Text;

        public object Description => "Insert inline Calcpad code block";

        public double Priority => 1.0;

        public void Complete(TextArea textArea, ISegment completionSegment, EventArgs insertionRequestEventArgs)
        {
            // Replace "Calcpad" with "@{calcpad:}"
            textArea.Document.Replace(completionSegment, "@{calcpad:}");

            // Move cursor before the closing }
            textArea.Caret.Offset = completionSegment.Offset + 10; // Position after ':'
        }
    }
}
