#!/bin/bash

# Lista de lenguajes soportados
languages=(
    "python" "csharp" "cpp" "javascript" "typescript" "java" 
    "ruby" "php" "go" "rust" "swift" "kotlin" "scala" "dart" 
    "lua" "perl" "r" "matlab" "octave" "bash"
)

# Contador de archivos modificados
count=0

# Buscar todos los archivos .cpd
while IFS= read -r file; do
    if [ -f "$file" ]; then
        modified=false
        
        # Para cada lenguaje, hacer los reemplazos
        for lang in "${languages[@]}"; do
            # Reemplazar #language por @{language}
            if grep -q "^#${lang}" "$file"; then
                sed -i "s|^#${lang}|@{${lang}}|g" "$file"
                modified=true
            fi
            
            # Reemplazar #end language por @{end language}
            if grep -q "^#end ${lang}" "$file"; then
                sed -i "s|^#end ${lang}|@{end ${lang}}|g" "$file"
                modified=true
            fi
        done
        
        if [ "$modified" = true ]; then
            count=$((count + 1))
            echo "✓ $file"
        fi
    fi
done < <(find . -name "*.cpd" -type f)

echo ""
echo "Total archivos modificados: $count"
