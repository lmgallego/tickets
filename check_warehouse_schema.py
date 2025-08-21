#!/usr/bin/env python3
"""Script para verificar el esquema real de la tabla warehouses"""

import logging
from supabase_config import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_warehouse_schema():
    """Verifica el esquema actual de la tabla warehouses"""
    try:
        client = get_supabase_client()
        
        logger.info("Verificando esquema de la tabla warehouses...")
        
        # Intentar obtener todos los registros para ver las columnas
        result = client.table('warehouses').select('*').execute()
        
        if result.data:
            logger.info(f"✅ Tabla warehouses existe con {len(result.data)} registros")
            if result.data:
                columns = list(result.data[0].keys())
                logger.info(f"Columnas encontradas: {columns}")
            else:
                logger.info("Tabla vacía, no se pueden determinar las columnas")
        else:
            logger.info("✅ Tabla warehouses existe pero está vacía")
            
        # Intentar insertar solo con columnas básicas
        logger.info("Probando inserción con columnas básicas...")
        
        # Probar solo con 'name'
        test_data_basic = {'name': 'Test Warehouse'}
        result_basic = client.table('warehouses').insert(test_data_basic).execute()
        
        if result_basic.data:
            logger.info(f"✅ Inserción básica exitosa: {result_basic.data}")
            inserted_id = result_basic.data[0]['id']
            
            # Ver qué columnas tiene realmente
            actual_columns = list(result_basic.data[0].keys())
            logger.info(f"Columnas reales en la tabla: {actual_columns}")
            
            # Limpiar el registro de prueba
            client.table('warehouses').delete().eq('id', inserted_id).execute()
            logger.info("✅ Registro de prueba eliminado")
            
            return actual_columns
        else:
            logger.error("❌ No se pudo insertar ni siquiera con columnas básicas")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error al verificar esquema: {e}")
        return None

def suggest_fix(actual_columns):
    """Sugiere cómo corregir el problema"""
    required_columns = ['id', 'name', 'codigo_consejo', 'zone']
    
    if actual_columns:
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        if missing_columns:
            print(f"\n🔧 SOLUCIÓN REQUERIDA:")
            print(f"Columnas faltantes: {missing_columns}")
            print(f"\nEjecuta este SQL en el dashboard de Supabase:")
            
            for col in missing_columns:
                if col == 'codigo_consejo':
                    print(f"ALTER TABLE warehouses ADD COLUMN {col} VARCHAR(50);")
                elif col == 'zone':
                    print(f"ALTER TABLE warehouses ADD COLUMN {col} VARCHAR(100);")
        else:
            print("\n✅ Todas las columnas requeridas están presentes")
    else:
        print("\n🔧 SOLUCIÓN: Recrear la tabla warehouses con el esquema correcto")
        print("Ejecuta este SQL en el dashboard de Supabase:")
        print("""
DROP TABLE IF EXISTS warehouses;
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    codigo_consejo VARCHAR(50),
    zone VARCHAR(100)
);
""")

if __name__ == "__main__":
    print("🔍 Verificando esquema de la tabla warehouses...")
    columns = check_warehouse_schema()
    suggest_fix(columns)