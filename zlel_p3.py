#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

.. module:: zlel_p3.py
    :synopsis: 3. praktikako zirkuitu ez-linealak

.. moduleauthor:: YOUR NAME AND E-MAIL

"""

import os
import sys
import math
import io
import contextlib
import numpy as np

if __name__ == "zlel.zlel_p3":
    import zlel.zlel_p1 as zl1
    import zlel.zlel_p2 as zl2
else:
    import zlel_p1 as zl1
    import zlel_p2 as zl2


def cir_parser_p3(filename):
    osagaiak = []

    with open(filename, 'r') as fitx:
        for lerroa in fitx:
            lerroa = lerroa.strip()

            if not lerroa:
                continue
            if lerroa.startswith('.'):
                continue

            zatiak = lerroa.split()

            if len(zatiak) < 9:
                continue

            try:
                izena = zatiak[0]
                n1 = int(zatiak[1])
                n2 = int(zatiak[2])
                n3 = int(zatiak[3])
                n4 = int(zatiak[4])
                bal1 = float(zatiak[5])
                bal2 = float(zatiak[6])
                bal3 = float(zatiak[7])
                kontrol = zatiak[8]
            except Exception:
                continue

            osagaiak.append((izena, n1, n2, n3, n4, bal1, bal2, bal3, kontrol))

    if len(osagaiak) == 0:
        sys.exit("File corrupted: .cir size is incorrect.")

    cir_el = np.array([elem[0] for elem in osagaiak], dtype=str).reshape(-1, 1)
    cir_nd = np.array([elem[1:5] for elem in osagaiak], dtype=int)
    cir_val = np.array([elem[5:8] for elem in osagaiak], dtype=float)
    cir_ctrl = np.array([elem[8] for elem in osagaiak], dtype=str).reshape(-1, 1)

    return cir_el, cir_nd, cir_val, cir_ctrl


def parse_analyses(filename):
    analisi_zerrenda = []

    with open(filename, 'r') as fitx:
        for lerroa in fitx:
            lerroa = lerroa.strip()

            if not lerroa:
                continue

            zatiak = lerroa.split()

            if zatiak and zatiak[0].startswith('.'):
                analisi_zerrenda.append(zatiak)

    return analisi_zerrenda


def expand_for_p3(cir_el, cir_nd, cir_val, cir_ctrl):
    cir_el_zabalduta = []
    cir_nd_zabalduta = []
    cir_val_zabalduta = []
    cir_ctrl_zabalduta = []

    for i in range(len(cir_el)):
        elem_izena = str(cir_el[i][0])
        elem_mota = elem_izena[0].upper()

        if elem_mota == 'A':
            cir_el_zabalduta.append(elem_izena + '_in')
            cir_nd_zabalduta.append([int(cir_nd[i][0]), int(cir_nd[i][1])])
            cir_val_zabalduta.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            cir_ctrl_zabalduta.append(str(cir_ctrl[i][0]))

            cir_el_zabalduta.append(elem_izena + '_out')
            cir_nd_zabalduta.append([int(cir_nd[i][2]), int(cir_nd[i][3])])
            cir_val_zabalduta.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            cir_ctrl_zabalduta.append(str(cir_ctrl[i][0]))

        elif elem_mota == 'Q':
            kolektorea = int(cir_nd[i][0])
            oinarria = int(cir_nd[i][1])
            igorlea = int(cir_nd[i][2])

            cir_el_zabalduta.append(elem_izena + '_be')
            cir_nd_zabalduta.append([oinarria, igorlea])
            cir_val_zabalduta.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            cir_ctrl_zabalduta.append(str(cir_ctrl[i][0]))

            cir_el_zabalduta.append(elem_izena + '_bc')
            cir_nd_zabalduta.append([oinarria, kolektorea])
            cir_val_zabalduta.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            cir_ctrl_zabalduta.append(str(cir_ctrl[i][0]))

        else:
            cir_el_zabalduta.append(elem_izena)
            cir_nd_zabalduta.append([int(cir_nd[i][0]), int(cir_nd[i][1])])
            cir_val_zabalduta.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            cir_ctrl_zabalduta.append(str(cir_ctrl[i][0]))

    cir_elx = np.array(cir_el_zabalduta, dtype=str).reshape(-1, 1)
    cir_ndx = np.array(cir_nd_zabalduta, dtype=int)
    cir_valx = np.array(cir_val_zabalduta, dtype=float)
    cir_ctrlx = np.array(cir_ctrl_zabalduta, dtype=str).reshape(-1, 1)
    nodoak = np.array(sorted(set(cir_ndx.flatten())), dtype=int)

    return cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak


def print_cir_info_p3(cir_el, cir_nd):
    adar_kont = 0
    circ_nd_bereziekin = []
    adar_inprimatzeko = []

    for i in range(len(cir_el)):
        elem_izena = cir_el[i][0]
        elem_mota = elem_izena[0].upper()
        nodoak = cir_nd[i]

        if elem_mota == 'A':
            adar_kont += 1
            circ_nd_bereziekin.append((int(nodoak[0]), int(nodoak[1])))
            adar_inprimatzeko.append(
                f"\t{adar_kont}. branch:\t{elem_izena}_in\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[0]} - e{nodoak[1]}"
            )

            adar_kont += 1
            circ_nd_bereziekin.append((int(nodoak[2]), int(nodoak[3])))
            adar_inprimatzeko.append(
                f"\t{adar_kont}. branch:\t{elem_izena}_out\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[2]} - e{nodoak[3]}"
            )

        elif elem_mota == 'Q':
            adar_kont += 1
            circ_nd_bereziekin.append((int(nodoak[1]), int(nodoak[2])))
            adar_inprimatzeko.append(
                f"\t{adar_kont}. branch:\t{elem_izena}_be\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[1]} - e{nodoak[2]}"
            )

            adar_kont += 1
            circ_nd_bereziekin.append((int(nodoak[1]), int(nodoak[0])))
            adar_inprimatzeko.append(
                f"\t{adar_kont}. branch:\t{elem_izena}_bc\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[1]} - e{nodoak[0]}"
            )

        else:
            adar_kont += 1
            circ_nd_bereziekin.append((int(nodoak[0]), int(nodoak[1])))
            adar_inprimatzeko.append(
                f"\t{adar_kont}. branch:\t{elem_izena}\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[0]} - e{nodoak[1]}"
            )

    elem_zenb = len(cir_el)
    nodo_zerrenda = sorted(set(cir_nd.flatten()))
    nodo_zenb = len(nodo_zerrenda)

    aldagaien_zerrenda = []
    for nodoa in nodo_zerrenda:
        if nodoa != 0:
            aldagaien_zerrenda.append(f"e{nodoa}")
    for i in range(1, adar_kont + 1):
        aldagaien_zerrenda.append(f"i{i}")
    for i in range(1, adar_kont + 1):
        aldagaien_zerrenda.append(f"v{i}")

    print(f"{elem_zenb} Elements")
    print(f"{nodo_zenb} Different nodes: {np.array(nodo_zerrenda)}")
    print("")
    print(f"{adar_kont} Branches: ")
    for lerroa in adar_inprimatzeko:
        print(lerroa)
    print("")
    print(f"{len(aldagaien_zerrenda)} variables: ")
    print(", ".join(aldagaien_zerrenda))
    print("")

    return circ_nd_bereziekin, nodo_zerrenda


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


def reduced_incidence(cir_ndx, nodes):
    Aa = incidence_matrix(cir_ndx.tolist(), list(nodes))
    erreferentzia_ind = list(nodes).index(0)
    A = np.delete(Aa, erreferentzia_ind, axis=0)
    return Aa, A


def check_reference_node(nodes):
    if 0 not in nodes:
        sys.exit('Reference node "0" is not defined in the circuit.')


def check_floating_nodes(Aa, nodes):
    for i, nodoa in enumerate(nodes):
        if np.count_nonzero(Aa[i, :]) == 1:
            sys.exit(f'Node {nodoa} is floating.')


def source_fixed_value(branch_name, branch_values, tr_mode=False, t=0.0):
    elem_mota = branch_name[0].upper()

    if elem_mota in ('V', 'I', 'R', 'E', 'G', 'H', 'F'):
        return float(branch_values[0])

    if elem_mota in ('B', 'Y'):
        anplitudea = float(branch_values[0])
        maiztasuna = float(branch_values[1])
        fasea = float(branch_values[2])

        if tr_mode:
            return anplitudea * math.sin(2 * math.pi * maiztasuna * t + math.pi / 180.0 * fasea)

        return anplitudea

    return float(branch_values[0])


def check_parallel_voltage_sources(cir_elx, cir_ndx, cir_valx):
    tentsio_iturri_indizeak = []

    for i in range(len(cir_elx)):
        elem_mota = cir_elx[i][0][0].upper()
        if elem_mota in ('V', 'B'):
            tentsio_iturri_indizeak.append(i)

    for a in range(len(tentsio_iturri_indizeak)):
        i = tentsio_iturri_indizeak[a]
        n1_i, n2_i = int(cir_ndx[i][0]), int(cir_ndx[i][1])
        balio_i = source_fixed_value(cir_elx[i][0], cir_valx[i], tr_mode=False)

        for b in range(a + 1, len(tentsio_iturri_indizeak)):
            j = tentsio_iturri_indizeak[b]
            n1_j, n2_j = int(cir_ndx[j][0]), int(cir_ndx[j][1])
            balio_j = source_fixed_value(cir_elx[j][0], cir_valx[j], tr_mode=False)

            if n1_i == n1_j and n2_i == n2_j:
                if abs(balio_i - balio_j) > 1e-12:
                    sys.exit(f'Parallel V sources at branches {i} and {j}.')
            elif n1_i == n2_j and n2_i == n1_j:
                if abs(balio_i + balio_j) > 1e-12:
                    sys.exit(f'Parallel V sources at branches {i} and {j}.')


def check_series_current_sources(cir_elx, cir_ndx, cir_valx, Aa, nodes):
    for lerro_ind in range(len(nodes)):
        konektatutako_adarrak = np.flatnonzero(Aa[lerro_ind, :] != 0)

        if len(konektatutako_adarrak) < 2:
            continue

        denak_korronte_iturriak = True
        kcl_batura = 0.0
        zero_ez_direnak = 0

        for adar_ind in konektatutako_adarrak:
            elem_mota = cir_elx[adar_ind][0][0].upper()

            if elem_mota not in ('I', 'Y'):
                denak_korronte_iturriak = False
                break

            sinatutako_balioa = Aa[lerro_ind, adar_ind] * source_fixed_value(
                cir_elx[adar_ind][0], cir_valx[adar_ind], tr_mode=False
            )
            kcl_batura += sinatutako_balioa

            if abs(sinatutako_balioa) > 1e-12:
                zero_ez_direnak += 1

        if denak_korronte_iturriak and zero_ez_direnak == len(konektatutako_adarrak) and abs(kcl_batura) > 1e-12:
            sys.exit(f'I sources in series at node {nodes[lerro_ind]}.')


def diode_NR(I0, nD, Vdj):
    """ https://documentation.help/Sphinx/math.html
        Calculates the g and the I of a diode for a NR discrete equivalent
        Given,

        :math:`Id = I_0(e^{(\\frac{V_d}{nV_T})}-1)`

        The NR discrete equivalent will be,

        :math:`i_{j+1} + g v_{j+1} = I`

        where,

        :math:`g = -\\frac{I_0}{nV_T}e^{(\\frac{V_d}{nV_T})}`

        and

        :math:`I = I_0(e^{(\\frac{V_{dj}}{nV_T})}-1) + gV_{dj}`

    Args:
        | I0: Value of I0.
        | nD: Value of nD.
        | Vdj: Value of Vd in the current iteration.

    Return:
        | gd: Conductance of the NR discrete equivalent for the diode.
        | Id: Current independent source of the NR discrete equivalent.
    """
    Vt = 8.6173324e-5 * 300 * nD
    exp_term = math.exp(Vdj / Vt)

    gd = -(I0 / Vt) * exp_term
    Id = I0 * (exp_term - 1.0) + gd * Vdj

    return gd, Id


def transistor_NR(IES, ICS, betaF, VBEj, VBCj):
    Vt = 8.6173324e-5 * 300
    alphaF = betaF / (1.0 + betaF)
    alphaR = (IES / ICS) * alphaF

    exp_be = math.exp(VBEj / Vt)
    exp_bc = math.exp(VBCj / Vt)

    iE = IES * (exp_be - 1.0) - alphaR * ICS * (exp_bc - 1.0)
    iC = -alphaF * IES * (exp_be - 1.0) + ICS * (exp_bc - 1.0)

    g11 = -(IES / Vt) * exp_be
    g12 = (alphaR * ICS / Vt) * exp_bc
    g21 = (alphaF * IES / Vt) * exp_be
    g22 = -(ICS / Vt) * exp_bc

    IE = iE + g11 * VBEj + g12 * VBCj
    IC = iC + g21 * VBEj + g22 * VBCj

    return g11, g12, g21, g22, IE, IC


def nonlinear_branch_indices(cir_elx):
    diodo_indizeak = []
    transistor_pareak = []

    for i in range(len(cir_elx)):
        elem_izena_maius = cir_elx[i][0].upper()

        if elem_izena_maius.startswith('D'):
            diodo_indizeak.append(i)

        elif elem_izena_maius.startswith('Q') and elem_izena_maius.endswith('_BE'):
            oina = elem_izena_maius[:-3]
            bc_izena = oina + '_BC'
            for j in range(len(cir_elx)):
                if cir_elx[j][0].upper() == bc_izena:
                    transistor_pareak.append((i, j))
                    break

    ezlin_indizeak = set(diodo_indizeak)
    for i, j in transistor_pareak:
        ezlin_indizeak.add(i)
        ezlin_indizeak.add(j)

    return diodo_indizeak, transistor_pareak, sorted(ezlin_indizeak)


def has_nonlinear(cir_elx):
    for i in range(len(cir_elx)):
        if cir_elx[i][0][0].upper() in ('D', 'Q'):
            return True
    return False


def build_M_N_Us_NR(cir_elx, cir_valx, cir_ctrlx, v_guess, tr_mode=False, t=0.0):
    b = len(cir_elx)

    M = np.zeros((b, b), dtype=float)
    N = np.zeros((b, b), dtype=float)
    Us = np.zeros((b, 1), dtype=float)

    elementu_izenak_maius = [cir_elx[i][0].upper() for i in range(b)]
    q_prozesatuak = set()

    for i in range(b):
        elem_izena = cir_elx[i][0]
        elem_izena_maius = elem_izena.upper()
        elem_mota = elem_izena_maius[0]

        if elem_mota == 'R':
            M[i, i] = 1.0
            N[i, i] = -float(cir_valx[i][0])

        elif elem_mota == 'V':
            M[i, i] = 1.0
            Us[i, 0] = float(cir_valx[i][0])

        elif elem_mota == 'I':
            N[i, i] = 1.0
            Us[i, 0] = float(cir_valx[i][0])

        elif elem_mota == 'B':
            M[i, i] = 1.0
            Us[i, 0] = source_fixed_value(elem_izena, cir_valx[i], tr_mode=tr_mode, t=t)

        elif elem_mota == 'Y':
            N[i, i] = 1.0
            Us[i, 0] = source_fixed_value(elem_izena, cir_valx[i], tr_mode=tr_mode, t=t)

        elif elem_mota == 'E':
            M[i, i] = 1.0
            kontrol_elem = str(cir_ctrlx[i][0]).upper()
            if kontrol_elem in elementu_izenak_maius:
                j = elementu_izenak_maius.index(kontrol_elem)
                M[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        elif elem_mota == 'G':
            N[i, i] = 1.0
            kontrol_elem = str(cir_ctrlx[i][0]).upper()
            if kontrol_elem in elementu_izenak_maius:
                j = elementu_izenak_maius.index(kontrol_elem)
                M[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        elif elem_mota == 'H':
            M[i, i] = 1.0
            kontrol_elem = str(cir_ctrlx[i][0]).upper()
            if kontrol_elem in elementu_izenak_maius:
                j = elementu_izenak_maius.index(kontrol_elem)
                N[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        elif elem_mota == 'F':
            N[i, i] = 1.0
            kontrol_elem = str(cir_ctrlx[i][0]).upper()
            if kontrol_elem in elementu_izenak_maius:
                j = elementu_izenak_maius.index(kontrol_elem)
                N[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        elif elem_mota == 'A':
            if elem_izena_maius.endswith('_IN'):
                M[i, i] = 1.0
            elif elem_izena_maius.endswith('_OUT'):
                if i - 1 < 0:
                    sys.exit(f'Unexpected opamp branch name {elem_izena}.')
                N[i, i - 1] = 1.0
            else:
                sys.exit(f'Unexpected opamp branch name {elem_izena}.')

        elif elem_mota == 'D':
            gd, Id = diode_NR(float(cir_valx[i][0]), float(cir_valx[i][1]), float(v_guess[i]))
            M[i, i] = gd
            N[i, i] = 1.0
            Us[i, 0] = Id

        elif elem_mota == 'Q':
            if i in q_prozesatuak:
                continue

            if not elem_izena_maius.endswith('_BE'):
                continue

            oina = elem_izena_maius[:-3]
            bc_izena = oina + '_BC'

            if bc_izena not in elementu_izenak_maius:
                sys.exit(f'Unexpected transistor branch name {elem_izena}.')

            j = elementu_izenak_maius.index(bc_izena)

            IES = float(cir_valx[i][0])
            ICS = float(cir_valx[i][1])
            betaF = float(cir_valx[i][2])

            g11, g12, g21, g22, IE, IC = transistor_NR(
                IES, ICS, betaF, float(v_guess[i]), float(v_guess[j])
            )

            M[i, i] = g11
            M[i, j] = g12
            N[i, i] = 1.0
            Us[i, 0] = IE

            M[j, i] = g21
            M[j, j] = g22
            N[j, j] = 1.0
            Us[j, 0] = IC

            q_prozesatuak.add(i)
            q_prozesatuak.add(j)

        else:
            sys.exit(f'Element {elem_izena} not supported in P3.')

    return M, N, Us


def build_tableau(A, M, N):
    n_minus_1 = A.shape[0]
    b = A.shape[1]
    I = np.eye(b, dtype=float)

    T = np.zeros((n_minus_1 + 2 * b, n_minus_1 + 2 * b), dtype=float)
    T[0:n_minus_1, n_minus_1 + b:] = A
    T[n_minus_1:n_minus_1 + b, 0:n_minus_1] = -A.T
    T[n_minus_1:n_minus_1 + b, n_minus_1:n_minus_1 + b] = I
    T[n_minus_1 + b:, n_minus_1:n_minus_1 + b] = M
    T[n_minus_1 + b:, n_minus_1 + b:] = N

    return T


def build_U(Us, n, b):
    U = np.zeros((n - 1 + 2 * b, 1), dtype=float)
    U[n - 1 + b:, 0] = Us[:, 0]
    return U


def print_solution(sol, b, n):
    if sol.dtype == np.float64:
        tmp = np.zeros((np.size(sol), 1), dtype=float)
        for i in range(np.size(sol)):
            tmp[i] = np.array(sol[i])
        sol = tmp

    tolerantzia = 1e-9

    print("\n========== Nodes voltage to reference ========")
    for i in range(1, n):
        balioa = sol[i - 1][0]
        if abs(balioa) < tolerantzia:
            balioa = 0.0
        print("e" + str(i) + " = ", "[{:10.9f}]".format(balioa))

    print("\n========== Branches voltage difference ========")
    for i in range(1, b + 1):
        balioa = sol[i + n - 2][0]
        if abs(balioa) < tolerantzia:
            balioa = 0.0
        print("v" + str(i) + " = ", "[{:10.9f}]".format(balioa))

    print("\n=============== Branches currents ==============")
    for i in range(1, b + 1):
        balioa = sol[i + b + n - 2][0]
        if abs(balioa) < tolerantzia:
            balioa = 0.0
        print("i" + str(i) + " = ", "[{:10.9f}]".format(balioa))

    print("\n================= End solution =================\n")


def solve_linear_or_NR(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=False, t=0.0, hasierako_sol=None, eps=1e-5, nmax=100):
    if not has_nonlinear(cir_elx):
        _, A = reduced_incidence(cir_ndx, nodes)
        b = len(cir_elx)
        n = len(nodes)

        M, N, Us = build_M_N_Us_NR(cir_elx, cir_valx, cir_ctrlx, np.zeros(b), tr_mode=tr_mode, t=t)
        T = build_tableau(A, M, N)
        U = build_U(Us, n, b)

        try:
            return np.linalg.solve(T, U)
        except np.linalg.LinAlgError:
            sys.exit('Error solving Tableau equations, check if det(T) != 0.')

    _, A = reduced_incidence(cir_ndx, nodes)
    b = len(cir_elx)
    n = len(nodes)

    _, _, ezlin_indizeak = nonlinear_branch_indices(cir_elx)

    v_guess = np.zeros(b, dtype=float)
    if hasierako_sol is not None:
        for i in range(b):
            v_guess[i] = float(hasierako_sol[n - 1 + i][0])
    else:
        for i in ezlin_indizeak:
            v_guess[i] = 0.6

    for _ in range(nmax):
        M, N, Us = build_M_N_Us_NR(cir_elx, cir_valx, cir_ctrlx, v_guess, tr_mode=tr_mode, t=t)
        T = build_tableau(A, M, N)
        U = build_U(Us, n, b)

        try:
            sol = np.linalg.solve(T, U)
        except np.linalg.LinAlgError:
            sys.exit('Error solving Tableau equations, check if det(T) != 0.')

        v_berriak = np.array([float(sol[n - 1 + i][0]) for i in range(b)])
        errorea = 0.0

        for i in ezlin_indizeak:
            errorea = max(errorea, abs(v_berriak[i] - v_guess[i]))

        if errorea < eps:
            return sol

        for i in ezlin_indizeak:
            v_guess[i] = v_berriak[i]

    sys.exit('Error: Newton-Raphson did not converge.')


def build_csv_header(first_label, b, n):
    goiburua = first_label
    for i in range(1, n):
        goiburua += ',e' + str(i)
    for i in range(1, b + 1):
        goiburua += ',v' + str(i)
    for i in range(1, b + 1):
        goiburua += ',i' + str(i)
    return goiburua


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save_sim_output(filename, extension):
    proiektu_erroa = get_project_root()
    sims_karpeta = os.path.join(proiektu_erroa, 'sims')
    os.makedirs(sims_karpeta, exist_ok=True)

    oin_izena = os.path.splitext(os.path.basename(filename))[0]
    return os.path.join(sims_karpeta, oin_izena + extension)


def solution_row(sol):
    return ','.join('{:.9f}'.format(float(x[0])) for x in sol)


def save_output_text(filename, text):
    proiektu_erroa = get_project_root()
    outputs_karpeta = os.path.join(proiektu_erroa, 'outputs')
    os.makedirs(outputs_karpeta, exist_ok=True)

    oin_izena = os.path.splitext(os.path.basename(filename))[0]
    irteera_izena = os.path.join(outputs_karpeta, oin_izena + '.out')

    with open(irteera_izena, 'w', encoding='utf-8') as fitx:
        fitx.write(text)

    return irteera_izena


def run_dc(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, start, end, step, source_name):
    iturri_indizea = None

    for i in range(len(cir_elx)):
        if cir_elx[i][0].upper() == source_name.upper():
            iturri_indizea = i
            break

    if iturri_indizea is None:
        sys.exit(f'Source {source_name} not found.')

    elem_mota = cir_elx[iturri_indizea][0][0].upper()
    lehen_label = 'V' if elem_mota in ('V', 'B', 'E', 'H') else 'I'
    irteera_izena = save_sim_output(filename, '_' + source_name + '.dc')

    b = len(cir_elx)
    n = len(nodes)

    uneko_balioa = float(start)
    amaiera = float(end)
    pausoa = float(step)

    if pausoa == 0:
        sys.exit('DC step cannot be zero.')

    aurreko_sol = None

    with open(irteera_izena, 'w') as fitx:
        print(build_csv_header(lehen_label, b, n), file=fitx)

        if pausoa > 0:
            baldintza = lambda x: x <= amaiera + 1e-12
        else:
            baldintza = lambda x: x >= amaiera - 1e-12

        balioak = cir_valx.copy()

        while baldintza(uneko_balioa):
            balioak[iturri_indizea][0] = uneko_balioa
            sol = solve_linear_or_NR(cir_elx, cir_ndx, balioak, cir_ctrlx, nodes, tr_mode=False, t=0.0, hasierako_sol=aurreko_sol)
            print('{:.9f},{}'.format(uneko_balioa, solution_row(sol)), file=fitx)
            aurreko_sol = sol
            uneko_balioa = round(uneko_balioa + pausoa, 10)

    return irteera_izena


def run_tr(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, start, end, step):
    irteera_izena = save_sim_output(filename, '.tr')

    b = len(cir_elx)
    n = len(nodes)

    denbora = float(start)
    amaiera = float(end)
    pausoa = float(step)

    if pausoa == 0:
        sys.exit('TR step cannot be zero.')

    aurreko_sol = None

    with open(irteera_izena, 'w') as fitx:
        print(build_csv_header('t', b, n), file=fitx)

        if pausoa > 0:
            baldintza = lambda x: x <= amaiera + 1e-12
        else:
            baldintza = lambda x: x >= amaiera - 1e-12

        while baldintza(denbora):
            sol = solve_linear_or_NR(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=True, t=denbora, hasierako_sol=aurreko_sol)
            print('{:.9f},{}'.format(denbora, solution_row(sol)), file=fitx)
            aurreko_sol = sol
            denbora = round(denbora + pausoa, 10)

    return irteera_izena


def run_file(filename):
    irteera_bufferra = io.StringIO()

    try:
        with contextlib.redirect_stdout(irteera_bufferra):
            cir_el, cir_nd, cir_val, cir_ctrl = cir_parser_p3(filename)
            cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak = expand_for_p3(cir_el, cir_nd, cir_val, cir_ctrl)

            check_reference_node(nodoak)
            Aa_top, _ = reduced_incidence(cir_ndx, nodoak)
            check_floating_nodes(Aa_top, nodoak)
            check_parallel_voltage_sources(cir_elx, cir_ndx, cir_valx)
            check_series_current_sources(cir_elx, cir_ndx, cir_valx, Aa_top, nodoak)

            analisiak = parse_analyses(filename)

            if not analisiak:
                circ_nd_bereziekin, nodo_zerrenda = print_cir_info_p3(cir_el, cir_nd)
                Aa = incidence_matrix(circ_nd_bereziekin, nodo_zerrenda)
                print("Incidence Matrix: ")
                print(Aa)

            else:
                for analisia in analisiak:
                    komandoa = analisia[0].upper()

                    if komandoa == '.PR':
                        circ_nd_bereziekin, nodo_zerrenda = print_cir_info_p3(cir_el, cir_nd)
                        Aa = incidence_matrix(circ_nd_bereziekin, nodo_zerrenda)
                        print("Incidence Matrix: ")
                        print(Aa)

                    elif komandoa == '.OP':
                        sol = solve_linear_or_NR(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak, tr_mode=False, t=0.0)
                        print_solution(sol, len(cir_elx), len(nodoak))

                    elif komandoa == '.DC':
                        run_dc(
                            cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak,
                            filename, analisia[5], analisia[6], analisia[7], analisia[8]
                        )

                    elif komandoa == '.TR':
                        run_tr(
                            cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak,
                            filename, analisia[5], analisia[6], analisia[7]
                        )

                    else:
                        sys.exit(f'Analysis {analisia[0]} not supported.')

    except SystemExit as errorea:
        print(str(errorea), file=irteera_bufferra)
        testua = irteera_bufferra.getvalue()
        output_file = save_output_text(filename, testua)
        print(testua, end='')
        print("Archivo OUTPUT guardado en:", output_file)
        return

    testua = irteera_bufferra.getvalue()
    output_file = save_output_text(filename, testua)
    print(testua, end='')
    print("Archivo OUTPUT guardado en:", output_file)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        base_dir = os.path.dirname(__file__)
        filename = os.path.join(base_dir, '..', 'cirs', 'all', '2_zlel_1D.cir')

    run_file(filename)
