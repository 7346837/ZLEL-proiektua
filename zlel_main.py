#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# añadir carpeta zlel al path
sys.path.append(os.path.join(os.path.dirname(__file__), "zlel"))

import zlel_p2 as zl2


if __name__ == "__main__":

    base_dir = os.path.dirname(__file__)
    cir_folder = os.path.join(base_dir, "cirs", "all")

    cir_files = sorted(f for f in os.listdir(cir_folder) if f.endswith(".cir"))

    print("\n=== Ejecutando todos los circuitos ===\n")

    for file in cir_files:

        path = os.path.join(cir_folder, file)

        print("----------------------------------")
        print("Circuito:", file)

        try:
            zl2.run_file(path)
        except SystemExit as e:
            print("ERROR:", e)

    print("\n=== Fin de simulaciones ===")
