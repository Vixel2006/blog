#!/usr/bin/env python3
"""Build blog: convert posts/*.md to HTML with syntax highlighting.
Usage: python3 build.py
"""

import os
import re
import glob
from datetime import datetime
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


POSTS_SRC_DIR = "posts"
POSTS_OUT_DIR = "writing"

GITHUB_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>'
X_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
MAIL_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>'
LINKEDIN_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'

FOOTER_ICONS = f"""    <div class="footer-links">
        <a href="mailto:yusufshihata2006@gmail.com" target="_blank">{MAIL_ICON}</a>
        <a href="https://github.com/Vixel2006" target="_blank">{GITHUB_ICON}</a>
        <a href="https://x.com/this_vixel" target="_blank">{X_ICON}</a>
        <a href="https://www.linkedin.com/in/yusufmohamed2006" target="_blank">{LINKEDIN_ICON}</a>
    </div>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_path}">
    {extra_css}
</head>
<body>
    <nav>
        <a href="{root}index.html" class="site-name">Vixel</a>
        <span class="nav-links">
            <a href="{root}index.html">About</a>
            <a href="{root}writing.html">Writing</a>
            <a href="{root}misc.html">Misc</a>
        </span>
    </nav>
{content}
    <footer>
        {footer_icons}
    </footer>
</body>
</html>"""

INDEX_CONTENT = """    <header>
        <p>
            I&#39;m a self-taught programmer. I taught myself calculus from books at 14, Lagrangian mechanics at 16, and wrote my first line of code at 11. I&#39;ve been programming in C and Python for years, and now I&#39;m all in on Zig — it&#39;s the closest thing to a language that actually respects the programmer. Unfortunately the self-taught label gets taken from me in 2 years when I finish college.
        </p>
        <p>
            I build <a href="https://github.com/Vixel2006/plast" target="_blank">plast</a> (a deep learning engine in C/CUDA) and <a href="https://github.com/Vixel2006/glu" target="_blank">glu</a> (a robotics communication framework in Zig). I want to build a new software stack for robotics from the ground up — no bloat, no abstractions that leak, no corporate rot. I work on infra and research for real AGI with world models and deep learning.
        </p>
        <p>
            This blog is an archive of my journey to becoming a great engineer in the robotics space — or failing badly trying. Philosophy, principles, tech opinions, and incomplete shit.
        </p>
        <p>
            My favorite novel is <em>1984</em>.             I listen to rap and rock &amp; roll.
        </p>
    </header>"""

WRITING_CONTENT = """    <main>
        <h1>Writing</h1>
        <ul>
{posts_list}
        </ul>
    </main>"""

MISC_CONTENT = """    <main>
        <h1>Software &amp; Frameworks</h1>
        <ul>
            <li>
                <div class="item-row">
                    <a href="https://github.com/Vixel2006/glu" target="_blank">glu</a>
                    <span class="item-detail">zig</span>
                </div>
                <span class="desc">A lightweight, high-performance robotics communication framework. Serves as a zero-bloat alternative to ROS2, featuring zero-overhead serialization and deterministic real-time communication.</span>
            </li>
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
    </main>"""

POST_CONTENT = """    <main>
        <article>
            <h1 class="post-title">{title}</h1>
            <div class="post-meta">{date}</div>
            {content}
        </article>
    </main>"""


def render_page(title, content, root="", extra_css=""):
    css_path = root + "style.css"
    return PAGE_TEMPLATE.format(
        title=title,
        content=content,
        root=root,
        css_path=css_path,
        extra_css=extra_css,
        footer_icons=FOOTER_ICONS,
    )


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
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if not m:
        return ""
    dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def post_item_html(title, date, slug):
    date_str = f'<span class="item-detail">{date}</span>' if date else ''
    return (
        f'            <li>'
        f'<div class="item-row">'
        f'<a href="{POSTS_OUT_DIR}/{slug}.html">{title}</a>'
        f'{date_str}'
        f'</div>'
        f'</li>'
    )


def make_slug(filename):
    return os.path.splitext(os.path.basename(filename))[0]


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
    print("  \u2713 pygments.css")


def main():
    os.makedirs(POSTS_OUT_DIR, exist_ok=True)

    md_files = sorted(glob.glob(f"{POSTS_SRC_DIR}/*.md"))
    posts = []

    for path in md_files:
        slug = make_slug(path)

        with open(path) as f:
            raw = f.read()

        title = extract_title(raw)
        date = extract_date(slug)

        body_raw = re.sub(r'^#\s.+(\n|$)', '', raw, count=1)
        body_html = convert_md(body_raw.strip())

        extra_css = '\n    <link rel="stylesheet" href="../pygments.css">'
        post_body = POST_CONTENT.format(title=title, date=date, content=body_html)
        page = render_page(
            f"{title} \u2014 Vixel",
            post_body,
            root="../",
            extra_css=extra_css
        )

        out = os.path.join(POSTS_OUT_DIR, f"{slug}.html")
        with open(out, 'w') as f:
            f.write(page)

        print(f"  \u2713 {path} \u2192 {out}")
        posts.append((title, date, slug))

    posts.reverse()
    posts_html = '\n'.join(post_item_html(t, d, s) for t, d, s in posts)
    writing_body = WRITING_CONTENT.format(posts_list=posts_html)

    index_html = render_page("Vixel", INDEX_CONTENT)
    with open("index.html", 'w') as f:
        f.write(index_html)
    print("  \u2713 index.html")

    writing_html = render_page("Writing \u2014 Vixel", writing_body)
    with open("writing.html", 'w') as f:
        f.write(writing_html)
    print("  \u2713 writing.html")

    misc_html = render_page("Misc \u2014 Vixel", MISC_CONTENT)
    with open("misc.html", 'w') as f:
        f.write(misc_html)
    print("  \u2713 misc.html")

    generate_pygments_css()
    print("Done.")


if __name__ == '__main__':
    main()
