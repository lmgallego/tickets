#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para identificar el problema de actualización de estado en la UI
Este script simula exactamente lo que hace el formulario de Streamlit
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_supabase import (
    get_supabase_connection, 
    insert_incident_action, 
    get_incident_record_details,
    get_dashboard_stats,
    get_incident_records,
    get_incident_actions
)
import datetime

def simulate_ui_workflow():
    """Simula exactamente el flujo de trabajo de la UI"""
    print("=== SIMULACIÓN DEL FLUJO DE TRABAJO DE LA UI ===")
    
    try:
        # 1. Obtener registros de incidencias (como hace el selectbox)
        print("1. Obteniendo registros de incidencias...")
        incident_records = get_incident_records()
        
        if not incident_records:
            print("❌ No hay registros de incidencias")
            return False
            
        # Tomar el primer registro para la prueba
        selected_record = incident_records[0]
        incident_record_id = selected_record[0]
        record_description = selected_record[1]
        
        print(f"✅ Registro seleccionado: ID {incident_record_id} - {record_description}")
        
        # 2. Obtener detalles del registro (como hace la UI)
        print("\n2. Obteniendo detalles del registro...")
        details = get_incident_record_details(incident_record_id)
        
        if details:
            original_status = details.get('status', 'N/A')
            print(f"✅ Estado original: {original_status}")
        else:
            print("❌ No se pudieron obtener los detalles")
            return False
            
        # 3. Obtener historial de acciones (como hace la UI)
        print("\n3. Obteniendo historial de acciones...")
        actions = get_incident_actions(incident_record_id)
        print(f"✅ Acciones existentes: {len(actions)}")
        
        # 4. Simular el guardado de una nueva acción con estado 'Solucionado'
        print("\n4. Simulando guardado de acción con estado 'Solucionado'...")
        
        action_date = datetime.date.today()
        action_description = "TEST UI: Cambio de estado a Solucionado desde formulario"
        new_status = "Solucionado"
        performed_by = 1  # ID del coordinador
        
        # Llamar a insert_incident_action (exactamente como lo hace la UI)
        success = insert_incident_action(
            incident_record_id, 
            action_date, 
            action_description, 
            new_status, 
            performed_by
        )
        
        if success:
            print("✅ insert_incident_action retornó True")
        else:
            print("❌ insert_incident_action retornó False")
            return False
            
        # 5. Simular lo que haría la UI después del st.rerun()
        print("\n5. Simulando refresco de datos (como st.rerun())...")
        
        # Volver a obtener detalles (como haría la UI después del rerun)
        updated_details = get_incident_record_details(incident_record_id)
        
        if updated_details:
            updated_status = updated_details.get('status', 'N/A')
            print(f"Estado después del 'rerun': {updated_status}")
            
            if updated_status == "Solucionado":
                print("✅ El estado se actualizó correctamente en la UI")
            else:
                print(f"❌ El estado NO se actualizó en la UI. Esperado: 'Solucionado', Actual: '{updated_status}'")
                
                # Verificar directamente en la BD
                client = get_supabase_connection()
                direct_check = client.table('incident_records').select('status').eq('id', incident_record_id).execute()
                if direct_check.data:
                    db_status = direct_check.data[0]['status']
                    print(f"Estado directo en BD: {db_status}")
                    
                    if db_status == "Solucionado":
                        print("⚠️  PROBLEMA IDENTIFICADO: El estado está correcto en BD pero get_incident_record_details no lo refleja")
                        print("🔍 Esto indica un problema de cache en get_incident_record_details")
                    else:
                        print("❌ El problema está en insert_incident_action - no actualiza la BD")
                        
                return False
        
        # 6. Verificar historial de acciones actualizado
        print("\n6. Verificando historial de acciones actualizado...")
        updated_actions = get_incident_actions(incident_record_id)
        print(f"Acciones después del guardado: {len(updated_actions)}")
        
        if len(updated_actions) > len(actions):
            last_action = updated_actions[-1]  # La más reciente
            print(f"✅ Nueva acción agregada:")
            print(f"   - Descripción: {last_action['action_description']}")
            print(f"   - Nuevo estado: {last_action['new_status']}")
            print(f"   - Fecha: {last_action['action_date']}")
        else:
            print("❌ No se agregó la nueva acción al historial")
            return False
            
        # 7. Verificar estadísticas del dashboard (como las vería el usuario)
        print("\n7. Verificando estadísticas del dashboard...")
        stats = get_dashboard_stats()
        print(f"Incidencias resueltas (dashboard): {stats['resolved_incidents']}")
        
        # Verificar conteo directo
        client = get_supabase_connection()
        direct_count = client.table('incident_records').select('count', count='exact').eq('status', 'Solucionado').execute()
        db_resolved_count = direct_count.count if direct_count.count else 0
        print(f"Incidencias resueltas (BD directa): {db_resolved_count}")
        
        if stats['resolved_incidents'] == db_resolved_count:
            print("✅ Las estadísticas del dashboard están actualizadas")
        else:
            print(f"❌ Las estadísticas del dashboard NO están actualizadas")
            print(f"   Dashboard: {stats['resolved_incidents']}, BD: {db_resolved_count}")
            print("🔍 Esto indica un problema de cache en get_dashboard_stats")
            
        return True
        
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functions():
    """Prueba específica de las funciones que pueden tener cache"""
    print("\n=== TEST DE FUNCIONES CON POSIBLE CACHE ===")
    
    try:
        # Obtener un registro para probar
        incident_records = get_incident_records()
        if not incident_records:
            print("❌ No hay registros para probar")
            return False
            
        test_record_id = incident_records[0][0]
        
        # Probar get_incident_record_details múltiples veces
        print(f"\n--- Probando get_incident_record_details (ID: {test_record_id}) ---")
        for i in range(3):
            details = get_incident_record_details(test_record_id)
            status = details.get('status', 'N/A') if details else 'ERROR'
            print(f"Intento {i+1}: Estado = {status}")
            
        # Probar get_dashboard_stats múltiples veces
        print("\n--- Probando get_dashboard_stats ---")
        for i in range(3):
            stats = get_dashboard_stats()
            print(f"Intento {i+1}: Resueltas = {stats['resolved_incidents']}, Pendientes = {stats['pending_incidents']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en test de cache: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando simulación del problema de UI...\n")
    
    # Ejecutar tests
    test1_result = simulate_ui_workflow()
    test2_result = test_cache_functions()
    
    print("\n=== DIAGNÓSTICO FINAL ===")
    print(f"Simulación de flujo UI: {'✅ PASÓ' if test1_result else '❌ FALLÓ'}")
    print(f"Test de funciones cache: {'✅ PASÓ' if test2_result else '❌ FALLÓ'}")
    
    if not test1_result:
        print("\n🔍 POSIBLES CAUSAS DEL PROBLEMA:")
        print("1. La función get_incident_record_details tiene cache y no se actualiza")
        print("2. La función get_dashboard_stats tiene cache y no se actualiza")
        print("3. Streamlit no está ejecutando st.rerun() correctamente")
        print("4. Hay un problema en la función insert_incident_action")
        print("\n💡 SOLUCIONES SUGERIDAS:")
        print("1. Limpiar cache de Streamlit después de guardar")
        print("2. Forzar recarga de datos sin cache")
        print("3. Verificar que st.rerun() se ejecute correctamente")
    else:
        print("\n✅ El flujo de trabajo funciona correctamente a nivel de backend")
        print("🔍 El problema debe estar en la interfaz de Streamlit")