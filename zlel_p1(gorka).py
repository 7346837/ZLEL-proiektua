#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: zlel_main.py
    :synopsis:

.. moduleauthor:: YOUR NAME AND E-MAIL


"""

import numpy as np
import sys

# -------------------- Zirkuituko parserra --------------------
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
                if not linea or linea.startswith("."):
                    continue

                partes = linea.split()
                #ignorar títulos (una sola palabra)
                if len(partes) < 4:
                    continue

                nombre = partes[0]
                nodo1, nodo2, nodo3, nodo4 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
                valor1, valor2, valor3 = float(partes[5]), float(partes[6]), float(partes[7])
                kontrol = partes[8]

                componentes.append((nombre, nodo1, nodo2, nodo3, nodo4, valor1, valor2, valor3, kontrol))

        #2garren zatia
        cir_el_lista, cir_nd_lista, cir_val_lista, cir_ctrl_lista = [], [], [], []
        for lista in componentes:
            cir_el_lista.append(lista[0])
            cir_nd_lista.append(lista[1:5])  #PARA HACER NODOAK TIENE QUE TENER 4 COLUMAS, SI NO TIENE 4 COLUMAS, HAY QUE RELLENAR CON CEROS
            cir_val_lista.append(lista[5:8])
            cir_ctrl_lista.append(lista[8])

        cir_el = np.array(cir_el_lista).reshape(-1, 1)
        cir_nd = np.array(cir_nd_lista)
        cir_val = np.array(cir_val_lista)
        cir_ctrl = np.array(cir_ctrl_lista).reshape(-1,1)

        return cir_el, cir_nd, cir_val, cir_ctrl
    except ValueError:
        sys.exit("File corrupted: .cir size is incorrect.")


# -------------------- Elememtu bereziak ateratzeko funtzioa --------------------
def elementu_bereziak(cir_el, cir_nd):
    """
    This function identifies special elements: transistors (Q), diodes (D), and OPAMPs (A)
    and returns a list of dictionaries containing the relevant nodes for each element.

    Args:
        | cir_el: np.array with the elements
        | cir_nd: np.array with the circuit nodes

    Returns:
        elementu_berezien_zerrenda: list of dictionaries with nodes for each special element
"""
    elementu_berezien_zerrenda=[]
    for elem, lista in zip(cir_el, cir_nd):
        letra = elem[0]
        if letra.startswith("Q"):
            elementu_berezien_zerrenda.append({
                "N_kolektor": lista[0],
                "N_oinarri": lista[1],
                "N_igorle": lista[2]
            })
        elif letra.startswith("D"):
            elementu_berezien_zerrenda.append({
                "N_terminal+": lista[0],
                "N_terminal-": lista[1]
            })
        elif letra.startswith("A"):
            elementu_berezien_zerrenda.append({
                "N+": lista[0],
                "N-": lista[1],
                "N_out": lista[2],
                "N_ref(0)": lista[3]
            })
    return elementu_berezien_zerrenda


# -------------------- Zirkuituko informazio orokorra --------------------
def get_circuit_info(cir_el, cir_nd):
    """
    Returns basic information about the circuit: number of branches, unique nodes, 
    sorted list of nodes, and total number of elements.

    Args:
        | cir_el: np.array with the elements
        | cir_nd: np.array with the nodes

    Returns:
        b: number of branches
        n: number of nodes
        nodes: sorted list of unique nodes
        el_num: total number of elements
"""
    b = len(cir_el)
    n = len(set(cir_nd.flatten()))
    nodes = sorted(list(set(cir_nd.flatten())))
    el_num = len(cir_el)
    return b, n, nodes, el_num


# -------------------- Zirkuituaren informazioa eta adarrak ikusteko --------------------
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
    adar_kont=0
    circ_nd_bereziekin=[]
    elem_berezien_kont=0

    for branch, lista in zip(cir_el, cir_nd):
        letra = branch[0]
        if letra.startswith("A"):
            adar_kont += 1
            nplus = berezi_elem_nodo[elem_berezien_kont]["N+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N-"]
            n_out = berezi_elem_nodo[elem_berezien_kont]["N_out"]
            n_ref = berezi_elem_nodo[elem_berezien_kont]["N_ref(0)"]
            circ_nd_bereziekin.append((nminus, n_out))
            print(f" {adar_kont} branch:  {letra}_in    i{adar_kont}     v{adar_kont} = e{nplus} - e{nminus}")
            adar_kont += 1
            circ_nd_bereziekin.append((n_out, n_ref))
            print(f" {adar_kont} branch:  {letra}_out  i{adar_kont}     v{adar_kont} = e{n_out} - e{n_ref}")
            elem_berezien_kont += 1
        elif letra.startswith("Q"):
            adar_kont += 1
            oinarri = berezi_elem_nodo[elem_berezien_kont]["N_oinarri"]
            igorle = berezi_elem_nodo[elem_berezien_kont]["N_igorle"]
            kolektor = berezi_elem_nodo[elem_berezien_kont]["N_kolektor"]
            circ_nd_bereziekin.append((oinarri, igorle))
            print(f" {adar_kont} branch:  {letra}_be    i{adar_kont}     v{adar_kont} = e{oinarri} - e{igorle}")
            adar_kont += 1
            circ_nd_bereziekin.append((oinarri, kolektor))
            print(f" {adar_kont} branch:  {letra}_bc    i{adar_kont}     v{adar_kont} = e{oinarri} - e{kolektor}")
            elem_berezien_kont += 1
        elif letra.startswith("D"):
            adar_kont += 1
            nplus = berezi_elem_nodo[elem_berezien_kont]["N_terminal+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N_terminal-"]
            circ_nd_bereziekin.append((nminus, nplus))
            print(f" {adar_kont} branch:  {letra} diode i{adar_kont}  v{adar_kont} = e{nminus} - e{nplus}")
            elem_berezien_kont += 1
        else:
            adar_kont += 1
            circ_nd_bereziekin.append((lista[0], lista[1]))
            print(f" {adar_kont} branch:  {letra}      i{adar_kont}     v{adar_kont} = e{lista[0]} - e{lista[1]}")

    # Variables generales
    elem_zenb = cir_el.size
    print("\n", elem_zenb, " Elements")
    nodo_zerrenda = [0]
    for lista in cir_nd:
        for elem in lista:
            if elem != 0 and elem not in nodo_zerrenda:
                nodo_zerrenda.append(elem)
    nodo_zerrenda_ordenatua = sorted(nodo_zerrenda)
    nodo_zenb = len(nodo_zerrenda)
    print(nodo_zenb," Different nodes:", np.array(nodo_zerrenda_ordenatua))

    aldagaien_zerrenda = []
    for i in range(1, nodo_zenb):
        aldagaien_zerrenda.append(f"e{nodo_zerrenda[i]}")
    for i in range(1, adar_kont+1):
        aldagaien_zerrenda.append(f"i{i}")
    for i in range(1, adar_kont+1):
        aldagaien_zerrenda.append(f"v{i}")
    aldagai_kop = len(aldagaien_zerrenda)
    print(aldagai_kop,"Variables:", aldagaien_zerrenda)

    return circ_nd_bereziekin


# -------------------- Intzidentzia matrizea --------------------
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
    for lista in Aa_matriz_array_benetakoa.T:
        if sum(lista) != 0:
            return False
    return True
