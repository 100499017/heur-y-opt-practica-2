import sys
from constraint import *

def leer_fichero(ruta):
    """
    Lee el fichero de entrada.
    Devuelve una lista de strings (filas) y el tamaño N.
    """
    try:
        with open(ruta, 'r') as f:
            # Leemos las líneas no vacías y eliminamos espacios extra
            lineas = [l.strip() for l in f.readlines() if l.strip()]
        
        if not lineas:
            raise ValueError("El fichero está vacío.")

        n = len(lineas)

        if n % 2 != 0:
            raise ValueError(f"El tamaño de la rejilla (N={n}) debe ser par.")
        
        for i, linea in enumerate(lineas):
            if len(linea) != n:
                raise ValueError(f"La fila {i} no tiene longitud N={n}.")
                
        return lineas, n
    except FileNotFoundError:
        print(f"Error: No se encontró el fichero {ruta}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el fichero de entrada: {e}")
        sys.exit(1)

def formatear_fila(valores_fila):
    """
    Formatea una lista de caracteres [' ', 'X', 'O'] como una fila de la tabla: "|   | X | O |"
    """
    # Cada celda ocupa 3 espacios: " C "
    celdas = [f" {v} " for v in valores_fila]
    return "|" + "|".join(celdas) + "|"

def imprimir_tabla(datos_tabla, n, f_out=None):
    """
    Imprime la rejilla con formato  +---+---+---+
                                    | C | C | C |
                                    | C | C | C |
                                    | C | C | C |
                                    +---+---+---+
    donde 'C' se refiere al color negro o blanco ('X' u 'O').
    Parámetros:
        - datos_tabla: 
    """
    # Crear línea separadora: +---+---+
    separador = "+" + "---+" * n
    
    output = []
    output.append(separador)
    
    for r in range(n):
        valores_fila = []
        for c in range(n):
            val = None
            # Detectar si es formato lista de strings (entrada) o dict (solución)
            if isinstance(datos_tabla, list):
                char = datos_tabla[r][c]
                if char == '.': val = ' '
                elif char in ['X', 'O']: val = char
                else: val = '?'
            elif isinstance(datos_tabla, dict):
                # 1=Negro(X), 0=Blanco(O)
                num = datos_tabla.get((r, c))
                val = 'X' if num == 1 else 'O'
            
            valores_fila.append(val)
        
        output.append(formatear_fila(valores_fila))
    
    output.append(separador)
    
    output = "\n".join(output)
    
    if f_out:
        f_out.write(output + "\n")
    else:
        print(output)

def restriccion_no_tres_consecutivos(a, b, c):
    """Devuelve False si a == b == c (tres colores iguales seguidos)."""
    return not (a == b == c)

def main():
    if len(sys.argv) != 3:
        print("Uso: ./parte-1.py <fichero-entrada> <fichero-salida>")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    ruta_salida = sys.argv[2]

    # Leer y procesar entrada
    tabla_inicial, n = leer_fichero(ruta_entrada)

    # Configurar CSP
    problem = Problem()
    
    # Variables: (fila, col). Dominio: {0 (Blanco), 1 (Negro)}
    # Usaremos 0 para 'O' y 1 para 'X'
    vars_tabla = [(i, j) for i in range(n) for j in range(n)]
    problem.addVariables(vars_tabla, [0, 1])

    # Restricciones Unarias (instancia inicial)
    for r in range(n):
        for c in range(n):
            char = tabla_inicial[r][c]
            if char == 'X':
                problem.addConstraint(lambda v: v == 1, [(r, c)])
            elif char == 'O':
                problem.addConstraint(lambda v: v == 0, [(r, c)])

    # Restricciones: Mismo número de blancos y negros
    # Como 1=Negro y 0=Blanco, la suma de la fila/columna debe ser N/2
    objetivo = n // 2
    
    # Filas
    for r in range(n):
        problem.addConstraint(ExactSumConstraint(objetivo), 
                              [(r, c) for c in range(n)])
    # Columnas
    for c in range(n):
        problem.addConstraint(ExactSumConstraint(objetivo), 
                              [(r, c) for r in range(n)])

    # Restricciones: No más de 2 consecutivos del mismo color
    # Filas
    for r in range(n):
        for c in range(n - 2):
            problem.addConstraint(restriccion_no_tres_consecutivos, 
                                  [(r, c), (r, c+1), (r, c+2)])
    # Columnas
    for c in range(n):
        for r in range(n - 2):
            problem.addConstraint(restriccion_no_tres_consecutivos, 
                                  [(r, c), (r+1, c), (r+2, c)])

    # Resolver
    soluciones = problem.getSolutions()
    num_sols = len(soluciones)

    # Salida por pantalla
    # Primero la instancia, luego el número de soluciones
    imprimir_tabla(tabla_inicial, n)
    print(f"{num_sols} soluciones encontradas")

    # Salida a fichero
    # Debe contener la instancia y luego una solución (si existe)
    with open(ruta_salida, 'w') as f:
        f.write("Instancia inicial:\n")
        imprimir_tabla(tabla_inicial, n, f_out=f)
        
        f.write("\nSolucion:\n")
        if num_sols > 0:
            # Tomamos la primera solución
            imprimir_tabla(soluciones[0], n, f_out=f)
        else:
            f.write("No se encontró solución.\n")

if __name__ == "__main__":
    main()
