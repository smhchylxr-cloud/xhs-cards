"""Command line: xhs-cards build <spec.json> [-o DIR] [--jpeg]"""

import argparse
import sys

from . import __version__
from .export import export_dir
from .render import build, load_spec


def main(argv=None):
    parser = argparse.ArgumentParser(prog="xhs-cards", description="Render card decks from JSON.")
    parser.add_argument("--version", action="version", version=f"xhs-cards {__version__}")
    sub = parser.add_subparsers(dest="command")

    build_cmd = sub.add_parser("build", help="render every page of a spec")
    build_cmd.add_argument("spec", help="path to issue.json")
    build_cmd.add_argument("-o", "--out", default=None, help="output directory (default: next to spec)")
    build_cmd.add_argument("--jpeg", action="store_true", help="write white-background JPEG instead of PNG")
    build_cmd.add_argument("--quality", type=int, default=92)

    export_cmd = sub.add_parser("export", help="convert a folder of images into upload-ready JPEGs")
    export_cmd.add_argument("src")
    export_cmd.add_argument("-o", "--out", default=None)

    serve_cmd = sub.add_parser("serve", help="open a local web UI (no terminal needed)")
    serve_cmd.add_argument("--port", type=int, default=8000)
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--open", action="store_true", help="open the browser")

    args = parser.parse_args(argv)
    if args.command == "serve":
        from .serve import serve

        serve(host=args.host, port=args.port, open_browser=args.open)
        return 0
    if args.command == "build":
        spec = load_spec(args.spec)
        out = args.out or (args.spec.rsplit(".", 1)[0] + "_out")
        paths = build(spec, out, jpeg=args.jpeg, quality=args.quality)
        for p in paths:
            print(f"  {p}")
        print(f"{len(paths)} page(s) written to {out}")
        return 0

    if args.command == "export":
        out = args.out or (args.src.rstrip("/\\") + "/upload")
        for path, size, nbytes in export_dir(args.src, out):
            print(f"  {path}  {size[0]}x{size[1]}  {nbytes/1024:.1f} KB")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
