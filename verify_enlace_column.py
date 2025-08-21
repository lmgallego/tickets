#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar si la columna 'enlace' existe en la tabla incident_records
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_config import get_supabase_client

def verify_enlace_column():
    try:
        # Obtener cliente de Supabase
        supabase = get_supabase_client()
        
        print("Verificando estructura de la tabla incident_records...")
        
        # Intentar hacer una consulta que incluya la columna enlace
        response = supabase.table('incident_records').select('id, enlace').limit(1).execute()
        
        if response.data is not None:
            print("✅ La columna 'enlace' existe en la tabla incident_records")
            print(f"Respuesta: {response.data}")
        else:
            print("❌ Error al consultar la tabla")
            
    except Exception as e:
        print(f"❌ Error al verificar la columna 'enlace': {str(e)}")
        
        # Intentar obtener información del esquema
        try:
            print("\nIntentando obtener información del esquema...")
            # Consulta para obtener información de las columnas
            schema_response = supabase.rpc('get_table_columns', {'table_name': 'incident_records'}).execute()
            print(f"Información del esquema: {schema_response.data}")
        except Exception as schema_error:
            print(f"Error al obtener esquema: {str(schema_error)}")

if __name__ == "__main__":
    verify_enlace_column()