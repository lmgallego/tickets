#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar específicamente el flujo de exportar Excel desde el dashboard
"""

import sys
import os
sys.path.append('.')

def simulate_dashboard_export_flow():
    """
    Simula el flujo completo de exportar Excel desde el dashboard
    """
    print("=== SIMULACIÓN FLUJO EXPORTAR EXCEL DESDE DASHBOARD ===")
    
    # Paso 1: Simular clic en botón de dashboard
    print("\n1️⃣ Simulando clic en '📋 Exportar Excel' desde dashboard...")
    
    # Simular el estado de sesión que se establece en dashboard.py
    session_state = {}
    session_state['navigate_to'] = 'export'
    print(f"   ✅ Estado establecido: navigate_to = '{session_state['navigate_to']}'")
    
    # Paso 2: Simular handle_dashboard_navigation()
    print("\n2️⃣ Simulando handle_dashboard_navigation()...")
    
    try:
        from components.dashboard import handle_dashboard_navigation
        
        # Simular el comportamiento de la función
        if 'navigate_to' in session_state:
            destination = session_state['navigate_to']
            del session_state['navigate_to']
            dashboard_nav = destination
        else:
            dashboard_nav = None
            
        print(f"   ✅ Navegación detectada: '{dashboard_nav}'")
        
    except Exception as e:
        print(f"   ❌ Error en handle_dashboard_navigation: {e}")
        return
    
    # Paso 3: Simular lógica de app.py
    print("\n3️⃣ Simulando lógica de navegación en app.py...")
    
    if dashboard_nav == 'export':
        session_state['main_menu_override'] = 'Administración'
        session_state['sub_menu_override'] = 'Exportar a Excel'
        print(f"   ✅ Menú principal: {session_state['main_menu_override']}")
        print(f"   ✅ Submenú: {session_state['sub_menu_override']}")
    else:
        print(f"   ❌ Navegación no reconocida: {dashboard_nav}")
        return
    
    # Paso 4: Verificar que export_excel_form existe y funciona
    print("\n4️⃣ Verificando función export_excel_form...")
    
    try:
        from components.delete import export_excel_form
        print("   ✅ Función export_excel_form importada correctamente")
        
        # Verificar que la función de exportación existe
        from utils.database_supabase import export_incidents_to_excel
        print("   ✅ Función export_incidents_to_excel disponible")
        
    except Exception as e:
        print(f"   ❌ Error importando funciones: {e}")
        return
    
    # Paso 5: Probar exportación real
    print("\n5️⃣ Probando exportación real...")
    
    try:
        filename = export_incidents_to_excel()
        print(f"   ✅ Archivo creado: {filename}")
        
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   ✅ Archivo verificado: {size:,} bytes")
        else:
            print(f"   ❌ Archivo no encontrado: {filename}")
            
    except Exception as e:
        print(f"   ❌ Error en exportación: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ FLUJO COMPLETO EXITOSO")
    print("\n=== DIAGNÓSTICO ===")
    print("Si el problema persiste desde la interfaz web, podría ser:")
    print("1. 🔄 Problema de rerun() que interfiere con el estado")
    print("2. 🎯 Conflicto en el manejo de estados de sesión")
    print("3. 🖥️ Problema específico de la interfaz Streamlit")
    print("4. ⏱️ Timing issue entre el clic y la navegación")

def check_streamlit_session_behavior():
    """
    Verifica comportamientos específicos de Streamlit que podrían causar problemas
    """
    print("\n=== VERIFICACIÓN COMPORTAMIENTO STREAMLIT ===")
    
    # Verificar imports de Streamlit
    try:
        import streamlit as st
        print("✅ Streamlit importado correctamente")
    except ImportError:
        print("❌ Error importando Streamlit")
        return
    
    # Verificar estructura de archivos críticos
    critical_files = {
        'app.py': 'Archivo principal de la aplicación',
        'components/dashboard.py': 'Dashboard con accesos rápidos', 
        'components/delete.py': 'Funciones de administración incluyendo export_excel_form'
    }
    
    print("\n📁 Verificando archivos críticos:")
    for file_path, description in critical_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {file_path} - FALTANTE - {description}")

if __name__ == "__main__":
    simulate_dashboard_export_flow()
    check_streamlit_session_behavior()