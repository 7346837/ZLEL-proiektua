#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: zlel_main.py
    :synopsis:

.. moduleauthor:: YOUR NAME AND E-MAIL
"""

import numpy as np
import sys
import os


def cir_parser(FILENAME):
    """
        This function takes a .cir test circuit and parse it into
        4 matices.
        If the file has not the proper dimensions it warns and exit.

    Args:
        filename: string with the name of the file

    Returns:
        | cir_el: np array of strings with the elements to parse. size(1,b)
        | cir_nd: np array with the nodes to the circuit. size(b,4)
        | cir_val: np array with the values of the elements. size(b,3)
        | cir_ctrl: np array of strings with the element which branch
        | controls the controlled sources. size(1,b)

    Rises:
        SystemExit
    """
    componentes = []

    try:
        with open(FILENAME, "r") as f:
            for linea in f:
                linea = linea.strip()

                if not linea:
                    continue
                if linea.startswith("."):
                    continue

                partes = linea.split()

                if len(partes) < 4:
                    continue

                nombre = partes[0]
                nodo1 = int(partes[1])
                nodo2 = int(partes[2])
                nodo3 = int(partes[3])
                nodo4 = int(partes[4])
                valor1 = float(partes[5])
                valor2 = float(partes[6])
                valor3 = float(partes[7])
                kontrol = partes[8]

                componentes.append(
                    (nombre, nodo1, nodo2, nodo3, nodo4,
                     valor1, valor2, valor3, kontrol)
                )

        cir_el_lista = []
        cir_nd_lista = []
        cir_val_lista = []
        cir_ctrl_lista = []

        for lista in componentes:
            cir_el_lista.append(lista[0])
            cir_nd_lista.append(lista[1:5])
            cir_val_lista.append(lista[5:8])
            cir_ctrl_lista.append(lista[8])

        cir_el = np.array(cir_el_lista, dtype=str).reshape(-1, 1)
        cir_nd = np.array(cir_nd_lista, dtype=int)
        cir_val = np.array(cir_val_lista, dtype=float)
        cir_ctrl = np.array(cir_ctrl_lista, dtype=str).reshape(-1, 1)

        return cir_el, cir_nd, cir_val, cir_ctrl

    except ValueError:
        sys.exit("File corrupted: .cir size is incorrect.")


def elementu_bereziak(cir_el, cir_nd):
    elementu_berezien_zerrenda = []

    for elem, lista in zip(cir_el, cir_nd):
        for letra in elem:
            if letra.startswith("Q"):
                hiztegi_transistor = {}
                hiztegi_transistor["N_kolektor"] = lista[0]
                hiztegi_transistor["N_oinarri"] = lista[1]
                hiztegi_transistor["N_igorle"] = lista[2]
                elementu_berezien_zerrenda.append(hiztegi_transistor)

            elif letra.startswith("D"):
                hiztegi_diodo = {}
                hiztegi_diodo["N_terminal+"] = lista[0]
                hiztegi_diodo["N_terminal-"] = lista[1]
                elementu_berezien_zerrenda.append(hiztegi_diodo)

            elif letra.startswith("A"):
                hiztegi_opamp = {}
                hiztegi_opamp["N+"] = lista[0]
                hiztegi_opamp["N-"] = lista[1]
                hiztegi_opamp["N_out"] = lista[2]
                hiztegi_opamp["N_ref(0)"] = lista[3]
                elementu_berezien_zerrenda.append(hiztegi_opamp)

    return elementu_berezien_zerrenda


def get_circuit_info(cir_el, cir_nd):
    b = len(cir_el)
    n = len(set(cir_nd.flatten()))
    nodes = np.array(sorted(list(set(cir_nd.flatten()))))
    el_num = len(cir_el)
    return b, n, nodes, el_num


def print_cir_info(cir_el, cir_nd, b, n, nodes, el_num):
    """ Prints the info of the circuit:
        |     1.- Elements info
        |     2.- Node info
        |     3.- Branch info
        |     4.- Variable info
    Args:
        | cir_el: reshaped cir_el
        | cir_nd: reshaped cir_nd. Now it will be a(b,2) matrix
        | b: # of branches
        | n: # number of nodes
        | nodes: an array with the circuit nodes sorted
        | el_num:  the # of elements
    """

    berezi_elem_nodo = elementu_bereziak(cir_el, cir_nd)

    adar_kont = 0
    circ_nd_bereziekin = []
    adar_izenak = []
    elem_berezien_kont = 0

    for branch, lista in zip(cir_el, cir_nd):

        if branch[0].startswith("A"):
            nplus = berezi_elem_nodo[elem_berezien_kont]["N+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N-"]
            n_out = berezi_elem_nodo[elem_berezien_kont]["N_out"]
            n_ref = berezi_elem_nodo[elem_berezien_kont]["N_ref(0)"]

            adar_kont += 1
            circ_nd_bereziekin.append((int(nplus), int(nminus)))
            adar_izenak.append(branch[0] + "_in")

            adar_kont += 1
            circ_nd_bereziekin.append((int(n_out), int(n_ref)))
            adar_izenak.append(branch[0] + "_out")

            elem_berezien_kont += 1

        elif branch[0].startswith("Q"):
            oinarri = berezi_elem_nodo[elem_berezien_kont]["N_oinarri"]
            igorle = berezi_elem_nodo[elem_berezien_kont]["N_igorle"]
            kolektor = berezi_elem_nodo[elem_berezien_kont]["N_kolektor"]

            adar_kont += 1
            circ_nd_bereziekin.append((int(oinarri), int(igorle)))
            adar_izenak.append(branch[0] + "_be")

            adar_kont += 1
            circ_nd_bereziekin.append((int(oinarri), int(kolektor)))
            adar_izenak.append(branch[0] + "_bc")

            elem_berezien_kont += 1

        elif branch[0].startswith("D"):
            nplus = berezi_elem_nodo[elem_berezien_kont]["N_terminal+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N_terminal-"]

            adar_kont += 1
            circ_nd_bereziekin.append((int(nminus), int(nplus)))
            adar_izenak.append(branch[0])

            elem_berezien_kont += 1

        else:
            adar_kont += 1
            circ_nd_bereziekin.append((int(lista[0]), int(lista[1])))
            adar_izenak.append(branch[0])

    circ_nd_bereziekin = np.array(circ_nd_bereziekin, dtype=int)
    adar_izenak = np.array(adar_izenak, dtype=str)

    print(str(el_num) + ' Elements')
    print(str(len(nodes)) + ' Different nodes: ' + str(nodes))
    print("\n" + str(len(adar_izenak)) + " Branches: ")

    for i in range(1, len(adar_izenak) + 1):
        indent = 12
        string = (
            "\t" + str(i) + ". branch:\t" +
            str(adar_izenak[i - 1]) +
            "i".rjust(indent - len(str(adar_izenak[i - 1]))) +
            str(i) +
            "v".rjust(indent - len(str(i))) +
            str(i) +
            " = e" + str(circ_nd_bereziekin[i - 1, 0]) +
            " - e" + str(circ_nd_bereziekin[i - 1, 1])
        )
        print(string)

    print("\n" + str(2 * len(adar_izenak) + (len(nodes) - 1)) + " variables: ")

    for i in nodes[1:]:
        print("e" + str(i) + ", ", end="", flush=True)
    for i in range(len(adar_izenak)):
        print("i" + str(i + 1) + ", ", end="", flush=True)
    for i in range(len(adar_izenak) - 1):
        print("v" + str(i + 1) + ", ", end="", flush=True)
    print("v" + str(len(adar_izenak)))

    return circ_nd_bereziekin


def incidence_matrix(branches, nodes):
    Aa = []
    for nodo in nodes:
        fila = []
        for rama in branches:
            if nodo == rama[0]:
                fila.append(1)
            elif nodo == rama[1]:
                fila.append(-1)
            else:
                fila.append(0)
        Aa.append(fila)
    return np.array(Aa)


def matrizea_ondo(Aa_matriz_array_benetakoa):
    intzidentzia_mat_irauli = Aa_matriz_array_benetakoa.T
    txarto = 0
    for lista in intzidentzia_mat_irauli:
        batuketa = sum(lista)
        if batuketa != 0:
            return False
        else:
            continue
    if txarto == 0:
        return True


def A_matrizea(Aamatrizea):
    A = np.delete(Aamatrizea, 0, axis=0)
    return A


def run_p1(FILENAME):
    cir_el, cir_nd, cir_val, cir_ctrl = cir_parser(FILENAME)

    b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)
    circ_nd_bereziekin = print_cir_info(cir_el, cir_nd, b, n, nodes, el_num)
    Aa_matriz_array_benetakoa = incidence_matrix(circ_nd_bereziekin, nodes)

    if matrizea_ondo(Aa_matriz_array_benetakoa) is True:
        print("\nIncidence Matrix: ")
        print(Aa_matriz_array_benetakoa)
    else:
        print("intzidentzia matrizea ez da zuzena")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        FILENAME = os.path.join(base_dir, "cirs", "all", "0_zlel_V_R_Q.cir")

    run_p1(FILENAME)
