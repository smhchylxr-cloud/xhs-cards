# xhs-cards

[![ci](https://github.com/smhchylxr-cloud/xhs-cards/actions/workflows/ci.yml/badge.svg)](https://github.com/smhchylxr-cloud/xhs-cards/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![python](https://img.shields.io/badge/python-3.9%2B-blue)

**Render 1080×1440 social card decks from a JSON spec.** Pure Pillow — no browser, no API key, no account.

Designed for the pipeline behind a "one GitHub project a day" account: you keep your copy in a text file, and a single command turns it into a cover plus a few content pages.

![example cover](docs/example-cover.png)

```bash
pip install xhs-cards
xhs-cards build issue.json -o out/
xhs-cards export out/
```

## Why this exists

Most card generators are built for humans clicking around a web page. That breaks down the moment you want to produce 30 posts a week, or run it on a server, or let another program drive it.

|  | Browser-based tools | Image-model generators | **xhs-cards** |
|---|---|---|---|
| Install | Chromium / Playwright (~300 MB) | Docker + API key | **`pip install`, one dependency** |
| Cost per image | 0 | billed per image | **0** |
| Text accuracy | high | text is rendered by a model — names and versions get mangled | **exact, it is real text** |
| Runs in CI / cron | painful | painful | **yes** |
| Output | manual export | manual download | **a list of file paths** |

The point is not prettier cards. The point is that `render()` is a function you can call.

## Quickstart

`issue.json`:

```json
{
  "theme": "ikb",
  "pages": [
    {
      "type": "cover",
      "eyebrow": "每日一个 GITHUB 项目",
      "no": "NO.001",
      "headline": ["把一本技术书", "变成 AI 的", "随身技能"],
      "repo": "acme/awesome-tool",
      "stats": ["★ 12,345 stars", "678 fork", "MIT"],
      "in": "一本书 / 一个 docs 目录",
      "out": "结构化文件 + 术语表",
      "cmd": "npx skills add acme/awesome-tool",
      "hook": ["不是把书塞进上下文，", "是把书拆成能按需翻的技能"]
    },
    {
      "type": "list",
      "eyebrow": "它解决了什么",
      "no": "01 / 01",
      "h2": ["读完就忘", "不是你的错"],
      "items": [
        { "n": "01", "title": "书是线性的，工作不是", "desc": ["翻文档找到的是页码，不是答案。"] }
      ],
      "foot": ["说明", "一行小字备注"]
    }
  ]
}
```

```bash
xhs-cards build issue.json -o out/       # -> out/01_cover.png, out/02_list.png
xhs-cards export out/                    # -> out/upload/01_cover.jpg ...
```

From Python:

```python
from xhs_cards import build, load_spec
build(load_spec("issue.json"), "out/", jpeg=True)
```

## Page types

| Type | Use | Required keys |
|---|---|---|
| `cover` | the hook. One claim, big type | `headline`, `repo`, `stats`, `cmd`, `hook` (+ `in` / `out` optional) |
| `list` | 2–3 numbered arguments | `h2`, `items[{n,title,desc}]` |
| `steps` | how to use it, with commands | `h2`, `steps[{n,title,desc}]` (prefix a line with `$` to render it as a command) |
| `note` | caveats, boundaries, "don't use it when" | `h2`, `blocks[{label,lines}]` |

Every page shares `eyebrow` (small label, top-left) and `no` (top-right marker). `list` / `steps` / `note` also need `foot: [label, text]`.

Themes: `ikb` (Klein blue), `ink` (monochrome), `lemon`. Override the accent with `"accent": [r, g, b]`.

### Compact covers

A cover that carries too much reads as a document in the feed thumbnail. Set `"compact": true` (deck-level or on the cover page) to drop the `in` / `out` / `cmd` block and keep only the headline, the repo and the stats:

```json
{ "theme": "ikb", "compact": true, "pages": [ { "type": "cover", "...": "..." } ] }
```

### Hand-made touches

Clean output reads as generated. `"texture": true` adds a faint paper grain and a vignette, and any page can take pen marks:

```json
{ "type": "cover", "marks": [
  { "kind": "note",      "xy": [96, 968], "text": "这套图就是它出的", "size": 48, "angle": -2.2 },
  { "kind": "underline", "x0": 96, "x1": 560, "y": 1032 },
  { "kind": "circle",    "center": [110, 494], "rx": 46, "ry": 36 },
  { "kind": "highlight", "box": [88, 700, 460, 760], "alpha": 70 }
] }
```

Commands on `steps` pages are drawn as dark terminal pills automatically.

## What it deliberately does not do

- **No AI calls.** You write the copy; this places it.
- **No publishing.** It produces files. Posting stays a human action.
- **No GUI.** It is a library and a CLI.

Keeping those out is why it is ~700 lines instead of a product.

## Fonts

Chinese text needs a CJK font. The loader probes the usual system paths (Windows 微软雅黑, macOS 苹方, Linux Noto CJK). If yours lives elsewhere:

```bash
export XHS_FONT_DIR=/path/to/fonts          # or:
export XHS_FONT_REGULAR=/path/to/regular.ttc
export XHS_FONT_BOLD=/path/to/bold.ttc
export XHS_FONT_MONO=/path/to/mono.ttf
```

On Debian: `apt install fonts-noto-cjk`.

## Layout guarantees

Text is measured with the real font, never estimated, so:

- long lines wrap automatically, CJK breaks anywhere, latin prefers spaces;
- headlines shrink (112 → 72 px) until they fit, then fail loudly rather than overflow;
- if a page still exceeds the 1180 px safe area, `LayoutError` tells you which page and by how much.

## License

MIT
