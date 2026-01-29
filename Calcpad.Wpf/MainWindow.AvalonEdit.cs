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

                // Sync @{code}/@{ucode} with their closing tags
                SyncAllCodeUcodeClosingTags();

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

            // Sync @{code}/@{ucode} closing tags when user types '}'
            if (e.Text == "}")
            {
                SyncCodeUcodeClosingTags();
            }

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
        /// Synchronize @{code}/@{ucode} opening tags with their closing tags when user types '}'.
        /// </summary>
        private void SyncCodeUcodeClosingTags()
        {
            if (TextEditor == null) return;

            try
            {
                string text = TextEditor.Text;
                int caretPos = TextEditor.CaretOffset;

                // Check if cursor is just after @{code} or @{ucode}
                string textBeforeCursor = text.Substring(0, Math.Min(caretPos, text.Length));

                // Look for @{code} or @{ucode} ending at cursor position
                bool justTypedCode = textBeforeCursor.EndsWith("@{code}", StringComparison.OrdinalIgnoreCase);
                bool justTypedUcode = textBeforeCursor.EndsWith("@{ucode}", StringComparison.OrdinalIgnoreCase);

                if (!justTypedCode && !justTypedUcode)
                    return;

                string expectedClosing = justTypedCode ? "@{end code}" : "@{end ucode}";
                string wrongClosing = justTypedCode ? "@{end ucode}" : "@{end code}";

                // Find the corresponding closing tag after cursor
                string textAfterCursor = text.Substring(caretPos);

                // Look for the wrong closing tag and replace it
                int wrongClosingIdx = textAfterCursor.IndexOf(wrongClosing, StringComparison.OrdinalIgnoreCase);

                if (wrongClosingIdx >= 0)
                {
                    // Found wrong closing tag - replace it
                    int absolutePosition = caretPos + wrongClosingIdx;

                    // Disable text change events temporarily
                    _isTextChangedEnabled = false;

                    TextEditor.Document.Replace(absolutePosition, wrongClosing.Length, expectedClosing);

                    _isTextChangedEnabled = true;
                }
            }
            catch
            {
                // Ignore errors in sync logic
            }
        }

        // Flag to prevent recursive sync
        private bool _isSyncingCodeUcodeTags = false;

        /// <summary>
        /// Synchronize @{code}/@{ucode} tags and convert content between formats.
        /// When user changes @{code} to @{ucode}: convert HTML to directives
        /// When user changes @{ucode} to @{code}: convert directives to HTML
        /// </summary>
        private void SyncAllCodeUcodeClosingTags()
        {
            if (TextEditor == null) return;
            if (_isSyncingCodeUcodeTags) return;

            try
            {
                string text = TextEditor.Text;
                if (string.IsNullOrEmpty(text)) return;

                // Check for @{ucode} with @{end code} (user changed from @{code} to @{ucode})
                // This means we need to convert HTML content to directives
                if (text.Contains("@{ucode}", StringComparison.OrdinalIgnoreCase) &&
                    text.Contains("@{end code}", StringComparison.OrdinalIgnoreCase))
                {
                    ConvertCodeToUcode();
                    return;
                }

                // Check for @{code} with @{end ucode} (user changed from @{ucode} to @{code})
                // This means we need to convert directives to HTML
                if (text.Contains("@{code}", StringComparison.OrdinalIgnoreCase) &&
                    !text.Contains("@{ucode}", StringComparison.OrdinalIgnoreCase) &&
                    text.Contains("@{end ucode}", StringComparison.OrdinalIgnoreCase))
                {
                    ConvertUcodeToCode();
                    return;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"SyncAllCodeUcodeClosingTags error: {ex.Message}");
                _isSyncingCodeUcodeTags = false;
            }
        }

        /// <summary>
        /// Convert from @{code} format (HTML) to @{ucode} format (directives)
        /// </summary>
        private void ConvertCodeToUcode()
        {
            if (TextEditor == null) return;
            _isSyncingCodeUcodeTags = true;

            try
            {
                string text = TextEditor.Text;

                // Find the content between @{ucode} and @{end code}
                int ucodeStart = text.IndexOf("@{ucode}", StringComparison.OrdinalIgnoreCase);
                int endCodeStart = text.IndexOf("@{end code}", StringComparison.OrdinalIgnoreCase);

                if (ucodeStart < 0 || endCodeStart < 0 || endCodeStart <= ucodeStart) return;

                // Check if there's @{html-ifc} inside
                int htmlIfcStart = text.IndexOf("@{html-ifc}", StringComparison.OrdinalIgnoreCase);
                int htmlIfcEnd = text.IndexOf("@{end html-ifc}", StringComparison.OrdinalIgnoreCase);

                string newContent;
                if (htmlIfcStart >= 0 && htmlIfcEnd >= 0 && htmlIfcStart > ucodeStart && htmlIfcEnd < endCodeStart)
                {
                    // Extract content between @{html-ifc} and @{end html-ifc}
                    int contentStart = htmlIfcStart + "@{html-ifc}".Length;
                    string htmlContent = text.Substring(contentStart, htmlIfcEnd - contentStart).Trim();

                    // Convert HTML to directives
                    string directives = ExtractDirectivesFromHtml(htmlContent);

                    // Build new content with directives
                    newContent = $"@{{ucode}}\r\n@{{html-ifc}}\r\n{directives}\r\n@{{end html-ifc}}\r\n@{{end ucode}}";
                }
                else
                {
                    // No @{html-ifc}, just fix the closing tag
                    int contentStart = ucodeStart + "@{ucode}".Length;
                    string innerContent = text.Substring(contentStart, endCodeStart - contentStart);
                    newContent = $"@{{ucode}}{innerContent}@{{end ucode}}";
                }

                // Replace entire block
                int blockEnd = endCodeStart + "@{end code}".Length;
                TextEditor.Document.Replace(ucodeStart, blockEnd - ucodeStart, newContent);
            }
            finally
            {
                _isSyncingCodeUcodeTags = false;
            }
        }

        /// <summary>
        /// Convert from @{ucode} format (directives) to @{code} format (HTML)
        /// </summary>
        private void ConvertUcodeToCode()
        {
            if (TextEditor == null) return;
            _isSyncingCodeUcodeTags = true;

            try
            {
                string text = TextEditor.Text;

                // Find the content between @{code} and @{end ucode}
                int codeStart = text.IndexOf("@{code}", StringComparison.OrdinalIgnoreCase);
                int endUcodeStart = text.IndexOf("@{end ucode}", StringComparison.OrdinalIgnoreCase);

                if (codeStart < 0 || endUcodeStart < 0 || endUcodeStart <= codeStart) return;

                // Check if there's @{html-ifc} inside
                int htmlIfcStart = text.IndexOf("@{html-ifc}", StringComparison.OrdinalIgnoreCase);
                int htmlIfcEnd = text.IndexOf("@{end html-ifc}", StringComparison.OrdinalIgnoreCase);

                string newContent;
                if (htmlIfcStart >= 0 && htmlIfcEnd >= 0 && htmlIfcStart > codeStart && htmlIfcEnd < endUcodeStart)
                {
                    // Extract directives between @{html-ifc} and @{end html-ifc}
                    int contentStart = htmlIfcStart + "@{html-ifc}".Length;
                    string directivesContent = text.Substring(contentStart, htmlIfcEnd - contentStart).Trim();

                    // Convert directives to HTML
                    string htmlContent = Calcpad.Common.MultLangCode.IfcLanguageHandler.ConvertDirectivesToHtml(directivesContent);

                    // Build new content with HTML
                    newContent = $"@{{code}}\r\n@{{html-ifc}}\r\n{htmlContent}\r\n@{{end html-ifc}}\r\n@{{end code}}";
                }
                else
                {
                    // No @{html-ifc}, just fix the closing tag
                    int contentStart = codeStart + "@{code}".Length;
                    string innerContent = text.Substring(contentStart, endUcodeStart - contentStart);
                    newContent = $"@{{code}}{innerContent}@{{end code}}";
                }

                // Replace entire block
                int blockEnd = endUcodeStart + "@{end ucode}".Length;
                TextEditor.Document.Replace(codeStart, blockEnd - codeStart, newContent);
            }
            finally
            {
                _isSyncingCodeUcodeTags = false;
            }
        }

        /// <summary>
        /// Extract simplified directives from HTML content
        /// </summary>
        private string ExtractDirectivesFromHtml(string html)
        {
            var sb = new System.Text.StringBuilder();

            // Extract background color
            var bgMatch = System.Text.RegularExpressions.Regex.Match(html, @"background:\s*([#\w]+)", System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            string fondo = bgMatch.Success ? bgMatch.Groups[1].Value : "#1e1e1e";
            sb.AppendLine($"@{{fondo: {fondo}}}");

            // Extract height
            var heightMatch = System.Text.RegularExpressions.Regex.Match(html, @"height:\s*(\d+)px", System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            string altura = heightMatch.Success ? heightMatch.Groups[1].Value : "600";
            sb.AppendLine($"@{{altura: {altura}}}");

            // Extract IFC file URL
            var ifcMatch = System.Text.RegularExpressions.Regex.Match(html, @"https://calcpad\.ifc/([^'""\s<>]+\.ifc)", System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            if (ifcMatch.Success)
            {
                sb.AppendLine($"@{{visor: https://calcpad.ifc/{ifcMatch.Groups[1].Value}}}");
            }

            return sb.ToString().TrimEnd();
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

            // Ctrl+V - Check if pasting an image
            var modifiers = e.KeyboardDevice.Modifiers;
            var isCtrl = modifiers == ModifierKeys.Control;
            var isCtrlShift = modifiers == (ModifierKeys.Control | ModifierKeys.Shift);

            if (e.Key == Key.V && isCtrl && !isCtrlShift)
            {
                if (System.Windows.Clipboard.ContainsImage())
                {
                    // Image in clipboard - show paste dialog
                    e.Handled = true;
                    Dispatcher.InvokeAsync(() => PasteImage(null), System.Windows.Threading.DispatcherPriority.ApplicationIdle);
                    return;
                }
                // Text paste - let AvalonEdit handle it normally
            }

            // Ctrl+Q - Comment line(s)
            if (e.Key == Key.Q && isCtrl && !isCtrlShift)
            {
                CommentUncomment(true);
                e.Handled = true;
                return;
            }

            // Ctrl+Shift+Q - Uncomment line(s)
            if (e.Key == Key.Q && isCtrlShift)
            {
                CommentUncomment(false);
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

        // ========== TOOLTIP/HOVER HELP SYSTEM ==========
        private System.Windows.Controls.ToolTip? _editorToolTip;

        /// <summary>
        /// Show tooltip when mouse hovers over code elements
        /// </summary>
        private void TextEditor_MouseHover(object sender, MouseEventArgs e)
        {
            if (TextEditor == null) return;

            var position = TextEditor.GetPositionFromPoint(e.GetPosition(TextEditor));
            if (position == null) return;

            int offset = TextEditor.Document.GetOffset(position.Value.Line, position.Value.Column);
            string text = TextEditor.Text;

            // Get the current line
            var line = TextEditor.Document.GetLineByOffset(offset);
            string lineText = TextEditor.Document.GetText(line.Offset, line.Length);

            // Find tooltip for the current position
            string? tooltip = GetTooltipForPosition(lineText, text, offset, line.Offset);

            if (!string.IsNullOrEmpty(tooltip))
            {
                if (_editorToolTip == null)
                {
                    _editorToolTip = new System.Windows.Controls.ToolTip();
                }
                _editorToolTip.Content = tooltip;
                _editorToolTip.IsOpen = true;
                e.Handled = true;
            }
        }

        /// <summary>
        /// Hide tooltip when mouse stops hovering
        /// </summary>
        private void TextEditor_MouseHoverStopped(object sender, MouseEventArgs e)
        {
            if (_editorToolTip != null)
            {
                _editorToolTip.IsOpen = false;
            }
        }

        /// <summary>
        /// Get tooltip text based on cursor position and line content
        /// </summary>
        private string? GetTooltipForPosition(string lineText, string fullText, int offset, int lineOffset)
        {
            string trimmedLine = lineText.Trim();

            // ===== DIRECTIVAS @{} =====
            if (trimmedLine.StartsWith("@{html-ifc}"))
                return "📦 VISOR IFC 3D\n\nPermite mostrar modelos IFC en 3D.\nEl contenido puede ser:\n• HTML/JS directo\n• @{ucode}...@{end ucode} con directivas simplificadas\n• Ruta a un archivo .ifc\n\nEjecuta con F5 para ver el modelo.";

            if (trimmedLine.StartsWith("@{end html-ifc}"))
                return "🔚 FIN DEL BLOQUE IFC\n\nCierra el bloque @{html-ifc}";

            // ===== @{code} y @{ucode} =====
            if (trimmedLine.StartsWith("@{code}"))
                return "💻 MODO CÓDIGO\n\nHTML/JavaScript completo editable.\n\nEstructura:\n@{code}\n@{html-ifc}\n<!DOCTYPE html>...\n@{end html-ifc}\n@{end code}\n\nTip: Usa @{ucode} para directivas simplificadas";

            if (trimmedLine.StartsWith("@{end code}"))
                return "🔚 FIN DEL BLOQUE\n\nCierra @{code}";

            if (trimmedLine.StartsWith("@{ucode}"))
                return "✨ MODO SIMPLIFICADO\n\nUsa directivas fáciles sin escribir código.\n\nDirectivas disponibles:\n• @{fondo: #1e1e1e}\n• @{altura: 600}\n• @{visor: archivo.ifc}\n\nEstructura:\n@{ucode}\n@{html-ifc}\n@{fondo: #1e1e1e}\n@{end html-ifc}\n@{end ucode}";

            if (trimmedLine.StartsWith("@{end ucode}"))
                return "🔚 FIN DEL BLOQUE\n\nCierra @{ucode}";

            // ===== Directiva @{visor} =====
            if (trimmedLine.StartsWith("@{visor"))
                return "🖼️ CONFIGURACIÓN DEL VISOR\n\nParámetros:\n• fondo = Color de fondo (hex)\n  Ejemplos: #1a1a2e, #ffffff, #000000\n\n• altura = Altura en píxeles\n  Ejemplos: 400, 500, 600, 800\n\n• archivo = Ruta al archivo IFC\n  Ejemplo: C:\\modelo.ifc";

            // ===== Directiva @{camara} =====
            if (trimmedLine.StartsWith("@{camara"))
                return "📷 CONFIGURACIÓN DE CÁMARA\n\nParámetros:\n• tipo = Tipo de cámara\n  Opciones: perspectiva, ortografica\n\n• pos = Posición X,Y,Z\n  Ejemplos:\n  50,50,50 (vista diagonal)\n  0,100,0 (vista superior)\n  0,0,100 (vista frontal)\n  100,0,0 (vista lateral)";

            // ===== Directiva @{controles} =====
            if (trimmedLine.StartsWith("@{controles"))
                return "🎮 CONTROLES DEL VISOR\n\nOpciones (separadas por coma):\n• vistas - Botones: 3D, Superior, Frontal, Lateral\n• zoom - Slider de zoom\n• rotacion - Slider de rotación\n• color - Selector de color de fondo\n\nEjemplo:\n@{controles: vistas, zoom, color}";

            // ===== Parámetros individuales =====
            if (trimmedLine.Contains("fondo=") || trimmedLine.Contains("fondo ="))
                return "🎨 COLOR DE FONDO\n\nFormato: #RRGGBB (hexadecimal)\n\nEjemplos:\n• #1a1a2e - Azul oscuro (default)\n• #ffffff - Blanco\n• #000000 - Negro\n• #2d2d44 - Gris azulado\n• #1e1e1e - Gris oscuro\n• #87ceeb - Azul cielo\n• #2e8b57 - Verde mar\n\n💡 Usa un selector de color online\npara encontrar más colores.";

            if (trimmedLine.Contains("altura=") || trimmedLine.Contains("altura ="))
                return "📏 ALTURA DEL VISOR\n\nValor en píxeles.\n\nEjemplos:\n• 400 - Pequeño\n• 500 - Mediano\n• 600 - Standard (default)\n• 800 - Grande\n• 100vh - Pantalla completa";

            if (trimmedLine.Contains("pos=") || trimmedLine.Contains("pos ="))
                return "📍 POSICIÓN DE CÁMARA\n\nFormato: X,Y,Z (coordenadas)\n\nEjemplos:\n• 50,50,50 - Vista diagonal (default)\n• 0,100,0 - Vista superior (planta)\n• 0,0,100 - Vista frontal (elevación)\n• 100,0,0 - Vista lateral (corte)\n• 0,50,100 - Vista frontal elevada\n\n💡 Y es la altura (arriba/abajo)\nX y Z son horizontal.";

            if (trimmedLine.Contains("tipo=") || trimmedLine.Contains("tipo ="))
                return "📷 TIPO DE CÁMARA\n\nOpciones:\n• perspectiva - Vista realista con\n  profundidad (objetos lejanos más pequeños)\n\n• ortografica - Vista técnica sin\n  perspectiva (para planos y dibujos)";

            if (trimmedLine.Contains("archivo=") || trimmedLine.Contains("archivo ="))
                return "📁 ARCHIVO IFC\n\nRuta completa al archivo .ifc\n\nEjemplos:\n• C:\\Users\\nombre\\modelo.ifc\n• C:\\Proyectos\\edificio.ifc\n\n💡 Arrastra un archivo IFC\nal editor para obtener la ruta.";

            if (trimmedLine.StartsWith("@{ifc-create}"))
                return "🏗️ CREAR GEOMETRÍA IFC\n\nPermite crear elementos IFC programáticamente.\nUsa comandos como:\n• BEAM x1,y1,z1 -> x2,y2,z2\n• COLUMN x,y,z height\n• SLAB points...";

            if (trimmedLine.StartsWith("@{html}"))
                return "🌐 BLOQUE HTML\n\nInserta HTML directo en la salida.\nNota: Usa NavigateToString (file:// origin)";

            if (trimmedLine.StartsWith("@{python}"))
                return "🐍 CÓDIGO PYTHON\n\nEjecuta código Python.\nRequiere Python instalado en el sistema.";

            if (trimmedLine.StartsWith("@{markdown}") || trimmedLine.StartsWith("@{md}"))
                return "📝 MARKDOWN\n\nFormatea texto usando Markdown.\nSoporta: **negrita**, *cursiva*, listas, etc.";

            // ===== COMENTARIOS HTML CON AYUDA =====
            // Colores de fondo
            if (lineText.Contains("COLOR DE FONDO DE LA PAGINA"))
                return "🎨 COLOR DE FONDO\n\nCambia el color de fondo de toda la página.\nEjemplos:\n• #1e1e1e (gris oscuro)\n• #ffffff (blanco)\n• #000000 (negro)";

            if (lineText.Contains("COLOR DE FONDO DE LA ESCENA 3D"))
                return "🎨 COLOR DE ESCENA 3D\n\nCambia el fondo del visor 3D.\nUsa formato hex: 0xRRGGBB\nEjemplos:\n• 0x1e1e1e (gris oscuro)\n• 0xffffff (blanco)\n• 0x87ceeb (azul cielo)";

            if (lineText.Contains("scene.background"))
                return "🎨 FONDO DE ESCENA\n\nThree.js Color para el fondo 3D.\nnew THREE.Color(0xRRGGBB)\n\nCambia 0x1e1e1e por otro color.";

            // Iluminación
            if (lineText.Contains("LUZ AMBIENTAL"))
                return "💡 LUZ AMBIENTAL\n\nIlumina todo uniformemente.\nAmbientLight(color, intensidad)\n• color: 0xffffff (blanco)\n• intensidad: 0.0 a 1.0";

            if (lineText.Contains("LUZ DIRECCIONAL"))
                return "☀️ LUZ DIRECCIONAL\n\nComo el sol, crea sombras.\nDirectionalLight(color, intensidad)\nPosición: dirLight.position.set(x, y, z)";

            if (lineText.Contains("AmbientLight"))
                return "💡 THREE.AmbientLight\n\nLuz que ilumina todo por igual.\nParámetros: (color, intensidad)\n• intensidad 0.5 = 50%";

            if (lineText.Contains("DirectionalLight"))
                return "☀️ THREE.DirectionalLight\n\nLuz direccional (como el sol).\nParámetros: (color, intensidad)\nUsa .position.set(x,y,z) para orientarla.";

            // Grid
            if (lineText.Contains("GRID") || lineText.Contains("CUADRICULA"))
                return "📐 CUADRÍCULA (GRID)\n\nMuestra una cuadrícula en el suelo.\nGridHelper(tamaño, divisiones, colorPrincipal, colorSecundario)\n\nPara quitar: comenta o elimina estas líneas.";

            if (lineText.Contains("GridHelper"))
                return "📐 THREE.GridHelper\n\nCrea una cuadrícula.\nParámetros:\n• tamaño: 100\n• divisiones: 100\n• colorLineasPrincipales: 0x444444\n• colorLineasSecundarias: 0x333333";

            // Material y colores
            if (lineText.Contains("MATERIAL Y COLOR"))
                return "🎨 MATERIAL DE ELEMENTOS\n\nControla cómo se ven los objetos 3D.\nPuedes cambiar:\n• color: Color del objeto\n• wireframe: Ver solo líneas\n• shininess: Brillo (0-100)";

            if (lineText.Contains("MeshPhongMaterial"))
                return "🎨 THREE.MeshPhongMaterial\n\nMaterial con iluminación Phong.\nOpciones:\n• color: color base\n• wireframe: true/false\n• flatShading: true/false\n• shininess: 0-100\n• transparent/opacity";

            if (lineText.Contains("wireframe: true"))
                return "🔲 MODO WIREFRAME\n\nMuestra solo las líneas/aristas.\nDescomenta para activar.";

            // Cámara
            if (lineText.Contains("CONFIGURACION DE CAMARA") || lineText.Contains("PerspectiveCamera"))
                return "📷 CÁMARA\n\nPerspectiveCamera(fov, aspect, near, far)\n• fov: ángulo de visión (75°)\n• near: distancia mínima (0.1)\n• far: distancia máxima (10000)";

            if (lineText.Contains("camera.position.set"))
                return "📷 POSICIÓN DE CÁMARA\n\ncamera.position.set(x, y, z)\nCoordenadas donde se ubica la cámara.";

            // Controles
            if (lineText.Contains("OrbitControls"))
                return "🎮 CONTROLES DE ÓRBITA\n\nPermite rotar, hacer zoom y pan.\n• Click + arrastrar: Rotar\n• Scroll: Zoom\n• Click derecho + arrastrar: Pan";

            if (lineText.Contains("enableDamping"))
                return "🎮 SUAVIZADO\n\nenableDamping: Activa suavizado de movimiento.\ndampingFactor: Intensidad (0.05 = suave)";

            // Spinner y progreso
            if (lineText.Contains("COLOR DEL SPINNER"))
                return "🔄 COLOR DEL SPINNER\n\nCambia border-top-color para cambiar\nel color del indicador de carga.\nEjemplo: #0078d4 (azul)";

            if (lineText.Contains("COLOR DE LA BARRA DE PROGRESO"))
                return "📊 BARRA DE PROGRESO\n\nCambia background para cambiar\nel color de la barra de carga.\nEjemplo: #0078d4 (azul)";

            // Teclas
            if (lineText.Contains("TECLA F") || lineText.Contains("Fit to view"))
                return "⌨️ TECLA F\n\nPresiona F para centrar la vista\nen el modelo (Fit to View).";

            // Eventos
            if (lineText.Contains("LOOP DE ANIMACION") || lineText.Contains("requestAnimationFrame"))
                return "🔄 LOOP DE ANIMACIÓN\n\nSe ejecuta ~60 veces por segundo.\nActualiza controles y renderiza la escena.";

            if (lineText.Contains("resize"))
                return "📐 EVENTO RESIZE\n\nAjusta la cámara y el renderer\ncuando cambia el tamaño de la ventana.";

            // Scripts
            if (lineText.Contains("three.min.js"))
                return "📦 THREE.JS\n\nBiblioteca de gráficos 3D.\nVersión incluida localmente.";

            if (lineText.Contains("OrbitControls.js"))
                return "📦 ORBIT CONTROLS\n\nExtensión de Three.js para\ncontroles de cámara interactivos.";

            if (lineText.Contains("web-ifc"))
                return "📦 WEB-IFC\n\nBiblioteca para parsear archivos IFC.\nIncluye archivo WASM para rendimiento.";

            // Calcpad específico
            if (trimmedLine.StartsWith("#if"))
                return "🔀 CONDICIONAL\n\nEjecuta código si la condición es verdadera.\n#if condición\n  código\n#else\n  alternativa\n#end if";

            if (trimmedLine.StartsWith("#for"))
                return "🔁 BUCLE FOR\n\nRepite código N veces.\n#for i = inicio : fin\n  código con $i\n#next";

            if (trimmedLine.StartsWith("#while"))
                return "🔁 BUCLE WHILE\n\nRepite mientras condición sea verdadera.\n#while condición\n  código\n#loop";

            return null;
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
                // Stack for JavaScript/TypeScript blocks with braces: if, for, while, function, etc.
                var jsBraceStack = new Stack<(int line, string type)>();

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

                    // JavaScript/TypeScript blocks: if, for, while, function, try, catch, else, switch, class
                    // Detect opening brace at end of line: "if (...) {" or "function foo() {"
                    if (lineText.TrimEnd().EndsWith("{"))
                    {
                        string blockType = null;
                        var trimmed = lineText.TrimStart();

                        // Check for common JS block patterns
                        if (trimmed.StartsWith("if ") || trimmed.StartsWith("if("))
                            blockType = "if";
                        else if (trimmed.StartsWith("else if ") || trimmed.StartsWith("else if("))
                            blockType = "else if";
                        else if (trimmed.StartsWith("else ") || trimmed.StartsWith("else{") || trimmed == "else {")
                            blockType = "else";
                        else if (trimmed.StartsWith("for ") || trimmed.StartsWith("for("))
                            blockType = "for";
                        else if (trimmed.StartsWith("while ") || trimmed.StartsWith("while("))
                            blockType = "while";
                        else if (trimmed.StartsWith("function ") || trimmed.StartsWith("function("))
                            blockType = "function";
                        else if (trimmed.StartsWith("async function"))
                            blockType = "async function";
                        else if (trimmed.Contains("=> {"))
                            blockType = "arrow function";
                        else if (trimmed.StartsWith("try ") || trimmed.StartsWith("try{") || trimmed == "try {")
                            blockType = "try";
                        else if (trimmed.StartsWith("catch ") || trimmed.StartsWith("catch("))
                            blockType = "catch";
                        else if (trimmed.StartsWith("finally ") || trimmed.StartsWith("finally{") || trimmed == "finally {")
                            blockType = "finally";
                        else if (trimmed.StartsWith("switch ") || trimmed.StartsWith("switch("))
                            blockType = "switch";
                        else if (trimmed.StartsWith("class "))
                            blockType = "class";
                        else if (trimmed.StartsWith("constructor(") || trimmed.StartsWith("constructor ("))
                            blockType = "constructor";
                        else if (trimmed.StartsWith("do ") || trimmed.StartsWith("do{") || trimmed == "do {")
                            blockType = "do";
                        // Method definitions in objects/classes
                        else if (System.Text.RegularExpressions.Regex.IsMatch(trimmed, @"^\w+\s*\([^)]*\)\s*\{"))
                            blockType = "method";

                        if (blockType != null)
                        {
                            jsBraceStack.Push((lineNumber, blockType));
                        }
                    }
                    // Detect closing brace on its own line or with minimal content
                    else if (lineText.Trim() == "}" || lineText.Trim() == "};" ||
                             lineText.Trim() == "});" || lineText.Trim() == "})," ||
                             lineText.Trim().StartsWith("} else") ||
                             lineText.Trim().StartsWith("} catch") ||
                             lineText.Trim().StartsWith("} finally"))
                    {
                        if (jsBraceStack.Count > 0)
                        {
                            var (startLine, blockType) = jsBraceStack.Pop();
                            var startDocLine = document.GetLineByNumber(startLine);
                            foldings.Add(new NewFolding
                            {
                                StartOffset = startDocLine.Offset,
                                EndOffset = documentLine.EndOffset,
                                Name = $"▼ {blockType} {{...}}"
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
