import sqlite3
import pandas as pd
import os
import logging
import datetime
from .backup_restore import backup_db
try:
    from config import is_deployed_environment, DB_CONFIG
except ImportError:
    # Fallback si no existe config.py
    def is_deployed_environment():
        return False
    DB_CONFIG = {'path': 'db/cavacrm.db', 'preserve_data': True}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = DB_CONFIG['path']

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Verificar entorno y configuración
    deployed = is_deployed_environment()
    preserve_data = DB_CONFIG.get('preserve_data', True)
    
    logger.info(f"Environment - Deployed: {deployed}, Preserve data: {preserve_data}")
    
    # Verificar si la base de datos ya existe y tiene datos
    db_exists = os.path.exists(DB_PATH)
    logger.info(f"Database exists: {db_exists}")
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar si hay datos existentes antes de ejecutar el schema
    existing_records = 0
    tables_exist = False
    
    if db_exists:
        try:
            # Verificar si las tablas existen
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coordinators'")
            tables_exist = cursor.fetchone() is not None
            
            if tables_exist:
                count_result = cursor.execute('SELECT COUNT(*) FROM coordinators').fetchone()
                existing_records = count_result[0] if count_result else 0
                logger.info(f"Existing coordinators in database: {existing_records}")
            else:
                logger.info("Database file exists but tables don't exist yet")
        except sqlite3.OperationalError as e:
            logger.info(f"Database tables don't exist yet: {e}")
            tables_exist = False
    else:
        logger.info("Creating new database...")
    
    # Crear backup automático si estamos en deploy y hay datos
    if deployed and existing_records > 0 and DB_CONFIG.get('backup_on_deploy', True):
        try:
            backup_path = backup_db()
            logger.info(f"Automatic backup created before init: {backup_path}")
        except Exception as e:
            logger.warning(f"Could not create automatic backup: {e}")
    
    # Solo ejecutar el schema si las tablas no existen
    # En entornos de deploy, ser extra cuidadoso
    if not tables_exist or (not deployed and not preserve_data):
        logger.info("Executing schema to create/update tables...")
        with open(os.path.join('db', 'schema.sql'), 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        conn.commit()
        logger.info("Schema executed successfully")
    else:
        logger.info("Tables already exist, skipping schema execution to preserve data")
    
    # Verificar datos después de la inicialización
    try:
        final_count = cursor.execute('SELECT COUNT(*) FROM coordinators').fetchone()[0]
        logger.info(f"Final coordinators count after init: {final_count}")
        
        # Verificar otras tablas importantes
        incident_count = cursor.execute('SELECT COUNT(*) FROM incident_records').fetchone()[0]
        logger.info(f"Total incident records: {incident_count}")
        
    except sqlite3.OperationalError as e:
        logger.warning(f"Could not count records after init: {e}")
    
    # Chequeo de integridad
    try:
        integrity_result = cursor.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity_result != 'ok':
            logger.error(f"Integrity check failed: {integrity_result}")
            raise sqlite3.IntegrityError("Database integrity check failed")
        else:
            logger.info("Database integrity check passed")
    except Exception as e:
        logger.error(f"Error during integrity check: {e}")
    
    conn.close()
    logger.info("Database initialization completed successfully")

def insert_coordinator(name, surnames):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO coordinators (name, surnames) VALUES (?, ?)', (name, surnames))
        conn.commit()
        logger.info(f"Inserted coordinator: {name} {surnames}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting coordinator: {e}")
    finally:
        conn.close()

def insert_verifier(name, surnames, phone, zone):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO verifiers (name, surnames, phone, zone) VALUES (?, ?, ?, ?)', (name, surnames, phone, zone))
        conn.commit()
        logger.info(f"Inserted verifier: {name} {surnames}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting verifier: {e}")
    finally:
        conn.close()

def insert_warehouse(name, codigo_consejo, zone):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO warehouses (name, codigo_consejo, zone) VALUES (?, ?, ?)', (name, codigo_consejo, zone))
        conn.commit()
        logger.info(f"Inserted warehouse: {name} with Código Consejo {codigo_consejo}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting warehouse: {e}")
    finally:
        conn.close()

def load_csv_to_verifiers(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    conn = get_db_connection()
    for _, row in df.iterrows():
        name = row['name']
        surnames = row['surnames']
        cursor = conn.execute('SELECT COUNT(*) FROM verifiers WHERE name = ? AND surnames = ?', (name, surnames))
        if cursor.fetchone()[0] == 0:
            insert_verifier(name, surnames, row.get('phone', ''), row.get('zone', ''))
        else:
            print(f"Verifier {name} {surnames} already exists, skipping.")
    conn.close()

def load_csv_to_warehouses(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    conn = get_db_connection()
    for _, row in df.iterrows():
        codigo_consejo = row['codigo_consejo']
        cursor = conn.execute('SELECT COUNT(*) FROM warehouses WHERE codigo_consejo = ?', (codigo_consejo,))
        if cursor.fetchone()[0] == 0:
            insert_warehouse(row['name'], codigo_consejo, row.get('zone', ''))
        else:
            print(f"Warehouse with Código Consejo {codigo_consejo} already exists, skipping.")
    conn.close()

def insert_incident(description, custom_code=None):
    """Inserta una nueva incidencia con código automático o personalizado"""
    try:
        conn = get_db_connection()
        
        if custom_code:
            # Verificar si el código personalizado ya existe
            existing = conn.execute('SELECT id FROM incidents WHERE code = ?', (custom_code,)).fetchone()
            if existing:
                return {'success': False, 'error': f'El código "{custom_code}" ya existe. Por favor, use un código diferente.'}
            code = custom_code
        else:
            # Generar código automático
            cursor = conn.execute('SELECT COUNT(*) FROM incidents')
            count = cursor.fetchone()[0]
            code = f"{count + 1:03d}"
            
            # Verificar que el código automático no exista (por seguridad)
            while conn.execute('SELECT id FROM incidents WHERE code = ?', (code,)).fetchone():
                count += 1
                code = f"{count + 1:03d}"
        
        conn.execute('INSERT INTO incidents (code, description) VALUES (?, ?)', (code, description))
        conn.commit()
        logger.info(f"Inserted incident with code {code}")
        return {'success': True, 'code': code}
        
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident: {e}")
        return {'success': False, 'error': f'Error al guardar la incidencia: {str(e)}'}
    finally:
        conn.close()

def get_coordinators():
    try:
        conn = get_db_connection()
        coordinators = conn.execute('SELECT id, name, surnames FROM coordinators').fetchall()
        return [dict(row) for row in coordinators]
    except sqlite3.Error as e:
        print(f"Error getting coordinators: {e}")
        return []
    finally:
        conn.close()

def get_verifiers():
    conn = get_db_connection()
    verifiers = conn.execute('SELECT id, name, surnames, phone, zone FROM verifiers').fetchall()
    conn.close()
    return [dict(row) for row in verifiers]

def get_warehouses():
    conn = get_db_connection()
    warehouses = conn.execute('SELECT id, name, codigo_consejo, zone FROM warehouses').fetchall()
    conn.close()
    return [dict(row) for row in warehouses]

def get_incidents():
    conn = get_db_connection()
    incidents = conn.execute('SELECT id, code || " - " || description AS label FROM incidents').fetchall()
    conn.close()
    return [(row['id'], row['label']) for row in incidents]

def insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO incident_records (date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                     (date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible))
        conn.commit()
        logger.info(f"Inserted incident record on date {date}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident record: {e}")
    finally:
        conn.close()

def get_incident_records():
    conn = get_db_connection()
    records = conn.execute('SELECT ir.id, ir.date, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, v.name || " " || v.surnames AS causing_verifier, i.code || " - " || i.description AS incident, ac.name || " " || ac.surnames AS assigned_coordinator, ir.explanation, ir.status, ir.responsible FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id ORDER BY ir.date DESC').fetchall()
    conn.close()
    return [(row['id'], f"ID: {row['id']} - Fecha: {row['date']} - Incidencia: {row['incident']} - Bodega: {row['warehouse']} - Verificador: {row['causing_verifier']} - Coordinador: {row['assigned_coordinator']}") for row in records]

def insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO incident_actions (incident_record_id, action_date, action_description, new_status, performed_by) VALUES (?, ?, ?, ?, ?)', (incident_record_id, action_date, action_description, new_status, performed_by))
        if new_status:
            conn.execute('UPDATE incident_records SET status = ? WHERE id = ?', (new_status, incident_record_id))
        conn.commit()
        logger.info(f"Inserted action for incident record {incident_record_id}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident action: {e}")
    finally:
        conn.close()

def get_incident_actions(incident_record_id):
    conn = get_db_connection()
    actions = conn.execute('SELECT ia.action_date, ia.action_description, ia.new_status, c.name || " " || c.surnames AS performed_by FROM incident_actions ia JOIN coordinators c ON ia.performed_by = c.id WHERE ia.incident_record_id = ? ORDER BY ia.action_date', (incident_record_id,)).fetchall()
    conn.close()
    return actions

def get_all_incident_records_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT ir.id, ir.date, ir.explanation, ir.enlace, ir.status, ir.responsible, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, w.zone AS warehouse_zone, v.name || " " || v.surnames AS causing_verifier, v.zone AS verifier_zone, i.description AS incident_type, ac.name || " " || ac.surnames AS assigned_coordinator FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id', conn)
    conn.close()
    return df

def get_all_verifiers_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM verifiers', conn)
    conn.close()
    return df

def get_all_warehouses_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM warehouses', conn)
    conn.close()
    return df

def get_incidents_by_zone():
    df = get_all_incident_records_df()
    return df.groupby('warehouse_zone').size().reset_index(name='count')

def get_incidents_by_verifier():
    df = get_all_incident_records_df()
    return df.groupby('causing_verifier').size().reset_index(name='count')

def get_incidents_by_warehouse():
    df = get_all_incident_records_df()
    return df.groupby('warehouse').size().reset_index(name='count')

def get_incidents_by_type():
    df = get_all_incident_records_df()
    return df.groupby('incident_type').size().reset_index(name='count')

def get_incidents_by_status():
    df = get_all_incident_records_df()
    return df.groupby('status').size().reset_index(name='count')

def get_assignments_by_verifier():
    df = get_all_incident_records_df()
    return df[df['responsible'] == 'Verificador'].groupby('causing_verifier').size().reset_index(name='count')

def reset_database():
    conn = get_db_connection()
    tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
    for table in tables:
        conn.execute(f'DELETE FROM {table}')
    conn.commit()
    conn.close()

def get_incident_record_details(incident_record_id):
    conn = get_db_connection()
    row = conn.execute('SELECT ir.*, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, w.zone AS warehouse_zone, v.name || " " || v.surnames AS causing_verifier, v.zone AS verifier_zone, i.description AS incident_type, ac.name || " " || ac.surnames AS assigned_coordinator FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id WHERE ir.id = ?', (incident_record_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}

def export_incidents_to_excel():
    """Exporta historial completo de incidencias con acciones a Excel"""
    conn = get_db_connection()
    
    # Obtener datos de incidencias
    incidents_query = '''
    SELECT 
        ir.id as 'ID Registro',
        ir.date as 'Fecha',
        c.name || " " || c.surnames as 'Coordinador Registrador',
        w.name as 'Bodega',
        w.zone as 'Zona Bodega',
        v.name || " " || v.surnames as 'Verificador Causante',
        v.zone as 'Zona Verificador',
        i.code || " - " || i.description as 'Incidencia',
        ac.name || " " || ac.surnames as 'Coordinador Asignado',
        ir.explanation as 'Explicación',
        ir.status as 'Estado',
        ir.responsible as 'Responsable'
    FROM incident_records ir 
    JOIN coordinators c ON ir.registering_coordinator_id = c.id 
    JOIN warehouses w ON ir.warehouse_id = w.id 
    JOIN verifiers v ON ir.causing_verifier_id = v.id 
    JOIN incidents i ON ir.incident_id = i.id 
    JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
    ORDER BY ir.date DESC
    '''
    
    # Obtener datos de acciones
    actions_query = '''
    SELECT 
        ia.incident_record_id as 'ID Registro',
        ia.action_date as 'Fecha Acción',
        ia.action_description as 'Descripción Acción',
        ia.new_status as 'Nuevo Estado',
        c.name || " " || c.surnames as 'Realizado Por'
    FROM incident_actions ia
    JOIN coordinators c ON ia.performed_by = c.id
    ORDER BY ia.incident_record_id, ia.action_date
    '''
    
    df_incidents = pd.read_sql_query(incidents_query, conn)
    df_actions = pd.read_sql_query(actions_query, conn)
    conn.close()
    
    # Crear archivo Excel
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'historial_incidencias_{timestamp}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_incidents.to_excel(writer, sheet_name='Incidencias', index=False)
        df_actions.to_excel(writer, sheet_name='Acciones', index=False)
    
    return filename

def create_backup():
    """Crea una copia de seguridad de la base de datos"""
    try:
        backup_path = backup_db()
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise e

def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    conn = get_db_connection()
    
    # Estadísticas generales
    stats = {}
    
    # Total de incidencias
    stats['total_incidents'] = conn.execute('SELECT COUNT(*) FROM incident_records').fetchone()[0]
    
    # Incidencias no resueltas (pendientes)
    stats['pending_incidents'] = conn.execute('SELECT COUNT(*) FROM incident_records WHERE status != "Solucionado"').fetchone()[0]
    
    # Incidencias resueltas
    stats['resolved_incidents'] = conn.execute('SELECT COUNT(*) FROM incident_records WHERE status = "Solucionado"').fetchone()[0]
    
    # Incidencias por estado
    status_query = '''
    SELECT status, COUNT(*) as count 
    FROM incident_records 
    GROUP BY status 
    ORDER BY count DESC
    '''
    stats['by_status'] = pd.read_sql_query(status_query, conn)
    
    # Incidencias recientes (últimos 7 días)
    recent_query = '''
    SELECT COUNT(*) 
    FROM incident_records 
    WHERE date >= date('now', '-7 days')
    '''
    stats['recent_incidents'] = conn.execute(recent_query).fetchone()[0]
    
    conn.close()
    return stats

def get_pending_incidents_summary():
    """Obtiene resumen de incidencias pendientes para el dashboard"""
    conn = get_db_connection()
    
    query = '''
    SELECT 
        ir.id,
        ir.date,
        w.name as warehouse,
        w.zone as warehouse_zone,
        v.name || " " || v.surnames as causing_verifier,
        i.description as incident_type,
        ac.name || " " || ac.surnames as assigned_coordinator,
        ir.status,
        ir.responsible
    FROM incident_records ir 
    JOIN warehouses w ON ir.warehouse_id = w.id 
    JOIN verifiers v ON ir.causing_verifier_id = v.id 
    JOIN incidents i ON ir.incident_id = i.id 
    JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
    WHERE ir.status != "Solucionado"
    ORDER BY ir.date DESC
    LIMIT 10
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_recent_actions():
    """Obtiene las acciones más recientes para el dashboard"""
    conn = get_db_connection()
    
    query = '''
    SELECT 
        ia.action_date,
        ia.action_description,
        ia.new_status,
        c.name || " " || c.surnames as performed_by,
        ir.id as incident_id,
        w.name as warehouse
    FROM incident_actions ia
    JOIN coordinators c ON ia.performed_by = c.id
    JOIN incident_records ir ON ia.incident_record_id = ir.id
    JOIN warehouses w ON ir.warehouse_id = w.id
    ORDER BY ia.action_date DESC
    LIMIT 5
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def search_incident_by_code(code):
    """Busca una incidencia por su código único"""
    try:
        conn = get_db_connection()
        incident = conn.execute('SELECT * FROM incidents WHERE code = ?', (code,)).fetchone()
        if incident:
            return {'success': True, 'incident': dict(incident)}
        else:
            return {'success': False, 'error': f'No se encontró ninguna incidencia con el código "{code}"'}
    except sqlite3.Error as e:
        logger.error(f"Error searching incident by code: {e}")
        return {'success': False, 'error': f'Error al buscar la incidencia: {str(e)}'}
    finally:
        conn.close()

def get_incident_records_by_incident_code(code):
    """Obtiene todos los registros de incidencia asociados a un código de incidencia"""
    try:
        conn = get_db_connection()
        query = '''
        SELECT 
            ir.id,
            ir.date,
            ir.explanation,
            ir.enlace,
            ir.status,
            ir.responsible,
            i.code as incident_code,
            i.description as incident_description,
            c.name || " " || c.surnames as registering_coordinator,
            w.name as warehouse,
            w.zone as warehouse_zone,
            v.name || " " || v.surnames as causing_verifier,
            ac.name || " " || ac.surnames as assigned_coordinator
        FROM incident_records ir
        JOIN incidents i ON ir.incident_id = i.id
        JOIN coordinators c ON ir.registering_coordinator_id = c.id
        JOIN warehouses w ON ir.warehouse_id = w.id
        JOIN verifiers v ON ir.causing_verifier_id = v.id
        JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
        WHERE i.code = ?
        ORDER BY ir.date DESC
        '''
        
        records = conn.execute(query, (code,)).fetchall()
        if records:
            return {'success': True, 'records': [dict(record) for record in records]}
        else:
            return {'success': False, 'error': f'No se encontraron registros para el código de incidencia "{code}"'}
    except sqlite3.Error as e:
        logger.error(f"Error getting incident records by code: {e}")
        return {'success': False, 'error': f'Error al buscar registros: {str(e)}'}
    finally:
        conn.close()

# Funciones de actualización/edición
def update_coordinator(coordinator_id, name, surnames):
    """Actualizar un coordinador existente"""
    try:
        conn = get_db_connection()
        conn.execute('UPDATE coordinators SET name = ?, surnames = ? WHERE id = ?', (name, surnames, coordinator_id))
        conn.commit()
        logger.info(f"Updated coordinator ID {coordinator_id}: {name} {surnames}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating coordinator: {e}")
        return False
    finally:
        conn.close()

def update_verifier(verifier_id, name, surnames, phone, zone):
    """Actualizar un verificador existente"""
    try:
        conn = get_db_connection()
        conn.execute('UPDATE verifiers SET name = ?, surnames = ?, phone = ?, zone = ? WHERE id = ?', 
                     (name, surnames, phone, zone, verifier_id))
        conn.commit()
        logger.info(f"Updated verifier ID {verifier_id}: {name} {surnames}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating verifier: {e}")
        return False
    finally:
        conn.close()

def update_warehouse(warehouse_id, name, codigo_consejo, zone):
    """Actualizar una bodega existente"""
    try:
        conn = get_db_connection()
        conn.execute('UPDATE warehouses SET name = ?, codigo_consejo = ?, zone = ? WHERE id = ?', 
                     (name, codigo_consejo, zone, warehouse_id))
        conn.commit()
        logger.info(f"Updated warehouse ID {warehouse_id}: {name}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating warehouse: {e}")
        return False
    finally:
        conn.close()

def update_incident(incident_id, code, description):
    """Actualizar un tipo de incidencia existente"""
    try:
        conn = get_db_connection()
        conn.execute('UPDATE incidents SET code = ?, description = ? WHERE id = ?', 
                     (code, description, incident_id))
        conn.commit()
        logger.info(f"Updated incident ID {incident_id}: {code}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating incident: {e}")
        return False
    finally:
        conn.close()

# Funciones para obtener registros individuales
def get_coordinator_by_id(coordinator_id):
    """Obtener un coordinador por ID"""
    try:
        conn = get_db_connection()
        coordinator = conn.execute('SELECT * FROM coordinators WHERE id = ?', (coordinator_id,)).fetchone()
        return dict(coordinator) if coordinator else None
    except sqlite3.Error as e:
        logger.error(f"Error getting coordinator: {e}")
        return None
    finally:
        conn.close()

def get_verifier_by_id(verifier_id):
    """Obtener un verificador por ID"""
    try:
        conn = get_db_connection()
        verifier = conn.execute('SELECT * FROM verifiers WHERE id = ?', (verifier_id,)).fetchone()
        return dict(verifier) if verifier else None
    except sqlite3.Error as e:
        logger.error(f"Error getting verifier: {e}")
        return None
    finally:
        conn.close()

def get_warehouse_by_id(warehouse_id):
    """Obtener una bodega por ID"""
    try:
        conn = get_db_connection()
        warehouse = conn.execute('SELECT * FROM warehouses WHERE id = ?', (warehouse_id,)).fetchone()
        return dict(warehouse) if warehouse else None
    except sqlite3.Error as e:
        logger.error(f"Error getting warehouse: {e}")
        return None
    finally:
        conn.close()

def get_incident_by_id(incident_id):
    """Obtener un tipo de incidencia por ID"""
    try:
        conn = get_db_connection()
        incident = conn.execute('SELECT * FROM incidents WHERE id = ?', (incident_id,)).fetchone()
        return dict(incident) if incident else None
    except sqlite3.Error as e:
        logger.error(f"Error getting incident: {e}")
        return None
    finally:
        conn.close()

def get_pending_incidents_by_coordinator(coordinator_id=None):
    """Obtiene incidencias pendientes filtradas por coordinador asignado"""
    try:
        conn = get_db_connection()
        
        if coordinator_id:
            query = '''
            SELECT ir.id, ir.date, ir.status, ir.responsible,
                   w.name as warehouse, w.zone as warehouse_zone,
                   v.name || " " || v.surnames as causing_verifier,
                   i.description as incident_type,
                   ac.name || " " || ac.surnames as assigned_coordinator
            FROM incident_records ir
            JOIN warehouses w ON ir.warehouse_id = w.id
            JOIN verifiers v ON ir.causing_verifier_id = v.id
            JOIN incidents i ON ir.incident_id = i.id
            JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
            WHERE ir.status != 'Solucionado' AND ir.assigned_coordinator_id = ?
            ORDER BY ir.date DESC
            LIMIT 10
            '''
            records = conn.execute(query, (coordinator_id,)).fetchall()
        else:
            query = '''
            SELECT ir.id, ir.date, ir.status, ir.responsible,
                   w.name as warehouse, w.zone as warehouse_zone,
                   v.name || " " || v.surnames as causing_verifier,
                   i.description as incident_type,
                   ac.name || " " || ac.surnames as assigned_coordinator
            FROM incident_records ir
            JOIN warehouses w ON ir.warehouse_id = w.id
            JOIN verifiers v ON ir.causing_verifier_id = v.id
            JOIN incidents i ON ir.incident_id = i.id
            JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
            WHERE ir.status != 'Solucionado'
            ORDER BY ir.date DESC
            LIMIT 10
            '''
            records = conn.execute(query).fetchall()
        
        import pandas as pd
        return pd.DataFrame([dict(record) for record in records])
    except sqlite3.Error as e:
        logger.error(f"Error getting pending incidents by coordinator: {e}")
        import pandas as pd
        return pd.DataFrame()
    finally:
        conn.close()

def get_filtered_pending_incidents(coordinator_id=None, status=None, days=None):
    """Obtiene incidencias pendientes con filtros múltiples"""
    try:
        conn = get_db_connection()
        
        # Construir la consulta base
        query = '''
        SELECT ir.id, ir.date, ir.status, ir.responsible,
               w.name as warehouse, w.zone as warehouse_zone,
               v.name || " " || v.surnames as causing_verifier,
               i.description as incident_type,
               ac.name || " " || ac.surnames as assigned_coordinator
        FROM incident_records ir
        JOIN warehouses w ON ir.warehouse_id = w.id
        JOIN verifiers v ON ir.causing_verifier_id = v.id
        JOIN incidents i ON ir.incident_id = i.id
        JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id
        WHERE ir.status != 'Solucionado'
        '''
        
        params = []
        
        # Agregar filtros según los parámetros
        if coordinator_id:
            query += " AND ir.assigned_coordinator_id = ?"
            params.append(coordinator_id)
        
        if status:
            query += " AND ir.status = ?"
            params.append(status)
        
        if days:
            query += " AND ir.date >= date('now', '-{} days')".format(days)
        
        query += " ORDER BY ir.date DESC LIMIT 20"
        
        records = conn.execute(query, params).fetchall()
        
        import pandas as pd
        return pd.DataFrame([dict(record) for record in records])
    except sqlite3.Error as e:
        logger.error(f"Error getting filtered pending incidents: {e}")
        import pandas as pd
        return pd.DataFrame()
    finally:
        conn.close()