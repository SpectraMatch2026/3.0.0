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
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))
    print("Netlify publish directory ready.")


if __name__ == "__main__":
    main()
