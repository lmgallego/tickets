#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar las zonas PENEDES y CONCA en la base de datos
Cambia PENEDES por PENEDÈS y CONCA por CONCA DE BARBERÀ
"""

import logging
try:
    from utils.database import get_db_connection as get_sqlite_connection
    from utils.database_supabase import get_supabase_connection
    from config import DB_CONFIG
except ImportError as e:
    print(f"Error importing modules: {e}")
    exit(1)

# Determinar qué base de datos usar
USE_SUPABASE = DB_CONFIG.get('use_supabase', False)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_zones_sqlite():
    """Actualizar zonas en SQLite"""
    try:
        conn = get_sqlite_connection()
        
        # Actualizar verificadores
        cursor = conn.execute("UPDATE verifiers SET zone = 'PENEDÈS' WHERE zone = 'PENEDES'")
        penedes_verifiers = cursor.rowcount
        
        cursor = conn.execute("UPDATE verifiers SET zone = 'CONCA DE BARBERÀ' WHERE zone = 'CONCA'")
        conca_verifiers = cursor.rowcount
        
        # Actualizar bodegas
        cursor = conn.execute("UPDATE warehouses SET zone = 'PENEDÈS' WHERE zone = 'PENEDES'")
        penedes_warehouses = cursor.rowcount
        
        cursor = conn.execute("UPDATE warehouses SET zone = 'CONCA DE BARBERÀ' WHERE zone = 'CONCA'")
        conca_warehouses = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite - Verificadores actualizados: PENEDES→PENEDÈS ({penedes_verifiers}), CONCA→CONCA DE BARBERÀ ({conca_verifiers})")
        logger.info(f"SQLite - Bodegas actualizadas: PENEDES→PENEDÈS ({penedes_warehouses}), CONCA→CONCA DE BARBERÀ ({conca_warehouses})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando zonas en SQLite: {e}")
        return False

def update_zones_supabase():
    """Actualizar zonas en Supabase"""
    try:
        client = get_supabase_connection()
        
        # Actualizar verificadores PENEDES → PENEDÈS
        result1 = client.table('verifiers').update({'zone': 'PENEDÈS'}).eq('zone', 'PENEDES').execute()
        penedes_verifiers = len(result1.data) if result1.data else 0
        
        # Actualizar verificadores CONCA → CONCA DE BARBERÀ
        result2 = client.table('verifiers').update({'zone': 'CONCA DE BARBERÀ'}).eq('zone', 'CONCA').execute()
        conca_verifiers = len(result2.data) if result2.data else 0
        
        # Actualizar bodegas PENEDES → PENEDÈS
        result3 = client.table('warehouses').update({'zone': 'PENEDÈS'}).eq('zone', 'PENEDES').execute()
        penedes_warehouses = len(result3.data) if result3.data else 0
        
        # Actualizar bodegas CONCA → CONCA DE BARBERÀ
        result4 = client.table('warehouses').update({'zone': 'CONCA DE BARBERÀ'}).eq('zone', 'CONCA').execute()
        conca_warehouses = len(result4.data) if result4.data else 0
        
        logger.info(f"Supabase - Verificadores actualizados: PENEDES→PENEDÈS ({penedes_verifiers}), CONCA→CONCA DE BARBERÀ ({conca_verifiers})")
        logger.info(f"Supabase - Bodegas actualizadas: PENEDES→PENEDÈS ({penedes_warehouses}), CONCA→CONCA DE BARBERÀ ({conca_warehouses})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando zonas en Supabase: {e}")
        return False

def main():
    """Función principal para actualizar las zonas"""
    logger.info("Iniciando actualización de zonas...")
    
    try:
        if USE_SUPABASE:
            logger.info("Usando Supabase para actualizar zonas")
            success = update_zones_supabase()
        else:
            logger.info("Usando SQLite para actualizar zonas")
            success = update_zones_sqlite()
        
        if success:
            logger.info("✅ Actualización de zonas completada exitosamente")
            print("\n✅ ACTUALIZACIÓN COMPLETADA")
            print("Las zonas han sido actualizadas:")
            print("• PENEDES → PENEDÈS")
            print("• CONCA → CONCA DE BARBERÀ")
        else:
            logger.error("❌ Error durante la actualización de zonas")
            print("\n❌ ERROR EN LA ACTUALIZACIÓN")
            print("Revisa los logs para más detalles")
            
    except Exception as e:
        logger.error(f"Error general en la actualización: {e}")
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()