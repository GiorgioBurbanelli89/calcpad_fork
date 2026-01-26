using System;
using Markdig;

var markdown = @"## Tabla de Comparación

| Aspecto | Valor A | Valor B | Suma |
|---------|---------|---------|------|
| Números | 10 | 20 | 30 |
| **Tipo** | Entero | Entero | Entero |
| Estado | ✅ OK | ✅ OK | ✅ OK |
";

var pipeline = new MarkdownPipelineBuilder()
    .UseEmphasisExtras()
    .UseListExtras()
    .UsePipeTables()
    .Build();

var html = Markdown.ToHtml(markdown, pipeline);
Console.WriteLine(html);
