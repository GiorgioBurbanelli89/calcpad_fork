import xml.etree.ElementTree as ET

# Read the XML file
with open(r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\MathCadPrime\temp_grafica\mathcad\worksheet.xml", 'r', encoding='utf-8') as f:
    content = f.read()

root = ET.fromstring(content)

ns = {
    'ws': 'http://schemas.mathsoft.com/worksheet50',
    'ml': 'http://schemas.mathsoft.com/math50',
    '': 'http://schemas.mathsoft.com/worksheet50'
}

print("=== Analyzing worksheet.xml ===\n")

# Find all regions
regions = root.findall('.//{http://schemas.mathsoft.com/worksheet50}region')
print(f"Found {len(regions)} regions\n")

for i, r in enumerate(regions):
    rid = r.get('region-id', 'unknown')
    print(f"--- Region {rid} ---")

    # Check for spec-table
    spec = r.find('.//{http://schemas.mathsoft.com/worksheet50}spec-table')
    if spec is not None:
        print("  Type: spec-table")
        # Find all math elements (direct children)
        maths = spec.findall('{http://schemas.mathsoft.com/worksheet50}math')
        if not maths:
            maths = list(spec)
        print(f"  Children: {[m.tag for m in spec]}")
        print(f"  Math elements: {len(maths)}")

        for j, m in enumerate(maths):
            print(f"    math[{j}]: tag={m.tag}")
            defines = m.findall('.//{http://schemas.mathsoft.com/math50}define')
            for d in defines:
                id_elem = d.find('{http://schemas.mathsoft.com/math50}id')
                if id_elem is not None:
                    print(f"      define: {id_elem.text}")

    # Check for plot
    plot = r.find('.//{http://schemas.mathsoft.com/worksheet50}plot')
    if plot is not None:
        print("  Type: plot")
        xyplot = plot.find('.//{http://schemas.mathsoft.com/worksheet50}xyPlot')
        if xyplot is not None:
            print("    Has xyPlot")
            # Find axes
            axes = xyplot.find('.//{http://schemas.mathsoft.com/worksheet50}axes')
            if axes is not None:
                xaxis = axes.find('.//{http://schemas.mathsoft.com/worksheet50}xAxis')
                yaxis = axes.find('.//{http://schemas.mathsoft.com/worksheet50}yAxis')
                if xaxis is not None:
                    xvar = xaxis.find('.//{http://schemas.mathsoft.com/math50}id')
                    if xvar is not None:
                        print(f"    X axis variable: {xvar.text}")
                if yaxis is not None:
                    yvar = yaxis.find('.//{http://schemas.mathsoft.com/math50}id')
                    if yvar is not None:
                        print(f"    Y axis variable: {yvar.text}")

    print()
