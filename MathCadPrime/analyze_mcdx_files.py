#!/usr/bin/env python3
"""
Analizador de archivos .mcdx de MathCad Prime
Extrae y analiza la estructura de regiones, ecuaciones, gráficas, etc.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import json

# Namespaces de MathCad Prime
NS = {
    'ws': 'http://schemas.mathsoft.com/worksheet50',
    'ml': 'http://schemas.mathsoft.com/math50',
    'u': 'http://schemas.mathsoft.com/units10',
    'p': 'http://schemas.mathsoft.com/provenance10'
}

def analyze_mcdx(mcdx_path):
    """Analiza un archivo .mcdx y retorna su estructura"""

    result = {
        'filename': Path(mcdx_path).name,
        'regions': [],
        'stats': {
            'text_regions': 0,
            'math_regions': 0,
            'plot_regions': 0,
            'picture_regions': 0,
            'solve_blocks': 0,
            'chart_components': 0
        }
    }

    with zipfile.ZipFile(mcdx_path, 'r') as zip_ref:
        # Leer worksheet.xml
        worksheet_xml = zip_ref.read('mathcad/worksheet.xml')
        root = ET.fromstring(worksheet_xml)

        # Analizar regiones
        regions_element = root.find('ws:regions', NS)
        if regions_element is None:
            return result

        for region in regions_element.findall('ws:region', NS):
            region_data = {
                'id': region.get('region-id'),
                'top': region.get('top'),
                'left': region.get('left'),
                'width': region.get('width'),
                'height': region.get('height'),
                'type': 'unknown',
                'content': None
            }

            # Detectar tipo de región
            if region.find('ws:text', NS) is not None:
                region_data['type'] = 'text'
                result['stats']['text_regions'] += 1

            elif region.find('ws:math', NS) is not None:
                region_data['type'] = 'math'
                result['stats']['math_regions'] += 1

                # Extraer contenido matemático
                math_elem = region.find('ws:math', NS)
                region_data['content'] = extract_math_content(math_elem)

            elif region.find('ws:plot', NS) is not None:
                region_data['type'] = 'plot'
                result['stats']['plot_regions'] += 1

                # Extraer info de gráfica
                plot_elem = region.find('ws:plot', NS)
                region_data['content'] = extract_plot_info(plot_elem)

            elif region.find('ws:picture', NS) is not None:
                region_data['type'] = 'picture'
                result['stats']['picture_regions'] += 1

            elif region.find('ws:solveblock', NS) is not None:
                region_data['type'] = 'solveblock'
                result['stats']['solve_blocks'] += 1

                # Extraer info del solve block
                solve_elem = region.find('ws:solveblock', NS)
                region_data['content'] = extract_solveblock_info(solve_elem)

            elif region.find('ws:chartComponent', NS) is not None:
                region_data['type'] = 'chartComponent'
                result['stats']['chart_components'] += 1

            result['regions'].append(region_data)

    return result

def extract_math_content(math_elem):
    """Extrae contenido de una región matemática"""
    content = {
        'defines': [],
        'expressions': []
    }

    # Buscar definiciones
    for define in math_elem.findall('.//ml:define', NS):
        var_id = define.find('.//ml:id', NS)
        if var_id is not None:
            var_name = get_text_content(var_id)
            content['defines'].append(var_name)

    # Buscar keywords especiales (odesolve, solve, etc.)
    for keyword in math_elem.findall('.//ml:id[@labels="KEYWORD"]', NS):
        content['expressions'].append(get_text_content(keyword))

    return content

def extract_plot_info(plot_elem):
    """Extrae información de una gráfica"""
    info = {
        'type': 'unknown',
        'axes': {}
    }

    # Detectar tipo de gráfica
    if plot_elem.find('.//ws:xyPlot', NS) is not None:
        info['type'] = 'xyPlot'

        # Extraer info de ejes
        xy_plot = plot_elem.find('.//ws:xyPlot', NS)
        axes = xy_plot.find('.//ws:axes', NS)

        if axes is not None:
            for axis in axes.findall('.//ws:xAxis', NS):
                info['axes']['x'] = {
                    'start': axis.get('start'),
                    'end': axis.get('end')
                }

            for axis in axes.findall('.//ws:yAxis', NS):
                info['axes']['y'] = {
                    'start': axis.get('start'),
                    'end': axis.get('end')
                }

    return info

def extract_solveblock_info(solve_elem):
    """Extrae información de un solve block"""
    info = {
        'constraints': [],
        'solver_type': None,
        'variables': []
    }

    # Buscar regiones internas
    regions = solve_elem.find('.//ws:regions', NS)
    if regions is not None:
        for region in regions.findall('ws:region', NS):
            category = region.get('solve-block-category')

            if category == 'constraint':
                # Ecuación o restricción
                info['constraints'].append('equation')

            elif category == 'solver':
                # Tipo de solver
                math_elem = region.find('.//ws:math', NS)
                if math_elem is not None:
                    for keyword in math_elem.findall('.//ml:id[@labels="KEYWORD"]', NS):
                        solver_type = get_text_content(keyword)
                        info['solver_type'] = solver_type

    return info

def get_text_content(elem):
    """Obtiene el contenido de texto de un elemento XML"""
    if elem.text:
        return elem.text.strip()

    # Manejar elementos con subscripts/superscripts
    text = elem.text or ''
    for child in elem:
        if child.tail:
            text += child.tail

    return text.strip()

def main():
    """Analiza todos los archivos .mcdx en MathCadPrime/"""

    mcdx_dir = Path(__file__).parent
    mcdx_files = list(mcdx_dir.glob('*.mcdx'))

    print(f"Encontrados {len(mcdx_files)} archivos .mcdx\n")
    print("="*80)

    all_results = []

    for mcdx_file in sorted(mcdx_files):
        print(f"\nAnalizando: {mcdx_file.name}")
        print("-"*80)

        result = analyze_mcdx(mcdx_file)
        all_results.append(result)

        # Mostrar estadísticas
        stats = result['stats']
        print(f"  Regiones totales: {len(result['regions'])}")
        print(f"  - Texto: {stats['text_regions']}")
        print(f"  - Matemáticas: {stats['math_regions']}")
        print(f"  - Gráficas: {stats['plot_regions']}")
        print(f"  - Imágenes: {stats['picture_regions']}")
        print(f"  - Solve Blocks: {stats['solve_blocks']}")
        print(f"  - Chart Components: {stats['chart_components']}")

        # Mostrar info especial
        for region in result['regions']:
            if region['type'] == 'solveblock' and region['content']:
                content = region['content']
                print(f"\n  Solve Block encontrado:")
                print(f"     Solver: {content['solver_type']}")
                print(f"     Restricciones: {len(content['constraints'])}")

            elif region['type'] == 'plot' and region['content']:
                content = region['content']
                print(f"\n  Grafica {content['type']} encontrada:")
                if 'x' in content['axes']:
                    print(f"     Eje X: {content['axes']['x']['start']} a {content['axes']['x']['end']}")
                if 'y' in content['axes']:
                    print(f"     Eje Y: {content['axes']['y']['start']} a {content['axes']['y']['end']}")

    print("\n" + "="*80)
    print("\nRESUMEN GENERAL:")
    print("-"*80)

    total_stats = {
        'text_regions': 0,
        'math_regions': 0,
        'plot_regions': 0,
        'picture_regions': 0,
        'solve_blocks': 0,
        'chart_components': 0
    }

    for result in all_results:
        for key in total_stats:
            total_stats[key] += result['stats'][key]

    print(f"Total de archivos: {len(all_results)}")
    print(f"Total regiones de texto: {total_stats['text_regions']}")
    print(f"Total regiones matemáticas: {total_stats['math_regions']}")
    print(f"Total gráficas: {total_stats['plot_regions']}")
    print(f"Total imágenes: {total_stats['picture_regions']}")
    print(f"Total solve blocks: {total_stats['solve_blocks']}")
    print(f"Total chart components: {total_stats['chart_components']}")

    # Guardar resultados en JSON
    output_file = mcdx_dir / 'mcdx_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nAnalisis guardado en: {output_file}")

if __name__ == '__main__':
    main()
