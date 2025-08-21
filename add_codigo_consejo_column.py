#!/usr/bin/env python3
"""Script para agregar la columna codigo_consejo a la tabla warehouses"""

import logging
from supabase_config import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_codigo_consejo_column():
    """Agrega la columna codigo_consejo a la tabla warehouses"""
    try:
        client = get_supabase_client()
        
        # SQL para agregar la columna
        sql_command = "ALTER TABLE warehouses ADD COLUMN codigo_consejo VARCHAR(50);"
        
        logger.info("Agregando columna codigo_consejo a la tabla warehouses...")
        logger.info(f"SQL: {sql_command}")
        
        # Intentar ejecutar usando RPC
        try:
            result = client.rpc('execute_sql', {'sql': sql_command}).execute()
            logger.info("✅ Columna codigo_consejo agregada exitosamente")
            return True
        except Exception as rpc_error:
            logger.error(f"❌ Error con RPC: {rpc_error}")
            
            # Si RPC no funciona, intentar método alternativo
            logger.info("Intentando método alternativo...")
            
            # Verificar si la columna ya existe
            test_result = client.table('warehouses').select('*').limit(1).execute()
            if test_result.data:
                columns = list(test_result.data[0].keys())
                if 'codigo_consejo' in columns:
                    logger.info("✅ La columna codigo_consejo ya existe")
                    return True
            
            logger.error("❌ No se pudo agregar la columna automáticamente")
            print("\n🔧 INSTRUCCIONES MANUALES:")
            print("1. Ve al dashboard de Supabase: https://supabase.com/dashboard")
            print("2. Selecciona tu proyecto")
            print("3. Ve a 'SQL Editor'")
            print("4. Ejecuta este comando:")
            print(f"   {sql_command}")
            print("5. Ejecuta este script nuevamente para verificar")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

def verify_column_added():
    """Verifica que la columna se haya agregado correctamente"""
    try:
        client = get_supabase_client()
        
        # Probar insertar con la nueva columna
        test_data = {
            'name': 'Test Verification',
            'codigo_consejo': 'VERIFY001',
            'zone': 'Test Zone'
        }
        
        logger.info("Verificando que la columna funcione...")
        result = client.table('warehouses').insert(test_data).execute()
        
        if result.data:
            logger.info("✅ Verificación exitosa - la columna funciona correctamente")
            
            # Limpiar el registro de prueba
            warehouse_id = result.data[0]['id']
            client.table('warehouses').delete().eq('id', warehouse_id).execute()
            logger.info("✅ Registro de verificación eliminado")
            
            return True
        else:
            logger.error("❌ La verificación falló")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Agregando columna codigo_consejo a la tabla warehouses...")
    
    success = add_codigo_consejo_column()
    
    if success:
        print("\n🧪 Verificando que la columna funcione...")
        verify_success = verify_column_added()
        
        if verify_success:
            print("\n✅ ¡Problema resuelto! La tabla warehouses ahora tiene la columna codigo_consejo")
            print("💡 Ahora puedes cargar tu CSV sin problemas")
        else:
            print("\n⚠️ La columna se agregó pero hay problemas con la verificación")
    else:
        print("\n❌ No se pudo agregar la columna automáticamente")
        print("💡 Sigue las instrucciones manuales mostradas arriba")