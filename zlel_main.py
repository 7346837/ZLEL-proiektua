#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Añadir la carpeta 'zlel' al path para importar zlel_p1
sys.path.append(os.path.join(os.path.dirname(__file__), "zlel"))

from zlel_p1 import cir_parser, get_circuit_info, print_cir_info, incidence_matrix, matrizea_ondo

if __name__ == "__main__":
    # Si pasas un archivo por argumento
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
    else:
        # Archivo por defecto en la carpeta cirs
        FILENAME = os.path.join(os.path.dirname(__file__), "cirs", "all", "0_zlel_serial_I_IV.cir")

    cir_el, cir_nd, cir_val, cir_ctrl = cir_parser(FILENAME)
    b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)
    circ_nd_bereziekin = print_cir_info(cir_el, cir_nd, b, n, nodes, el_num)

    Aa_matriz_array_benetakoa = incidence_matrix(circ_nd_bereziekin, nodes)

    if matrizea_ondo(Aa_matriz_array_benetakoa):
        print("Incidence Matrix :")
        print(Aa_matriz_array_benetakoa)
    else:
        print("intzidentzia matrizea ez da zuzena")
