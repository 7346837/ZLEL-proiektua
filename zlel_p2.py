import os
import sys
import math
import io
import contextlib
import numpy as np

if __name__ == "zlel.zlel_p2":
    import zlel.zlel_p1 as zl1
else:
    import zlel_p1 as zl1


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


def expand_for_p2(cir_el, cir_nd, cir_val, cir_ctrl):
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

            cir_el_zabalduta.append(elem_izena + '_ou')
            cir_nd_zabalduta.append([int(cir_nd[i][2]), int(cir_nd[i][3])])
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


def reduced_incidence(cir_ndx, nodes):
    Aa = zl1.incidence_matrix(cir_ndx.tolist(), list(nodes))
    erreferentzia_ind = list(nodes).index(0)
    A = np.delete(Aa, erreferentzia_ind, axis=0)
    return Aa, A


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


def check_reference_node(nodes):
    if 0 not in nodes:
        sys.exit('Reference node "0" is not defined in the circuit.')


def check_floating_nodes(Aa, nodes):
    for i, nodoa in enumerate(nodes):
        if np.count_nonzero(Aa[i, :]) == 1:
            sys.exit(f'Node {nodoa} is floating.')


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


def check_integrity(cir_elx, cir_ndx, cir_valx, nodes):
    check_reference_node(nodes)
    Aa, _ = reduced_incidence(cir_ndx, nodes)
    check_floating_nodes(Aa, nodes)
    check_parallel_voltage_sources(cir_elx, cir_ndx, cir_valx)
    check_series_current_sources(cir_elx, cir_ndx, cir_valx, Aa, nodes)


def build_M_N_Us(cir_elx, cir_valx, cir_ctrlx, tr_mode=False, t=0.0):
    b = len(cir_elx)

    M = np.zeros((b, b), dtype=float)
    N = np.zeros((b, b), dtype=float)
    Us = np.zeros((b, 1), dtype=float)

    elementu_izenak_maius = [cir_elx[i][0].upper() for i in range(b)]

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
            elif elem_izena_maius.endswith('_OU'):
                if i - 1 < 0:
                    sys.exit(f'Unexpected opamp branch name {elem_izena}.')
                N[i, i - 1] = 1.0
            else:
                sys.exit(f'Unexpected opamp branch name {elem_izena}.')

        else:
            sys.exit(f'Element {elem_izena} not supported in P2.')

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


def solve_tableau(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=False, t=0.0):
    _, A = reduced_incidence(cir_ndx, nodes)

    b = len(cir_elx)
    n = len(nodes)

    M, N, Us = build_M_N_Us(cir_elx, cir_valx, cir_ctrlx, tr_mode=tr_mode, t=t)
    T = build_tableau(A, M, N)
    U = build_U(Us, n, b)

    try:
        sol = np.linalg.solve(T, U)
    except np.linalg.LinAlgError:
        sys.exit('Error solving Tableau equations, check if det(T) != 0.')

    return sol


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
    irteera_izena = os.path.join(outputs_karpeta, oin_izena + '.txt')

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

    with open(irteera_izena, 'w') as fitx:
        print(build_csv_header(lehen_label, b, n), file=fitx)

        if pausoa > 0:
            baldintza = lambda x: x <= amaiera + 1e-12
        else:
            baldintza = lambda x: x >= amaiera - 1e-12

        balioak = cir_valx.copy()

        while baldintza(uneko_balioa):
            balioak[iturri_indizea][0] = uneko_balioa
            sol = solve_tableau(cir_elx, cir_ndx, balioak, cir_ctrlx, nodes, tr_mode=False, t=0.0)
            print('{:.9f},{}'.format(uneko_balioa, solution_row(sol)), file=fitx)
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

    with open(irteera_izena, 'w') as fitx:
        print(build_csv_header('t', b, n), file=fitx)

        if pausoa > 0:
            baldintza = lambda x: x <= amaiera + 1e-12
        else:
            baldintza = lambda x: x >= amaiera - 1e-12

        while baldintza(denbora):
            sol = solve_tableau(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=True, t=denbora)
            print('{:.9f},{}'.format(denbora, solution_row(sol)), file=fitx)
            denbora = round(denbora + pausoa, 10)

    return irteera_izena


def run_file(filename):
    irteera_bufferra = io.StringIO()

    try:
        with contextlib.redirect_stdout(irteera_bufferra):
            try:
                cir_el, cir_nd, cir_val, cir_ctrl = zl1.cir_parser(filename)
            except IndexError:
                sys.exit("File corrupted: .cir size is incorrect.")
            except ValueError:
                sys.exit("File corrupted: .cir size is incorrect.")

            cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak = expand_for_p2(cir_el, cir_nd, cir_val, cir_ctrl)

            check_integrity(cir_elx, cir_ndx, cir_valx, nodoak)

            analisiak = parse_analyses(filename)

            if not analisiak:
                b, n, nodoak0, el_num = zl1.get_circuit_info(cir_el, cir_nd)
                circ_nd = zl1.print_cir_info(cir_el, cir_nd, b, n, nodoak0, el_num)
                Aa = zl1.incidence_matrix(circ_nd, nodoak0)

                if zl1.matrizea_ondo(Aa):
                    print('Incidence Matrix :')
                    print(Aa)
                else:
                    print('intzidentzia matrizea ez da zuzena')

            else:
                for analisia in analisiak:
                    komandoa = analisia[0].upper()

                    if komandoa == '.PR':
                        b0, n0, nodoak0, el_num = zl1.get_circuit_info(cir_el, cir_nd)
                        circ_nd = zl1.print_cir_info(cir_el, cir_nd, b0, n0, nodoak0, el_num)
                        Aa = zl1.incidence_matrix(circ_nd, nodoak0)

                        if zl1.matrizea_ondo(Aa):
                            print('Incidence Matrix :')
                            print(Aa)
                        else:
                            print('intzidentzia matrizea ez da zuzena')

                    elif komandoa == '.OP':
                        sol = solve_tableau(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak, tr_mode=False, t=0.0)
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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
    else:
        base_dir = os.path.dirname(__file__)
        FILENAME = os.path.join(base_dir, '..', 'cirs', 'all', '1_zlel_V_R_op_dc.cir')

    run_file(FILENAME)
