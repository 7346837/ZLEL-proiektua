import os
import sys
import math
import numpy as np

# Esta parte permite importar zlel_p1 tanto si ejecutas este archivo
# directamente como si lo ejecutas desde el main del proyecto.
if __name__ == "zlel.zlel_p2":
    import zlel.zlel_p1 as zl1
else:
    import zlel_p1 as zl1


# =========================================================
# 1) LEER LOS ANALISIS DEL .cir
# =========================================================
# En tu P1, el parser ignora las líneas que empiezan por ".",
# así que aquí hacemos una lectura aparte del archivo para saber
# qué simulaciones pide el circuito: .PR, .OP, .DC, .TR
def parse_analyses(filename):
    analyses = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            # Saltamos líneas vacías
            if not line:
                continue

            parts = line.split()

            # Si la línea empieza por punto, es una orden de análisis
            # Ejemplo: .OP 0 0 0 0 0 0 0 0
            if parts and parts[0].startswith('.'):
                analyses.append(parts)

    return analyses


# =========================================================
# 2) ADAPTAR EL CIRCUITO A P2
# =========================================================
# En P2 necesitamos trabajar "por ramas".
# La mayoría de elementos ya son una rama.
# Pero el amplificador operacional ideal A_xx se convierte en DOS ramas:
#
#   A_xx_in  : rama de entrada (N+ -> N-)
#   A_xx_ou  : rama de salida  (Nout -> Nref)
#
# Esta función genera nuevas matrices "extendidas" ya listas para
# trabajar en el solver.
def expand_for_p2(cir_el, cir_nd, cir_val, cir_ctrl):
    el_list = []
    nd_list = []
    val_list = []
    ctrl_list = []

    for i in range(len(cir_el)):
        name = str(cir_el[i][0])
        kind = name[0].upper()

        # Caso especial: opamp ideal
        if kind == 'A':
            # Rama de entrada del opamp
            el_list.append(name + '_in')
            nd_list.append([int(cir_nd[i][0]), int(cir_nd[i][1])])
            val_list.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            ctrl_list.append(str(cir_ctrl[i][0]))

            # Rama de salida del opamp
            el_list.append(name + '_ou')
            nd_list.append([int(cir_nd[i][2]), int(cir_nd[i][3])])
            val_list.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            ctrl_list.append(str(cir_ctrl[i][0]))

        # Caso normal: cualquier otro elemento lineal ocupa una sola rama
        else:
            el_list.append(name)
            nd_list.append([int(cir_nd[i][0]), int(cir_nd[i][1])])
            val_list.append([float(cir_val[i][0]), float(cir_val[i][1]), float(cir_val[i][2])])
            ctrl_list.append(str(cir_ctrl[i][0]))

    # Convertimos listas a arrays numpy para trabajar cómodamente
    cir_elx = np.array(el_list, dtype=str).reshape(-1, 1)
    cir_ndx = np.array(nd_list, dtype=int)
    cir_valx = np.array(val_list, dtype=float)
    cir_ctrlx = np.array(ctrl_list, dtype=str).reshape(-1, 1)

    # Lista de nodos ordenada
    nodes = np.array(sorted(set(cir_ndx.flatten())), dtype=int)

    return cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes


# =========================================================
# 3) MATRIZ DE INCIDENCIA REDUCIDA
# =========================================================
# Tu P1 ya sabe construir la matriz de incidencia completa Aa.
# Aquí la reutilizamos y eliminamos la fila del nodo de referencia (0),
# para obtener la matriz reducida A, que es la que se usa en Tableau.
#
# Aa -> matriz completa con todos los nodos
# A  -> matriz sin la fila del nodo 0
def reduced_incidence(cir_ndx, nodes):
    Aa = zl1.incidence_matrix(cir_ndx.tolist(), list(nodes))
    zero_index = list(nodes).index(0)
    A = np.delete(Aa, zero_index, axis=0)
    return Aa, A


# =========================================================
# 4) VALOR "EFECTIVO" DE CADA FUENTE
# =========================================================
# Esta función devuelve el valor que toma una fuente en cada análisis.
#
# - En .OP y .DC:
#   * V, I, R, E, G, H, F usan su valor fijo habitual
#   * B e Y usan SU AMPLITUD
#
# - En .TR:
#   * B e Y usan el valor sinusoidal en el instante t
def source_fixed_value(branch_name, branch_values, tr_mode=False, t=0.0):
    kind = branch_name[0].upper()

    # Elementos de valor fijo
    if kind in ('V', 'I', 'R', 'E', 'G', 'H', 'F'):
        return float(branch_values[0])

    # Fuentes sinusoidales
    if kind in ('B', 'Y'):
        amp = float(branch_values[0])
        freq = float(branch_values[1])
        phase = float(branch_values[2])

        # En análisis temporal calculamos el seno
        if tr_mode:
            return amp * math.sin(2 * math.pi * freq * t + math.pi / 180.0 * phase)

        # En OP y DC usamos la amplitud
        return amp

    return float(branch_values[0])


# =========================================================
# 5) COMPROBACIONES DE INTEGRIDAD DEL CIRCUITO
# =========================================================
# Estas funciones revisan errores típicos que pide la práctica:
#
# - que exista nodo 0
# - que no haya nodos flotantes
# - que no haya fuentes de tensión en paralelo incompatibles
# - que no haya fuentes de corriente en serie incompatibles

def check_reference_node(nodes):
    if 0 not in nodes:
        sys.exit('Reference node "0" is not defined in the circuit.')


def check_floating_nodes(Aa, nodes):
    # Si un nodo solo aparece conectado a una única rama, está "flotando"
    for idx, node in enumerate(nodes):
        if np.count_nonzero(Aa[idx, :]) == 1:
            sys.exit(f'Node {node} is floating.')


def check_parallel_voltage_sources(cir_elx, cir_ndx, cir_valx):
    voltage_indices = []

    # Guardamos índices de ramas que son fuentes de tensión
    # En P2 también consideramos B como fuente de tensión
    for i in range(len(cir_elx)):
        kind = cir_elx[i][0][0].upper()
        if kind in ('V', 'B'):
            voltage_indices.append(i)

    # Comparamos entre sí las fuentes de tensión
    for a in range(len(voltage_indices)):
        i = voltage_indices[a]
        n1_i, n2_i = int(cir_ndx[i][0]), int(cir_ndx[i][1])
        val_i = source_fixed_value(cir_elx[i][0], cir_valx[i], tr_mode=False)

        for b in range(a + 1, len(voltage_indices)):
            j = voltage_indices[b]
            n1_j, n2_j = int(cir_ndx[j][0]), int(cir_ndx[j][1])
            val_j = source_fixed_value(cir_elx[j][0], cir_valx[j], tr_mode=False)

            # Mismo sentido y mismos nodos
            if n1_i == n1_j and n2_i == n2_j:
                if abs(val_i - val_j) > 1e-12:
                    sys.exit(f'Parallel V sources at branches {i} and {j}.')

            # Mismos nodos pero sentido contrario
            elif n1_i == n2_j and n2_i == n1_j:
                if abs(val_i + val_j) > 1e-12:
                    sys.exit(f'Parallel V sources at branches {i} and {j}.')


def check_series_current_sources(cir_elx, cir_ndx, cir_valx, Aa, nodes):
    # Recorremos cada nodo
    for row_idx in range(len(nodes)):
        connected = np.flatnonzero(Aa[row_idx, :] != 0)

        if len(connected) < 2:
            continue

        all_current_sources = True
        kcl_sum = 0.0
        nonzero_sources = 0

        # Miramos si todas las ramas conectadas a ese nodo
        # son fuentes de corriente
        for branch_idx in connected:
            kind = cir_elx[branch_idx][0][0].upper()

            if kind not in ('I', 'Y'):
                all_current_sources = False
                break

            signed_value = Aa[row_idx, branch_idx] * source_fixed_value(
                cir_elx[branch_idx][0], cir_valx[branch_idx], tr_mode=False
            )
            kcl_sum += signed_value

            if abs(signed_value) > 1e-12:
                nonzero_sources += 1

        # Si todas son fuentes de corriente y KCL no se cumple, error
        if all_current_sources and nonzero_sources == len(connected) and abs(kcl_sum) > 1e-12:
            sys.exit(f'I sources in series at node {nodes[row_idx]}.')


def check_integrity(cir_elx, cir_ndx, cir_valx, nodes):
    # Función "resumen" que llama a todas las comprobaciones
    check_reference_node(nodes)
    Aa, _ = reduced_incidence(cir_ndx, nodes)
    check_floating_nodes(Aa, nodes)
    check_parallel_voltage_sources(cir_elx, cir_ndx, cir_valx)
    check_series_current_sources(cir_elx, cir_ndx, cir_valx, Aa, nodes)


# =========================================================
# 6) CONSTRUIR M, N y Us
# =========================================================
# Esta es una de las funciones más importantes del código.
#
# Aquí se traduce cada elemento del circuito a su ecuación de rama
# en forma matricial:
#
#   M·v + N·i = Us
#
# Ejemplos:
#   Resistencia:   v - R i = 0
#   Fuente V:      v = V
#   Fuente I:      i = I
#
# M y N son matrices b x b
# Us es un vector columna b x 1
def build_M_N_Us(cir_elx, cir_valx, cir_ctrlx, tr_mode=False, t=0.0):
    b = len(cir_elx)

    M = np.zeros((b, b), dtype=float)
    N = np.zeros((b, b), dtype=float)
    Us = np.zeros((b, 1), dtype=float)

    # Lista de nombres en mayúsculas para encontrar fácilmente
    # elementos de control
    names_upper = [cir_elx[i][0].upper() for i in range(b)]

    for i in range(b):
        name = cir_elx[i][0]
        upper = name.upper()
        kind = upper[0]

        # ------------------------
        # Resistencia
        # v - R*i = 0
        # ------------------------
        if kind == 'R':
            M[i, i] = 1.0
            N[i, i] = -float(cir_valx[i][0])

        # ------------------------
        # Fuente de tensión independiente
        # v = V
        # ------------------------
        elif kind == 'V':
            M[i, i] = 1.0
            Us[i, 0] = float(cir_valx[i][0])

        # ------------------------
        # Fuente de corriente independiente
        # i = I
        # ------------------------
        elif kind == 'I':
            N[i, i] = 1.0
            Us[i, 0] = float(cir_valx[i][0])

        # ------------------------
        # Fuente sinusoidal de tensión
        # En OP/DC usa amplitud
        # En TR usa el seno en el instante t
        # ------------------------
        elif kind == 'B':
            M[i, i] = 1.0
            Us[i, 0] = source_fixed_value(name, cir_valx[i], tr_mode=tr_mode, t=t)

        # ------------------------
        # Fuente sinusoidal de corriente
        # ------------------------
        elif kind == 'Y':
            N[i, i] = 1.0
            Us[i, 0] = source_fixed_value(name, cir_valx[i], tr_mode=tr_mode, t=t)

        # ------------------------
        # Fuente de tensión controlada por tensión (E)
        # v = gain * v_control
        # ------------------------
        elif kind == 'E':
            M[i, i] = 1.0
            ctrl = str(cir_ctrlx[i][0]).upper()

            if ctrl in names_upper:
                j = names_upper.index(ctrl)
                M[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        # ------------------------
        # Fuente de corriente controlada por tensión (G)
        # i = gain * v_control
        # ------------------------
        elif kind == 'G':
            N[i, i] = 1.0
            ctrl = str(cir_ctrlx[i][0]).upper()

            if ctrl in names_upper:
                j = names_upper.index(ctrl)
                M[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        # ------------------------
        # Fuente de tensión controlada por corriente (H)
        # v = gain * i_control
        # ------------------------
        elif kind == 'H':
            M[i, i] = 1.0
            ctrl = str(cir_ctrlx[i][0]).upper()

            if ctrl in names_upper:
                j = names_upper.index(ctrl)
                N[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        # ------------------------
        # Fuente de corriente controlada por corriente (F)
        # i = gain * i_control
        # ------------------------
        elif kind == 'F':
            N[i, i] = 1.0
            ctrl = str(cir_ctrlx[i][0]).upper()

            if ctrl in names_upper:
                j = names_upper.index(ctrl)
                N[i, j] = -float(cir_valx[i][0])
            else:
                sys.exit(f'Control element {cir_ctrlx[i][0]} not found.')

        # ------------------------
        # Amplificador operacional ideal
        #
        # Se ha expandido en dos ramas:
        #   _IN  -> impone v_in = 0
        #   _OU  -> impone i_in = 0
        # ------------------------
        elif kind == 'A':
            if upper.endswith('_IN'):
                M[i, i] = 1.0

            elif upper.endswith('_OU'):
                if i - 1 < 0:
                    sys.exit(f'Unexpected opamp branch name {name}.')
                N[i, i - 1] = 1.0

            else:
                sys.exit(f'Unexpected opamp branch name {name}.')

        # ------------------------
        # Si aparece un elemento no contemplado en P2
        # ------------------------
        else:
            sys.exit(f'Element {name} not supported in P2.')

    return M, N, Us


# =========================================================
# 7) CONSTRUIR LA MATRIZ TABLEAU T
# =========================================================
# La ecuación que se resuelve es:
#
#     T · w = U
#
# donde:
#
#     w = [e ; v ; i]
#
# y
#
#     T = [  0    0    A ]
#         [ -A^T  I    0 ]
#         [  0    M    N ]
#
# Esta función construye la matriz T.
def build_tableau(A, M, N):
    n_minus_1 = A.shape[0]
    b = A.shape[1]
    I = np.eye(b, dtype=float)

    T = np.zeros((n_minus_1 + 2 * b, n_minus_1 + 2 * b), dtype=float)

    # Bloque superior: KCL
    T[0:n_minus_1, n_minus_1 + b:] = A

    # Bloque central: KVL
    T[n_minus_1:n_minus_1 + b, 0:n_minus_1] = -A.T
    T[n_minus_1:n_minus_1 + b, n_minus_1:n_minus_1 + b] = I

    # Bloque inferior: ecuaciones de los elementos
    T[n_minus_1 + b:, n_minus_1:n_minus_1 + b] = M
    T[n_minus_1 + b:, n_minus_1 + b:] = N

    return T


# =========================================================
# 8) CONSTRUIR EL VECTOR U
# =========================================================
# El vector del sistema tiene esta forma:
#
#     U = [ 0 ]
#         [ 0 ]
#         [ Us ]
#
# Es decir, la parte de nodos y ramas es cero,
# y solo al final se colocan las fuentes.
def build_U(Us, n, b):
    U = np.zeros((n - 1 + 2 * b, 1), dtype=float)
    U[n - 1 + b:, 0] = Us[:, 0]
    return U


# =========================================================
# 9) RESOLVER EL SISTEMA TABLEAU
# =========================================================
# Esta función junta todo:
#   - obtiene A
#   - construye M, N, Us
#   - construye T y U
#   - resuelve T·w = U
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


# =========================================================
# 10) IMPRIMIR LA SOLUCION EN PANTALLA
# =========================================================
# Muestra:
#   - tensiones de nodo e1, e2, ...
#   - tensiones de rama v1, v2, ...
#   - corrientes de rama i1, i2, ...
def print_solution(sol, b, n):
    # Reajuste por si numpy devuelve el vector en otro formato
    if sol.dtype == np.float64:
        tmp = np.zeros((np.size(sol), 1), dtype=float)
        for i in range(np.size(sol)):
            tmp[i] = np.array(sol[i])
        sol = tmp

    tolerance = 1e-9

    print("\n========== Nodes voltage to reference ========")
    for i in range(1, n):
        value = sol[i - 1][0]
        if abs(value) < tolerance:
            value = 0.0
        print("e" + str(i) + " = ", "[{:10.9f}]".format(value))

    print("\n========== Branches voltage difference ========")
    for i in range(1, b + 1):
        value = sol[i + n - 2][0]
        if abs(value) < tolerance:
            value = 0.0
        print("v" + str(i) + " = ", "[{:10.9f}]".format(value))

    print("\n=============== Branches currents ==============")
    for i in range(1, b + 1):
        value = sol[i + b + n - 2][0]
        if abs(value) < tolerance:
            value = 0.0
        print("i" + str(i) + " = ", "[{:10.9f}]".format(value))

    print("\n================= End solution =================\n")


# =========================================================
# 11) CREAR CABECERA PARA ARCHIVOS .dc y .tr
# =========================================================
# Formato pedido en la práctica:
#
# .DC:
#   V,e1,...,v1,...,i1,...
#   o
#   I,e1,...,v1,...,i1,...
#
# .TR:
#   t,e1,...,v1,...,i1,...
def build_csv_header(first_label, b, n):
    header = first_label

    for i in range(1, n):
        header += ',e' + str(i)

    for i in range(1, b + 1):
        header += ',v' + str(i)

    for i in range(1, b + 1):
        header += ',i' + str(i)

    return header


# =========================================================
# 12) ELEGIR LA RUTA DE SALIDA EN /sims
# =========================================================
# Guarda siempre en la carpeta sims de la raíz del proyecto,
# respetando la estructura del profesor.
def save_sim_output(filename, extension):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sims_folder = os.path.join(project_root, 'sims')

    # Si no existe, la crea automáticamente
    os.makedirs(sims_folder, exist_ok=True)

    base = os.path.splitext(os.path.basename(filename))[0]
    return os.path.join(sims_folder, base + extension)


# Convierte la solución del sistema en una línea CSV
def solution_row(sol):
    return ','.join('{:.9f}'.format(float(x[0])) for x in sol)


# =========================================================
# 13) ANALISIS .DC
# =========================================================
# Barre el valor de una fuente entre start y end con paso step.
# En cada paso resuelve el circuito y guarda una fila en el .dc
def run_dc(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, start, end, step, source_name):
    source_index = None

    # Buscamos qué rama es la fuente que se quiere barrer
    for i in range(len(cir_elx)):
        if cir_elx[i][0].upper() == source_name.upper():
            source_index = i
            break

    if source_index is None:
        sys.exit(f'Source {source_name} not found.')

    # Elegimos si la cabecera empieza con V o con I
    kind = cir_elx[source_index][0][0].upper()
    first_label = 'V' if kind in ('V', 'B', 'E', 'H') else 'I'

    outname = save_sim_output(filename, '_' + source_name + '.dc')

    b = len(cir_elx)
    n = len(nodes)

    current = float(start)
    end = float(end)
    step = float(step)

    if step == 0:
        sys.exit('DC step cannot be zero.')

    with open(outname, 'w') as f:
        print(build_csv_header(first_label, b, n), file=f)

        # Soporta barrido creciente o decreciente
        if step > 0:
            cond = lambda x: x <= end + 1e-12
        else:
            cond = lambda x: x >= end - 1e-12

        values = cir_valx.copy()

        while cond(current):
            # En cada paso cambiamos el valor de la fuente barrida
            values[source_index][0] = current

            # Resolvemos el circuito en ese punto del barrido
            sol = solve_tableau(cir_elx, cir_ndx, values, cir_ctrlx, nodes, tr_mode=False, t=0.0)

            # Guardamos una fila del csv
            print('{:.9f},{}'.format(current, solution_row(sol)), file=f)

            current = round(current + step, 10)

    print("Archivo DC guardado en:", outname)


# =========================================================
# 14) ANALISIS .TR
# =========================================================
# Barre el tiempo entre start y end con paso step.
# En cada instante resuelve el circuito y guarda una fila en el .tr
def run_tr(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, start, end, step):
    outname = save_sim_output(filename, '.tr')

    b = len(cir_elx)
    n = len(nodes)

    t = float(start)
    end = float(end)
    step = float(step)

    if step == 0:
        sys.exit('TR step cannot be zero.')

    with open(outname, 'w') as f:
        print(build_csv_header('t', b, n), file=f)

        # Soporta barrido creciente o decreciente
        if step > 0:
            cond = lambda x: x <= end + 1e-12
        else:
            cond = lambda x: x >= end - 1e-12

        while cond(t):
            # Aquí sí activamos tr_mode=True para que B e Y
            # se evalúen como senoidales en el instante t
            sol = solve_tableau(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=True, t=t)

            # Guardamos una fila
            print('{:.9f},{}'.format(t, solution_row(sol)), file=f)

            t = round(t + step, 10)

    print("Archivo TR guardado en:", outname)


# =========================================================
# 15) FUNCION PRINCIPAL DE P2
# =========================================================
# Esta es la función central del archivo.
# Hace todo el flujo:
#
#   1. parsear el circuito usando P1
#   2. expandir ramas para P2
#   3. comprobar integridad
#   4. leer qué análisis pide el .cir
#   5. ejecutar .PR / .OP / .DC / .TR
def run_file(filename):
    cir_el, cir_nd, cir_val, cir_ctrl = zl1.cir_parser(filename)

    # Adaptamos el circuito para P2
    cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes = expand_for_p2(cir_el, cir_nd, cir_val, cir_ctrl)

    # Comprobaciones topológicas y de fuentes
    check_integrity(cir_elx, cir_ndx, cir_valx, nodes)

    # Leemos qué órdenes de análisis hay en el archivo
    analyses = parse_analyses(filename)

    # Si no hay análisis, se comporta como una salida tipo P1
    if not analyses:
        b, n, nodes0, el_num = zl1.get_circuit_info(cir_el, cir_nd)
        circ_nd = zl1.print_cir_info(cir_el, cir_nd, b, n, nodes0, el_num)
        Aa = zl1.incidence_matrix(circ_nd, nodes0)

        if zl1.matrizea_ondo(Aa):
            print('Incidence Matrix :')
            print(Aa)
        else:
            print('intzidentzia matrizea ez da zuzena')

        return

    # Recorremos todos los análisis pedidos en el .cir
    for op in analyses:
        cmd = op[0].upper()

        # ------------------------
        # .PR -> imprimir info del circuito como en P1
        # ------------------------
        if cmd == '.PR':
            b0, n0, nodes0, el_num = zl1.get_circuit_info(cir_el, cir_nd)
            circ_nd = zl1.print_cir_info(cir_el, cir_nd, b0, n0, nodes0, el_num)
            Aa = zl1.incidence_matrix(circ_nd, nodes0)

            if zl1.matrizea_ondo(Aa):
                print('Incidence Matrix :')
                print(Aa)
            else:
                print('intzidentzia matrizea ez da zuzena')

        # ------------------------
        # .OP -> resolver el punto de operación
        # ------------------------
        elif cmd == '.OP':
            sol = solve_tableau(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, tr_mode=False, t=0.0)
            print_solution(sol, len(cir_elx), len(nodes))

        # ------------------------
        # .DC -> barrido de una fuente
        # ------------------------
        elif cmd == '.DC':
            run_dc(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, op[5], op[6], op[7], op[8])

        # ------------------------
        # .TR -> barrido temporal
        # ------------------------
        elif cmd == '.TR':
            run_tr(cir_elx, cir_ndx, cir_valx, cir_ctrlx, nodes, filename, op[5], op[6], op[7])

        # ------------------------
        # Cualquier análisis no soportado
        # ------------------------
        else:
            sys.exit(f'Analysis {op[0]} not supported.')


# =========================================================
# 16) EJECUCION DIRECTA DEL ARCHIVO
# =========================================================
# Si se ejecuta zlel_p2.py directamente:
#   - usa el archivo pasado por terminal
#   - o un ejemplo por defecto
if __name__ == '__main__':
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
    else:
        base_dir = os.path.dirname(__file__)
        FILENAME = os.path.join(base_dir, '..', 'cirs', 'all', '1_zlel_V_R_op_dc.cir')

    run_file(FILENAME)
