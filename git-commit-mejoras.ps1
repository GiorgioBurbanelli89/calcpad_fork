# Script PowerShell para hacer commit de todas las mejoras de UI
# Fecha: 2026-01-21

Write-Host "=== Preparando commit de mejoras de UI ===" -ForegroundColor Cyan
Write-Host ""

# Crear branch
Write-Host "1. Creando branch feature/ui-improvements-2026..." -ForegroundColor Yellow
git checkout -b feature/ui-improvements-2026

# Agregar archivos nuevos importantes
Write-Host "2. Agregando archivos nuevos..." -ForegroundColor Yellow
git add Calcpad.Wpf/HtmlSnippets.cs
git add Calcpad.Wpf/MathEditor/MathExternalBlock.cs
git add test_snippets.cpd
git add test_folding.cpd
git add RESUMEN_SNIPPETS_Y_FOLDING.md
git add RESUMEN_FINAL_COMPLETO.md

# Agregar archivos modificados
Write-Host "3. Agregando archivos modificados..." -ForegroundColor Yellow
git add Calcpad.Wpf/MainWindow.AvalonEdit.cs
git add Calcpad.Wpf/MathEditor/MathEditorControl.xaml
git add Calcpad.Wpf/MathEditor/MathEditorControl.xaml.cs

# Ver estado antes de commit
Write-Host ""
Write-Host "=== Archivos a commitear ===" -ForegroundColor Cyan
git status --short

Write-Host ""
$respuesta = Read-Host "¿Continuar con el commit? (s/n)"

if ($respuesta -eq "s" -or $respuesta -eq "S") {
    Write-Host ""
    Write-Host "4. Haciendo commit..." -ForegroundColor Yellow
    git commit -m "Add snippets, code folding, and MathEditor external blocks

- Implement HTML/CSS/TS snippets with Emmet-style autocomplete (23 snippets)
- Force FoldingMargin visibility in AvalonEdit with custom colors
- Add MathExternalBlock class for collapsible external code blocks in MathEditor
- Replace PreviewTextBlock with AvalonEdit for syntax highlighting in preview
- Support click to toggle collapse/expand in external blocks
- Add language-specific colors (HTML=orange, CSS=blue, C=gray, Fortran=purple)
- Create test files: test_snippets.cpd, test_folding.cpd
- Complete documentation in Spanish

Files added:
- Calcpad.Wpf/HtmlSnippets.cs (23 snippets for HTML/CSS/TS)
- Calcpad.Wpf/MathEditor/MathExternalBlock.cs (visual element for external blocks)
- test_snippets.cpd (test file for snippets)
- test_folding.cpd (test file for code folding)
- RESUMEN_SNIPPETS_Y_FOLDING.md (snippets and folding documentation)
- RESUMEN_FINAL_COMPLETO.md (complete summary)

Files modified:
- Calcpad.Wpf/MainWindow.AvalonEdit.cs (snippets logic, forced FoldingMargin)
- Calcpad.Wpf/MathEditor/MathEditorControl.xaml (AvalonEdit preview container)
- Calcpad.Wpf/MathEditor/MathEditorControl.xaml.cs (external block detection, preview with AvalonEdit)

Co-authored-by: Claude Sonnet 4.5 <noreply@anthropic.com>"

    Write-Host ""
    Write-Host "✅ Commit completado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "5. Para hacer push al remote, ejecuta:" -ForegroundColor Cyan
    Write-Host "   git push origin feature/ui-improvements-2026" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Después de revisar, merge a master con:" -ForegroundColor Cyan
    Write-Host "   git checkout master" -ForegroundColor White
    Write-Host "   git merge feature/ui-improvements-2026" -ForegroundColor White
    Write-Host "   git push origin master" -ForegroundColor White
} else {
    Write-Host "Commit cancelado." -ForegroundColor Red
}
