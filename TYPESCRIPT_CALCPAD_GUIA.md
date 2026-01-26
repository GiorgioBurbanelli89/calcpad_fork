# TypeScript en Calcpad - Guía Completa

## ¿Qué es?

TypeScript es JavaScript con **tipado estático**. Puedes usarlo en Calcpad para:
- ✓ Código más robusto (detecta errores antes)
- ✓ OOP avanzado (clases, interfaces, genéricos)
- ✓ Mejor autocompletado
- ✓ Integración con ecosistema Node.js

---

## Instalación

### Método 1: Instalar con NPM

```bash
npm install -g typescript ts-node
```

### Método 2: Usar el script automático

Ejecuta:
```
Examples\instalar_typescript.bat
```

---

## Uso Básico en Calcpad

### Sintaxis:

```calcpad
@{cmd}
ts-node -e "código TypeScript aquí"
@{cmd}
```

### Ejemplo simple:

```calcpad
@{cmd}
ts-node -e "
  const x: number = 10;
  const y: number = 20;
  console.log(x + y);
"
@{cmd}
```

---

## Ejemplos Prácticos

### 1. Funciones con tipos

```calcpad
@{cmd}
ts-node -e "
  function areaCirculo(radio: number): number {
    return Math.PI * radio ** 2;
  }

  console.log(areaCirculo(5).toFixed(2));
"
@{cmd}
```

### 2. Interfaces

```calcpad
@{cmd}
ts-node -e "
  interface Rectangulo {
    ancho: number;
    alto: number;
  }

  function area(rect: Rectangulo): number {
    return rect.ancho * rect.alto;
  }

  const miRect: Rectangulo = { ancho: 10, alto: 20 };
  console.log(area(miRect));
"
@{cmd}
```

### 3. Clases

```calcpad
@{cmd}
ts-node -e "
  class Viga {
    constructor(
      public longitud: number,
      public carga: number
    ) {}

    momentoMaximo(): number {
      return (this.carga * this.longitud ** 2) / 8;
    }
  }

  const viga = new Viga(6, 1000);
  console.log(viga.momentoMaximo());
"
@{cmd}
```

### 4. Genéricos

```calcpad
@{cmd}
ts-node -e "
  class Pila<T> {
    private items: T[] = [];

    push(item: T): void {
      this.items.push(item);
    }

    pop(): T | undefined {
      return this.items.pop();
    }

    size(): number {
      return this.items.length;
    }
  }

  const pila = new Pila<number>();
  pila.push(10);
  pila.push(20);
  console.log(pila.size());
"
@{cmd}
```

---

## Integración con Variables de Calcpad

Puedes pasar valores de Calcpad a TypeScript:

```calcpad
a = 10
b = 20

@{cmd}
ts-node -e "
  const a: number = $a;
  const b: number = $b;
  console.log(a + b);
"
@{cmd}

resultado = ?
```

---

## Alternativa: Deno

Deno soporta TypeScript **sin configuración**:

```calcpad
@{cmd}
deno eval "
  interface Punto {
    x: number;
    y: number;
  }

  const p: Punto = { x: 3, y: 4 };
  const distancia = Math.sqrt(p.x**2 + p.y**2);
  console.log(distancia);
"
@{cmd}
```

**Instalar Deno:**
```powershell
irm https://deno.land/install.ps1 | iex
```

---

## Crear Parser Personalizado

### Opción 1: Script Wrapper

Crea `ts-calc.bat`:
```batch
@echo off
ts-node %*
```

Luego en Calcpad:
```calcpad
@{cmd}
ts-calc -e "console.log(Math.PI)"
@{cmd}
```

### Opción 2: Archivo TypeScript

Crea `calcular.ts`:
```typescript
interface Viga {
  L: number;
  w: number;
}

function momento(v: Viga): number {
  return (v.w * v.L ** 2) / 8;
}

const viga: Viga = {
  L: parseFloat(process.argv[2]),
  w: parseFloat(process.argv[3])
};

console.log(momento(viga));
```

Usar en Calcpad:
```calcpad
L = 6
w = 1000

@{cmd}
ts-node calcular.ts $L $w
@{cmd}

M = ?
```

---

## Comparación: TypeScript vs JavaScript

| Característica | JavaScript | TypeScript |
|----------------|------------|------------|
| Tipado | ❌ Dinámico | ✓ Estático |
| Errores en tiempo de compilación | ❌ | ✓ |
| Interfaces | ❌ | ✓ |
| Genéricos | ❌ | ✓ |
| Autocompletado | Limitado | ✓ Excelente |
| Curva de aprendizaje | Fácil | Media |

---

## Ventajas en Calcpad

1. **Detección de errores temprana**
   ```typescript
   const x: number = "10"; // ❌ Error en compilación
   ```

2. **Documentación con tipos**
   ```typescript
   function calcular(a: number, b: number): number {
     return a + b;
   }
   // Autocompletado sabe que devuelve un número
   ```

3. **Refactoring seguro**
   - Cambias un tipo y TypeScript te avisa de todos los lugares afectados

4. **Mejor mantenibilidad**
   - Código más estructurado con interfaces y clases

---

## Ejemplos Completos

Ver archivos:
- `Examples/TypeScript_en_Calcpad.cpd` - Guía completa con ejemplos
- `Examples/test_typescript_simple.cpd` - Prueba rápida
- `Examples/instalar_typescript.bat` - Instalación automática

---

## Solución de Problemas

### Error: "ts-node no reconocido"

**Solución:**
```bash
npm install -g ts-node
```

### Error: "Cannot find module 'typescript'"

**Solución:**
```bash
npm install -g typescript
```

### Error: Código muy largo en -e

**Solución:** Usa un archivo `.ts`:
```calcpad
@{cmd}
echo const x = 10; > temp.ts
echo console.log(x); >> temp.ts
ts-node temp.ts
@{cmd}
```

---

## Recursos

- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [ts-node GitHub](https://github.com/TypeStrong/ts-node)
- [Deno Docs](https://deno.land/)

---

## Conclusión

TypeScript en Calcpad te da:
- ✓ Seguridad de tipos
- ✓ Mejor estructura de código
- ✓ Detección de errores temprana
- ✓ Ecosistema JavaScript/Node.js

**Para empezar:**
1. Instala: `npm install -g typescript ts-node`
2. Abre: `Examples/test_typescript_simple.cpd`
3. Calcula y disfruta TypeScript en Calcpad!
