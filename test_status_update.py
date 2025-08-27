#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar el problema de actualización de estado 'Solucionado'
Este script verifica si:
1. La función insert_incident_action actualiza correctamente el estado
2. Los datos se guardan correctamente en la base de datos
3. El cache de Streamlit interfiere con la visualización
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_supabase import (
    get_supabase_connection, 
    insert_incident_action, 
    get_incident_record_details,
    get_dashboard_stats
)
import datetime

def test_status_update():
    """Prueba la actualización de estado paso a paso"""
    print("=== TEST DE ACTUALIZACIÓN DE ESTADO ===")
    
    try:
        # 1. Conectar a la base de datos
        client = get_supabase_connection()
        print("✅ Conexión a Supabase establecida")
        
        # 2. Obtener un registro de incidencia existente para probar
        records_result = client.table('incident_records').select('id, status').limit(5).execute()
        
        if not records_result.data:
            print("❌ No hay registros de incidencia para probar")
            return False
            
        test_record = records_result.data[0]
        record_id = test_record['id']
        original_status = test_record['status']
        
        print(f"📋 Registro de prueba: ID {record_id}, Estado original: {original_status}")
        
        # 3. Verificar estado antes de la actualización
        print("\n--- ANTES DE LA ACTUALIZACIÓN ---")
        before_details = get_incident_record_details(record_id)
        print(f"Estado en get_incident_record_details: {before_details.get('status', 'N/A')}")
        
        # Verificar directamente en la base de datos
        direct_check = client.table('incident_records').select('status').eq('id', record_id).execute()
        if direct_check.data:
            print(f"Estado directo en BD: {direct_check.data[0]['status']}")
        
        # 4. Simular inserción de acción con cambio de estado a 'Solucionado'
        print("\n--- INSERTANDO ACCIÓN CON ESTADO 'Solucionado' ---")
        
        action_date = datetime.date.today()
        action_description = "TEST: Cambio de estado a Solucionado"
        new_status = "Solucionado"
        performed_by = 1  # Asumiendo que existe un coordinador con ID 1
        
        # Llamar a la función que debería actualizar el estado
        success = insert_incident_action(
            record_id, 
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
            
        # 5. Verificar estado después de la actualización
        print("\n--- DESPUÉS DE LA ACTUALIZACIÓN ---")
        
        # Verificar directamente en la base de datos (sin cache)
        direct_check_after = client.table('incident_records').select('status').eq('id', record_id).execute()
        if direct_check_after.data:
            db_status = direct_check_after.data[0]['status']
            print(f"Estado directo en BD: {db_status}")
            
            if db_status == "Solucionado":
                print("✅ El estado se actualizó correctamente en la base de datos")
            else:
                print(f"❌ El estado NO se actualizó. Esperado: 'Solucionado', Actual: '{db_status}'")
                return False
        
        # Verificar con la función de detalles (puede tener cache)
        after_details = get_incident_record_details(record_id)
        cached_status = after_details.get('status', 'N/A')
        print(f"Estado en get_incident_record_details (con cache): {cached_status}")
        
        # 6. Verificar que la acción se guardó correctamente
        actions_result = client.table('incident_actions').select('*').eq('incident_record_id', record_id).order('action_date', desc=True).limit(1).execute()
        
        if actions_result.data:
            last_action = actions_result.data[0]
            print(f"\n--- ÚLTIMA ACCIÓN REGISTRADA ---")
            print(f"Descripción: {last_action['action_description']}")
            print(f"Nuevo estado: {last_action['new_status']}")
            print(f"Fecha: {last_action['action_date']}")
            
            if last_action['new_status'] == "Solucionado":
                print("✅ La acción se guardó correctamente")
            else:
                print(f"❌ La acción no tiene el estado correcto. Esperado: 'Solucionado', Actual: '{last_action['new_status']}'")
        
        # 7. Verificar estadísticas del dashboard
        print("\n--- VERIFICANDO ESTADÍSTICAS DEL DASHBOARD ---")
        stats = get_dashboard_stats()
        print(f"Total incidencias: {stats['total_incidents']}")
        print(f"Incidencias resueltas (Solucionado): {stats['resolved_incidents']}")
        print(f"Incidencias pendientes: {stats['pending_incidents']}")
        
        # Verificar conteo directo de 'Solucionado'
        solucionado_count = client.table('incident_records').select('count', count='exact').eq('status', 'Solucionado').execute()
        direct_count = solucionado_count.count if solucionado_count.count else 0
        print(f"Conteo directo de 'Solucionado' en BD: {direct_count}")
        
        if stats['resolved_incidents'] == direct_count:
            print("✅ Las estadísticas del dashboard coinciden con la BD")
        else:
            print(f"❌ Las estadísticas NO coinciden. Dashboard: {stats['resolved_incidents']}, BD: {direct_count}")
            print("⚠️  Esto puede indicar un problema de cache")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_behavior():
    """Prueba específica para verificar el comportamiento del cache"""
    print("\n=== TEST DE COMPORTAMIENTO DEL CACHE ===")
    
    try:
        # Limpiar cache de Streamlit si existe
        try:
            import streamlit as st
            st.cache_data.clear()
            print("✅ Cache de Streamlit limpiado")
        except:
            print("ℹ️  No se pudo limpiar el cache de Streamlit (normal en script standalone)")
        
        # Obtener estadísticas múltiples veces
        print("\n--- OBTENIENDO ESTADÍSTICAS MÚLTIPLES VECES ---")
        
        for i in range(3):
            stats = get_dashboard_stats()
            print(f"Intento {i+1}: Resueltas = {stats['resolved_incidents']}, Pendientes = {stats['pending_incidents']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de cache: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando tests de actualización de estado...\n")
    
    # Ejecutar tests
    test1_result = test_status_update()
    test2_result = test_cache_behavior()
    
    print("\n=== RESUMEN DE RESULTADOS ===")
    print(f"Test de actualización de estado: {'✅ PASÓ' if test1_result else '❌ FALLÓ'}")
    print(f"Test de comportamiento de cache: {'✅ PASÓ' if test2_result else '❌ FALLÓ'}")
    
    if test1_result and test2_result:
        print("\n🎉 Todos los tests pasaron. El problema puede estar en la interfaz de usuario.")
    else:
        print("\n⚠️  Se detectaron problemas. Revisar los logs anteriores.")