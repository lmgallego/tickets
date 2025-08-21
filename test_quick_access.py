#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar todos los accesos rápidos del dashboard
"""

import streamlit as st
import sys
import os
sys.path.append('.')

# Simular el comportamiento de los accesos rápidos
def test_navigation_logic():
    """
    Prueba la lógica de navegación de los accesos rápidos
    """
    print("=== PRUEBA DE ACCESOS RÁPIDOS ===")
    
    # Definir los accesos rápidos y sus destinos esperados
    quick_access_tests = {
        'new_incident_record': {
            'main_menu': 'Incidencias',
            'sub_menu': 'Registro de Incidencia',
            'description': '📝 Nuevo Registro'
        },
        'new_incident_code': {
            'main_menu': 'Altas', 
            'sub_menu': 'Alta Incidencia',
            'description': '🏷️ Nuevo Código'
        },
        'manage_actions': {
            'main_menu': 'Incidencias',
            'sub_menu': 'Gestión de Acciones', 
            'description': '⚡ Gestión de Acciones'
        },
        'analytics': {
            'main_menu': 'Consultas y Analítica',
            'sub_menu': None,
            'description': '📊 Analítica Completa'
        },
        'export': {
            'main_menu': 'Administración',
            'sub_menu': 'Exportar a Excel',
            'description': '📋 Exportar Excel'
        }
    }
    
    print(f"\nProbando {len(quick_access_tests)} accesos rápidos...\n")
    
    # Simular la lógica de navegación de app.py
    for nav_key, expected in quick_access_tests.items():
        print(f"🔍 Probando: {expected['description']} ('{nav_key}')")
        
        # Simular el manejo de navegación
        session_state = {}
        
        # Aplicar la lógica de app.py
        if nav_key == 'manage_actions':
            session_state['main_menu_override'] = 'Incidencias'
            session_state['sub_menu_override'] = 'Gestión de Acciones'
        elif nav_key == 'new_incident_record':
            session_state['main_menu_override'] = 'Incidencias'
            session_state['sub_menu_override'] = 'Registro de Incidencia'
        elif nav_key == 'new_incident_code':
            session_state['main_menu_override'] = 'Altas'
            session_state['sub_menu_override'] = 'Alta Incidencia'
        elif nav_key == 'analytics':
            session_state['main_menu_override'] = 'Consultas y Analítica'
        elif nav_key == 'export':
            session_state['main_menu_override'] = 'Administración'
            session_state['sub_menu_override'] = 'Exportar a Excel'
        
        # Verificar resultados
        main_menu_ok = session_state.get('main_menu_override') == expected['main_menu']
        sub_menu_ok = True
        if expected['sub_menu']:
            sub_menu_ok = session_state.get('sub_menu_override') == expected['sub_menu']
        
        status = "✅ OK" if (main_menu_ok and sub_menu_ok) else "❌ ERROR"
        print(f"   {status} - Menú: {session_state.get('main_menu_override', 'N/A')}")
        if expected['sub_menu']:
            print(f"        - Submenú: {session_state.get('sub_menu_override', 'N/A')}")
        
        if not (main_menu_ok and sub_menu_ok):
            print(f"   ⚠️  Esperado - Menú: {expected['main_menu']}")
            if expected['sub_menu']:
                print(f"              - Submenú: {expected['sub_menu']}")
        
        print()
    
    print("=== VERIFICACIÓN DE ARCHIVOS ===")
    
    # Verificar que los archivos necesarios existen
    files_to_check = [
        'components/dashboard.py',
        'components/delete.py', 
        'app.py',
        'utils/database_supabase.py'
    ]
    
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
    
    print("\n=== VERIFICACIÓN DE FUNCIONES ===")
    
    # Verificar que las funciones clave existen
    try:
        from components.dashboard import handle_dashboard_navigation
        print("✅ handle_dashboard_navigation importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando handle_dashboard_navigation: {e}")
    
    try:
        from components.delete import export_excel_form
        print("✅ export_excel_form importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando export_excel_form: {e}")
    
    try:
        from utils.database_supabase import export_incidents_to_excel
        print("✅ export_incidents_to_excel importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando export_incidents_to_excel: {e}")

if __name__ == "__main__":
    test_navigation_logic()