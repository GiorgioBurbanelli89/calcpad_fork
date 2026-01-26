#!/bin/bash

file="MULTILANG_README.md"

# Backup
cp "$file" "${file}.bak"

# Reemplazar directivas en tabla
sed -i 's/| `#python`/| `@{python}`/g' "$file"
sed -i 's/| `#end python`/| `@{end python}`/g' "$file"
sed -i 's/| `#cpp`/| `@{cpp}`/g' "$file"
sed -i 's/| `#end cpp`/| `@{end cpp}`/g' "$file"
sed -i 's/| `#octave`/| `@{octave}`/g' "$file"
sed -i 's/| `#end octave`/| `@{end octave}`/g' "$file"
sed -i 's/| `#julia`/| `@{julia}`/g' "$file"
sed -i 's/| `#end julia`/| `@{end julia}`/g' "$file"
sed -i 's/| `#r`/| `@{r}`/g' "$file"
sed -i 's/| `#end r`/| `@{end r}`/g' "$file"
sed -i 's/| `#powershell`/| `@{powershell}`/g' "$file"
sed -i 's/| `#end powershell`/| `@{end powershell}`/g' "$file"
sed -i 's/| `#bash`/| `@{bash}`/g' "$file"
sed -i 's/| `#end bash`/| `@{end bash}`/g' "$file"
sed -i 's/| `#cmd`/| `@{cmd}`/g' "$file"
sed -i 's/| `#end cmd`/| `@{end cmd}`/g' "$file"

# Reemplazar en bloques de código y texto
sed -i 's/^#python/@{python}/g' "$file"
sed -i 's/^#end python/@{end python}/g' "$file"
sed -i 's/^#cpp/@{cpp}/g' "$file"
sed -i 's/^#end cpp/@{end cpp}/g' "$file"
sed -i 's/^#octave/@{octave}/g' "$file"
sed -i 's/^#end octave/@{end octave}/g' "$file"
sed -i 's/^#julia/@{julia}/g' "$file"
sed -i 's/^#end julia/@{end julia}/g' "$file"
sed -i 's/^#r$/@{r}/g' "$file"
sed -i 's/^#end r/@{end r}/g' "$file"
sed -i 's/^#bash/@{bash}/g' "$file"
sed -i 's/^#end bash/@{end bash}/g' "$file"
sed -i 's/^#powershell/@{powershell}/g' "$file"
sed -i 's/^#end powershell/@{end powershell}/g' "$file"
sed -i 's/^#cmd/@{cmd}/g' "$file"
sed -i 's/^#end cmd/@{end cmd}/g' "$file"

# Reemplazar en JSON config examples
sed -i 's/"directive": "#python"/"directive": "@{python}"/g' "$file"
sed -i 's/"endDirective": "#end python"/"endDirective": "@{end python}"/g' "$file"
sed -i 's/"directive": "#cpp"/"directive": "@{cpp}"/g' "$file"
sed -i 's/"endDirective": "#end cpp"/"endDirective": "@{end cpp}"/g' "$file"
sed -i 's/"directive": "#mi_lenguaje"/"directive": "@{mi_lenguaje}"/g' "$file"
sed -i 's/"endDirective": "#end mi_lenguaje"/"endDirective": "@{end mi_lenguaje}"/g' "$file"

# Reemplazar en sintaxis básica
sed -i 's/#lenguaje/@{lenguaje}/g' "$file"
sed -i 's/#end lenguaje/@{end lenguaje}/g' "$file"

echo "✓ MULTILANG_README.md actualizado"
echo "  Backup guardado en: MULTILANG_README.md.bak"
