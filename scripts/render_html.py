#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把园所安全活动（防火 / 防震 / 防拐）Markdown 渲染成单文件 HTML。

用法：
    python render_html.py 方案稿.md
    python render_html.py 总结稿.md -o 输出.html

生成的 HTML 不依赖外部资源，双击即可打开，也可直接 Ctrl+P 打印或存 PDF。
本地照片按 Markdown 图片语法 ``![说明](照片路径)`` 读取并 base64 内嵌进单文件；
图片限宽由 CSS 控制，不做压缩（原图多张时文件会偏大，后续可再接压缩工具）。
"""

import argparse
import base64
import html
import mimetypes
import os
import re
import sys

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


# ---------- 图片内嵌 ----------

IMG_WARN_BYTES = 700 * 1024  # 单图超过约 700KB 记为偏大，提示先压缩
_LARGE_IMAGES: list[str] = []


def compress_image(raw: bytes, mime: str) -> bytes:
    """图片压缩钩子。

    基线仅用标准库，不做解码缩放，原样返回；后续接入 Pillow 等库时，
    可在此按宽度 / 质量压缩后返回字节，再做 base64 内嵌。
    """
    return raw


def embed_image(src, base_dir):
    """读取本地图片并返回 data URI；已是 data URI 则直通；失败返回 None。"""
    if src.startswith("data:"):
        return src
    path = src
    if not os.path.isabs(path) and base_dir:
        path = os.path.join(base_dir, src)
    if not os.path.isfile(path):
        return None
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        ext = os.path.splitext(path)[1].lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".gif": "image/gif", ".webp": "image/webp"}.get(ext, "application/octet-stream")
    try:
        with open(path, "rb") as f:
            raw = f.read()
        if len(raw) > IMG_WARN_BYTES:
            _LARGE_IMAGES.append(f"{os.path.basename(path)}（{len(raw) // 1024}KB）")
        raw = compress_image(raw, mime)
        data = base64.b64encode(raw).decode("ascii")
        return f"data:{mime};base64,{data}"
    except OSError:
        return None


def render_image_line(alt, src, base_dir):
    uri = embed_image(src, base_dir)
    if uri is None:
        return f'<p class="muted">（图片缺失：{html.escape(src)}）</p>'
    caption = html.escape(alt) if alt else ""
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="figure"><img src="{uri}" alt="{html.escape(alt)}">{cap}</figure>'


# ---------- 行内处理 ----------

def inline(text, base_dir=None):
    """转义 + 行内加粗 + 【待填/待核实】高亮；行内图片在 base_dir 下转 data URI。"""
    if base_dir is None:
        t = html.escape(text, quote=False)
    else:
        placeholders = []

        def _stash(m):
            placeholders.append(render_image_line(m.group(1), m.group(2), base_dir))
            return f"\x00{len(placeholders) - 1}\x00"

        t = IMG_RE.sub(_stash, text)
        t = html.escape(t, quote=False)
        for i, ph in enumerate(placeholders):
            t = t.replace(f"\x00{i}\x00", ph)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"【(待填[^】]*)】", r'<span class="todo">【\1】</span>', t)
    t = re.sub(r"【(待核实[^】]*)】", r'<span class="todo">【\1】</span>', t)
    return t


# ---------- 解析 ----------

def parse(md):
    title = None
    meta = []
    sections = []
    cur = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            name = re.sub(r"^[一二三四五六七八九十]+\s*、\s*", "", m.group(1)).strip()
            cur = [name, []]
            sections.append(cur)
            continue
        if cur is None:
            if not line.strip():
                continue
            for k, v in re.findall(r"\*\*(.+?)\*\*[：:]\s*([^　]*)", line):
                meta.append((k.strip(), v.strip()))
            continue
        cur[1].append(line)

    return (title or "园所安全活动稿"), meta, sections


# ---------- 章节渲染 ----------

def render_table(lines, base_dir):
    rows = [l.strip() for l in lines if l.strip().startswith("|")]
    if not rows:
        body = "".join(
            f"<p>{inline(re.sub(r'^\\s*-\\s*', '', l), base_dir)}</p>"
            for l in lines if l.strip()
        )
        return body or '<p class="muted">（未填写）</p>'
    data = []
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        if all(re.match(r"^[-: ]*$", c) for c in cells):
            continue
        data.append(cells)
    if not data:
        return '<p class="muted">（未填写）</p>'
    head, body = data[0], data[1:]
    th = "".join(f"<th>{inline(c, base_dir)}</th>" for c in head)
    trs = "".join(
        "<tr>" + "".join(f"<td>{inline(c, base_dir)}</td>" for c in row) + "</tr>"
        for row in body
    )
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def render_list(lines, base_dir):
    items = []
    plain = []
    for l in lines:
        m = re.match(r"^\s*(?:\d+[.、]\s*|-\s+|\*\s+)(.*)$", l)
        if m and m.group(1).strip():
            items.append(m.group(1).strip())
        elif l.strip():
            plain.append(l.strip())
    if not items and not plain:
        return '<p class="muted">（未填写）</p>'
    out = []
    if items:
        out.append("<ul>" + "".join(f"<li>{inline(x, base_dir)}</li>" for x in items) + "</ul>")
    for l in plain:
        img = IMG_RE.match(l)
        if img:
            out.append(render_image_line(img.group(1), img.group(2), base_dir))
        else:
            out.append(f"<p>{inline(l, base_dir)}</p>")
    return "".join(out)


def render_section(name, lines, base_dir):
    if any(l.strip().startswith("|") for l in lines):
        return render_table(lines, base_dir)
    return render_list(lines, base_dir)


# ---------- 整页模板 ----------

CSS = """
:root{
  --wf-red:#9B1C2C; --wf-red-deep:#7A1420; --wf-gold:#C9A227; --wf-gold-deep:#8A6D1A;
  --wf-paper:#FAF6EE; --wf-ink:#2B2620; --wf-gray:#6B5F52; --line:#ddd3c4;
  --todo:#fff3c4;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:#eee9df; color:var(--wf-ink);
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC","Source Han Sans SC",sans-serif;
  font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased;
}
.toolbar{max-width:210mm;margin:18px auto 0;text-align:right}
.toolbar button{
  font:inherit;font-size:14px;padding:8px 18px;border-radius:6px;border:1px solid var(--line);
  background:#fff;color:var(--wf-ink);cursor:pointer
}
.toolbar button:hover{border-color:var(--wf-red);color:var(--wf-red)}
.sheet{
  max-width:210mm;margin:14px auto 40px;background:#fff;
  padding:16mm 15mm 18mm;box-shadow:0 6px 24px rgba(60,45,25,.12);border-radius:2px;
  border-top:4px solid var(--wf-red);
}
.eyebrow{font-size:12.5px;letter-spacing:.18em;color:var(--wf-gray);margin-bottom:6px}
h1{font-family:Georgia,"Noto Serif SC","Source Han Serif SC",serif;font-size:26px;line-height:1.35;margin:0 0 10px;padding-bottom:10px;border-bottom:2px solid var(--wf-gold)}
.meta{display:flex;flex-wrap:wrap;gap:9px 24px;margin:0 0 4px;padding:0;font-size:14px;color:var(--wf-ink)}
.meta span{display:inline-flex;align-items:baseline}
.meta span strong{color:var(--wf-gray);font-weight:500;margin-right:7px;flex:0 0 auto}
section{margin-top:22px}
h2{font-family:Georgia,"Noto Serif SC","Source Han Serif SC",serif;font-size:17px;margin:0 0 12px;display:flex;align-items:center;gap:9px;color:var(--wf-red-deep)}
h2::before{content:"";width:4px;height:16px;background:var(--wf-gold);border-radius:2px;display:inline-block}
ul{margin:0;padding-left:0;list-style:none}
ul li{position:relative;padding-left:17px;margin:5px 0}
ul li::before{content:"";position:absolute;left:2px;top:11px;width:5px;height:5px;border-radius:50%;background:var(--wf-gold)}
table{width:100%;border-collapse:collapse;font-size:14px;break-inside:avoid;page-break-inside:avoid}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th:first-child,td:first-child{white-space:nowrap}
th{background:var(--wf-paper);font-weight:600;color:var(--wf-red-deep)}
tbody tr:nth-child(even){background:#fcfaf5}
.muted{color:var(--wf-gray)}
.todo{background:var(--todo);border-radius:3px;padding:0 2px}
.figure{margin:10px 0;break-inside:avoid;page-break-inside:avoid}
.figure img{max-width:100%;border:1px solid var(--line);border-radius:4px;display:block}
.figure figcaption{font-size:13px;color:var(--wf-gray);margin-top:4px}
footer{margin-top:26px;padding-top:10px;border-top:1px solid var(--line);font-size:12.5px;color:var(--wf-gray);display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px}
@media print{
  @page{size:A4;margin:12mm 12mm 12mm}
  body{background:#fff;font-size:13.5px;line-height:1.62}
  .toolbar{display:none}
  .sheet{box-shadow:none;margin:0;padding:0;max-width:none;border-top-width:3px}
  .eyebrow{font-size:11px;margin-bottom:3px}
  h1{font-size:21px;margin-bottom:7px;padding-bottom:7px}
  .meta{font-size:12.5px;gap:5px 16px}
  section{margin-top:13px}
  h2{font-size:15px;margin-bottom:7px}
  table{font-size:12.5px}
  th,td{padding:5px 8px}
  footer{margin-top:14px;padding-top:7px}
}
@media (max-width:720px){
  .sheet{padding:20px 16px;margin:0;border-radius:0}
  h1{font-size:21px}
  .meta{font-size:13px}
}
"""


def build_html(title, meta, sections, base_dir):
    meta_html = "".join(
        f"<span><strong>{html.escape(k)}</strong>{inline(v, base_dir)}</span>" for k, v in meta
    )
    body = []
    for name, lines in sections:
        body.append(f"<section><h2>{html.escape(name)}</h2>{render_section(name, lines, base_dir)}</section>")

    is_summary = "总结" in title
    eyebrow = "幼儿园安全活动总结报告（内部留档）" if is_summary else "幼儿园安全活动工作台 · 方案稿（内部初稿）"
    footer_left = "活动总结 · 归档前人工核对数字与影像" if is_summary else "内部初稿 · 人工核定后再上报或对外"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="toolbar"><button onclick="window.print()">打印 / 存 PDF</button></div>
<main class="sheet">
  <header>
    <div class="eyebrow">{eyebrow}</div>
    <h1>{html.escape(title)}</h1>
    <div class="meta">{meta_html}</div>
  </header>
  {''.join(body)}
  <footer>
    <span>{footer_left}</span>
    <span>打印建议：A4 纵向，页边距选"默认"</span>
  </footer>
</main>
</body>
</html>
"""


def render_markdown(md_text, base_dir=None):
    title, meta, sections = parse(md_text)
    return build_html(title, meta, sections, base_dir)


def main():
    ap = argparse.ArgumentParser(description="把园所安全活动 Markdown 渲染为单文件 HTML")
    ap.add_argument("path", help="方案稿 / 总结稿 Markdown 文件")
    ap.add_argument("-o", "--out", default=None, help="输出 HTML 路径（默认同名 .html）")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print(f"[错误] 文件不存在：{args.path}", file=sys.stderr)
        return 2
    if os.path.isdir(args.path):
        print(f"[错误] 传入的是文件夹，请指定具体的 Markdown 文件：{args.path}", file=sys.stderr)
        return 2

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            md = f.read()
    except UnicodeDecodeError:
        print("[错误] 文件编码无法识别，请另存为 UTF-8 编码后再渲染", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"[错误] 文件读取失败：{e}", file=sys.stderr)
        return 2

    if not md.strip():
        print("[错误] 文件内容为空，请先填写稿子再渲染", file=sys.stderr)
        return 2

    base_dir = os.path.dirname(os.path.abspath(args.path))
    try:
        doc = render_markdown(md, base_dir)
        out = args.out or os.path.splitext(args.path)[0] + ".html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(doc)
    except OSError as e:
        print(f"[错误] 输出文件写入失败：{e}", file=sys.stderr)
        return 2

    print(f"[完成] 已生成 HTML：{out}")
    print("[提示] 双击打开即可阅读，Ctrl+P 可直接打印或存 PDF；本地照片已内嵌")
    if _LARGE_IMAGES:
        print(f"[提醒] {len(_LARGE_IMAGES)} 张原图偏大（{', '.join(_LARGE_IMAGES)}），内嵌后 HTML 体积较高；建议出稿前先压缩照片")
    return 0


if __name__ == "__main__":
    sys.exit(main())
