
import os
import sys
import io
import contextlib
import numpy as np

if __name__ == "zlel.zlel_p4":
    import zlel.zlel_p1 as zl1
    import zlel.zlel_p2 as zl2
    import zlel.zlel_p3 as zl3
else:
    import zlel_p1 as zl1
    import zlel_p2 as zl2
    import zlel_p3 as zl3


def has_dynamic(cir_elx):
    for i in range(len(cir_elx)):
        if cir_elx[i][0][0].upper() in ('C', 'L'):
            return True
    return False


def print_cir_info_p4(cir_el, cir_nd):
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
                f"\t{adar_kont}. branch:\t{elem_izena}_ou\t\ti{adar_kont}\t\tv{adar_kont} = e{nodoak[2]} - e{nodoak[3]}"
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


def build_M_N_Us_BE_NR(cir_elx, cir_valx, cir_ctrlx, v_guess, aurreko_sol, h, n_minus_1, tr_mode=False, t=0.0):
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
            Us[i, 0] = zl2.source_fixed_value(elem_izena, cir_valx[i], tr_mode=tr_mode, t=t)

        elif elem_mota == 'Y':
            N[i, i] = 1.0
            Us[i, 0] = zl2.source_fixed_value(elem_izena, cir_valx[i], tr_mode=tr_mode, t=t)

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

        elif elem_mota == 'D':
            gd, Id = zl3.diode_NR(float(cir_valx[i][0]), float(cir_valx[i][1]), float(v_guess[i]))
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

            g11, g12, g21, g22, IE, IC = zl3.transistor_NR(
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

        elif elem_mota == 'C':
            C = float(cir_valx[i][0])

            if aurreko_sol is None:
                vc_aurrekoa = float(cir_valx[i][1]) if cir_valx.shape[1] > 1 else 0.0
            else:
                vc_aurrekoa = float(aurreko_sol[n_minus_1 + i][0])

            M[i, i] = 1.0
            N[i, i] = -h / C
            Us[i, 0] = vc_aurrekoa

        elif elem_mota == 'L':
            L = float(cir_valx[i][0])

            if aurreko_sol is None:
                il_aurrekoa = float(cir_valx[i][1]) if cir_valx.shape[1] > 1 else 0.0
            else:
                il_aurrekoa = float(aurreko_sol[n_minus_1 + b + i][0])

            M[i, i] = -h / L
            N[i, i] = 1.0
            Us[i, 0] = il_aurrekoa

        else:
            sys.exit(f'Element {elem_izena} not supported in P4.')

    return M, N, Us


def solve_BE_or_NR(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, h, aurreko_sol=None, tr_mode=False, t=0.0, eps=1e-5, nmax=100):
    _, A = zl2.reduced_incidence(cir_ndx, nodes)

    b = len(cir_elx)
    n = len(nodes)
    n_minus_1 = n - 1

    if not zl3.has_nonlinear(cir_elx):
        M, N, Us = build_M_N_Us_BE_NR(
            cir_elx, cir_valx, cir_ctrlx,
            np.zeros(b), aurreko_sol, h, n_minus_1,
            tr_mode=tr_mode, t=t
        )

        T = zl2.build_tableau(A, M, N)
        U = zl2.build_U(Us, n, b)

        try:
            return np.linalg.solve(T, U)
        except np.linalg.LinAlgError:
            sys.exit('Error solving Tableau equations, check if det(T) != 0.')

    _, _, ezlin_indizeak = zl3.nonlinear_branch_indices(cir_elx)

    v_guess = np.zeros(b, dtype=float)
    if aurreko_sol is not None:
        for i in range(b):
            v_guess[i] = float(aurreko_sol[n_minus_1 + i][0])
    else:
        for i in ezlin_indizeak:
            v_guess[i] = 0.6

    for _ in range(nmax):
        M, N, Us = build_M_N_Us_BE_NR(
            cir_elx, cir_valx, cir_ctrlx,
            v_guess, aurreko_sol, h, n_minus_1,
            tr_mode=tr_mode, t=t
        )

        T = zl2.build_tableau(A, M, N)
        U = zl2.build_U(Us, n, b)

        try:
            sol = np.linalg.solve(T, U)
        except np.linalg.LinAlgError:
            sys.exit('Error solving Tableau equations, check if det(T) != 0.')

        v_berriak = np.array([float(sol[n_minus_1 + i][0]) for i in range(b)])
        errorea = 0.0

        for i in ezlin_indizeak:
            errorea = max(errorea, abs(v_berriak[i] - v_guess[i]))

        if errorea < eps:
            return sol

        for i in ezlin_indizeak:
            v_guess[i] = v_berriak[i]

    sys.exit('Error: Newton-Raphson did not converge.')


def run_tr(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, start, end, step):
    irteera_izena = zl2.save_sim_output(filename, '.tr')

    b = len(cir_elx)
    n = len(nodes)

    denbora = float(start)
    amaiera = float(end)
    pausoa = float(step)

    if pausoa == 0:
        sys.exit('TR step cannot be zero.')

    aurreko_sol = None

    with open(irteera_izena, 'w') as fitx:
        print(zl2.build_csv_header('t', b, n), file=fitx)

        if pausoa > 0:
            baldintza = lambda x: x <= amaiera + 1e-12
        else:
            baldintza = lambda x: x >= amaiera - 1e-12

        while baldintza(denbora):
            sol = solve_BE_or_NR(
                cir_elx, cir_ndx, cir_valx, cir_ctrlx,
                nodes, pausoa, aurreko_sol,
                tr_mode=True, t=denbora
            )
            print('{:.9f},{}'.format(denbora, zl2.solution_row(sol)), file=fitx)

            aurreko_sol = sol
            denbora = round(denbora + pausoa, 10)

    return irteera_izena


def run_file(filename):
    try:
        cir_el, cir_nd, cir_val, cir_ctrl = zl1.cir_parser(filename)
    except IndexError:
        return zl3.run_file(filename)
    except ValueError:
        return zl3.run_file(filename)

    cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodoak = zl3.expand_for_p3(
        cir_el, cir_nd, cir_val, cir_ctrl
    )

    if not has_dynamic(cir_elx):
        return zl3.run_file(filename)

    irteera_bufferra = io.StringIO()

    try:
        with contextlib.redirect_stdout(irteera_bufferra):

            zl2.check_integrity(cir_elx, cir_ndx, cir_valx, nodoak)
            analisiak = zl2.parse_analyses(filename)

            if not analisiak:
                circ_nd_bereziekin, nodo_zerrenda = print_cir_info_p4(cir_el, cir_nd)
                Aa = zl1.incidence_matrix(circ_nd_bereziekin, nodo_zerrenda)
                print("Incidence Matrix: ")
                print(Aa)

            else:
                for analisia in analisiak:
                    komandoa = analisia[0].upper()

                    if komandoa == '.PR':
                        circ_nd_bereziekin, nodo_zerrenda = print_cir_info_p4(cir_el, cir_nd)
                        Aa = zl1.incidence_matrix(circ_nd_bereziekin, nodo_zerrenda)
                        print("Incidence Matrix: ")
                        print(Aa)

                    elif komandoa == '.OP':
                        sol = solve_BE_or_NR(
                            cir_elx, cir_ndx, cir_valx, cir_ctrlx,
                            nodoak, 1.0, None,
                            tr_mode=False, t=0.0
                        )
                        zl2.print_solution(sol, len(cir_elx), len(nodoak))

                    elif komandoa == '.DC':
                        sys.exit('DC analysis not supported in P4.')

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
        output_file = zl2.save_output_text(filename, testua)
        print(testua, end='')
        print("Archivo OUTPUT guardado en:", output_file)
        return

    testua = irteera_bufferra.getvalue()
    output_file = zl2.save_output_text(filename, testua)
    print(testua, end='')
    print("Archivo OUTPUT guardado en:", output_file)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        filename = os.path.join(base_dir, "cirs", "all", "3_zlel_RC.cir")

    run_file(filename)
