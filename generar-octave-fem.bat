@echo off
REM Script para generar graficas FEM con Octave

set OUTPUT_DIR=C:\Users\j-b-j\AppData\Local\Temp
set OCTAVE_SCRIPT=%OUTPUT_DIR%\fem_octave_script.m

REM Crear script de Octave
echo %% Script FEM Octave > %OCTAVE_SCRIPT%
echo set(0, 'DefaultFigureVisible', 'off'); >> %OCTAVE_SCRIPT%
echo a = 6; >> %OCTAVE_SCRIPT%
echo b = 4; >> %OCTAVE_SCRIPT%
echo n_a = 6; >> %OCTAVE_SCRIPT%
echo n_b = 4; >> %OCTAVE_SCRIPT%
echo [X, Y] = meshgrid(linspace(0, a, n_a+1), linspace(0, b, n_b+1)); >> %OCTAVE_SCRIPT%
echo x_nodes = X(:); >> %OCTAVE_SCRIPT%
echo y_nodes = Y(:); >> %OCTAVE_SCRIPT%
echo elements = []; >> %OCTAVE_SCRIPT%
echo for i = 1:n_a >> %OCTAVE_SCRIPT%
echo     for j = 1:n_b >> %OCTAVE_SCRIPT%
echo         n1 = (i-1)*(n_b+1) + j; >> %OCTAVE_SCRIPT%
echo         elements = [elements; n1 n1+(n_b+1) n1+(n_b+1)+1 n1+1]; >> %OCTAVE_SCRIPT%
echo     end >> %OCTAVE_SCRIPT%
echo end >> %OCTAVE_SCRIPT%
echo h = figure(); >> %OCTAVE_SCRIPT%
echo hold on; >> %OCTAVE_SCRIPT%
echo for e = 1:size(elements, 1) >> %OCTAVE_SCRIPT%
echo     nodes = elements(e, :); >> %OCTAVE_SCRIPT%
echo     patch(x_nodes(nodes), y_nodes(nodes), [0.5 1 0.5]); >> %OCTAVE_SCRIPT%
echo end >> %OCTAVE_SCRIPT%
echo plot(x_nodes, y_nodes, 'ro'); >> %OCTAVE_SCRIPT%
echo axis equal; >> %OCTAVE_SCRIPT%
echo title('Mesh FEM - Octave'); >> %OCTAVE_SCRIPT%
echo output_file = '%OUTPUT_DIR%/fem_mesh_octave.png'; >> %OCTAVE_SCRIPT%
echo drawnow; >> %OCTAVE_SCRIPT%
echo print(h, output_file, '-dpng', '-r150'); >> %OCTAVE_SCRIPT%
echo close(h); >> %OCTAVE_SCRIPT%
echo fprintf('OK\n'); >> %OCTAVE_SCRIPT%

REM Ejecutar Octave
octave-cli --no-gui --quiet %OCTAVE_SCRIPT%

echo Imagen generada en: %OUTPUT_DIR%\fem_mesh_octave.png
