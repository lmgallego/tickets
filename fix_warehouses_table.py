#!/usr/bin/env python3
"""Script para verificar y corregir la estructura de la tabla warehouses"""

import logging
from supabase_config import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_warehouses_table():
    """Verifica y corrige la estructura de la tabla warehouses"""
    try:
        client = get_supabase_client()
        
        # Primero, intentar hacer una consulta simple para verificar si la tabla existe
        logger.info("Verificando estructura de la tabla warehouses...")
        
        try:
            # Intentar obtener la estructura de la tabla
            result = client.table('warehouses').select('*').limit(1).execute()
            logger.info("✅ Tabla warehouses existe y es accesible")
            
            # Verificar si tiene las columnas necesarias
            if result.data:
                columns = list(result.data[0].keys())
                logger.info(f"Columnas encontradas: {columns}")
                
                required_columns = ['id', 'name', 'codigo_consejo', 'zone']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    logger.error(f"❌ Columnas faltantes: {missing_columns}")
                    return False
                else:
                    logger.info("✅ Todas las columnas requeridas están presentes")
                    return True
            else:
                logger.info("✅ Tabla existe pero está vacía")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error al acceder a la tabla warehouses: {e}")
            
            # Intentar recrear la tabla
            logger.info("Intentando recrear la tabla warehouses...")
            
            # SQL para recrear la tabla
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS warehouses (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                codigo_consejo VARCHAR(50),
                zone VARCHAR(100)
            );
            """
            
            # Ejecutar el SQL usando RPC si está disponible
            try:
                client.rpc('execute_sql', {'sql': create_table_sql}).execute()
                logger.info("✅ Tabla warehouses recreada exitosamente")
                return True
            except Exception as rpc_error:
                logger.error(f"❌ Error al recrear tabla con RPC: {rpc_error}")
                logger.info("💡 Por favor, ejecuta manualmente este SQL en el dashboard de Supabase:")
                print(create_table_sql)
                return False
                
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando y corrigiendo tabla warehouses...")
    success = fix_warehouses_table()
    
    if success:
        print("✅ Tabla warehouses está lista para usar")
    else:
        print("❌ Hay problemas con la tabla warehouses")
        print("💡 Revisa los logs arriba para más detalles")