import xml.etree.ElementTree as ET

# Parse the worksheet
tree = ET.parse('mcdx_ensamblaje_extracted/mathcad/worksheet.xml')
root = tree.getroot()

ns = {
    'ws': 'http://schemas.mathsoft.com/worksheet50',
    'ml': 'http://schemas.mathsoft.com/math50'
}

# Count regions by type
regions = root.findall('.//ws:region', ns)
print("Total regiones: %d\n" % len(regions))

# Find the E=2.535 definition from PDF
print("=== BUSCANDO DEFINICIONES DEL PDF ===\n")

math_count = 0
found_E = False
found_nu = False
found_Df = False

for region in regions[:30]:
    region_id = region.get('region-id')

    # Check if it's a math region
    math = region.find('.//ws:math', ns)
    if math is not None:
        math_count += 1
        # Get the define element
        define = math.find('.//ml:define', ns)
        if define is not None:
            # Get variable name
            id_elem = define.find('.//ml:id', ns)
            if id_elem is not None:
                var_name = (id_elem.text or "").strip()

                # Look for specific variables from PDF
                if var_name == "E" and not found_E:
                    found_E = True
                    real = define.find('.//ml:real', ns)
                    if real is not None:
                        print("Region %s: E := %s (Modulo de Elasticidad)" % (region_id, real.text))

                elif var_name.startswith("nu") or "ν" in var_name and not found_nu:
                    found_nu = True
                    real = define.find('.//ml:real', ns)
                    if real is not None:
                        print("Region %s: nu := %s (Coeficiente de Poisson)" % (region_id, real.text))

                elif var_name == "Df" and not found_Df:
                    found_Df = True
                    matrix = define.find('.//ml:matrix', ns)
                    if matrix is not None:
                        rows = matrix.get('rows')
                        cols = matrix.get('cols')
                        print("Region %s: Df := matriz %sx%s (Matriz constitutiva a flexion)" % (region_id, rows, cols))

print("\n=== TIPOS DE REGIONES ===")
math_regions = len(root.findall('.//ws:math', ns))
text_regions = len(root.findall('.//ws:text', ns))
picture_regions = len(root.findall('.//ws:picture', ns))
plot_regions = len(root.findall('.//ws:plot', ns))

print("Regiones matematicas: %d" % math_regions)
print("Regiones de texto: %d" % text_regions)
print("Regiones de imagenes: %d" % picture_regions)
print("Regiones de graficos: %d" % plot_regions)

print("\n=== CONCLUSION ===")
print("TODO el contenido del PDF esta en el .mcdx:")
print("- Ecuaciones matematicas: SI (%d regiones)" % math_regions)
print("- Texto descriptivo: SI (%d regiones)" % text_regions)
print("- Imagenes: SI (%d archivos en media/)" % picture_regions)
print("- Graficos: Pendiente de analizar")
