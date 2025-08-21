#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar la columna 'enlace' directamente usando SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_config import get_supabase_client

def add_enlace_column_direct():
    try:
        # Obtener cliente de Supabase
        supabase = get_supabase_client()
        
        print("Agregando columna 'enlace' a la tabla incident_records...")
        
        # Usar rpc para ejecutar SQL directo
        sql_query = "ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;"
        
        # Ejecutar el SQL usando rpc
        response = supabase.rpc('exec_sql', {'sql': sql_query}).execute()
        
        print(f"✅ Columna 'enlace' agregada exitosamente")
        print(f"Respuesta: {response.data}")
        
        # Verificar que la columna se agregó
        print("\nVerificando que la columna se agregó...")
        verify_response = supabase.table('incident_records').select('enlace').limit(1).execute()
        print(f"✅ Verificación exitosa: {verify_response.data}")
        
    except Exception as e:
        print(f"❌ Error al agregar la columna 'enlace': {str(e)}")
        
        # Intentar método alternativo usando postgrest
        try:
            print("\nIntentando método alternativo...")
            # Crear una función temporal para ejecutar SQL
            create_function_sql = """
            CREATE OR REPLACE FUNCTION add_enlace_column()
            RETURNS void AS $$
            BEGIN
                ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            # Ejecutar la función
            exec_function_sql = "SELECT add_enlace_column();"
            
            print("Creando función temporal...")
            supabase.rpc('exec_sql', {'sql': create_function_sql}).execute()
            
            print("Ejecutando función...")
            result = supabase.rpc('exec_sql', {'sql': exec_function_sql}).execute()
            
            print(f"✅ Método alternativo exitoso: {result.data}")
            
        except Exception as alt_error:
            print(f"❌ Error en método alternativo: {str(alt_error)}")
            
            # Último intento: usar SQL directo sin rpc
            try:
                print("\nÚltimo intento: SQL directo...")
                from supabase import create_client
                from supabase_config import SUPABASE_URL, SUPABASE_KEY
                
                # Crear cliente con configuración específica
                client = create_client(SUPABASE_URL, SUPABASE_KEY)
                
                # Intentar ejecutar directamente
                response = client.postgrest.rpc('exec_sql', {'sql': 'ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;'}).execute()
                print(f"✅ SQL directo exitoso: {response.data}")
                
            except Exception as direct_error:
                print(f"❌ Error en SQL directo: {str(direct_error)}")
                print("\n⚠️  SOLUCIÓN MANUAL REQUERIDA:")
                print("Debe ejecutar manualmente en el SQL Editor de Supabase:")
                print("ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;")

if __name__ == "__main__":
    add_enlace_column_direct()