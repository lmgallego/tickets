#!/usr/bin/env python3
"""
Script para agregar la columna 'enlace' a la tabla incident_records en Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_config import get_supabase_client
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def add_enlace_column():
    """Agregar columna enlace a Supabase usando SQL directo"""
    try:
        client = get_supabase_client()
        
        # Ejecutar ALTER TABLE para agregar la columna enlace
        result = client.rpc('exec_sql', {
            'sql': 'ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;'
        })
        
        print("✓ Columna 'enlace' agregada exitosamente a Supabase")
        return True
        
    except Exception as e:
        print(f"Error agregando columna: {e}")
        print("Intentando método alternativo...")
        
        try:
            # Método alternativo: usar postgrest directamente
            from supabase import create_client
            import os
            
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_ANON_KEY')
            
            if not url or not key:
                print("Error: Variables de entorno SUPABASE_URL y SUPABASE_ANON_KEY no configuradas")
                return False
                
            # Crear cliente con service_role key si está disponible
            service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            if service_key:
                client = create_client(url, service_key)
            else:
                client = create_client(url, key)
            
            # Intentar ejecutar SQL directo
            response = client.postgrest.rpc('exec_sql', {
                'sql': 'ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;'
            }).execute()
            
            print("✓ Columna 'enlace' agregada exitosamente (método alternativo)")
            return True
            
        except Exception as e2:
            print(f"Error con método alternativo: {e2}")
            print("\nPor favor, ejecuta manualmente en el SQL Editor de Supabase:")
            print("ALTER TABLE incident_records ADD COLUMN IF NOT EXISTS enlace TEXT;")
            return False

if __name__ == "__main__":
    print("Agregando columna 'enlace' a la tabla incident_records...")
    success = add_enlace_column()
    if success:
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n✗ Proceso falló - se requiere intervención manual")