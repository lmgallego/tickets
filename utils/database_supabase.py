import pandas as pd
import os
import logging
import datetime
from supabase_config import get_supabase_client, test_connection
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

def get_supabase_connection():
    """Obtiene el cliente de Supabase"""
    return get_supabase_client()

def init_db():
    """Inicializa la base de datos Supabase"""
    # Verificar entorno y configuración
    deployed = is_deployed_environment()
    preserve_data = DB_CONFIG.get('preserve_data', True)
    
    logger.info(f"Environment - Deployed: {deployed}, Preserve data: {preserve_data}")
    
    try:
        # Verificar conexión con Supabase
        client = get_supabase_connection()
        
        # Verificar si las tablas existen y tienen datos
        existing_records = 0
        tables_exist = True
        
        try:
            # Verificar si las tablas existen consultando coordinators
            result = client.table('coordinators').select('count', count='exact').limit(1).execute()
            existing_records = result.count if result.count else 0
            logger.info(f"Existing coordinators in database: {existing_records}")
        except Exception as e:
            logger.info(f"Database tables don't exist yet or are not accessible: {e}")
            tables_exist = False
        
        if not tables_exist:
            logger.warning("⚠️ Las tablas no existen en Supabase.")
            logger.info("Por favor, ejecuta el script supabase_schema.sql en el SQL Editor de Supabase")
            return False
        
        # Verificar datos después de la inicialización
        try:
            coordinators_result = client.table('coordinators').select('count', count='exact').limit(1).execute()
            final_count = coordinators_result.count if coordinators_result.count else 0
            logger.info(f"Final coordinators count after init: {final_count}")
            
            # Verificar otras tablas importantes
            incidents_result = client.table('incident_records').select('count', count='exact').limit(1).execute()
            incident_count = incidents_result.count if incidents_result.count else 0
            logger.info(f"Total incident records: {incident_count}")
            
        except Exception as e:
            logger.warning(f"Could not count records after init: {e}")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing Supabase database: {e}")
        return False

def insert_coordinator(name, surnames):
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').insert({
            'name': name,
            'surnames': surnames
        }).execute()
        logger.info(f"Inserted coordinator: {name} {surnames}")
        return True
    except Exception as e:
        logger.error(f"Error inserting coordinator: {e}")
        return False

def insert_verifier(name, surnames, phone, zone):
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').insert({
            'name': name,
            'surnames': surnames,
            'phone': phone,
            'zone': zone
        }).execute()
        logger.info(f"Inserted verifier: {name} {surnames}")
        return True
    except Exception as e:
        logger.error(f"Error inserting verifier: {e}")
        return False

def insert_warehouse(name, codigo_consejo, zone):
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').insert({
            'name': name,
            'nif': codigo_consejo,  # Usar 'nif' en lugar de 'codigo_consejo'
            'zone': zone
        }).execute()
        logger.info(f"Inserted warehouse: {name} with Código Consejo {codigo_consejo}")
        return True
    except Exception as e:
        logger.error(f"Error inserting warehouse: {e}")
        return False

def load_csv_to_verifiers(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    client = get_supabase_connection()
    
    for _, row in df.iterrows():
        name = row['name']
        surnames = row['surnames']
        
        # Verificar si ya existe
        existing = client.table('verifiers').select('id').eq('name', name).eq('surnames', surnames).execute()
        
        if not existing.data:
            insert_verifier(name, surnames, row.get('phone', ''), row.get('zone', ''))
        else:
            print(f"Verifier {name} {surnames} already exists, skipping.")

def load_csv_to_warehouses(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    client = get_supabase_connection()
    
    for _, row in df.iterrows():
        codigo_consejo = row['codigo_consejo']
        
        # Verificar si ya existe (usar 'nif' en lugar de 'codigo_consejo')
        existing = client.table('warehouses').select('id').eq('nif', codigo_consejo).execute()
        
        if not existing.data:
            insert_warehouse(row['name'], codigo_consejo, row.get('zone', ''))
        else:
            print(f"Warehouse with Código Consejo {codigo_consejo} already exists, skipping.")

def insert_incident(description, custom_code=None):
    """Inserta una nueva incidencia con código automático o personalizado"""
    try:
        client = get_supabase_connection()
        
        if custom_code:
            # Verificar si el código personalizado ya existe
            existing = client.table('incidents').select('id').eq('code', custom_code).execute()
            if existing.data:
                return {'success': False, 'error': f'El código "{custom_code}" ya existe. Por favor, use un código diferente.'}
            code = custom_code
        else:
            # Generar código automático
            count_result = client.table('incidents').select('count', count='exact').execute()
            count = count_result.count if count_result.count else 0
            code = f"{count + 1:03d}"
            
            # Verificar que el código automático no exista (por seguridad)
            while True:
                existing = client.table('incidents').select('id').eq('code', code).execute()
                if not existing.data:
                    break
                count += 1
                code = f"{count + 1:03d}"
        
        result = client.table('incidents').insert({
            'code': code,
            'description': description
        }).execute()
        
        logger.info(f"Inserted incident with code {code}")
        return {'success': True, 'code': code}
        
    except Exception as e:
        logger.error(f"Error inserting incident: {e}")
        return {'success': False, 'error': f'Error al guardar la incidencia: {str(e)}'}

def get_coordinators():
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').select('id, name, surnames').execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting coordinators: {e}")
        return []

def get_verifiers():
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('id, name, surnames, phone, zone').execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting verifiers: {e}")
        return []

def get_warehouses():
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('id, name, nif, zone').execute()
        # Mapear 'nif' a 'codigo_consejo' para mantener compatibilidad
        warehouses = []
        for warehouse in result.data:
            warehouse_copy = warehouse.copy()
            warehouse_copy['codigo_consejo'] = warehouse_copy.pop('nif', '')
            warehouses.append(warehouse_copy)
        return warehouses
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        return []

def get_incidents():
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('id, code, description').execute()
        return [(row['id'], f"{row['code']} - {row['description']}") for row in result.data]
    except Exception as e:
        logger.error(f"Error getting incidents: {e}")
        return []

def insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible):
    try:
        client = get_supabase_connection()
        # Convertir fecha a string si es necesario
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        
        # Temporalmente excluir 'enlace' hasta que se agregue la columna en Supabase
        result = client.table('incident_records').insert({
            'date': date_str,
            'registering_coordinator_id': registering_coordinator_id,
            'warehouse_id': warehouse_id,
            'causing_verifier_id': causing_verifier_id,
            'incident_id': incident_id,
            'assigned_coordinator_id': assigned_coordinator_id,
            'explanation': explanation,
            # 'enlace': enlace,  # Comentado temporalmente - columna no existe en Supabase
            'status': status,
            'responsible': responsible
        }).execute()
        logger.info(f"Inserted incident record on date {date_str}")
        return True
    except Exception as e:
        logger.error(f"Error inserting incident record: {e}")
        return False

def get_incident_records():
    try:
        client = get_supabase_connection()
        # Temporalmente excluir 'enlace' de la consulta hasta que se agregue la columna en Supabase
        result = client.table('incident_records').select(
            'id, date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible'
        ).order('date', desc=True).execute()
        
        # Obtener datos relacionados por separado para evitar conflictos
        coordinators = {coord['id']: coord for coord in client.table('coordinators').select('*').execute().data}
        warehouses = {wh['id']: wh for wh in client.table('warehouses').select('*').execute().data}
        verifiers = {ver['id']: ver for ver in client.table('verifiers').select('*').execute().data}
        incidents = {inc['id']: inc for inc in client.table('incidents').select('*').execute().data}
        
        records = []
        for record in result.data:
            reg_coord = coordinators.get(record['registering_coordinator_id'], {})
            warehouse = warehouses.get(record['warehouse_id'], {})
            verifier = verifiers.get(record['causing_verifier_id'], {})
            incident = incidents.get(record['incident_id'], {})
            assigned_coord = coordinators.get(record['assigned_coordinator_id'], {})
            
            registering_coordinator = f"{reg_coord.get('name', '')} {reg_coord.get('surnames', '')}"
            warehouse_name = warehouse.get('name', 'N/A')
            causing_verifier = f"{verifier.get('name', '')} {verifier.get('surnames', '')}"
            incident_desc = f"{incident.get('code', '')} - {incident.get('description', '')}"
            assigned_coordinator = f"{assigned_coord.get('name', '')} {assigned_coord.get('surnames', '')}"
            
            display_text = f"ID: {record['id']} - Fecha: {record['date']} - Incidencia: {incident_desc} - Bodega: {warehouse_name} - Verificador: {causing_verifier} - Coordinador: {assigned_coordinator}"
            records.append((record['id'], display_text))
        
        return records
    except Exception as e:
        logger.error(f"Error getting incident records: {e}")
        return []

def insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by):
    try:
        client = get_supabase_connection()
        
        # Convertir la fecha a string si es necesario
        if hasattr(action_date, 'strftime'):
            action_date_str = action_date.strftime('%Y-%m-%d')
        else:
            action_date_str = str(action_date)
        
        # Insertar la acción
        result = client.table('incident_actions').insert({
            'incident_record_id': incident_record_id,
            'action_date': action_date_str,
            'action_description': action_description,
            'new_status': new_status,
            'performed_by': performed_by
        }).execute()
        
        # Actualizar el estado del registro si se proporciona un nuevo estado
        if new_status:
            client.table('incident_records').update({
                'status': new_status
            }).eq('id', incident_record_id).execute()
        
        logger.info(f"Inserted action for incident record {incident_record_id}")
        return True
    except Exception as e:
        logger.error(f"Error inserting incident action: {e}")
        return False

def get_incident_actions(incident_record_id):
    try:
        client = get_supabase_connection()
        result = client.table('incident_actions').select(
            'action_date, action_description, new_status, performed_by'
        ).eq('incident_record_id', incident_record_id).order('action_date').execute()
        
        actions = []
        for row in result.data:
            actions.append({
                'action_date': row['action_date'],
                'action_description': row['action_description'],
                'new_status': row['new_status'],
                'performed_by': row['performed_by'] or "N/A"
            })
        
        return actions
    except Exception as e:
        logger.error(f"Error getting incident actions: {e}")
        return []

def get_all_incident_records_df():
    try:
        client = get_supabase_connection()
        
        # Obtener todos los registros de incidencias
        result = client.table('incident_records').select('*').execute()
        
        # Obtener datos relacionados por separado para evitar conflictos
        coordinators = {coord['id']: coord for coord in client.table('coordinators').select('*').execute().data}
        warehouses = {wh['id']: wh for wh in client.table('warehouses').select('*').execute().data}
        verifiers = {ver['id']: ver for ver in client.table('verifiers').select('*').execute().data}
        incidents = {inc['id']: inc for inc in client.table('incidents').select('*').execute().data}
        
        # Procesar los datos para crear el DataFrame
        processed_data = []
        for row in result.data:
            reg_coord = coordinators.get(row['registering_coordinator_id'], {})
            warehouse = warehouses.get(row['warehouse_id'], {})
            verifier = verifiers.get(row['causing_verifier_id'], {})
            incident = incidents.get(row['incident_id'], {})
            assigned_coord = coordinators.get(row['assigned_coordinator_id'], {})
            
            processed_row = {
                'ID': row['id'],
                'Fecha': row['date'],
                'Coordinador Registrante': f"{reg_coord.get('name', '')} {reg_coord.get('surnames', '')}" if reg_coord else "N/A",
                'Bodega': warehouse.get('name', 'N/A'),
                'Zona Bodega': warehouse.get('zone', 'N/A'),
                'Verificador Causante': f"{verifier.get('name', '')} {verifier.get('surnames', '')}" if verifier else "N/A",
                'Zona Verificador': verifier.get('zone', 'N/A'),
                'Tipo de Incidencia': incident.get('description', 'N/A'),
                'Coordinador Asignado': f"{assigned_coord.get('name', '')} {assigned_coord.get('surnames', '')}" if assigned_coord else "N/A",
                'Explicación': row['explanation'],
                'Enlace': '',  # Temporalmente vacío - columna no existe en Supabase
                'Estado': row['status'],
                'Responsable': row['responsible']
            }
            processed_data.append(processed_row)
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting incident records dataframe: {e}")
        return pd.DataFrame()

def get_all_verifiers_df():
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        logger.error(f"Error getting verifiers dataframe: {e}")
        return pd.DataFrame()

def get_all_warehouses_df():
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        logger.error(f"Error getting warehouses dataframe: {e}")
        return pd.DataFrame()

def get_incidents_by_zone():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('Zona Bodega').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_verifier():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('Verificador Causante').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_warehouse():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('Bodega').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_type():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('Tipo de Incidencia').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_status():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('Estado').size().reset_index(name='count')
    return pd.DataFrame()

def get_assignments_by_verifier():
    df = get_all_incident_records_df()
    if not df.empty:
        return df[df['Responsable'] == 'Verificador'].groupby('Verificador Causante').size().reset_index(name='count')
    return pd.DataFrame()

def reset_database():
    try:
        client = get_supabase_connection()
        tables = ['incident_actions', 'incident_records', 'incidents', 'warehouses', 'verifiers', 'coordinators']
        
        for table in tables:
            try:
                # Eliminar todos los registros de cada tabla
                result = client.table(table).delete().neq('id', 0).execute()
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.warning(f"Could not clear table {table}: {e}")
        
        logger.info("Database reset completed")
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False

def get_incident_record_details(incident_record_id):
    try:
        client = get_supabase_connection()
        # Temporalmente excluir 'enlace' de la consulta hasta que se agregue la columna en Supabase
        result = client.table('incident_records').select(
            'id, date, explanation, status, responsible, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id'
        ).eq('id', incident_record_id).execute()
        
        if result.data:
            record = result.data[0]
            
            # Obtener datos relacionados por separado
            warehouse = client.table('warehouses').select('name, zone').eq('id', record['warehouse_id']).execute().data[0] if record['warehouse_id'] else {}
            verifier = client.table('verifiers').select('name, surnames').eq('id', record['causing_verifier_id']).execute().data[0] if record['causing_verifier_id'] else {}
            incident = client.table('incidents').select('code, description').eq('id', record['incident_id']).execute().data[0] if record['incident_id'] else {}
            assigned_coord = client.table('coordinators').select('name, surnames').eq('id', record['assigned_coordinator_id']).execute().data[0] if record['assigned_coordinator_id'] else {}
            
            return {
                'id': record['id'],
                'date': record['date'],
                'explanation': record['explanation'],
                'enlace': '',  # Temporalmente vacío - columna no existe en Supabase
                'status': record['status'],
                'responsible': record['responsible'],
                'warehouse': warehouse.get('name', 'N/A'),
                'warehouse_zone': warehouse.get('zone', 'N/A'),
                'causing_verifier': f"{verifier.get('name', '')} {verifier.get('surnames', '')}" if verifier else 'N/A',
                'incident_type': f"{incident.get('code', '')} - {incident.get('description', '')}" if incident else 'N/A',
                'assigned_coordinator': f"{assigned_coord.get('name', '')} {assigned_coord.get('surnames', '')}" if assigned_coord else 'N/A',
                'registering_coordinator_id': record['registering_coordinator_id']
            }
        return None
    except Exception as e:
        logger.error(f"Error getting incident record details: {e}")
        return None

def export_incidents_to_excel():
    """Exporta historial completo de incidencias con acciones a Excel"""
    try:
        # Obtener datos usando las funciones existentes
        df_incidents = get_all_incident_records_df()
        
        # Formatear fechas en el DataFrame de incidencias
        if not df_incidents.empty and 'Fecha' in df_incidents.columns:
            df_incidents['Fecha'] = pd.to_datetime(df_incidents['Fecha']).dt.strftime('%d/%m/%Y')
        
        # Para las acciones, necesitamos una consulta separada con nombres de coordinadores
        client = get_supabase_connection()
        actions_result = client.table('incident_actions').select(
            'incident_record_id, action_date, action_description, new_status, performed_by'
        ).execute()
        
        # Obtener coordinadores para resolver los IDs
        coordinators = {coord['id']: f"{coord['name']} {coord['surnames']}" 
                       for coord in client.table('coordinators').select('*').execute().data}
        
        actions_data = []
        for row in actions_result.data:
            # Formatear fecha de acción
            action_date = row['action_date']
            if action_date:
                try:
                    formatted_date = pd.to_datetime(action_date).strftime('%d/%m/%Y')
                except:
                    formatted_date = action_date
            else:
                formatted_date = "N/A"
            
            # Resolver nombre del coordinador
            performed_by_name = "N/A"
            if row['performed_by']:
                try:
                    coord_id = int(row['performed_by'])
                    performed_by_name = coordinators.get(coord_id, f"ID: {coord_id}")
                except:
                    performed_by_name = str(row['performed_by'])
            
            actions_data.append({
                'ID Registro': row['incident_record_id'],
                'Fecha Acción': formatted_date,
                'Descripción Acción': row['action_description'],
                'Nuevo Estado': row['new_status'],
                'Realizado Por': performed_by_name
            })
        
        df_actions = pd.DataFrame(actions_data)
        
        # Crear archivo Excel con formato mejorado
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'historial_incidencias_{timestamp}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_incidents.to_excel(writer, sheet_name='Incidencias', index=False)
            df_actions.to_excel(writer, sheet_name='Acciones', index=False)
            
            # Aplicar formato a las hojas
            workbook = writer.book
            
            # Formatear hoja de Incidencias
            if 'Incidencias' in writer.sheets:
                worksheet_incidents = writer.sheets['Incidencias']
                for column in worksheet_incidents.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet_incidents.column_dimensions[column_letter].width = adjusted_width
            
            # Formatear hoja de Acciones
            if 'Acciones' in writer.sheets:
                worksheet_actions = writer.sheets['Acciones']
                for column in worksheet_actions.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet_actions.column_dimensions[column_letter].width = adjusted_width
        
        return filename
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise e

def create_backup():
    """Crea una copia de seguridad de la base de datos"""
    try:
        # Para Supabase, podríamos exportar los datos a JSON o CSV
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'supabase_backup_{timestamp}.json'
        
        # Exportar todas las tablas
        client = get_supabase_connection()
        backup_data = {}
        
        tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
        
        for table in tables:
            try:
                result = client.table(table).select('*').execute()
                backup_data[table] = result.data
            except Exception as e:
                logger.warning(f"Could not backup table {table}: {e}")
                backup_data[table] = []
        
        # Guardar en archivo JSON
        import json
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Backup created: {backup_filename}")
        return backup_filename
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise e

def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    try:
        client = get_supabase_connection()
        
        # Estadísticas generales
        stats = {}
        
        # Total de incidencias
        total_result = client.table('incident_records').select('count', count='exact').execute()
        stats['total_incidents'] = total_result.count if total_result.count else 0
        
        # Incidencias no resueltas (pendientes)
        pending_result = client.table('incident_records').select('count', count='exact').neq('status', 'Solucionado').execute()
        stats['pending_incidents'] = pending_result.count if pending_result.count else 0
        
        # Incidencias resueltas
        resolved_result = client.table('incident_records').select('count', count='exact').eq('status', 'Solucionado').execute()
        stats['resolved_incidents'] = resolved_result.count if resolved_result.count else 0
        
        # Incidencias por estado
        df = get_all_incident_records_df()
        if not df.empty:
            stats['by_status'] = df.groupby('Estado').size().reset_index(name='count')
            stats['by_status'].rename(columns={'Estado': 'status'}, inplace=True)
        else:
            stats['by_status'] = pd.DataFrame()
        
        # Incidencias recientes (últimos 7 días)
        from datetime import datetime, timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_result = client.table('incident_records').select('count', count='exact').gte('date', seven_days_ago).execute()
        stats['recent_incidents'] = recent_result.count if recent_result.count else 0
        
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            'total_incidents': 0,
            'pending_incidents': 0,
            'resolved_incidents': 0,
            'by_status': pd.DataFrame(),
            'recent_incidents': 0
        }

def get_pending_incidents_summary():
    """Obtiene resumen de incidencias pendientes para el dashboard"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            'id, date, status, responsible, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id'
        ).neq('status', 'Solucionado').order('date', desc=True).limit(10).execute()
        
        processed_data = []
        for row in result.data:
            # Obtener datos relacionados mediante consultas separadas para evitar joins problemáticos
            warehouse_name = "N/A"
            warehouse_zone = "N/A"
            if row.get('warehouse_id'):
                try:
                    warehouse_result = client.table('warehouses').select('name, zone').eq('id', row['warehouse_id']).execute()
                    if warehouse_result.data:
                        warehouse_name = warehouse_result.data[0]['name']
                        warehouse_zone = warehouse_result.data[0]['zone']
                except:
                    pass
            
            verifier_name = "N/A"
            if row.get('causing_verifier_id'):
                try:
                    verifier_result = client.table('verifiers').select('name, surnames').eq('id', row['causing_verifier_id']).execute()
                    if verifier_result.data:
                        verifier_name = f"{verifier_result.data[0]['name']} {verifier_result.data[0]['surnames']}"
                except:
                    pass
            
            incident_description = "N/A"
            if row.get('incident_id'):
                try:
                    incident_result = client.table('incidents').select('description').eq('id', row['incident_id']).execute()
                    if incident_result.data:
                        incident_description = incident_result.data[0]['description']
                except:
                    pass
            
            coordinator_name = "N/A"
            if row.get('assigned_coordinator_id'):
                try:
                    coordinator_result = client.table('coordinators').select('name, surnames').eq('id', row['assigned_coordinator_id']).execute()
                    if coordinator_result.data:
                        coordinator_name = f"{coordinator_result.data[0]['name']} {coordinator_result.data[0]['surnames']}"
                except:
                    pass
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse_name,
                'warehouse_zone': warehouse_zone,
                'causing_verifier': verifier_name,
                'incident_type': incident_description,
                'assigned_coordinator': coordinator_name,
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting pending incidents summary: {e}")
        return pd.DataFrame()

def get_recent_actions():
    """Obtiene las acciones más recientes para el dashboard"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_actions').select(
            'action_date, action_description, new_status, performed_by, incident_record_id'
        ).order('action_date', desc=True).limit(5).execute()
        
        processed_data = []
        for row in result.data:
            processed_data.append({
                'action_date': row['action_date'],
                'action_description': row['action_description'],
                'new_status': row['new_status'],
                'performed_by': row['performed_by'] or "N/A",
                'incident_id': row['incident_record_id'] or "N/A",
                'warehouse': "N/A"  # Simplificado para evitar joins complejos
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting recent actions: {e}")
        return pd.DataFrame()

def search_incident_by_code(code):
    """Busca una incidencia por su código único"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('*').eq('code', code).execute()
        
        if result.data:
            return {'success': True, 'incident': result.data[0]}
        else:
            return {'success': False, 'error': f'No se encontró ninguna incidencia con el código "{code}"'}
    except Exception as e:
        logger.error(f"Error searching incident by code: {e}")
        return {'success': False, 'error': f'Error al buscar la incidencia: {str(e)}'}

def get_incident_records_by_incident_code(code):
    """Obtiene todos los registros de incidencia asociados a un código de incidencia"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            '*, incidents!inner(code, description), '
            'coordinators!registering_coordinator_id(name, surnames), '
            'warehouses(name, zone), verifiers(name, surnames), '
            'coordinators!assigned_coordinator_id(name, surnames)'
        ).eq('incidents.code', code).order('date', desc=True).execute()
        
        if result.data:
            processed_records = []
            for row in result.data:
                incident = row['incidents']
                reg_coord = row['coordinators']
                warehouse = row['warehouses']
                verifier = row['verifiers']
                assigned_coord = row.get('coordinators', {})
                
                processed_records.append({
                    'id': row['id'],
                    'date': row['date'],
                    'incident_code': incident['code'] if incident else "N/A",
                    'incident_description': incident['description'] if incident else "N/A",
                    'registering_coordinator': f"{reg_coord['name']} {reg_coord['surnames']}" if reg_coord else "N/A",
                    'warehouse': warehouse['name'] if warehouse else "N/A",
                    'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                    'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                    'assigned_coordinator': f"{assigned_coord['name']} {assigned_coord['surnames']}" if assigned_coord else "N/A",
                    'explanation': row['explanation'],
                    'enlace': '',  # Temporalmente vacío - columna no existe en Supabase
                    'status': row['status'],
                    'responsible': row['responsible']
                })
            
            return {'success': True, 'records': processed_records}
        else:
            return {'success': False, 'error': f'No se encontraron registros para el código de incidencia "{code}"'}
    except Exception as e:
        logger.error(f"Error getting incident records by code: {e}")
        return {'success': False, 'error': f'Error al buscar registros: {str(e)}'}

# Funciones de actualización/edición
def update_coordinator(coordinator_id, name, surnames):
    """Actualizar un coordinador existente"""
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').update({
            'name': name,
            'surnames': surnames
        }).eq('id', coordinator_id).execute()
        
        if result.data:
            logger.info(f"Updated coordinator ID {coordinator_id}: {name} {surnames}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating coordinator: {e}")
        return False

def update_verifier(verifier_id, name, surnames, phone, zone):
    """Actualizar un verificador existente"""
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').update({
            'name': name,
            'surnames': surnames,
            'phone': phone,
            'zone': zone
        }).eq('id', verifier_id).execute()
        
        if result.data:
            logger.info(f"Updated verifier ID {verifier_id}: {name} {surnames}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating verifier: {e}")
        return False

def update_warehouse(warehouse_id, name, codigo_consejo, zone):
    """Actualizar una bodega existente"""
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').update({
            'name': name,
            'codigo_consejo': codigo_consejo,
            'zone': zone
        }).eq('id', warehouse_id).execute()
        
        if result.data:
            logger.info(f"Updated warehouse ID {warehouse_id}: {name}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating warehouse: {e}")
        return False

def update_incident(incident_id, code, description):
    """Actualizar un tipo de incidencia existente"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').update({
            'code': code,
            'description': description
        }).eq('id', incident_id).execute()
        
        if result.data:
            logger.info(f"Updated incident ID {incident_id}: {code}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating incident: {e}")
        return False

def update_incident_record(incident_record_id, date, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible):
    """Actualizar un registro de incidencia existente"""
    try:
        client = get_supabase_connection()
        # Convertir fecha a string si es necesario
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        
        # Temporalmente excluir 'enlace' hasta que se agregue la columna en Supabase
        result = client.table('incident_records').update({
            'date': date_str,
            'warehouse_id': warehouse_id,
            'causing_verifier_id': causing_verifier_id,
            'incident_id': incident_id,
            'assigned_coordinator_id': assigned_coordinator_id,
            'explanation': explanation,
            # 'enlace': enlace,  # Comentado temporalmente - columna no existe en Supabase
            'status': status,
            'responsible': responsible
        }).eq('id', incident_record_id).execute()
        
        if result.data:
            logger.info(f"Updated incident record ID {incident_record_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating incident record: {e}")
        return False

# Funciones para obtener registros individuales
def get_coordinator_by_id(coordinator_id):
    """Obtener un coordinador por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').select('*').eq('id', coordinator_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting coordinator: {e}")
        return None

def get_verifier_by_id(verifier_id):
    """Obtener un verificador por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('*').eq('id', verifier_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting verifier: {e}")
        return None

def get_warehouse_by_id(warehouse_id):
    """Obtener una bodega por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('*').eq('id', warehouse_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting warehouse: {e}")
        return None

def get_incident_by_id(incident_id):
    """Obtener un tipo de incidencia por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('*').eq('id', incident_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting incident: {e}")
        return None

def get_pending_incidents_by_coordinator(coordinator_id=None):
    """Obtiene incidencias pendientes filtradas por coordinador asignado"""
    try:
        client = get_supabase_connection()
        
        if coordinator_id:
            result = client.table('incident_records').select(
                'id, date, status, responsible, '
                'warehouses!incident_records_warehouse_id_fkey(name, zone), '
                'verifiers!incident_records_causing_verifier_id_fkey(name, surnames), '
                'incidents!incident_records_incident_id_fkey(description), '
                'coordinators!incident_records_assigned_coordinator_id_fkey(name, surnames)'
            ).neq('status', 'Solucionado').eq('assigned_coordinator_id', coordinator_id).order('date', desc=True).limit(10).execute()
        else:
            result = client.table('incident_records').select(
                'id, date, status, responsible, '
                'warehouses!incident_records_warehouse_id_fkey(name, zone), '
                'verifiers!incident_records_causing_verifier_id_fkey(name, surnames), '
                'incidents!incident_records_incident_id_fkey(description), '
                'coordinators!incident_records_assigned_coordinator_id_fkey(name, surnames)'
            ).neq('status', 'Solucionado').order('date', desc=True).limit(10).execute()
        
        processed_data = []
        for row in result.data:
            # Obtener datos relacionados mediante consultas separadas para evitar joins problemáticos
            warehouse_name = "N/A"
            warehouse_zone = "N/A"
            if row.get('warehouse_id'):
                try:
                    warehouse_result = client.table('warehouses').select('name, zone').eq('id', row['warehouse_id']).execute()
                    if warehouse_result.data:
                        warehouse_name = warehouse_result.data[0]['name']
                        warehouse_zone = warehouse_result.data[0]['zone']
                except:
                    pass
            
            verifier_name = "N/A"
            if row.get('causing_verifier_id'):
                try:
                    verifier_result = client.table('verifiers').select('name, surnames').eq('id', row['causing_verifier_id']).execute()
                    if verifier_result.data:
                        verifier_name = f"{verifier_result.data[0]['name']} {verifier_result.data[0]['surnames']}"
                except:
                    pass
            
            incident_description = "N/A"
            if row.get('incident_id'):
                try:
                    incident_result = client.table('incidents').select('description').eq('id', row['incident_id']).execute()
                    if incident_result.data:
                        incident_description = incident_result.data[0]['description']
                except:
                    pass
            
            coordinator_name = "N/A"
            if row.get('assigned_coordinator_id'):
                try:
                    coordinator_result = client.table('coordinators').select('name, surnames').eq('id', row['assigned_coordinator_id']).execute()
                    if coordinator_result.data:
                        coordinator_name = f"{coordinator_result.data[0]['name']} {coordinator_result.data[0]['surnames']}"
                except:
                    pass
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse_name,
                'warehouse_zone': warehouse_zone,
                'causing_verifier': verifier_name,
                'incident_type': incident_description,
                'assigned_coordinator': coordinator_name,
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting pending incidents by coordinator: {e}")
        return pd.DataFrame()

def get_filtered_pending_incidents(coordinator_id=None, status=None, days=None):
    """Obtiene incidencias pendientes con filtros múltiples"""
    try:
        client = get_supabase_connection()
        
        # Construir la consulta base SIN joins para evitar problemas de ambigüedad
        query = client.table('incident_records').select(
            'id, date, status, responsible, explanation, '
            'warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id'
        )
        
        # Agregar filtros según los parámetros
        if coordinator_id:
            query = query.eq('assigned_coordinator_id', coordinator_id)
        
        if status:
            query = query.eq('status', status)
        else:
            # Solo excluir 'Solucionado' si no se especifica un status particular
            # Esto permite mostrar todos los estados cuando status=None
            pass  # No aplicar filtro de status, mostrar todos
        
        if days:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = query.gte('date', cutoff_date)
        
        result = query.order('date', desc=True).limit(20).execute()
        
        processed_data = []
        for row in result.data:
            # Obtener datos relacionados mediante consultas separadas para evitar joins problemáticos
            warehouse_name = "N/A"
            warehouse_zone = "N/A"
            if row.get('warehouse_id'):
                try:
                    warehouse_result = client.table('warehouses').select('name, zone').eq('id', row['warehouse_id']).execute()
                    if warehouse_result.data:
                        warehouse_name = warehouse_result.data[0]['name']
                        warehouse_zone = warehouse_result.data[0]['zone']
                except:
                    pass
            
            verifier_name = "N/A"
            if row.get('causing_verifier_id'):
                try:
                    verifier_result = client.table('verifiers').select('name, surnames').eq('id', row['causing_verifier_id']).execute()
                    if verifier_result.data:
                        verifier_name = f"{verifier_result.data[0]['name']} {verifier_result.data[0]['surnames']}"
                except:
                    pass
            
            incident_description = "N/A"
            if row.get('incident_id'):
                try:
                    incident_result = client.table('incidents').select('description').eq('id', row['incident_id']).execute()
                    if incident_result.data:
                        incident_description = incident_result.data[0]['description']
                except:
                    pass
            
            coordinator_name = "N/A"
            if row.get('assigned_coordinator_id'):
                try:
                    coordinator_result = client.table('coordinators').select('name, surnames').eq('id', row['assigned_coordinator_id']).execute()
                    if coordinator_result.data:
                        coordinator_name = f"{coordinator_result.data[0]['name']} {coordinator_result.data[0]['surnames']}"
                except:
                    pass
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse_name,
                'warehouse_zone': warehouse_zone,
                'causing_verifier': verifier_name,
                'incident_type': incident_description,
                'assigned_coordinator': coordinator_name,
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting filtered pending incidents: {e}")
        return pd.DataFrame()