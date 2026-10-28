#!/usr/bin/env python3
"""Compila el curso Ruta Trader.

Lee los módulos en curso/*.md y la plantilla plantilla/app.html, y genera:
  - ruta-trading/index.html  (versión para publicar como Artifact en claude.ai)
  - index.html               (versión independiente para abrir en el navegador o GitHub Pages)

Formato de cada módulo (curso/mNN.md):
  Encabezado entre líneas '---' con id, title, short, hours, level, group.
  '# intro'            texto de presentación del módulo.
  '# lección: Título'  una lección; '## ' son sus secciones.
  '# práctica'         preguntas del módulo.
Bloques especiales dentro de una lección:
  :::clave Título ... :::        idea clave
  :::ejemplo Título ... :::      ejemplo numérico
  :::alerta Título ... :::       advertencia
  :::formula ... :::             fórmula destacada
  :::ejercicio Título ... ??? solución ... :::   ejercicio con solución desplegable
Enlaces abreviados: (yt:búsqueda) YouTube, (gs:búsqueda) Google Scholar.
Preguntas de práctica:
  ? enunciado / - opción / + opción correcta / > explicación
  = enunciado numérico / answer: 10 | tol: 0.5 | unit: USD / > explicación
"""
import json, math, re, sys, urllib.parse
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])


def md(text):
    MD.reset()
    return MD.convert(text)


def expand_links(text):
    def rep(m):
        kind, q = m.group(1), m.group(2)
        base = {"yt": "https://www.youtube.com/results?search_query=",
                "gs": "https://scholar.google.com/scholar?q="}[kind]
        return "](" + base + urllib.parse.quote_plus(q) + ")"
    return re.sub(r"\]\((yt|gs):([^)]+)\)", rep, text)


def slug(s):
    s = s.lower()
    for a, b in zip("áéíóúüñ", "aeiouun"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]


CALLOUT = re.compile(r"^:::(clave|ejemplo|alerta|formula|ejercicio)[ \t]*(.*?)\n(.*?)\n:::[ \t]*$", re.S | re.M)


def render_lesson(body, lid):
    blocks = {}

    def stash(m):
        kind, title, inner = m.group(1), m.group(2).strip(), m.group(3)
        key = f"CALLOUT{len(blocks)}X"
        if kind == "formula":
            html = f'<div class="formula">{md(inner)}</div>'
        elif kind == "ejercicio":
            prob, _, sol = inner.partition("\n???\n")
            html = (f'<div class="callout ejercicio"><p class="callout-t">Ejercicio · {title}</p>{md(prob)}'
                    f'<details class="solve"><summary>Ver solución</summary>{md(sol)}</details></div>')
        else:
            label = {"clave": "Idea clave", "ejemplo": "Ejemplo", "alerta": "Atención"}[kind]
            t = f"{label} · {title}" if title else label
            html = f'<div class="callout {kind}"><p class="callout-t">{t}</p>{md(inner)}</div>'
        blocks[key] = html
        return "\n\n" + key + "\n\n"

    body = CALLOUT.sub(stash, expand_links(body))
    html = md(body)
    for k, v in blocks.items():
        html = html.replace(f"<p>{k}</p>", v)
    outline = []

    def h2(m):
        title = re.sub(r"<[^>]+>", "", m.group(1))
        sid = f"{lid}--{slug(title)}"
        outline.append({"id": sid, "t": title})
        cls = ' class="src-h"' if title.lower().startswith("fuentes") else ""
        return f'<h2 id="{sid}"{cls}>{m.group(1)}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", h2, html)
    html = re.sub(r'(<h2 id="[^"]+" class="src-h">.*?</h2>\s*)<ul>', r'\1<ul class="sources">', html)
    html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    html = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', html)
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    return html, outline, max(4, math.ceil(words / 140))


def parse_quiz(text, mid):
    qs = []
    for i, chunk in enumerate(re.split(r"\n\s*\n(?=[?=] )", "\n" + text.strip())):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        head, rest = lines[0], lines[1:]
        q = {"id": f"{mid}-q{len(qs)+1}", "q": md(head[2:].strip())}
        expl = [l[1:].strip() for l in rest if l.startswith(">")]
        q["e"] = md("\n".join(expl))
        if head.startswith("?"):
            q["type"] = "mc"
            q["o"] = [md(l[1:].strip()) for l in rest if l[:1] in "+-"]
            q["a"] = [l[:1] for l in rest if l[:1] in "+-"].index("+")
        else:
            q["type"] = "num"
            spec = next(l for l in rest if l.startswith("answer:"))
            parts = dict(p.split(":", 1) for p in spec.split("|"))
            parts = {k.strip(): v.strip() for k, v in parts.items()}
            q["ans"] = float(parts["answer"])
            q["tol"] = float(parts.get("tol", "0"))
            q["unit"] = parts.get("unit", "")
        qs.append(q)
    return qs


def parse_module(path):
    raw = path.read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    mod = {"id": meta["id"], "title": meta["title"], "short": meta["short"],
           "hours": int(meta["hours"]), "level": meta["level"], "group": meta["group"],
           "key": meta.get("key") == "si", "lessons": [], "quiz": [], "intro": ""}
    parts = re.split(r"^# (intro|lección:.*|práctica)[ \t]*$", body, flags=re.M)
    if parts[0].strip():
        sys.exit(f"{path.name}: texto antes de la primera sección")
    for head, content in zip(parts[1::2], parts[2::2]):
        head = head.strip()
        if head == "intro":
            mod["intro"] = md(expand_links(content))
        elif head.startswith("lección:"):
            n = len(mod["lessons"]) + 1
            lid = f'{mod["id"]}-{n}'
            html, outline, mins = render_lesson(content, lid)
            mod["lessons"].append({"id": lid, "title": head.split(":", 1)[1].strip(),
                                   "html": html, "outline": outline, "min": mins})
        elif head == "práctica":
            mod["quiz"] = parse_quiz(content, mod["id"])
    return mod


def main():
    mods = [parse_module(p) for p in sorted((ROOT / "curso").glob("m*.md"))]
    data = json.dumps({"modules": mods}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tpl = (ROOT / "plantilla" / "app.html").read_text(encoding="utf-8")
    page = tpl.replace("{{DATA}}", data)
    (ROOT / "ruta-trading").mkdir(exist_ok=True)
    (ROOT / "ruta-trading" / "index.html").write_text(page, encoding="utf-8")
    standalone = ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
                  "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
                  "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
                  "body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n</head>\n<body>\n"
                  + page + "\n</body>\n</html>\n")
    (ROOT / "index.html").write_text(standalone, encoding="utf-8")
    nl = sum(len(m["lessons"]) for m in mods)
    nq = sum(len(m["quiz"]) for m in mods)
    words = sum(len(re.sub(r"<[^>]+>", " ", l["html"]).split()) for m in mods for l in m["lessons"])
    print(f"{len(mods)} módulos · {nl} lecciones · {nq} preguntas · {words} palabras · {len(page)//1024} KB")


if __name__ == "__main__":
    main()
