#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear el problema de exportación a Excel
"""

import os
import sys
sys.path.append('.')

from utils.database_supabase import export_incidents_to_excel

def debug_export():
    print("=== DEBUG EXPORTACIÓN EXCEL ===")
    print(f"Directorio actual: {os.getcwd()}")
    
    try:
        # Intentar exportar
        print("\nIntentando exportar...")
        filename = export_incidents_to_excel()
        print(f"Función devolvió: {filename}")
        
        # Verificar si el archivo existe
        print(f"\n¿Existe el archivo '{filename}'? {os.path.exists(filename)}")
        
        # Verificar ruta absoluta
        abs_path = os.path.abspath(filename)
        print(f"Ruta absoluta: {abs_path}")
        print(f"¿Existe en ruta absoluta? {os.path.exists(abs_path)}")
        
        # Listar archivos Excel en el directorio actual
        print("\nArchivos Excel en directorio actual:")
        for file in os.listdir('.'):
            if file.endswith('.xlsx'):
                print(f"  - {file} (tamaño: {os.path.getsize(file)} bytes)")
                
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"\nTamaño del archivo creado: {size} bytes")
            
    except Exception as e:
        print(f"Error durante la exportación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_export()