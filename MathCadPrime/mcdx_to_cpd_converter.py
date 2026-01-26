#!/usr/bin/env python3
"""
Convertidor avanzado de archivos .mcdx (MathCad Prime) a .cpd (Calcpad)
Soporta: ecuaciones, variables con unidades, gráficas, solve blocks, etc.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import base64

# Namespaces de MathCad Prime
NS = {
    'ws': 'http://schemas.mathsoft.com/worksheet50',
    'ml': 'http://schemas.mathsoft.com/math50',
    'u': 'http://schemas.mathsoft.com/units10',
    'p': 'http://schemas.mathsoft.com/provenance10'
}

class McdxToCalcpadConverter:
    """Convertidor de .mcdx a .cpd"""

    def __init__(self):
        self.output = []
        self.warnings = []
        self.variables = {}  # Variable definitions
        self.images = {}     # Image data

    def convert(self, mcdx_path, output_path=None):
        """Convierte .mcdx a .cpd"""

        mcdx_file = Path(mcdx_path)
        if not mcdx_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {mcdx_path}")

        # Resetear estado
        self.output = []
        self.warnings = []
        self.variables = {}
        self.images = {}

        # Header
        self.output.append("' " + "="*60)
        self.output.append(f"' Convertido de MathCad Prime: {mcdx_file.name}")
        self.output.append("' " + "="*60)
        self.output.append("")

        # Extraer y procesar
        with zipfile.ZipFile(mcdx_path, 'r') as zip_ref:
            # Leer worksheet.xml
            worksheet_xml = zip_ref.read('mathcad/worksheet.xml')
            root = ET.fromstring(worksheet_xml)

            # Extraer imágenes
            self._extract_images(zip_ref)

            # Procesar regiones
            regions = root.find('ws:regions', NS)
            if regions is not None:
                for region in regions.findall('ws:region', NS):
                    self._process_region(region)

        # Generar output
        cpd_content = "\n".join(self.output)

        # Guardar si se especificó ruta
        if output_path:
            output_file = Path(output_path)
            output_file.write_text(cpd_content, encoding='utf-8')
            print(f"Convertido: {mcdx_file.name} -> {output_file.name}")

        return cpd_content

    def _extract_images(self, zip_ref):
        """Extrae imágenes del archivo .mcdx"""
        try:
            # Buscar archivos PNG en mathcad/xaml/
            for file_name in zip_ref.namelist():
                if file_name.startswith('mathcad/xaml/') and file_name.endswith('.png'):
                    image_data = zip_ref.read(file_name)
                    image_id = Path(file_name).stem
                    self.images[image_id] = base64.b64encode(image_data).decode('ascii')
        except Exception as e:
            self.warnings.append(f"Error extrayendo imágenes: {e}")

    def _process_region(self, region):
        """Procesa una región del worksheet"""

        # Detectar tipo de región
        if region.find('ws:text', NS) is not None:
            self._process_text_region(region)

        elif region.find('ws:math', NS) is not None:
            self._process_math_region(region)

        elif region.find('ws:plot', NS) is not None:
            self._process_plot_region(region)

        elif region.find('ws:picture', NS) is not None:
            self._process_picture_region(region)

        elif region.find('ws:solveblock', NS) is not None:
            self._process_solveblock_region(region)

        elif region.find('ws:chartComponent', NS) is not None:
            self._process_chart_component(region)

    def _process_text_region(self, region):
        """Procesa una región de texto"""
        text_elem = region.find('ws:text', NS)

        # Extraer texto del FlowDocument (simplificado)
        # TODO: Parser completo de FlowDocument XAML
        text_content = self._extract_text_from_flowdocument(text_elem)

        if text_content and text_content.strip():
            # Agregar como comentario
            self.output.append(f"' {text_content.strip()}")
            self.output.append("")

    def _extract_text_from_flowdocument(self, text_elem):
        """Extrae texto de un FlowDocument XAML"""
        # Simplificado: solo obtener el texto plano
        text = ""
        for node in text_elem.iter():
            if node.text:
                text += node.text.strip() + " "
            if node.tail:
                text += node.tail.strip() + " "

        return text.strip()

    def _process_math_region(self, region):
        """Procesa una región matemática"""
        math_elem = region.find('ws:math', NS)

        # Buscar define (definición)
        define = math_elem.find('.//ml:define', NS)
        if define is not None:
            expr = self._convert_define(define)
            if expr:
                self.output.append(expr)
                return

        # Buscar eval (evaluación)
        eval_elem = math_elem.find('.//ml:eval', NS)
        if eval_elem is not None:
            expr = self._convert_eval(eval_elem)
            if expr:
                self.output.append(expr)
                return

        # Otras expresiones
        self.warnings.append("Expresión matemática no reconocida")

    def _convert_define(self, define):
        """Convierte una definición ml:define a sintaxis Calcpad"""

        # Obtener el ID (nombre de variable)
        id_elem = define.find('ml:id', NS)
        if id_elem is None:
            return None

        var_name = self._get_element_text(id_elem)
        var_name = self._clean_variable_name(var_name)

        # Obtener el valor
        value_expr = self._convert_expression(define, skip_first_id=True)

        if value_expr:
            # Guardar variable para referencia
            self.variables[var_name] = value_expr

            # Formato: variable = valor
            return f"{var_name} = {value_expr}"

        return None

    def _convert_eval(self, eval_elem):
        """Convierte una evaluación ml:eval"""
        expr = self._convert_expression(eval_elem)
        return f"' Resultado: {expr}" if expr else None

    def _convert_expression(self, elem, skip_first_id=False):
        """Convierte una expresión matemática ML a sintaxis Calcpad"""

        expressions = []
        id_count = 0

        for child in elem:
            tag = child.tag.replace('{' + NS['ml'] + '}', '')

            if tag == 'id':
                # Variable o función
                if skip_first_id and id_count == 0:
                    id_count += 1
                    continue

                var_name = self._get_element_text(child)
                var_name = self._clean_variable_name(var_name)
                expressions.append(var_name)

            elif tag == 'real':
                # Número real
                expressions.append(child.text.strip())

            elif tag == 'apply':
                # Aplicar operador
                op_expr = self._convert_apply(child)
                if op_expr:
                    expressions.append(op_expr)

            elif tag == 'matrix':
                # Matriz
                matrix_expr = self._convert_matrix(child)
                expressions.append(matrix_expr)

            elif tag == 'range':
                # Rango (secuencia)
                range_expr = self._convert_range(child)
                expressions.append(range_expr)

        return ' '.join(expressions) if expressions else None

    def _convert_apply(self, apply_elem):
        """Convierte ml:apply (operadores)"""

        # Obtener operador
        op_elem = apply_elem[0] if len(apply_elem) > 0 else None
        if op_elem is None:
            return None

        op_tag = op_elem.tag.replace('{' + NS['ml'] + '}', '')

        # Obtener operandos
        operands = [self._convert_expression(child) for child in apply_elem[1:]]
        operands = [op for op in operands if op]

        # Mapeo de operadores
        if op_tag == 'plus':
            return ' + '.join(operands)
        elif op_tag == 'minus':
            return f"({operands[0]} - {operands[1]})" if len(operands) == 2 else f"-{operands[0]}"
        elif op_tag == 'mult':
            return ' * '.join(f"({op})" for op in operands)
        elif op_tag == 'div':
            return f"({operands[0]}) / ({operands[1]})" if len(operands) == 2 else None
        elif op_tag == 'pow':
            return f"({operands[0]})^({operands[1]})" if len(operands) == 2 else None
        elif op_tag == 'scale':
            # Valor con unidad: valor * unidad
            if len(operands) == 2:
                return f"{operands[0]}*{operands[1]}"
            return operands[0] if operands else None
        elif op_tag == 'equal':
            # Igualdad (para solve blocks)
            return ' = '.join(operands)
        elif op_tag == 'functionDerivative':
            # Derivada d/dx
            if operands:
                return f"d({operands[0]})"
            return "d(?)"
        else:
            self.warnings.append(f"Operador no soportado: {op_tag}")
            return f"#{op_tag}#"

    def _convert_matrix(self, matrix_elem):
        """Convierte ml:matrix a sintaxis Calcpad"""

        rows = int(matrix_elem.get('rows', '1'))
        cols = int(matrix_elem.get('cols', '1'))

        # Extraer valores
        values = []
        for real in matrix_elem.findall('ml:real', NS):
            values.append(real.text.strip())

        # Formato de vector o matriz
        if rows == 1:
            # Vector fila
            return '[' + ', '.join(values) + ']'
        elif cols == 1:
            # Vector columna
            return '[' + ', '.join(values) + ']'
        else:
            # Matriz
            matrix_rows = []
            idx = 0
            for r in range(rows):
                row_values = values[idx:idx+cols]
                matrix_rows.append('[' + ', '.join(row_values) + ']')
                idx += cols
            return '[\n  ' + ';\n  '.join(matrix_rows) + '\n]'

    def _convert_range(self, range_elem):
        """Convierte ml:range (secuencia)"""

        # Buscar sequence
        sequence = range_elem.find('ml:sequence', NS)
        if sequence is not None:
            # start..step..end
            values = [self._convert_expression(child) for child in sequence]
            if len(values) == 2:
                return f"{values[0]}..{values[1]}"

        # Buscar end value
        end_value = [self._convert_expression(child) for child in range_elem if child.tag.endswith('apply')]
        if end_value:
            return f"..{end_value[0]}"

        return None

    def _process_plot_region(self, region):
        """Procesa una región de gráfica"""

        plot_elem = region.find('ws:plot', NS)
        xy_plot = plot_elem.find('.//ws:xyPlot', NS)

        if xy_plot is not None:
            # Extraer ejes
            x_var = None
            y_var = None

            axes = xy_plot.find('.//ws:axes', NS)
            if axes is not None:
                x_axis = axes.find('.//ws:xAxis', NS)
                y_axis = axes.find('.//ws:yAxis', NS)

                if x_axis is not None:
                    x_id = x_axis.find('.//ml:id', NS)
                    if x_id is not None:
                        x_var = self._get_element_text(x_id)

                if y_axis is not None:
                    y_id = y_axis.find('.//ml:id', NS)
                    if y_id is not None:
                        y_var = self._get_element_text(y_id)

            # Generar comentario de gráfica
            self.output.append("' ---- Gráfica ----")
            if x_var and y_var:
                self.output.append(f"' Plot: {y_var} vs {x_var}")
            self.output.append("' (Gráfica no implementada en Calcpad)")
            self.output.append("")

    def _process_picture_region(self, region):
        """Procesa una región de imagen"""

        picture_elem = region.find('ws:picture', NS)
        png_elem = picture_elem.find('.//ws:png', NS)

        if png_elem is not None:
            item_id = png_elem.get('item-idref')

            if item_id in self.images:
                # Generar directiva de imagen Base64
                self.output.append(f"#img:\"data:image/png;base64,{self.images[item_id]}\"")
                self.output.append("")
            else:
                self.output.append("' [Imagen no encontrada]")
                self.output.append("")

    def _process_solveblock_region(self, region):
        """Procesa un solve block (ecuaciones diferenciales, etc.)"""

        solveblock_elem = region.find('ws:solveblock', NS)
        regions = solveblock_elem.find('.//ws:regions', NS)

        if regions is not None:
            self.output.append("' ---- Solve Block ----")

            constraints = []
            solver = None

            for sub_region in regions.findall('ws:region', NS):
                category = sub_region.get('solve-block-category')

                if category == 'constraint':
                    # Ecuación o restricción
                    math_elem = sub_region.find('.//ws:math', NS)
                    if math_elem is not None:
                        expr = self._convert_expression(math_elem)
                        if expr:
                            constraints.append(expr)

                elif category == 'solver':
                    # Tipo de solver
                    math_elem = sub_region.find('.//ws:math', NS)
                    if math_elem is not None:
                        for keyword in math_elem.findall('.//ml:id[@labels="KEYWORD"]', NS):
                            solver = self._get_element_text(keyword)

            # Generar output
            for constraint in constraints:
                self.output.append(f"' Restricción: {constraint}")

            if solver:
                self.output.append(f"' Solver: {solver}")

            self.output.append("' (Solve blocks no implementados en Calcpad)")
            self.output.append("")

    def _process_chart_component(self, region):
        """Procesa un componente de gráfica (chart)"""
        self.output.append("' ---- Componente de Gráfica ----")
        self.output.append("' (Charts no implementados en Calcpad)")
        self.output.append("")

    def _get_element_text(self, elem):
        """Obtiene el texto completo de un elemento (incluyendo subscripts)"""
        text = elem.text or ''

        # Manejar subscripts/superscripts en Span elements
        for child in elem:
            if child.tail:
                # Extraer subscript
                if 'Subscript' in str(child.tag):
                    text += '_' + (child.text or '')
                elif 'Superscript' in str(child.tag):
                    text += '^' + (child.text or '')
                text += child.tail

        return text.strip()

    def _clean_variable_name(self, name):
        """Limpia el nombre de una variable"""
        # Eliminar espacios
        name = name.replace(' ', '')

        # Reemplazar caracteres especiales
        name = name.replace('′', '_prime')  # Prima

        return name

def main():
    """Convierte todos los archivos .mcdx en el directorio actual"""

    converter = McdxToCalcpadConverter()
    mcdx_dir = Path(__file__).parent

    mcdx_files = list(mcdx_dir.glob('*.mcdx'))

    if not mcdx_files:
        print("No se encontraron archivos .mcdx")
        return

    print(f"Encontrados {len(mcdx_files)} archivos .mcdx\n")
    print("="*80)

    for mcdx_file in sorted(mcdx_files):
        # Generar nombre de salida
        output_file = mcdx_file.with_suffix('.cpd')

        try:
            # Convertir
            cpd_content = converter.convert(str(mcdx_file), str(output_file))

            # Mostrar warnings
            if converter.warnings:
                print(f"\n  Advertencias en {mcdx_file.name}:")
                for warning in converter.warnings:
                    print(f"    - {warning}")

        except Exception as e:
            print(f"ERROR en {mcdx_file.name}: {e}")

    print("\n" + "="*80)
    print(f"\nConversion completada: {len(mcdx_files)} archivos procesados")

if __name__ == '__main__':
    main()
