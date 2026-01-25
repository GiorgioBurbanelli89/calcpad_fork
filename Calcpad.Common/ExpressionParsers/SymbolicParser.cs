using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;

namespace Calcpad.Common.ExpressionParsers
{
    /// <summary>
    /// Parser para operaciones simbólicas usando AngouriMath.
    /// Permite derivadas, integrales, simplificación, resolver ecuaciones, etc.
    /// </summary>
    public class SymbolicParser : BaseExpressionParser
    {
        public override string Name => "Symbolic Math Parser (AngouriMath)";
        public override string Directive => "@{symbolic}";
        public override string EndDirective => "@{end symbolic}";
        public override ParserMode Mode => ParserMode.Hybrid; // Puede traducir o ejecutar

        private readonly Type _entityType;
        private readonly Type _mathSType;
        private readonly Assembly _angouriAssembly;
        private readonly bool _isAvailable;

        public SymbolicParser()
        {
            try
            {
                // DEBUG: Log intentos de carga
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-symbolic-debug.txt");
                System.IO.File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] Intentando cargar AngouriMath...\n");

                _angouriAssembly = AppDomain.CurrentDomain.GetAssemblies()
                    .FirstOrDefault(a => a.GetName().Name == "AngouriMath");

                if (_angouriAssembly == null)
                {
                    System.IO.File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] No encontrado en AppDomain, intentando Assembly.Load...\n");
                    _angouriAssembly = Assembly.Load("AngouriMath");
                }

                if (_angouriAssembly != null)
                {
                    System.IO.File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] AngouriMath assembly cargado: {_angouriAssembly.FullName}\n");
                }

                _entityType = _angouriAssembly?.GetType("AngouriMath.Entity");
                _mathSType = _angouriAssembly?.GetType("AngouriMath.MathS");
                _isAvailable = _entityType != null && _mathSType != null;

                System.IO.File.AppendAllText(debugPath,
                    $"[{DateTime.Now:HH:mm:ss}] IsAvailable={_isAvailable}, EntityType={_entityType != null}, MathSType={_mathSType != null}\n");
            }
            catch (Exception ex)
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-symbolic-debug.txt");
                System.IO.File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] ERROR: {ex.Message}\n{ex.StackTrace}\n");
                _isAvailable = false;
            }
        }

        public bool IsAvailable => _isAvailable;

        private void LogDebug(string message)
        {
            try
            {
                var debugPath = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "calcpad-symbolic-debug.txt");
                System.IO.File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss.fff}] {message}\n");
            }
            catch { }
        }

        private object ParseExpression(string expression)
        {
            if (!_isAvailable)
                throw new InvalidOperationException("AngouriMath not available. Install AngouriMath package.");

            // Usar conversión implícita de string a Entity
            var method = _entityType.GetMethod("op_Implicit", new[] { typeof(string) });
            return method?.Invoke(null, new object[] { expression });
        }

        public override string Translate(string expression)
        {
            if (!_isAvailable)
                return $"' Error: AngouriMath not available\n{expression}";

            // Si el contenido tiene múltiples líneas, procesarlas por separado
            if (expression.Contains('\n') || expression.Contains('\r'))
            {
                return TranslateBlock(expression);
            }

            try
            {
                // Detectar operaciones simbólicas especiales
                var result = ProcessSymbolicOperations(expression);
                return result ?? expression;
            }
            catch (Exception ex)
            {
                return $"' Symbolic error: {ex.Message}\n{expression}";
            }
        }

        /// <summary>
        /// Traduce bloques simbólicos multilínea
        /// </summary>
        public string TranslateBlock(string symbolicBlock)
        {
            LogDebug($"TranslateBlock called with {symbolicBlock.Length} chars");
            var lines = symbolicBlock.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
            var result = new List<string>();

            LogDebug($"Split into {lines.Length} lines");
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                LogDebug($"Processing line: '{trimmed}'");

                // Ignorar líneas vacías y comentarios
                if (string.IsNullOrWhiteSpace(trimmed) || trimmed.StartsWith("'"))
                {
                    LogDebug($"Line is comment or empty, keeping as-is");
                    result.Add(line);
                    continue;
                }

                // Traducir la línea
                try
                {
                    var translated = ProcessSymbolicOperations(trimmed);
                    LogDebug($"Translated to: '{translated}'");
                    result.Add(translated ?? trimmed);
                }
                catch (Exception ex)
                {
                    LogDebug($"Translation error: {ex.Message}");
                    result.Add($"' Error: {ex.Message}");
                }
            }

            var final = string.Join("\n", result);
            LogDebug($"Final result length: {final.Length}");
            return final;
        }

        /// <summary>
        /// Procesa operaciones simbólicas y las convierte a sintaxis Calcpad
        /// </summary>
        private string ProcessSymbolicOperations(string expression)
        {
            var lines = expression.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
            var output = new List<string>();

            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (string.IsNullOrWhiteSpace(trimmed) || trimmed.StartsWith("'"))
                {
                    output.Add(line);
                    continue;
                }

                string processed = null;

                // 1. Derivada: d/dx(expresión) o derive(expresión, x)
                if (Regex.IsMatch(trimmed, @"d/d[a-zA-Z]\(") || trimmed.Contains("derive("))
                {
                    processed = ProcessDerivative(trimmed);
                }
                // 2. Integral: ∫(expresión, x) o integrate(expresión, x)
                else if (trimmed.Contains("∫(") || trimmed.Contains("integrate("))
                {
                    processed = ProcessIntegral(trimmed);
                }
                // 3. Simplificar: simplify(expresión)
                else if (trimmed.Contains("simplify("))
                {
                    processed = ProcessSimplify(trimmed);
                }
                // 4. Expandir: expand(expresión)
                else if (trimmed.Contains("expand("))
                {
                    processed = ProcessExpand(trimmed);
                }
                // 5. Resolver: solve(ecuación, variable)
                else if (trimmed.Contains("solve("))
                {
                    processed = ProcessSolve(trimmed);
                }
                // 6. Límite: limit(expresión, x, valor)
                else if (trimmed.Contains("limit("))
                {
                    processed = ProcessLimit(trimmed);
                }
                // 7. Asignación normal con evaluación simbólica
                else if (trimmed.Contains("="))
                {
                    processed = ProcessAssignment(trimmed);
                }

                output.Add(processed ?? line);
            }

            return string.Join("\n", output);
        }

        private string ProcessDerivative(string line)
        {
            // d/dx(expresión) → derivada
            var match = Regex.Match(line, @"(\w+)\s*=\s*d/d([a-zA-Z])\((.+)\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var variable = match.Groups[2].Value;
                var expr = match.Groups[3].Value;

                try
                {
                    LogDebug($"ProcessDerivative: expr={expr}, variable={variable}");
                    var entity = ParseExpression(expr);
                    LogDebug($"Entity parsed: {entity}");

                    // Enumerar todos los métodos Differentiate para evitar ambigüedad
                    var methods = _entityType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                        .Where(m => m.Name == "Differentiate")
                        .ToArray();

                    LogDebug($"Found {methods.Length} Differentiate overloads");
                    foreach (var m in methods)
                    {
                        var pars = m.GetParameters();
                        LogDebug($"  - Differentiate({string.Join(", ", pars.Select(p => p.ParameterType.Name))})");
                    }

                    // Buscar el método que toma un Variable o Entity como parámetro
                    var diffMethod = methods.FirstOrDefault(m =>
                    {
                        var pars = m.GetParameters();
                        return pars.Length == 1 &&
                               (pars[0].ParameterType.Name == "Variable" ||
                                pars[0].ParameterType.Name == "Entity");
                    });

                    LogDebug($"Selected method: {diffMethod?.ToString()}");

                    object result = null;
                    if (diffMethod != null)
                    {
                        var variableEntity = ParseExpression(variable);
                        LogDebug($"Variable entity: {variableEntity}");
                        result = diffMethod.Invoke(entity, new object[] { variableEntity });
                    }
                    else
                    {
                        LogDebug($"No suitable Differentiate method found, trying MathS.Differentiate");
                        // Último intento: usar MathS.Differentiate
                        var mathsDiff = _mathSType?.GetMethod("Differentiate",
                            BindingFlags.Public | BindingFlags.Static,
                            null,
                            new[] { _entityType, _entityType },
                            null);

                        if (mathsDiff != null)
                        {
                            var variableEntity = ParseExpression(variable);
                            result = mathsDiff.Invoke(null, new object[] { entity, variableEntity });
                        }
                    }

                    LogDebug($"Differentiation result: {result}");
                    var simplified = Simplify(result);
                    LogDebug($"Simplified result: {simplified}");

                    // Mostrar resultado simbólico como comentario
                    return $"' {varName} = d/d{variable}({expr})\n' {varName} = {simplified}";
                }
                catch (Exception ex)
                {
                    LogDebug($"ProcessDerivative ERROR: {ex.Message}\n{ex.StackTrace}");
                    return $"' {varName} = d/d{variable}({expr})\n' Error: {ex.Message}";
                }
            }

            // derive(expresión, x)
            match = Regex.Match(line, @"(\w+)\s*=\s*derive\((.+?),\s*([a-zA-Z])\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;
                var variable = match.Groups[3].Value;

                try
                {
                    var entity = ParseExpression(expr);
                    var variableEntity = ParseExpression(variable);

                    var methods = _entityType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                        .Where(m => m.Name == "Differentiate")
                        .ToArray();

                    var diffMethod = methods.FirstOrDefault(m =>
                    {
                        var pars = m.GetParameters();
                        return pars.Length == 1 &&
                               (pars[0].ParameterType.Name == "Variable" ||
                                pars[0].ParameterType.Name == "Entity");
                    });

                    var result = diffMethod?.Invoke(entity, new object[] { variableEntity });
                    var simplified = Simplify(result);

                    return $"' {varName} = d/d{variable}({expr})\n' {varName} = {simplified}";
                }
                catch (Exception ex)
                {
                    return $"' {varName} = derive({expr}, {variable})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessIntegral(string line)
        {
            // ∫(expresión, x) o integrate(expresión, x)
            var pattern = @"(\w+)\s*=\s*(?:∫|integrate)\((.+?),\s*([a-zA-Z])\)";
            var match = Regex.Match(line, pattern);

            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;
                var variable = match.Groups[3].Value;

                try
                {
                    var entity = ParseExpression(expr);
                    var variableEntity = ParseExpression(variable);

                    var methods = _entityType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                        .Where(m => m.Name == "Integrate")
                        .ToArray();

                    var intMethod = methods.FirstOrDefault(m =>
                    {
                        var pars = m.GetParameters();
                        return pars.Length == 1 &&
                               (pars[0].ParameterType.Name == "Variable" ||
                                pars[0].ParameterType.Name == "Entity");
                    });

                    var result = intMethod?.Invoke(entity, new object[] { variableEntity });
                    var simplified = Simplify(result);

                    return $"' {varName} = ∫({expr}, {variable})\n' {varName} = {simplified}";
                }
                catch (Exception ex)
                {
                    return $"' {varName} = ∫({expr}, {variable})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessSimplify(string line)
        {
            // simplify(expresión)
            var match = Regex.Match(line, @"(\w+)\s*=\s*simplify\((.+)\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;

                try
                {
                    var entity = ParseExpression(expr);
                    var simplified = Simplify(entity);

                    return $"' {varName} = simplify({expr})\n' {varName} = {simplified}";
                }
                catch (Exception ex)
                {
                    return $"' {varName} = simplify({expr})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessExpand(string line)
        {
            // expand(expresión)
            var match = Regex.Match(line, @"(\w+)\s*=\s*expand\((.+)\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;

                try
                {
                    LogDebug($"ProcessExpand: expr={expr}");
                    var entity = ParseExpression(expr);
                    LogDebug($"Entity parsed: {entity}");

                    // Enumerar todos los métodos Expand para evitar ambigüedad
                    var methods = _entityType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                        .Where(m => m.Name == "Expand")
                        .ToArray();

                    LogDebug($"Found {methods.Length} Expand overloads");
                    foreach (var m in methods)
                    {
                        var pars = m.GetParameters();
                        LogDebug($"  - Expand({string.Join(", ", pars.Select(p => p.ParameterType.Name))})");
                    }

                    // Buscar el método que toma Int32 como parámetro (depth)
                    var expandMethod = methods.FirstOrDefault(m =>
                    {
                        var pars = m.GetParameters();
                        return pars.Length == 1 && pars[0].ParameterType == typeof(int);
                    });

                    // Si no se encuentra, buscar método sin parámetros
                    if (expandMethod == null)
                        expandMethod = methods.FirstOrDefault(m => m.GetParameters().Length == 0);

                    LogDebug($"Selected method: {expandMethod?.ToString()}");

                    object result = null;
                    if (expandMethod != null && expandMethod.GetParameters().Length == 1)
                    {
                        // Llamar con profundidad 10
                        result = expandMethod.Invoke(entity, new object[] { 10 });
                    }
                    else if (expandMethod != null)
                    {
                        result = expandMethod.Invoke(entity, null);
                    }
                    LogDebug($"Expand result: {result}");

                    return $"' {varName} = expand({expr})\n' {varName} = {result}";
                }
                catch (Exception ex)
                {
                    LogDebug($"ProcessExpand ERROR: {ex.Message}\n{ex.StackTrace}");
                    return $"' {varName} = expand({expr})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessSolve(string line)
        {
            // solve(ecuación, variable)
            var match = Regex.Match(line, @"(\w+)\s*=\s*solve\((.+?),\s*([a-zA-Z])\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var equation = match.Groups[2].Value;
                var variable = match.Groups[3].Value;

                try
                {
                    var entity = ParseExpression(equation);
                    var solveMethod = _entityType.GetMethod("SolveEquation", new[] { typeof(string) });
                    var result = solveMethod?.Invoke(entity, new object[] { variable });

                    return $"' {varName} = solve({equation}, {variable})\n' Soluciones: {result}";
                }
                catch (Exception ex)
                {
                    return $"' {varName} = solve({equation}, {variable})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessLimit(string line)
        {
            // limit(expresión, x, valor)
            var match = Regex.Match(line, @"(\w+)\s*=\s*limit\((.+?),\s*([a-zA-Z]),\s*(.+?)\)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;
                var variable = match.Groups[3].Value;
                var value = match.Groups[4].Value;

                try
                {
                    LogDebug($"ProcessLimit: expr={expr}, variable={variable}, value={value}");
                    var entity = ParseExpression(expr);
                    LogDebug($"Entity parsed: {entity}");
                    var variableEntity = ParseExpression(variable);
                    LogDebug($"Variable entity: {variableEntity}");
                    var valueEntity = ParseExpression(value);
                    LogDebug($"Value entity: {valueEntity}");

                    var methods = _mathSType.GetMethods(BindingFlags.Public | BindingFlags.Static)
                        .Where(m => m.Name == "Limit")
                        .ToArray();

                    LogDebug($"Found {methods.Length} Limit overloads");
                    foreach (var m in methods)
                    {
                        var pars = m.GetParameters();
                        LogDebug($"  - Limit({string.Join(", ", pars.Select(p => p.ParameterType.Name))})");
                    }

                    // Buscar método con 4 parámetros: (Entity, Entity, Entity, ApproachFrom)
                    var limitMethod = methods.FirstOrDefault(m =>
                    {
                        var pars = m.GetParameters();
                        return pars.Length == 4 &&
                               pars[0].ParameterType == _entityType &&
                               pars[1].ParameterType == _entityType &&
                               pars[2].ParameterType == _entityType &&
                               pars[3].ParameterType.Name == "ApproachFrom";
                    });

                    // Si no se encuentra con 4 parámetros, buscar con 3
                    if (limitMethod == null)
                    {
                        limitMethod = methods.FirstOrDefault(m =>
                        {
                            var pars = m.GetParameters();
                            return pars.Length == 3 &&
                                   pars[0].ParameterType == _entityType &&
                                   pars[1].ParameterType == _entityType &&
                                   pars[2].ParameterType == _entityType;
                        });
                    }

                    LogDebug($"Selected method: {limitMethod?.ToString()}");

                    object result = null;
                    if (limitMethod != null)
                    {
                        var pars = limitMethod.GetParameters();
                        if (pars.Length == 4)
                        {
                            // Obtener el tipo ApproachFrom y usar el valor por defecto (BothSides = 0)
                            var approachFromType = pars[3].ParameterType;
                            var approachFromValue = Enum.GetValues(approachFromType).GetValue(0);
                            result = limitMethod.Invoke(null, new object[] { entity, variableEntity, valueEntity, approachFromValue });
                        }
                        else
                        {
                            result = limitMethod.Invoke(null, new object[] { entity, variableEntity, valueEntity });
                        }
                    }
                    LogDebug($"Limit result: {result}");

                    // Evaluar el límite usando Evaled o InnerSimplified
                    var evaluated = result;
                    try
                    {
                        // Intentar obtener la propiedad Evaled
                        var evaledProp = result?.GetType().GetProperty("Evaled");
                        if (evaledProp != null)
                        {
                            evaluated = evaledProp.GetValue(result);
                            LogDebug($"Limit evaled: {evaluated}");
                        }
                        else
                        {
                            // Intentar InnerSimplified
                            var innerSimplifiedProp = result?.GetType().GetProperty("InnerSimplified");
                            if (innerSimplifiedProp != null)
                            {
                                evaluated = innerSimplifiedProp.GetValue(result);
                                LogDebug($"Limit inner simplified: {evaluated}");
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        LogDebug($"Evaled/InnerSimplified error: {ex.Message}");
                    }

                    // Simplificar el resultado
                    var simplified = Simplify(evaluated);
                    LogDebug($"Limit simplified: {simplified}");

                    return $"' {varName} = limit({expr}, {variable}→{value})\n' {varName} = {simplified}";
                }
                catch (Exception ex)
                {
                    LogDebug($"ProcessLimit ERROR: {ex.Message}\n{ex.StackTrace}");
                    return $"' {varName} = limit({expr}, {variable}→{value})\n' Error: {ex.Message}";
                }
            }

            return null;
        }

        private string ProcessAssignment(string line)
        {
            // Asignación normal: variable = expresión
            var match = Regex.Match(line, @"(\w+)\s*=\s*(.+)");
            if (match.Success)
            {
                var varName = match.Groups[1].Value;
                var expr = match.Groups[2].Value;

                try
                {
                    var entity = ParseExpression(expr);
                    var simplified = Simplify(entity);

                    return $"{varName} = {simplified} ' simplified";
                }
                catch
                {
                    return line; // Si falla, devolver línea original
                }
            }

            return null;
        }

        private string Simplify(object entity)
        {
            if (entity == null) return "";

            try
            {
                // Enumerar todos los métodos Simplify para evitar ambigüedad
                var methods = _entityType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                    .Where(m => m.Name == "Simplify")
                    .ToArray();

                // Buscar el método sin parámetros
                var simplifyMethod = methods.FirstOrDefault(m => m.GetParameters().Length == 0);

                if (simplifyMethod != null)
                {
                    var result = simplifyMethod.Invoke(entity, null);
                    return result?.ToString() ?? entity.ToString();
                }
                else
                {
                    // Si no hay método sin parámetros, devolver la entidad tal cual
                    return entity.ToString();
                }
            }
            catch (Exception ex)
            {
                LogDebug($"Simplify ERROR: {ex.Message}");
                return entity.ToString();
            }
        }

        public override object Evaluate(string expression, IDictionary<string, double> variables)
        {
            if (!_isAvailable)
                throw new InvalidOperationException("AngouriMath not available");

            var entity = ParseExpression(expression);

            // Sustituir variables
            if (variables != null)
            {
                var substituteMethod = _entityType.GetMethod("Substitute", new[] { typeof(string), typeof(double) });
                foreach (var v in variables)
                {
                    entity = substituteMethod?.Invoke(entity, new object[] { v.Key, v.Value });
                }
            }

            // Evaluar numéricamente
            var evalMethod = _entityType.GetMethod("EvalNumerical");
            var result = evalMethod?.Invoke(entity, null);

            return result;
        }

        public override bool Validate(string expression, out string error)
        {
            error = null;

            if (!_isAvailable)
            {
                error = "AngouriMath not available";
                return false;
            }

            try
            {
                ParseExpression(expression);
                return true;
            }
            catch (Exception ex)
            {
                error = ex.Message;
                return false;
            }
        }
    }
}
