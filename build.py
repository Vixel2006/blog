#!/usr/bin/env python3
"""Build blog: convert posts/*.md to HTML with syntax highlighting.
Usage: python3 build.py
"""

import os
import re
import glob
import markdown
from pygments.style import Style
from pygments.token import (
    Keyword, Name, Comment, String, Error, Number,
    Operator, Generic, Whitespace, Punctuation
)
from pygments.formatters import HtmlFormatter


class CatppuccinMocha(Style):
    background_color = "#1e1e2e"
    default_style = "color:#cdd6f4"
    highlight_color = "#313244"
    line_number_color = "#585b70"
    line_number_background_color = "#1e1e2e"

    styles = {
        Comment:        "italic #6c7086",
        Comment.Hashbang: "italic #6c7086",
        Comment.Multiline: "italic #6c7086",
        Comment.Single: "italic #6c7086",
        Comment.Special: "italic #6c7086",
        Comment.Preproc: "italic #6c7086",

        Keyword:        "#cba6f7",
        Keyword.Constant:  "#cba6f7",
        Keyword.Declaration: "#cba6f7",
        Keyword.Namespace: "#f38ba8",
        Keyword.Pseudo: "#cba6f7",
        Keyword.Reserved: "#cba6f7",
        Keyword.Type:   "#f9e2af",

        Name.Attribute: "#89b4fa",
        Name.Builtin:   "#89b4fa",
        Name.Builtin.Pseudo: "#89b4fa",
        Name.Class:     "#f9e2af",
        Name.Constant:  "#fab387",
        Name.Decorator: "#f5c2e7",
        Name.Entity:    "#f5c2e7",
        Name.Exception: "#f38ba8",
        Name.Function:  "#89b4fa",
        Name.Function.Magic: "#89b4fa",
        Name.Label:     "#89b4fa",
        Name.Namespace: "#f9e2af",
        Name.Tag:       "#f38ba8",
        Name.Variable:  "#cdd6f4",
        Name.Variable.Class: "#cdd6f4",
        Name.Variable.Global: "#cdd6f4",
        Name.Variable.Magic: "#cdd6f4",

        String:         "#a6e3a1",
        String.Affix:   "#a6e3a1",
        String.Backtick: "#a6e3a1",
        String.Char:    "#a6e3a1",
        String.Delimiter: "#a6e3a1",
        String.Doc:     "#a6e3a1",
        String.Double:  "#a6e3a1",
        String.Escape:  "#f5c2e7",
        String.Heredoc: "#a6e3a1",
        String.Interpol: "#f5c2e7",
        String.Other:   "#a6e3a1",
        String.Regex:   "#f5c2e7",
        String.Single:  "#a6e3a1",
        String.Symbol:  "#f5c2e7",

        Number:         "#fab387",
        Number.Bin:     "#fab387",
        Number.Float:   "#fab387",
        Number.Hex:     "#fab387",
        Number.Integer: "#fab387",
        Number.Integer.Long: "#fab387",
        Number.Oct:     "#fab387",

        Operator:       "#89dceb",
        Operator.Word:  "#89dceb",

        Punctuation:    "#cdd6f4",

        Generic.Deleted:  "#f38ba8",
        Generic.Emph:     "italic #cdd6f4",
        Generic.Error:    "#f38ba8",
        Generic.Heading:  "#89b4fa",
        Generic.Inserted: "#a6e3a1",
        Generic.Output:   "#6c7086",
        Generic.Prompt:   "#cba6f7",
        Generic.Strong:   "bold #cdd6f4",
        Generic.Subheading: "#89b4fa",
        Generic.Traceback: "#f38ba8",

        Error:          "#f38ba8",
        Whitespace:     "#6c7086",
    }


class CatppuccinLatte(Style):
    background_color = "#eff1f5"
    default_style = "color:#4c4f69"
    highlight_color = "#e6e9ef"
    line_number_color = "#bcc0cc"
    line_number_background_color = "#eff1f5"

    styles = {
        Comment:        "italic #9ca0b0",
        Comment.Hashbang: "italic #9ca0b0",
        Comment.Multiline: "italic #9ca0b0",
        Comment.Single: "italic #9ca0b0",
        Comment.Special: "italic #9ca0b0",
        Comment.Preproc: "italic #9ca0b0",

        Keyword:        "#8839ef",
        Keyword.Constant:  "#8839ef",
        Keyword.Declaration: "#8839ef",
        Keyword.Namespace: "#d20f39",
        Keyword.Pseudo: "#8839ef",
        Keyword.Reserved: "#8839ef",
        Keyword.Type:   "#df8e1d",

        Name.Attribute: "#1e66f5",
        Name.Builtin:   "#1e66f5",
        Name.Builtin.Pseudo: "#1e66f5",
        Name.Class:     "#df8e1d",
        Name.Constant:  "#fe640b",
        Name.Decorator: "#ea76cb",
        Name.Entity:    "#ea76cb",
        Name.Exception: "#d20f39",
        Name.Function:  "#1e66f5",
        Name.Function.Magic: "#1e66f5",
        Name.Label:     "#1e66f5",
        Name.Namespace: "#df8e1d",
        Name.Tag:       "#d20f39",
        Name.Variable:  "#4c4f69",
        Name.Variable.Class: "#4c4f69",
        Name.Variable.Global: "#4c4f69",
        Name.Variable.Magic: "#4c4f69",

        String:         "#40a02b",
        String.Affix:   "#40a02b",
        String.Backtick: "#40a02b",
        String.Char:    "#40a02b",
        String.Delimiter: "#40a02b",
        String.Doc:     "#40a02b",
        String.Double:  "#40a02b",
        String.Escape:  "#ea76cb",
        String.Heredoc: "#40a02b",
        String.Interpol: "#ea76cb",
        String.Other:   "#40a02b",
        String.Regex:   "#ea76cb",
        String.Single:  "#40a02b",
        String.Symbol:  "#ea76cb",

        Number:         "#fe640b",
        Number.Bin:     "#fe640b",
        Number.Float:   "#fe640b",
        Number.Hex:     "#fe640b",
        Number.Integer: "#fe640b",
        Number.Integer.Long: "#fe640b",
        Number.Oct:     "#fe640b",

        Operator:       "#04a5e5",
        Operator.Word:  "#04a5e5",

        Punctuation:    "#4c4f69",

        Generic.Deleted:  "#d20f39",
        Generic.Emph:     "italic #4c4f69",
        Generic.Error:    "#d20f39",
        Generic.Heading:  "#1e66f5",
        Generic.Inserted: "#40a02b",
        Generic.Output:   "#9ca0b0",
        Generic.Prompt:   "#8839ef",
        Generic.Strong:   "bold #4c4f69",
        Generic.Subheading: "#1e66f5",
        Generic.Traceback: "#d20f39",

        Error:          "#d20f39",
        Whitespace:     "#9ca0b0",
    }

POSTS_DIR = "posts"

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Systems &amp; ML Engineer</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="../pygments.css">
</head>
<body>
    <nav><a href="../index.html">← back</a></nav>

    <main>
        <article>
            <h1 class="post-title">{title}</h1>
            <div class="post-meta">{date}</div>
            {content}
        </article>
    </main>

    <footer>
        <p><a href="../index.html">← back to index</a></p>
    </footer>
</body>
</html>"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systems &amp; ML Engineer</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Systems &amp; ML Engineer</h1>
        <div class="subtitle">c / cuda / zig / go</div>
        <p>
            I build performance-critical infrastructure, low-level development tools, and deep learning internals from scratch. I care about mechanical sympathy, high concurrency, and stripping away unnecessary abstraction layers.
        </p>
        <p>
            <a href="https://github.com/Vixel2006" target="_blank">github</a> &middot;
            <a href="mailto:yusufshihata2006@gmail.com">email</a>
        </p>
    </header>

    <main>
        <section>
            <h2>Software &amp; Frameworks</h2>
            <ul>
                <li>
                    <div class="item-row">
                        <a href="https://github.com/Vixel2006/plast" target="_blank">plast</a>
                        <span class="item-detail">c / cuda</span>
                    </div>
                    <span class="desc">A deep learning library written from scratch. Includes hand-optimized CUDA kernels, a custom graph-based scheduler, and a minimal JIT backend to eliminate high-level runtime overhead.</span>
                </li>
                <li>
                    <div class="item-row">
                        <a href="https://argossecops.com" target="_blank">argos</a>
                        <span class="item-detail">go / kafka / redis / c</span>
                    </div>
                    <span class="desc">An intelligent API security engine. Features a zero-allocation high-concurrency ingestion pipeline coupled with a low-latency native detection core designed to parse traffic at line rate.</span>
                </li>
                <li>
                    <div class="item-row">
                        <a href="https://github.com/Vixel2006/GRF" target="_blank">GRF</a>
                        <span class="item-detail">multimodal learning</span>
                    </div>
                    <span class="desc">A pre-print research paper on multimodal fusion layers in transformer architectures, exploring linear-scaling attention mechanisms for vision-language models.</span>
                </li>
            </ul>
        </section>

        <section>
            <h2>Writing &amp; Research Notes</h2>
            <ul>
                {posts_list}
            </ul>
        </section>
    </main>

    <footer>
        <p>No analytics. No tracking. Rendered with raw HTML/CSS.</p>
    </footer>
</body>
</html>"""


def convert_md(text):
    return markdown.markdown(text, extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'md_in_html',
    ])


def extract_title(text):
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    return m.group(1).strip() if m else "Untitled"


def extract_date(filename):
    m = re.search(r'(\d{4}-\d{2})', filename)
    return m.group(1) if m else ""


def post_item_html(title, date, slug):
    date_str = f'<span class="item-detail">{date}</span>' if date else ''
    return (
        f'<li>'
        f'<div class="item-row">'
        f'<a href="posts/{slug}.html">{title}</a>'
        f'{date_str}'
        f'</div>'
        f'</li>'
    )


def generate_pygments_css():
    light = HtmlFormatter(style=CatppuccinLatte).get_style_defs('.codehilite')
    dark = HtmlFormatter(style=CatppuccinMocha).get_style_defs('.codehilite')
    indented = '\n'.join('    ' + l for l in dark.strip().split('\n'))
    combined = f"""{light}
@media (prefers-color-scheme: dark) {{
{indented}
}}"""
    with open("pygments.css", 'w') as f:
        f.write(combined)
    print("  ✓ pygments.css")


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)

    md_files = sorted(glob.glob(f"{POSTS_DIR}/*.md"))
    posts = []

    for path in md_files:
        name = os.path.splitext(os.path.basename(path))[0]

        with open(path) as f:
            raw = f.read()

        title = extract_title(raw)
        date = extract_date(name)

        body_raw = re.sub(r'^#\s.+(\n|$)', '', raw, count=1)
        body_html = convert_md(body_raw.strip())

        page = POST_TEMPLATE.format(title=title, date=date, content=body_html)

        out = os.path.join(POSTS_DIR, f"{name}.html")
        with open(out, 'w') as f:
            f.write(page)

        print(f"  ✓ {path} → {out}")
        posts.append((title, date, name))

    posts.reverse()
    posts_html = '\n'.join(post_item_html(t, d, s) for t, d, s in posts)
    index_html = INDEX_TEMPLATE.replace("{posts_list}", posts_html)

    with open("index.html", 'w') as f:
        f.write(index_html)
    print("  ✓ index.html")

    generate_pygments_css()
    print("Done.")


if __name__ == '__main__':
    main()
