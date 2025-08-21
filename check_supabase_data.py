#!/usr/bin/env python3
"""Script para verificar datos en Supabase"""

from supabase_config import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_supabase_data():
    """Verifica si hay datos en las tablas de Supabase"""
    try:
        client = get_supabase_client()
        
        print("=" * 60)
        print("VERIFICACIÓN DE DATOS EN SUPABASE")
        print("=" * 60)
        
        # Verificar cada tabla
        tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
        
        for table in tables:
            try:
                # Contar registros
                count_result = client.table(table).select('count', count='exact').execute()
                count = count_result.count if count_result.count else 0
                
                print(f"Tabla '{table}': {count} registros")
                
                # Si hay registros, mostrar algunos ejemplos (sin joins)
                if count > 0:
                    sample_result = client.table(table).select('*').limit(3).execute()
                    if sample_result.data:
                        print(f"  Ejemplos:")
                        for i, record in enumerate(sample_result.data[:2], 1):
                            print(f"    {i}. {record}")
                
            except Exception as e:
                print(f"Error verificando tabla '{table}': {e}")
        
        print("\n" + "=" * 60)
        
        # Verificar específicamente incident_records SIN joins para evitar el error
        print("DETALLES DE INCIDENT_RECORDS (sin joins):")
        try:
            records_result = client.table('incident_records').select('*').execute()
            
            if records_result.data:
                print(f"Total de registros de incidencias: {len(records_result.data)}")
                for record in records_result.data:
                    print(f"  ID: {record['id']} | Fecha: {record['date']} | Estado: {record['status']}")
                    print(f"    Warehouse ID: {record.get('warehouse_id')} | Verifier ID: {record.get('causing_verifier_id')}")
                    print(f"    Incident ID: {record.get('incident_id')} | Coordinator ID: {record.get('assigned_coordinator_id')}")
                    print(f"    Explicación: {record.get('explanation', 'N/A')}")
                    print(f"    Responsable: {record.get('responsible', 'N/A')}")
                    print()
            else:
                print("No hay registros de incidencias")
                
        except Exception as e:
            print(f"Error obteniendo detalles de incident_records: {e}")
        
        # Verificar incident_actions
        print("DETALLES DE INCIDENT_ACTIONS:")
        try:
            actions_result = client.table('incident_actions').select('*').execute()
            
            if actions_result.data:
                print(f"Total de acciones: {len(actions_result.data)}")
                for action in actions_result.data:
                    print(f"  ID: {action['id']} | Registro ID: {action['incident_record_id']}")
                    print(f"    Fecha: {action['action_date']} | Descripción: {action['action_description']}")
                    print(f"    Nuevo Estado: {action.get('new_status', 'N/A')} | Por: {action.get('performed_by', 'N/A')}")
                    print()
            else:
                print("No hay acciones registradas")
                
        except Exception as e:
            print(f"Error obteniendo acciones: {e}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == '__main__':
    check_supabase_data()