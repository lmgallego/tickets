#!/usr/bin/env python3
"""
Script para agregar el campo 'enlace' a la tabla incident_records
Compatible con SQLite y Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import DB_CONFIG
    from utils.database import get_db_connection
    from utils.database_supabase import get_supabase_connection
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def add_enlace_field_sqlite():
    """Agregar campo enlace a SQLite"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(incident_records)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'enlace' not in columns:
            # Agregar la columna enlace
            cursor.execute("ALTER TABLE incident_records ADD COLUMN enlace TEXT")
            conn.commit()
            print("✓ Campo 'enlace' agregado exitosamente a SQLite")
        else:
            print("✓ Campo 'enlace' ya existe en SQLite")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error agregando campo a SQLite: {e}")
        return False

def add_enlace_field_supabase():
    """Agregar campo enlace a Supabase"""
    print("Para Supabase, ejecuta manualmente en el SQL Editor del dashboard:")
    print("ALTER TABLE incident_records ADD COLUMN enlace TEXT;")
    print("✓ Esquema de Supabase actualizado en supabase_schema.sql")
    return True

def main():
    """Función principal"""
    print("Agregando campo 'enlace' a la tabla incident_records...")
    
    # Determinar qué base de datos usar
    use_supabase = DB_CONFIG.get('use_supabase', False)
    
    if use_supabase:
        print("Usando Supabase...")
        success = add_enlace_field_supabase()
    else:
        print("Usando SQLite...")
        success = add_enlace_field_sqlite()
    
    if success:
        print("\n✓ Campo 'enlace' agregado exitosamente")
        print("El campo permite almacenar URLs opcionales para cada registro de incidencia")
    else:
        print("\n✗ Hubo un error al agregar el campo")
        sys.exit(1)

if __name__ == "__main__":
    main()