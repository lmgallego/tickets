import pandas as pd
import os

# Leer el archivo Excel generado más reciente
filename = 'historial_incidencias_20250821_224746.xlsx'

if os.path.exists(filename):
    print(f"Leyendo archivo: {filename}")
    
    # Leer ambas hojas
    try:
        df_incidencias = pd.read_excel(filename, sheet_name='Incidencias')
        df_acciones = pd.read_excel(filename, sheet_name='Acciones')
        
        print("\n=== HOJA INCIDENCIAS ===")
        print(f"Columnas: {list(df_incidencias.columns)}")
        print(f"Número de filas: {len(df_incidencias)}")
        if len(df_incidencias) > 0:
            print("\nPrimeras 3 filas:")
            print(df_incidencias.head(3))
        
        print("\n=== HOJA ACCIONES ===")
        print(f"Columnas: {list(df_acciones.columns)}")
        print(f"Número de filas: {len(df_acciones)}")
        if len(df_acciones) > 0:
            print("\nPrimeras 3 filas:")
            print(df_acciones.head(3))
            
    except Exception as e:
        print(f"Error leyendo Excel: {e}")
else:
    print(f"Archivo {filename} no encontrado")
    
# Listar archivos Excel en el directorio
print("\n=== ARCHIVOS EXCEL DISPONIBLES ===")
for file in os.listdir('.'):
    if file.endswith('.xlsx'):
        print(f"- {file}")