# SOLUCIÓN: TypeScript no funciona (@{ts})

## PROBLEMA IDENTIFICADO

El archivo `Test_TypeScript_@ts.cpd` no funciona porque **ts-node no está instalado**.

### Estado Actual del Sistema
- ✅ Node.js v22.15.0 - Instalado
- ✅ TypeScript v5.8.3 - Instalado
- ❌ ts-node - NO instalado (requerido)

### Error Esperado
```
ts-node: command not found
```

---

## SOLUCIÓN RÁPIDA: Instalar ts-node

### Instalación Global (Recomendado)
```bash
npm install -g ts-node
```

### Verificar Instalación
```bash
ts-node --version
```

Debería mostrar algo como: `v10.x.x`

---

## SOLUCIÓN ALTERNATIVA: Usar Node + TypeScript Compiler

Si no quieres instalar ts-node, puedes modificar la configuración para usar `tsc` (ya instalado) + `node`:

### Opción A: Modificar MultLangConfig.json para usar compilación

Cambiar la configuración de TypeScript en `Calcpad.Common\MultLangCode\MultLangConfig.json`:

**ANTES:**
```json
"typescript": {
  "command": "ts-node",
  "extension": ".ts",
  "directive": "@{ts}",
  "endDirective": "@{end ts}",
  "requiresCompilation": false,
  "compileArgs": "",
  "runArgs": "\"{file}\""
}
```

**DESPUÉS:**
```json
"typescript": {
  "command": "tsc",
  "extension": ".ts",
  "directive": "@{ts}",
  "endDirective": "@{end ts}",
  "requiresCompilation": true,
  "compileArgs": "{input} --outFile {output}.js",
  "runArgs": "{output}.js"
}
```

**NOTA:** Esto requiere cambios en el código para manejar la compilación en dos pasos.

---

## RECOMENDACIÓN FINAL

**Instalar ts-node es la solución más simple y rápida:**

```bash
# En PowerShell o CMD
npm install -g ts-node

# Verificar
ts-node --version

# Probar TypeScript
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\Examples
ts-node --eval "console.log('TypeScript funciona!')"
```

Después de instalar ts-node, el archivo `Test_TypeScript_@ts.cpd` debería funcionar correctamente.

---

## TESTING

Una vez instalado ts-node, probar con este código simple:

```typescript
@{ts}
const mensaje: string = "Hola desde TypeScript!";
console.log(mensaje);
@{end ts}
```

---

**Fecha:** 2026-01-22
**Estado:** Problema identificado, solución documentada
