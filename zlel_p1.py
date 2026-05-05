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
import io
import contextlib

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
    try:
        with open(FILENAME, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                if linea.startswith("."):
                    continue

                partes = linea.split()

                #ignorar títulos (una sola palabra)
                if len(partes) == 1:
                    continue

                if len(partes) != 9:
                    sys.exit("File corrupted: .cir size is incorrect.")

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

        cir_el_lista=[]
        cir_nd_lista=[]
        cir_val_lista=[]
        cir_ctrl_lista=[]
        for lista in componentes:
            cir_el_lista.append(lista[0])
            cir_nd_lista.append(lista[1:5]) 
            cir_val_lista.append(lista[5:8])
            cir_ctrl_lista.append(lista[8])

        cir_el=np.array(cir_el_lista)
        cir_el=cir_el.reshape(-1,1)

        cir_nd=np.array(cir_nd_lista) 
        cir_val=np.array(cir_val_lista)

        cir_ctrl=np.array(cir_ctrl_lista)
        cir_ctrl=cir_ctrl.reshape(-1,1)

        return cir_el, cir_nd, cir_val, cir_ctrl
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
                elementu_berezien_zerrenda.append(hiztegi_transistor.copy())

            elif letra.startswith("D"):
                nodos_diodo=lista
                hiztegi_diodo["N_terminal+"]=nodos_diodo[0]
                hiztegi_diodo["N_terminal-"]=nodos_diodo[1]
                #return(elem, hiztegi_diodo)
                elementu_berezien_zerrenda.append(hiztegi_diodo.copy())
            elif letra.startswith("A"):
                hiztegi_opamp={}
                nodos_opamp=lista
                hiztegi_opamp["N+"]=nodos_opamp[0]
                hiztegi_opamp["N-"]=nodos_opamp[1]
                hiztegi_opamp["N_out"]=nodos_opamp[2]
                hiztegi_opamp["N_ref(0)"]=nodos_opamp[3]
                #return(elem, hiztegi_opamp)
                elementu_berezien_zerrenda.append(hiztegi_opamp.copy())
    return elementu_berezien_zerrenda

#HACER UNA FUNCION APARTE PARA SACAR B,N,NODES,EL_NUM
def get_circuit_info(cir_el, cir_nd):
    b = len(cir_el)
    n = len(set(cir_nd.flatten()))
    nodes = np.array(sorted(list(set(cir_nd.flatten()))))
    el_num = len(cir_el)
    return b, n, nodes, el_num


#b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)

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
    berezi_elem_nodo = elementu_bereziak(cir_el, cir_nd)
    #elementu_berezien_nodoa_lista=elementu_bereziak(cir_el, cir_nd)
    adar_kont=0
    circ_nd_bereziekin=[]
    elem_berezien_kont=0 #elementu bereziaren zenbakia
    adar_izenak=[]
    #elementu_berezien_nodoak=elementu_bereziak(cir_el, cir_nd)[1].values() #saca el hiztegi de los nodos del elemento berezi y luego sus valores
    #print("Branches:",elem_zenb+1) esto tienes que contarlo mas tarde
    for branch, lista in zip(cir_el, cir_nd):
        #for i in range(elementu_berezi_kop): 
            if branch[0].startswith("A"):
                nplus=berezi_elem_nodo[elem_berezien_kont]["N+"]
                nminus=berezi_elem_nodo[elem_berezien_kont]["N-"]
                n_out=berezi_elem_nodo[elem_berezien_kont]["N_out"]
                n_ref=berezi_elem_nodo[elem_berezien_kont]["N_ref(0)"]
                adar_kont+=1
                circ_nd_bereziekin.append((int(nplus),int(nminus)))
                adar_izenak.append(branch[0] + "_in")
                adar_kont+=1
                circ_nd_bereziekin.append((int(n_out),int(n_ref)))
                adar_izenak.append(branch[0] + "_ou")
                elem_berezien_kont+=1
            elif branch[0].startswith("Q"):
                #oinarri=elementu_berezien_nodoak[elem_berezien_kont]["N_oinarri"] # elementu_berezien_nodoak da error, tienes qie poner berezi_elem_nodo
                oinarri=berezi_elem_nodo[elem_berezien_kont]["N_oinarri"]
                igorle=berezi_elem_nodo[elem_berezien_kont]["N_igorle"]
                kolektor=berezi_elem_nodo[elem_berezien_kont]["N_kolektor"]
                adar_kont+=1
                circ_nd_bereziekin.append((int(oinarri),int(igorle))) #en vez de cojer con nombres haz con numeros y fuera
                adar_izenak.append(branch[0] + "_be")
                adar_kont+=1
                circ_nd_bereziekin.append((int(oinarri),int(kolektor)))
                adar_izenak.append(branch[0] + "_bc")
                elem_berezien_kont+=1 
            elif branch[0].startswith("D"): #N+ N- N_out N_ref(0)
                    #EL CASO DE DIODO NO ESTA COMPROBADO, SEGURAMENTE HAYA ALGO MAL
                    nplus=berezi_elem_nodo[elem_berezien_kont]["N_terminal+"]
                    nminus=berezi_elem_nodo[elem_berezien_kont]["N_terminal-"]
                    adar_kont+=1
                    circ_nd_bereziekin.append((nminus,nplus))
                    adar_izenak.append(branch[0])
                    elem_berezien_kont+=1      
            else:
                adar_kont+=1
                circ_nd_bereziekin.append((int(lista[0]),int(lista[1]))) #meter una tupla con los 2 nodos de cada branch normal
                adar_izenak.append(branch[0])

    circ_nd_bereziekin = np.array(circ_nd_bereziekin)

    #aldagaiak zenbakitu
    elem_zenb= cir_el.size
    nodo_zerrenda=[0] #ponemos del tiron el errefrentzia nodoa xq todos lo tienen no?
    for lista in cir_nd:
        for elem in lista:
            if elem != 0 and elem not in nodo_zerrenda:
                nodo_zerrenda.append(elem)
    nodo_zerrenda_ordenatua=np.array(sorted(nodo_zerrenda))
    nodo_zenb= len(nodo_zerrenda)

    print(str(elem_zenb) + ' Elements')
    print(str(nodo_zenb) + ' Different nodes: ' + str(nodo_zerrenda_ordenatua))
    print("\n" + str(len(adar_izenak)) + " Branches: ")

    for i in range(1, len(adar_izenak)+1):
        indent = 12
        string = ("\t" + str(i) + ". branch:\t" +
                  str(adar_izenak[i-1]) + "i".rjust(indent  - len(adar_izenak[i-1])) +
                  str(i) + "v".rjust(indent  - len(str(i))) + str(i) +
                  " = e" + str(circ_nd_bereziekin[i-1, 0]) +
                  " - e" + str(circ_nd_bereziekin[i-1, 1]))
        print(string)

    aldagai_kop = 2*len(adar_izenak) + (nodo_zenb-1)
    print("\n" + str(aldagai_kop) + " variables: ")

    for i in nodo_zerrenda_ordenatua[1:]:
        print("e"+str(i)+", ", end="", flush=True)
    for i in range(len(adar_izenak)):
        print("i"+str(i+1)+", ", end="", flush=True)
    for i in range(len(adar_izenak)-1):
        print("v"+str(i+1)+", ", end="", flush=True)
    print("v"+str(len(adar_izenak)))

    return circ_nd_bereziekin

 
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

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_output_text(filename, text):
    proiektu_erroa = get_project_root()
    outputs_karpeta = os.path.join(proiektu_erroa, 'outputs')
    os.makedirs(outputs_karpeta, exist_ok=True)

    oin_izena = os.path.splitext(os.path.basename(filename))[0]
    irteera_izena = os.path.join(outputs_karpeta, oin_izena + '.out')

    with open(irteera_izena, 'w', encoding='utf-8') as fitx:
        fitx.write(text)

    return irteera_izena

def run_p1(FILENAME):
    irteera_bufferra = io.StringIO()

    try:
        with contextlib.redirect_stdout(irteera_bufferra):
            cir_el, cir_nd, cir_val, cir_ctrl = cir_parser(FILENAME)

            b, n, nodes, el_num = get_circuit_info(cir_el, cir_nd)
            circ_nd_bereziekin= print_cir_info(cir_el, cir_nd, b, n, nodes, el_num) #esta funcion tiene que devolver circ_nd_bereziekin para poder usarlo en la siguiente funcion
            Aa_matriz_array_benetakoa = incidence_matrix(circ_nd_bereziekin,nodes)   #Aa_matriz_array_benetako es la intzidentzia matrize.
            #la movida es meter circ_nd_bereziekin que ya esta bien puesto pa que detecte todos los casos y bien detectados
            if matrizea_ondo(Aa_matriz_array_benetakoa)==True:
                print("Incidence Matrix: ")
                print(Aa_matriz_array_benetakoa)
            else:
                print("intzidentzia matrizea ez da zuzena")

    except SystemExit as errorea:
        print(str(errorea), file=irteera_bufferra)
        testua = irteera_bufferra.getvalue()
        save_output_text(FILENAME, testua)
        return

    testua = irteera_bufferra.getvalue()
    save_output_text(FILENAME, testua)
    print(testua, end='')

def run_all_p1():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cir_karpeta = os.path.join(base_dir, "cirs", "all")

    cir_fitxategiak = sorted(f for f in os.listdir(cir_karpeta) if f.endswith(".cir"))

    for fitx in cir_fitxategiak:
        bidea = os.path.join(cir_karpeta, fitx)

        try:
            run_p1(bidea)
        except SystemExit as errorea:
            save_output_text(bidea, str(errorea))
            continue

if __name__ == "__main__":
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
        run_p1(FILENAME)
    else:
        run_all_p1()

#    THIS FUNCTION IS NOT COMPLETE

