#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "zlel"))

import zlel_p3 as zl3


def run_all_circuits():

    base_dir = os.path.dirname(__file__)
    cir_folder = os.path.join(base_dir, "cirs", "all")

    cir_files = sorted(
        f for f in os.listdir(cir_folder) if f.endswith(".cir")
    )

    print("\n====================================")
    print(" Running ALL circuits (P1 + P2 + P3)")
    print("====================================\n")

    for cir in cir_files:

        filepath = os.path.join(cir_folder, cir)

        print("------------------------------------")
        print("Circuit:", cir)
        print("------------------------------------")

        try:
            zl3.run_file(filepath)

        except Exception as e:
            print("ERROR:", e)

    print("\n============ FINISHED ============\n")


if __name__ == "__main__":

    if len(sys.argv) > 1:

        filename = sys.argv[1]
        zl3.run_file(filename)

    else:

        run_all_circuits()
