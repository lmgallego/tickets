#!/usr/bin/env python3
"""Script para probar la inserción en la tabla warehouses"""

import logging
from supabase_config import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_warehouse_insert():
    """Prueba insertar un registro en warehouses"""
    try:
        client = get_supabase_client()
        
        # Datos de prueba (usar 'nif' en lugar de 'codigo_consejo')
        test_data = {
            'name': 'Bodega Test',
            'nif': 'TEST001',
            'zone': 'Zona Test'
        }
        
        logger.info("Intentando insertar registro de prueba...")
        logger.info(f"Datos: {test_data}")
        
        # Intentar insertar
        result = client.table('warehouses').insert(test_data).execute()
        
        if result.data:
            logger.info(f"✅ Inserción exitosa: {result.data}")
            
            # Intentar eliminar el registro de prueba
            warehouse_id = result.data[0]['id']
            delete_result = client.table('warehouses').delete().eq('id', warehouse_id).execute()
            logger.info("✅ Registro de prueba eliminado")
            
            return True
        else:
            logger.error("❌ No se pudo insertar el registro")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error al insertar en warehouses: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        
        # Intentar obtener más detalles del error
        if hasattr(e, 'details'):
            logger.error(f"Detalles: {e.details}")
        if hasattr(e, 'message'):
            logger.error(f"Mensaje: {e.message}")
        if hasattr(e, 'code'):
            logger.error(f"Código: {e.code}")
            
        return False

if __name__ == "__main__":
    print("🧪 Probando inserción en tabla warehouses...")
    success = test_warehouse_insert()
    
    if success:
        print("✅ La tabla warehouses funciona correctamente")
    else:
        print("❌ Hay problemas con la tabla warehouses")