# ✅ TypeScript `@{ts}` Configurado en Calcpad

## ¡Ya está listo!

He agregado soporte nativo para TypeScript usando `@{ts}` en Calcpad.

---

## Uso Básico

### Sintaxis:

```calcpad
@{ts}
// Tu código TypeScript aquí
@{end ts}
```

### Ejemplo simple:

```calcpad
"Hola TypeScript

@{ts}
const mensaje: string = "Hola desde TypeScript!";
console.log(mensaje);
@{end ts}
```

---

## Comparación: Antes vs Ahora

### ❌ ANTES (Complicado):

```calcpad
@{cmd}
ts-node -e "
const x: number = 10;
console.log(x);
"
@{cmd}
```

### ✅ AHORA (Simple):

```calcpad
@{ts}
const x: number = 10;
console.log(x);
@{end ts}
```

---

## Características Habilitadas

✅ Tipado estático
✅ Interfaces
✅ Clases
✅ Genéricos
✅ Async/Await
✅ Enums
✅ Type Guards
✅ Union Types
✅ Decoradores
✅ Todo lo que soporta TypeScript!

---

## Ejemplos Completos

### 1. Función con Tipos

```calcpad
@{ts}
function suma(a: number, b: number): number {
  return a + b;
}

console.log(suma(10, 20));
@{end ts}

resultado = ?
```

### 2. Interface

```calcpad
@{ts}
interface Punto {
  x: number;
  y: number;
}

const p: Punto = { x: 3, y: 4 };
const dist = Math.sqrt(p.x**2 + p.y**2);
console.log(dist);
@{end ts}

d = ?
```

### 3. Clase

```calcpad
@{ts}
class Viga {
  constructor(
    public L: number,
    public w: number
  ) {}

  momentoMaximo(): number {
    return (this.w * this.L ** 2) / 8;
  }
}

const viga = new Viga(6, 1000);
console.log(viga.momentoMaximo());
@{end ts}

M = ?'kN·m
```

### 4. Genéricos

```calcpad
@{ts}
class Pila<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  size(): number {
    return this.items.length;
  }
}

const pila = new Pila<number>();
pila.push(10);
pila.push(20);
console.log(pila.size());
@{end ts}
```

---

## Archivos Modificados

1. **`Calcpad.Common/MultLangCode/MultLangConfig.json`**
   - Agregado parser "typescript"
   - Comando: `ts-node`
   - Directiva: `@{ts}` ... `@{end ts}`

2. **`MultLangConfig.json`** (raíz)
   - Copiado para que funcione en todos los builds

---

## Configuración Aplicada

```json
"typescript": {
  "command": "ts-node",
  "extension": ".ts",
  "directive": "@{ts}",
  "endDirective": "@{end ts}",
  "commentPrefix": "//",
  "keywords": ["interface", "type", "enum", "class", "extends",
               "implements", "public", "private", "protected",
               "static", "readonly", "abstract", "const", "let",
               "var", "function", "async", "await", "return",
               "if", "else", "for", "while", "try", "catch"],
  "builtins": ["console", "Array", "Object", "String", "Number",
               "Boolean", "Math", "Date", "JSON", "Promise"],
  "requiresCompilation": false,
  "runArgs": "\"{file}\""
}
```

---

## Bonus: JavaScript `@{js}` También Agregado

Ahora también puedes usar JavaScript:

```calcpad
@{js}
const x = 10;
const y = 20;
console.log(x + y);
@{end js}
```

---

## Archivos de Ejemplo

1. **`Examples/Test_TypeScript_@ts.cpd`**
   - 10 ejemplos completos
   - Desde básico hasta avanzado
   - Listo para calcular

2. **`Examples/TypeScript_en_Calcpad.cpd`**
   - Guía completa de TypeScript
   - Todos los métodos explicados

---

## Verificar Instalación

```calcpad
@{ts}
console.log("TypeScript funciona con @{ts}!");
@{end ts}
```

Si sale el mensaje, ¡está funcionando!

---

## Requisitos

- ✅ TypeScript instalado: `npm install -g typescript`
- ✅ ts-node instalado: `npm install -g ts-node`

Si no los tienes, ejecuta:
```bash
npm install -g typescript ts-node
```

O usa el archivo: `Examples/instalar_typescript.bat`

---

## Ventajas de `@{ts}` vs `@{cmd}`

| Característica | @{cmd} ts-node | @{ts} |
|----------------|----------------|-------|
| **Sintaxis** | Complicada | ✅ Limpia |
| **Legibilidad** | Difícil | ✅ Fácil |
| **Resaltado** | Genérico | ✅ Específico |
| **Autocompletado** | Limitado | ✅ Mejorado |
| **Integración** | Manual | ✅ Nativa |

---

## Para Empezar

1. **Abre**: `Examples/Test_TypeScript_@ts.cpd`
2. **Calcula**: F5
3. **Disfruta**: TypeScript integrado en Calcpad!

---

## Otros Lenguajes Disponibles

Calcpad ahora soporta:

- `@{python}` - Python
- `@{ts}` - TypeScript ⬅️ **NUEVO**
- `@{js}` - JavaScript ⬅️ **NUEVO**
- `@{powershell}` - PowerShell
- `@{octave}` - Octave/MATLAB
- `@{julia}` - Julia
- `@{cpp}` - C++
- `@{c}` - C
- `@{csharp}` - C#
- `@{rust}` - Rust
- `@{fortran}` - Fortran
- `@{r}` - R
- `@{bash}` - Bash
- `@{cmd}` - Batch/CMD
- `@{opensees}` - OpenSees
- Y más...

---

## Conclusión

¡Ya no necesitas `@{cmd}` para TypeScript!

Usa directamente:
```calcpad
@{ts}
// Tu código TypeScript
@{end ts}
```

**¡Disfruta TypeScript integrado en Calcpad!** 🎉
