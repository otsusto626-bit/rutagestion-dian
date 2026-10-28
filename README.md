# Ruta Trader

Curso completo de trading, de cero a operar con método, en una sola página web.

- **12 módulos y 66 lecciones** escritas a fondo dentro de la plataforma: explicaciones, ejemplos numéricos, fórmulas, diagramas y ejercicios resueltos. Cada lección termina con las fuentes de donde sale la información (estudios académicos, documentación oficial, libros, cursos y videos) para verificarla o profundizar.
- **Práctica por módulo**: 123 preguntas de opción múltiple y de cálculo, con explicación de cada respuesta. Un módulo se completa con todas sus lecciones leídas y al menos 70% de respuestas correctas.
- **Herramientas**: calculadoras de tamaño de posición, expectativa y drawdown; glosario con buscador; biblioteca.
- **Avance guardado** automáticamente en el navegador (y en la cuenta del usuario cuando se abre como Artifact en claude.ai).

| Módulo | Tema |
|---|---|
| 00 | La realidad del trading |
| 01 | Fundamentos de finanzas y mercados |
| 02 | Cómo funciona un mercado por dentro |
| 03 | Instrumentos, apalancamiento y derivados |
| 04 | Análisis técnico |
| 05 | Análisis fundamental y macroeconomía |
| 06 | Gestión del riesgo |
| 07 | Psicología y disciplina |
| 08 | Diseñar y probar una estrategia |
| 09 | Práctica supervisada |
| 10 | Regulación, seguridad e impuestos |
| 11 | Trading algorítmico y cuantitativo |

## Uso

Abre `index.html` en el navegador. Para publicarla, activa GitHub Pages en *Settings → Pages* con la rama principal y la carpeta raíz.

## Estructura

- `curso/m00.md` … `curso/m11.md`: el contenido de cada módulo en Markdown (lecciones, ejercicios y preguntas de práctica). El formato está documentado al inicio de `build.py`.
- `plantilla/app.html`: la aplicación (diseño, navegación, práctica, calculadoras, glosario y guardado del avance).
- `build.py`: compila el contenido y la plantilla en `index.html` (versión independiente) y `ruta-trading/index.html` (versión para claude.ai).
- `favicon.svg`: el logo.

Para editar el contenido, cambia los archivos de `curso/` y ejecuta:

```
pip install markdown
python3 build.py
```

> Material educativo. No es asesoría financiera, tributaria ni legal.
