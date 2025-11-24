import subprocess
import time
import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Usamos tableros resueltos válidos para crear los tests vaciando celdas

tablas_iniciales = {
    4: [
        "OXXO",
        "OOXX",
        "XXOO",
        "XOOX"
    ],
    6: [
        "OOXOXX",
        "OXOXOX",
        "XXOXOO",
        "XOXOXO",
        "OOXXOX",
        "XXOOXO"
    ],
    8: [
        "XXOOXXOO",
        "XOXOXOOX",
        "OXOXOOXX",
        "XOXXOXOO",
        "OOXOXOXX",
        "XXOOXOOX",
        "OOXXOXXO",
        "OXOXOXXO"
    ]
}

def generar_fichero_test(n, huecos, filename):
    """Genera un fichero .in de tamaño N con celdas vacías ('.')"""
    tabla_inicial = tablas_iniciales[n]
    # Convertimos a lista de caracteres para manipular
    caracteres_tabla = [list(fila) for fila in tabla_inicial]
    
    # Lista de todas las posiciones posibles
    posiciones = [(r, c) for r in range(n) for c in range(n)]
    
    # Elegimos 'huecos' posiciones al azar para vaciar
    # Usamos semilla fija para que las 5 repeticiones sean sobre el mismo tablero
    random.seed(42)
    posiciones_a_borrar = random.sample(posiciones, huecos)
    
    for r, c in posiciones_a_borrar:
        caracteres_tabla[r][c] = '.'
        
    # Escribir fichero
    with open(filename, 'w') as f:
        for fila in caracteres_tabla:
            f.write("".join(fila) + "\n")

# Ejecución de pruebas

resultados = []
tamanios = [4, 6, 8]
celdas_faltantes = {4: [4, 8, 12], 6: [9, 18, 27], 8: [16, 32, 48]}
repeticiones = 5  # Número de veces que repetimos cada test

print(f"{'N':<4} | {'Huecos':<6} | {'Iteración':<7} | {'Tiempo (s)':<10}")
print("-" * 40)

for n in tamanios:
    for huecos in celdas_faltantes[n]:
        # Generar el fichero para este caso
        archivo_test = f"temp_{n}_{huecos}.in"
        generar_fichero_test(n, huecos, archivo_test)
        
        tiempos_tabla_actual = []
        
        for i in range(repeticiones):
            start = time.time()
            try:
                subprocess.run(
                    ["python", "parte-1.py", archivo_test, "temp_out.out"],
                    check=True,
                    stdout=subprocess.DEVNULL, # Silenciar salida
                    stderr=subprocess.DEVNULL
                )
                end = time.time()
                tiempo_ejecucion = end - start
                tiempos_tabla_actual.append(tiempo_ejecucion)
                # ':<n' significa que se alineará a la izquierda y rellenará con espacios hasta ocupar 'n' caracteres
                print(f"{n:<4} | {huecos:<6} | {i+1}/{repeticiones:<7} | {tiempo_ejecucion:.4f}")
            except Exception as e:
                print(f"Error en N={n} Huecos={huecos}: {e}")
                tiempos_tabla_actual.append(None) # Marcar error
        
        # Guardar todos los tiempos válidos para calcular media luego
        for t in tiempos_tabla_actual:
            if t is not None:
                resultados.append({
                    "Tamaño Tablero (N)": n,
                    "Huecos Vacíos": huecos,
                    "Tiempo (s)": t
                })
                
        # Limpieza fichero temporal
        if os.path.exists(archivo_test):
            os.remove(archivo_test)

if os.path.exists("temp_out.out"):
    os.remove("temp_out.out")

# Análisis y gráfico con 'pandas'

# Crear DataFrame
df = pd.DataFrame(resultados)

# Agrupar por Tamaño y Huecos, calculando la media
df_agrupado = df.groupby(["Tamaño Tablero (N)", "Huecos Vacíos"])["Tiempo (s)"].mean().reset_index()

print(f"\n{'='*13} RESULTADOS PROMEDIO {'='*13}")
print(df_agrupado)

# Configuración del Gráfico
plt.figure(figsize=(10, 6))
plt.title("Evolución del Tiempo de Ejecución según Tamaño y Huecos")
plt.xlabel("Número de celdas vacías")
plt.ylabel("Tiempo Medio de Ejecución (s)")
plt.grid(True, linestyle='-', alpha=0.7)

# Dibujar las 3 líneas (una para cada tamaño de tablero)
colores = {4: 'green', 6: 'orange', 8: 'red'}
marcadores = {4: 'o', 6: 's', 8: '^'}

for size in tamanios:
    datos = df_agrupado[df_agrupado["Tamaño Tablero (N)"] == size]
    plt.plot(
        ["25%", "50%", "75%"],
        datos["Tiempo (s)"],
        marker=marcadores[size],
        label=f"N = {size}",
        color=colores[size],
        linewidth=2
    )

plt.legend(title="Tamaño Tablero (N)")
plt.tight_layout()

# Guardar imagen
plt.savefig("grafica_tiempos.png")
print("\nGráfico guardado como 'grafica_tiempos.png'")
plt.show()
