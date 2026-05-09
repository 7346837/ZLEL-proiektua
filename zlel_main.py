#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

zlel_path = os.path.join(os.path.dirname(__file__), "zlel")
sys.path.insert(0, zlel_path)

import zlel_p4 as zl4


def run_all_circuits():
    base_dir = os.path.dirname(__file__)
    cir_folder = os.path.join(base_dir, "cirs")

    cir_files = sorted(
        f for f in os.listdir(cir_folder) if f.endswith(".cir")
    )

    for cir in cir_files:
        filepath = os.path.join(cir_folder, cir)

        try:
            zl4.run_file(filepath)
        except SystemExit:
            pass
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            zl4.run_file(filename)
        except SystemExit:
            pass
    else:
        run_all_circuits()
