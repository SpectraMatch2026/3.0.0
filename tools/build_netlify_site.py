#!/usr/bin/env python3
"""Assemble a static site folder for Netlify (no Flask required on hosting)."""
from __future__ import annotations

import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "netlify_publish")


def main() -> None:
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    shutil.copy2(
        os.path.join(ROOT, "templates", "index.html"),
        os.path.join(OUT, "index.html"),
    )
    # Product datasheets landing: /datasheets/ (served as index in folder)
    datasheets_dir = os.path.join(OUT, "datasheets")
    os.makedirs(datasheets_dir, exist_ok=True)
    shutil.copy2(
        os.path.join(ROOT, "templates", "datasheets.html"),
        os.path.join(datasheets_dir, "index.html"),
    )
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))
    # Short URLs: /datasheetEN.pdf and /datasheetTR.pdf
    en_pdf = os.path.join(ROOT, "static", "DataSheets", "Datasheet_EN.pdf")
    tr_pdf = os.path.join(ROOT, "static", "DataSheets", "Datasheet_TR.pdf")
    for src, name in ((en_pdf, "datasheetEN.pdf"), (tr_pdf, "datasheetTR.pdf")):
        if not os.path.isfile(src):
            raise FileNotFoundError(
                f"Build requires datasheet PDF: missing {os.path.relpath(src, ROOT)}"
            )
        shutil.copy2(src, os.path.join(OUT, name))
    print("Netlify publish directory ready.")


if __name__ == "__main__":
    main()
