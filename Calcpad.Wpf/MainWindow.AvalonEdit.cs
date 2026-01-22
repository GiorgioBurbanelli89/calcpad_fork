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

            // Install folding manager - this automatically adds FoldingMargin to LeftMargins
            _foldingManager = FoldingManager.Install(TextEditor.TextArea);
            _foldingStrategy = new CalcpadFoldingStrategy();

            // CRITICAL: Force add FoldingMargin to ensure it's always visible
            // Remove any existing folding margin first
            var existingMargins = TextEditor.TextArea.LeftMargins
                .OfType<ICSharpCode.AvalonEdit.Folding.FoldingMargin>()
                .ToList();
            foreach (var margin in existingMargins)
                TextEditor.TextArea.LeftMargins.Remove(margin);

            // Add fresh FoldingMargin
            var foldingMargin = new ICSharpCode.AvalonEdit.Folding.FoldingMargin
            {
                FoldingMarkerBackgroundBrush = new System.Windows.Media.SolidColorBrush(
                    System.Windows.Media.Color.FromRgb(0xF0, 0xF0, 0xF0)),
                FoldingMarkerBrush = new System.Windows.Media.SolidColorBrush(
                    System.Windows.Media.Color.FromRgb(0x80, 0x80, 0x80))
            };

            if (_foldingManager != null)
                foldingMargin.FoldingManager = _foldingManager;

            TextEditor.TextArea.LeftMargins.Insert(0, foldingMargin);

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
            TextEditor.TextChanged += (s, e) =>
            {
                ScheduleFoldingUpdate();
                // Sync with MathEditor if in Visual mode
                SyncAvalonEditToMathEditor();

                // AutoRun support - same logic as RichTextBox_TextChanged
                if (_isTextChangedEnabled && IsAutoRun)
                {
                    _autoRun = true;
                }
            };

            // Install autocomplete for @{calcpad:}
            TextEditor.TextArea.TextEntering += TextEditor_TextEntering;
            TextEditor.TextArea.TextEntered += TextEditor_TextEntered;

            // AutoRun: trigger when caret position changes (equivalent to RichTextBox SelectionChanged)
            TextEditor.TextArea.Caret.PositionChanged += TextEditor_CaretPositionChanged;

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

        /// <summary>
        /// Sync AvalonEdit content to MathEditor when in Visual mode
        /// </summary>
        private void SyncAvalonEditToMathEditor()
        {
            if (_isSyncingBetweenModes) return;
            if (!_isTextChangedEnabled) return;
            if (_currentEditorMode != EditorMode.Visual) return;
            if (MathEditorControl == null || MathEditorControl.Visibility != Visibility.Visible) return;

            try
            {
                _isSyncingBetweenModes = true;
                string currentCode = TextEditor?.Text ?? string.Empty;
                MathEditorControl.FromCalcpad(currentCode);
            }
            finally
            {
                Dispatcher.InvokeAsync(
                    () => { _isSyncingBetweenModes = false; },
                    System.Windows.Threading.DispatcherPriority.Background);
            }
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

            // Get current context (html, css, ts, etc.)
            string context = GetCurrentBlockContext();

            if (context == "calcpad")
            {
                // Calcpad context - show @{calcpad:} autocomplete
                string wordBeforeCursor = GetWordBeforeCursor();
                if (wordBeforeCursor.Equals("Calcpad", StringComparison.OrdinalIgnoreCase))
                {
                    ShowCalcpadAutocomplete();
                }
            }
            else if (!string.IsNullOrEmpty(context))
            {
                // Inside external block (html, css, ts, etc.) - show snippets
                string wordBeforeCursor = GetWordBeforeCursor();
                if (wordBeforeCursor.Length >= 1) // Show after typing at least 1 char
                {
                    ShowSnippetAutocomplete(context, wordBeforeCursor);
                }
            }
        }

        /// <summary>
        /// Get current block context: "html", "css", "ts", "calcpad", or empty
        /// </summary>
        private string GetCurrentBlockContext()
        {
            if (TextEditor == null) return string.Empty;

            var textUpToCursor = TextEditor.Document.GetText(0, TextEditor.CaretOffset);
            var lines = textUpToCursor.Split('\n');

            // Track open blocks with stack
            var blockStack = new Stack<string>();

            foreach (var line in lines)
            {
                var trimmed = line.Trim();

                // Check for opening blocks
                if (trimmed.StartsWith("@{"))
                {
                    if (trimmed.StartsWith("@{end"))
                    {
                        // Closing block
                        if (blockStack.Count > 0)
                            blockStack.Pop();
                    }
                    else
                    {
                        // Opening block - extract language
                        int endIdx = trimmed.IndexOf('}');
                        if (endIdx > 2)
                        {
                            string lang = trimmed.Substring(2, endIdx - 2).Trim().ToLowerInvariant();
                            blockStack.Push(lang);
                        }
                    }
                }
            }

            // Return innermost block context
            return blockStack.Count > 0 ? blockStack.Peek() : "calcpad";
        }

        private bool IsInsideExternalBlock()
        {
            string context = GetCurrentBlockContext();
            return !string.IsNullOrEmpty(context) && context != "calcpad";
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
        /// Show snippet autocomplete for HTML/CSS/TS blocks
        /// </summary>
        private void ShowSnippetAutocomplete(string context, string filter)
        {
            if (TextEditor == null) return;

            // Get snippets for this context
            var snippets = HtmlSnippets.GetSnippetsForContext(context);
            if (snippets == null || snippets.Count == 0)
                return;

            // Filter snippets that start with the typed word
            var matchingSnippets = snippets.Values
                .Where(s => s.Trigger.StartsWith(filter, StringComparison.OrdinalIgnoreCase))
                .ToList();

            if (matchingSnippets.Count == 0)
                return;

            // Close existing completion window if open
            if (_completionWindow != null)
            {
                _completionWindow.Close();
            }

            // Create new completion window
            _completionWindow = new CompletionWindow(TextEditor.TextArea);
            var data = _completionWindow.CompletionList.CompletionData;

            // Add matching snippets
            foreach (var snippet in matchingSnippets)
            {
                data.Add(new SnippetCompletionData(snippet));
            }

            if (data.Count > 0)
            {
                _completionWindow.Show();
                _completionWindow.Closed += delegate {
                    _completionWindow = null;
                };
            }
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

        /// <summary>
        /// Handle caret position changes to trigger AutoRun (equivalent to RichTextBox SelectionChanged)
        /// </summary>
        private async void TextEditor_CaretPositionChanged(object? sender, EventArgs e)
        {
            if (!_autoRun || !IsAutoRun)
                return;

            // Check if we're at the end of the document
            if (TextEditor == null) return;

            int caretOffset = TextEditor.CaretOffset;
            int docLength = TextEditor.Document.TextLength;
            bool isNearEnd = (docLength - caretOffset) <= 2;

            // Execute AutoRun
            await AutoRun(isNearEnd);
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

    /// <summary>
    /// Completion data for HTML/CSS/TS snippets with preview
    /// </summary>
    public class SnippetCompletionData : ICompletionData
    {
        private readonly HtmlSnippet _snippet;

        public SnippetCompletionData(HtmlSnippet snippet)
        {
            _snippet = snippet;
            Text = snippet.Trigger;
        }

        public System.Windows.Media.ImageSource? Image => null;

        public string Text { get; private set; }

        public object Content => Text;

        // Show full template as description (preview)
        public object Description => _snippet.Description + "\n\n" + _snippet.Template;

        public double Priority => 1.0;

        public void Complete(TextArea textArea, ISegment completionSegment, EventArgs insertionRequestEventArgs)
        {
            // Replace trigger word with full template
            textArea.Document.Replace(completionSegment, _snippet.Template);

            // Move cursor to specified position
            int cursorPosition = completionSegment.Offset + _snippet.Template.Length + _snippet.CursorOffset;
            if (cursorPosition >= 0 && cursorPosition <= textArea.Document.TextLength)
            {
                textArea.Caret.Offset = cursorPosition;
            }
        }
    }
}
