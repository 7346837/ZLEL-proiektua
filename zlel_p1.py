#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: zlel_main.py
    :synopsis:

.. moduleauthor:: YOUR NAME AND E-MAIL


"""

import numpy as np
import sys


def cir_parser(filename): #esta creo que directamente tiene que funcionar
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
    with open(filename, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith("."):
                continue

            partes = linea.split()
            print(partes)

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
        cir = np.array(np.loadtxt(filename, dtype=str))
    except ValueError:
        sys.exit("File corrupted: .cir size is incorrect.")

    # numpy usefull exmaples
    print("================ cir ==========")
    print(cir)
    print("\n======== a = np.array (cir[:,1], dtype = int) ==========")
    a = np.array(cir[:, 1], dtype=int)
    print(a)
    print("\n======== a = np.append(a,300) ==========")
    a = np.append(a, 300)
    print(a)
    print("\n======== b = a[a > 3] ==========")
    b = a[a > 3]
    print(b)
    print("\n======== c = np.unique(a) ==========")
    c = np.unique(a)
    print(c)
    print("\n======== d = np.flatnonzero(a != 0) ==========")
    d = np.flatnonzero(a != 0)
    print(d)
    print("\n======== e = np.flatnonzero(a == 0) ==========")
    e = np.flatnonzero(a == 0)
    print(e)
    print("\n======== f = np.array(cir[:, 1:2]) ==========")
    f = np.array(cir[:, 1:2])
    print(f)
    print("\n======== g = np.array(cir[2:4, :]) ==========")
    g = np.array(cir[2:4, :])
    print(g)
    print("\n======== h = np.empty([0], dtype=int) ==========")
    h = np.empty([0], dtype=int)
    print(h)
    print("\n======== i = np.append(h, 1) ==========")
    i = np.append(h, 1)
    print(i)
    print("\n======== i[0] = 2 ==========")
    i[0] = 2
    print(i)
    print("\n======== j = np.empty([0], dtype=str ==========")
    j = np.empty([0], dtype=str)
    print(j)
    print("\n======== k = np.append(j, \"123456\") ==========")
    k = np.append(j, "123456")
    print(k)
    print("\n======== k[0] = \"987654321\" ==========")
    k[0] = "987654321"
    print(k)
    ''' https://www.geeksforgeeks.org/modify-numpy-array-to-store-an-arbitrary-length-string/
    The dtype of any numpy array containing string values is the maximum
    length of any string present in the array. Once set, it will only be able
    to store new string having length not more than the maximum length at the
    time of the creation. If we try to reassign some another string value
    having length greater than the maximum length of the existing elements,
    it simply discards all the values beyond the maximum length.'''

    # THIS FUNCTION IS NOT COMPLETE

#HACER UNA FUNCION APARTE PARA SACAR B,N,NODES,EL_NUM
 
def print_cir_info(cir_el, cir_nd, b, n, nodes, el_num): #mnuetsra funcion solo tiene cir_el,cir_nd entonces hay qeu adaptarla
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
    # Element info
    print(str(el_num) + ' Elements')
    # Node info
    print(str(n) + ' Different nodes: ' +
          str(nodes))
    # Branch info
    print("\n" + str(b) + " Branches: ")

    for i in range(1, b+1):
        indent = 12  # Number of blanks for indent
        string = ("\t" + str(i) + ". branch:\t" +
                  str(cir_el[i-1]) + "i".rjust(indent  - len(cir_el[i-1])) +
                  str(i) + "v".rjust(indent  - len(str(i))) + str(i) +
                  " = e" + str(cir_nd[i-1, 0]) +
                  " - e" + str(cir_nd[i-1, 1]))
        print(string)

    # Variable info
    print("\n" + str(2*b + (n-1)) + " variables: ")
    # print all the nodes but the first(0 because is sorted)
    for i in nodes[1:]:
        print("e"+str(i)+", ", end="", flush=True)
    for i in range(b):
        print("i"+str(i+1)+", ", end="", flush=True)
    # print all the branches but the last to close it properly
    # It works because the minuimum amount of branches in a circuit must be 2.
    for i in range(b-1):
        print("v"+str(i+1)+", ", end="", flush=True)
    print("v"+str(b))

    # IT IS RECOMMENDED TO USE THIS FUNCTION WITH NO MODIFICATION.

def incidence_matrix(cir_nd, nodo_zerrenda_ordenatua):
    Aa_matriz= []
    #nodo_zerrenda_ordenatua= sorted(nodo_zerrenda). ya la hemos ordenador en la anterior funcion
    for elem in cir_nd:
        lista_A=[]
        for nodo in nodo_zerrenda_ordenatua:
            if elem[0]==nodo:
                lista_A.append(1)
            elif elem[1]==nodo:
                lista_A.append(-1)
            else:
                lista_A.append(0)
        Aa_matriz.append(lista_A)
    Aa_matriz_array=np.array(Aa_matriz)
    Aa_matriz_array_benetakoa= Aa_matriz_array.T
    return Aa_matriz_array_benetakoa

def matrizea_ondo(intzidentzia_matrizea):
    intzidentzia_mat_irauli =intzidentzia_matrizea.T
    txarto=0
    for lista in intzidentzia_mat_irauli:
        batuketa=sum(lista)
        if batuketa!=0:
            print("zerbait txarto dago:(")
            txarto=1
        else:
            continue
    if txarto==0:
        print("matrizea ondo")


"""
https://stackoverflow.com/questions/419163/what-does-if-name-main-do
https://stackoverflow.com/questions/19747371/
python-exit-commands-why-so-many-and-when-should-each-be-used
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "0_zlel_V_R_Q.cir"
    # Parse the circuit
    # [cir_el,cir_nd,cir_val,cir_ctr]=cir_parser(filename)
    cir_parser(filename)

#    THIS FUNCTION IS NOT COMPLETE
