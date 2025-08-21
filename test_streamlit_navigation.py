#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para simular el comportamiento de navegación de Streamlit
y diagnosticar problemas con los accesos rápidos del dashboard.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, patch
import streamlit as st

class MockSessionState:
    """Mock de st.session_state para simular el comportamiento de Streamlit"""
    def __init__(self):
        self._state = {}
    
    def __getitem__(self, key):
        return self._state.get(key)
    
    def __setitem__(self, key, value):
        self._state[key] = value
        print(f"🔄 Estado actualizado: {key} = {value}")
    
    def __delitem__(self, key):
        if key in self._state:
            del self._state[key]
            print(f"🗑️ Estado eliminado: {key}")
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __contains__(self, key):
        return key in self._state
    
    def clear_navigation_state(self):
        """Simula la limpieza del estado de navegación"""
        nav_keys = ['navigate_to', 'navigate_to_actions', 'main_menu_override', 'sub_menu_override']
        for key in nav_keys:
            if key in self._state:
                del self._state[key]
                print(f"🗑️ Estado eliminado: {key}")

def test_dashboard_navigation():
    """Prueba la navegación desde el dashboard"""
    print("\n=== PRUEBA DE NAVEGACIÓN DESDE DASHBOARD ===")
    
    # Simular st.session_state
    mock_session_state = MockSessionState()
    
    with patch('streamlit.session_state', mock_session_state):
        # Importar después del patch para que use el mock
        from components.dashboard import handle_dashboard_navigation
        
        print("\n1️⃣ Estado inicial:")
        print(f"   navigate_to: {mock_session_state.get('navigate_to')}")
        
        print("\n2️⃣ Simulando clic en 'Exportar Excel':")
        mock_session_state['navigate_to'] = 'export'
        
        print("\n3️⃣ Verificando navegación:")
        nav_result = handle_dashboard_navigation()
        print(f"   Resultado de navegación: {nav_result}")
        
        print("\n4️⃣ Simulando lógica de app.py:")
        if nav_result == 'export':
            mock_session_state['main_menu_override'] = 'Administración'
            mock_session_state['sub_menu_override'] = 'Exportar a Excel'
            print("   ✅ Navegación configurada correctamente")
        
        print("\n5️⃣ Estado final:")
        print(f"   navigate_to: {mock_session_state.get('navigate_to')}")
        print(f"   main_menu_override: {mock_session_state.get('main_menu_override')}")
        print(f"   sub_menu_override: {mock_session_state.get('sub_menu_override')}")

def test_export_form_behavior():
    """Prueba el comportamiento del formulario de exportación"""
    print("\n=== PRUEBA DE FORMULARIO DE EXPORTACIÓN ===")
    
    mock_session_state = MockSessionState()
    mock_session_state['main_menu_override'] = 'Administración'
    mock_session_state['sub_menu_override'] = 'Exportar a Excel'
    
    with patch('streamlit.session_state', mock_session_state):
        try:
            from components.delete import export_excel_form
            from utils.database_supabase import export_incidents_to_excel
            
            print("\n1️⃣ Probando exportación de Excel:")
            filename = export_incidents_to_excel()
            print(f"   ✅ Archivo generado: {filename}")
            
            # Verificar que el archivo existe
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"   ✅ Archivo verificado: {size:,} bytes")
            else:
                print(f"   ❌ Archivo no encontrado: {filename}")
            
            print("\n2️⃣ Estado después de exportación:")
            print(f"   main_menu_override: {mock_session_state.get('main_menu_override')}")
            print(f"   sub_menu_override: {mock_session_state.get('sub_menu_override')}")
            
        except Exception as e:
            print(f"   ❌ Error en exportación: {e}")
            import traceback
            traceback.print_exc()

def test_all_quick_access_points():
    """Prueba todos los puntos de acceso rápido"""
    print("\n=== PRUEBA DE TODOS LOS ACCESOS RÁPIDOS ===")
    
    quick_access_points = {
        'new_incident_record': ('Registros', 'Nuevo Registro'),
        'new_incident_code': ('Códigos', 'Nuevo Código'),
        'manage_actions': ('Registros', 'Gestión de Acciones'),
        'analytics': ('Analítica', 'Completa'),
        'export': ('Administración', 'Exportar a Excel')
    }
    
    mock_session_state = MockSessionState()
    
    with patch('streamlit.session_state', mock_session_state):
        from components.dashboard import handle_dashboard_navigation
        
        for nav_key, expected_menu in quick_access_points.items():
            print(f"\n🔍 Probando: {nav_key}")
            
            # Limpiar estado
            mock_session_state.clear_navigation_state()
            
            # Simular navegación
            mock_session_state['navigate_to'] = nav_key
            
            # Verificar navegación
            result = handle_dashboard_navigation()
            
            if result == nav_key:
                print(f"   ✅ Navegación exitosa: {nav_key}")
                print(f"   📍 Menú esperado: {expected_menu[0]} -> {expected_menu[1]}")
            else:
                print(f"   ❌ Navegación fallida: esperado {nav_key}, obtenido {result}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE NAVEGACIÓN")
    
    try:
        test_dashboard_navigation()
        test_export_form_behavior()
        test_all_quick_access_points()
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n📋 RECOMENDACIONES:")
    print("1. Verificar que no hay conflictos de estado en la interfaz web")
    print("2. Comprobar que los keys únicos evitan problemas de renderizado")
    print("3. El delay agregado debería mejorar la estabilidad")
    print("4. Probar desde la interfaz web para confirmar la corrección")