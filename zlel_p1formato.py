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

def cir_parser(FILENAME): #esta creo que directamente tiene que funcionar
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
    with open(FILENAME, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith("."):
                continue

            partes = linea.split()

            #ignorar títulos (una sola palabra)
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

            componentes.append((nombre, nodo1, nodo2, nodo3, nodo4, valor1, valor2, valor3, kontrol))
            #2garren zatia
            cir_el_lista=[]
            cir_nd_lista=[]
            cir_val_lista=[]
            cir_ctrl_lista=[]
            for lista in componentes:
                cir_el_lista.append(lista[0])
                cir_el=np.array(cir_el_lista) #para pasar la lista a array
                cir_el=cir_el.reshape(-1,1) #para poner la matriz en columna

                #PARA HACER NODOAK TIENE QUE TENER 4 COLUMAS, SI NO TIENE 4 COLUMAS, HAY QUE RELLENAR CON CEROS
                cir_nd_lista.append(lista[1:5]) 
                cir_nd=np.array(cir_nd_lista) 

                #balioak lo mismo
                cir_val_lista.append(lista[5:8])
                cir_val=np.array(cir_val_lista)

                cir_ctrl_lista.append(lista[8])
                cir_ctrl=np.array(cir_ctrl_lista)
                cir_ctrl=cir_ctrl.reshape(-1,1)

        return cir_el, cir_nd, cir_val, cir_ctrl
    try:
        cir = np.array(np.loadtxt(FILENAME, dtype=str))
    except ValueError:
        sys.exit("File corrupted: .cir size is incorrect.")

#cir_el, cir_nd, cir_val, cir_ctrl = cir_parser(FILENAME)
    # THIS FUNCTION IS NOT COMPLETE
#elememtu bereziak ateratzeko funtzioa

def elementu_bereziak(cir_el, cir_nd):  #cuando hay 2 elementos solo identifica 1
    elementu_berezien_zerrenda=[]
    hiztegi_transistor={}
    hiztegi_diodo={}
    hiztegi_opamp={}
    nodos_transistor=[]
    nodos_diodo=[]
    nodos_opamp=[]
    for elem, lista in zip(cir_el, cir_nd):
        for letra in elem:
            if letra.startswith("Q"):
                nodos_transistor=lista
                hiztegi_transistor["N_kolektor"]=nodos_transistor[0]
                hiztegi_transistor["N_oinarri"]=nodos_transistor[1]
                hiztegi_transistor["N_igorle"]=nodos_transistor[2]
                #return(elem, hiztegi_transistor)
                elementu_berezien_zerrenda.append(hiztegi_transistor)

            elif letra.startswith("D"):
                nodos_diodo=lista
                hiztegi_diodo["N_terminal+"]=nodos_diodo[0]
                hiztegi_diodo["N_terminal-"]=nodos_diodo[1]
                #return(elem, hiztegi_diodo)
                elementu_berezien_zerrenda.append(hiztegi_diodo)
            elif letra.startswith("A"):
                hiztegi_opamp={}
                nodos_opamp=lista
                hiztegi_opamp["N+"]=nodos_opamp[0]
                hiztegi_opamp["N-"]=nodos_opamp[1]
                hiztegi_opamp["N_out"]=nodos_opamp[2]
                hiztegi_opamp["N_ref(0)"]=nodos_opamp[3]
                #return(elem, hiztegi_opamp)
                elementu_berezien_zerrenda.append(hiztegi_opamp)
    return elementu_berezien_zerrenda
        
#HACER UNA FUNCION APARTE PARA SACAR B,N,NODES,EL_NUM
def get_circuit_info(cir_el, cir_nd):
    b = len(cir_el)
    n = len(set(cir_nd.flatten()))
    nodes = sorted(list(set(cir_nd.flatten())))
    el_num = len(cir_el)
    return b, n, nodes, el_num


#b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)

def circ_nd_berezi_atera(cir_el, cir_nd, b, n, nodes, el_num):

    import numpy as np

    berezi_elem_nodo = elementu_bereziak(cir_el, cir_nd)

    adar_kont = 0
    circ_nd_bereziekin = []
    cir_el_berezi = []

    elem_berezien_kont = 0

    for branch, lista in zip(cir_el, cir_nd):

        if branch[0].startswith("A"):
            nplus = berezi_elem_nodo[elem_berezien_kont]["N+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N-"]
            n_out = berezi_elem_nodo[elem_berezien_kont]["N_out"]
            n_ref = berezi_elem_nodo[elem_berezien_kont]["N_ref(0)"]

            adar_kont += 1
            cir_el_berezi.append([branch[0] + "_in"])
            circ_nd_bereziekin.append((int(nplus), int(nminus)))

            adar_kont += 1
            cir_el_berezi.append([branch[0] + "_out"])
            circ_nd_bereziekin.append((int(n_out), int(n_ref)))

            elem_berezien_kont += 1

        elif branch[0].startswith("Q"):
            oinarri = berezi_elem_nodo[elem_berezien_kont]["N_oinarri"]
            igorle = berezi_elem_nodo[elem_berezien_kont]["N_igorle"]
            kolektor = berezi_elem_nodo[elem_berezien_kont]["N_kolektor"]

            adar_kont += 1
            cir_el_berezi.append([branch[0] + "_be"])
            circ_nd_bereziekin.append((int(oinarri), int(igorle)))

            adar_kont += 1
            cir_el_berezi.append([branch[0] + "_bc"])
            circ_nd_bereziekin.append((int(oinarri), int(kolektor)))

            elem_berezien_kont += 1

        elif branch[0].startswith("D"):
            nplus = berezi_elem_nodo[elem_berezien_kont]["N_terminal+"]
            nminus = berezi_elem_nodo[elem_berezien_kont]["N_terminal-"]

            adar_kont += 1
            cir_el_berezi.append(branch)
            circ_nd_bereziekin.append((int(nminus), int(nplus)))

            elem_berezien_kont += 1

        else:
            adar_kont += 1
            cir_el_berezi.append(branch)
            circ_nd_bereziekin.append((int(lista[0]), int(lista[1])))

    # 🔴 CLAVE: convertir a numpy
    circ_nd_bereziekin = np.array(circ_nd_bereziekin)

    # nodos
    nodo_zerrenda = [0]
    for lista in circ_nd_bereziekin:
        for elem in lista:
            if elem != 0 and elem not in nodo_zerrenda:
                nodo_zerrenda.append(elem)

    nodo_zerrenda_ordenatua = sorted(nodo_zerrenda)
    nodo_zenb = len(nodo_zerrenda)

    # variables
    aldagai_kop = 2 * adar_kont + (nodo_zenb - 1)

    return cir_el_berezi, circ_nd_bereziekin, adar_kont, nodo_zenb, nodo_zerrenda_ordenatua, aldagai_kop

def print_cir_info(cir_el, cir_nd, adar_kont, nodo_zenb, nodo_zerrenda_ordenatua, aldagai_kop):
    """ Prints the info of the circuit:
        |     1.- Elements info
        |     2.- Node info
        |     3.- Branch info
        |     4.- Variable info
    Args:
        | cir_el: reshaped cir_el. 
        | cir_nd: reshaped cir_nd. Now it will be a(b,2) matrix
        | b: # of branches
        | n: # number of nodes
        | nodes: an array with the circuit nodes sorted
        | el_num:  the # of elements

    """
    # Element info
    print(str(aldagai_kop) + ' Elements')
    # Node info
    print(str(nodo_zenb) + ' Different nodes: ' +
          str(nodo_zerrenda_ordenatua))
    # Branch info
    print("\n" + str(adar_kont) + " Branches: ")

    for i in range(1, adar_kont+1):
        indent = 12  # Number of blanks for indent
        string = ("\t" + str(i) + ". branch:\t" +
                  str(cir_el[i-1]) + "i".rjust(indent  - len(cir_el[i-1])) +
                  str(i) + "v".rjust(indent  - len(str(i))) + str(i) +
                  " = e" + str(cir_nd[i-1, 0]) +
                  " - e" + str(cir_nd[i-1, 1]))
        print(string)

    # Variable info
    print("\n" + str(2*adar_kont + (nodo_zenb-1)) + " variables: ")
    # print all the nodes but the first(0 because is sorted)
    for i in nodo_zerrenda_ordenatua[1:]:
        print("e"+str(i)+", ", end="", flush=True)
    for i in range(adar_kont):
        print("i"+str(i+1)+", ", end="", flush=True)
    # print all the branches but the last to close it properly
    # It works because the minuimum amount of branches in a circuit must be 2.
    for i in range(adar_kont-1):
        print("v"+str(i+1)+", ", end="", flush=True)
    print("v"+str(adar_kont))

    # IT IS RECOMMENDED TO USE THIS FUNCTION WITH NO MODIFICATION.

        # IT IS RECOMMENDED TO USE THIS FUNCTION WITH NO MODIFICATION.
         #no funciona hay que arreglarla
def incidence_matrix(branches, nodes):
    Aa = []
    for nodo in nodes:
        fila = []
        for rama in branches:
            #print(rama)
            if nodo == rama[0]:
                fila.append(1)
            elif nodo == rama[1]:
                fila.append(-1)
            else:
                fila.append(0)
        Aa.append(fila)
    return np.array(Aa)
def matrizea_ondo(Aa_matriz_array_benetakoa):
    intzidentzia_mat_irauli =Aa_matriz_array_benetakoa.T
    txarto=0
    for lista in intzidentzia_mat_irauli:
        batuketa=sum(lista)
        if batuketa!=0:
            return False
        else:
            continue
    if txarto==0:
        return True

def A_matrizea(Aamatrizea):
    #lehenengo lerroa 0 nodoarekin erlazionatuta dago, beraz hori kenduko dugu Aa matrize linealki ind lortzeko
    A = np.delete(Aamatrizea, 0, axis=0)
    return A

def run_p1(FILENAME):
    cir_el, cir_nd, cir_val, cir_ctrl = cir_parser(FILENAME)
    b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)
    cir_el_berezi, circ_nd_bereziekin, adar_kont, nodo_zenb, nodo_zerrenda_ordenatua, aldagai_kop = circ_nd_berezi_atera(cir_el, cir_nd, b, n, nodes, el_num)    
    print_cir_info(cir_el_berezi, circ_nd_bereziekin, adar_kont, nodo_zenb, nodo_zerrenda_ordenatua, aldagai_kop)


    Aa_matriz_array_benetakoa = incidence_matrix(circ_nd_bereziekin,nodes)   #Aa_matriz_array_benetako es la intzidentzia matrize.
    #la movida es meter circ_nd_bereziekin que ya esta bien puesto pa que detecte todos los casos y bien detectados
    if matrizea_ondo(Aa_matriz_array_benetakoa)==True:
        print("Incidence Matrix: ")
        print(Aa_matriz_array_benetakoa)
    else:
        print("intzidentzia matrizea ez da zuzena")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cir_karpeta = os.path.join(base_dir, "cirs", "all")

    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
        run_p1(FILENAME)
    else:
        cir_fitxategiak = sorted(f for f in os.listdir(cir_karpeta) if f.endswith(".cir"))

       # print("\n=== P1eko zirkuitu guztiak exekutatzen ===\n")

        for fitx in cir_fitxategiak:
            bidea = os.path.join(cir_karpeta, fitx)


            try:
                run_p1(bidea)
            except Exception as e:
                print("ERROR:", e)

        #print("\n=== Amaiera ===")

#    THIS FUNCTION IS NOT COMPLETE
