import sympy as sp #deribatuak zuzenean egin ahal izateko
import math

def newton(f, df, x0, eps, max_iter=100):

    x = x0
    i = 0

    while i < max_iter:

        fx = f(x)
        dfx = df(x)

        if abs(dfx) < 1e-12:
            print("Derivada cercana a cero")
            return None

        x_new = x - fx/dfx

        error = abs(x_new - x)

        if error < eps:
            return x_new, i+1

        x = x_new
        i += 1

    return x, i
 #ariketako datuekin
x0 = 3/4
eps = 5e-4
x = sp.symbols('x')
f = sp.cos(2*x)**2 - x**2
derivada = sp.diff(f, x)

print("f(x) =", f)
print("f'(x) =", derivada)
f_num = sp.lambdify(x, f, "math")
df_num = sp.lambdify(x, derivada, "math")

raiz, iteraciones = newton(f_num, df_num, x0, eps)

print("e1 ≈", raiz)
print("iteraciones =", iteraciones)