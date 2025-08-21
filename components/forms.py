import streamlit as st
import pandas as pd
import datetime
from utils.database_unified import insert_coordinator, insert_verifier, insert_warehouse, load_csv_to_verifiers, load_csv_to_warehouses, insert_incident, get_coordinators, get_verifiers, get_warehouses, get_incidents, insert_incident_record, get_incident_records, insert_incident_action, get_incident_actions, get_incident_record_details, search_incident_by_code, get_incident_records_by_incident_code, update_coordinator, update_verifier, update_warehouse, update_incident, get_coordinator_by_id, get_verifier_by_id, get_warehouse_by_id, get_incident_by_id

def coordinator_form():
    st.subheader('Alta de Coordinador')
    
    if 'coord_form_counter' not in st.session_state:
        st.session_state.coord_form_counter = 0
    
    name = st.text_input('Nombre', key=f'coord_name_{st.session_state.coord_form_counter}', help='Ingrese un nombre válido (mínimo 2 caracteres)')
    surnames = st.text_input('Apellidos', key=f'coord_surnames_{st.session_state.coord_form_counter}', help='Ingrese apellidos válidos (mínimo 2 caracteres)')
    
    if st.button('Guardar Coordinador'):
        if name and len(name) >= 2 and surnames and len(surnames) >= 2:
            insert_coordinator(name, surnames)
            st.success('Coordinador guardado exitosamente.')
            st.session_state.coord_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete todos los campos con valores válidos (mínimo 2 caracteres cada uno).')

def verifier_form():
    st.subheader('Alta de Verificador')
    
    if 'verif_form_counter' not in st.session_state:
        st.session_state.verif_form_counter = 0
    
    name = st.text_input('Nombre', key=f'verif_name_{st.session_state.verif_form_counter}', help='Mínimo 2 caracteres')
    surnames = st.text_input('Apellidos', key=f'verif_surnames_{st.session_state.verif_form_counter}', help='Mínimo 2 caracteres')
    phone = st.text_input('Teléfono', key=f'verif_phone_{st.session_state.verif_form_counter}', help='Formato: 9 dígitos')
    zones = ['PENEDÈS', 'ALT CAMP', 'CONCA DE BARBERÀ', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
    zone = st.selectbox('Zona', options=zones, key=f'verif_zone_{st.session_state.verif_form_counter}')
    
    if st.button('Guardar Verificador'):
        if name and len(name) >= 2 and surnames and len(surnames) >= 2 and (phone.isdigit() and len(phone) == 9 or not phone):
            insert_verifier(name, surnames, phone, zone)
            st.success('Verificador guardado exitosamente.')
            st.session_state.verif_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete nombre y apellidos con mínimo 2 caracteres, y teléfono con 9 dígitos si se proporciona.')

def warehouse_form():
    st.subheader('Alta de Bodega')
    
    if 'warehouse_form_counter' not in st.session_state:
        st.session_state.warehouse_form_counter = 0
    
    name = st.text_input('Nombre', key=f'wh_name_{st.session_state.warehouse_form_counter}', help='Nombre de la bodega')
    codigo_consejo = st.text_input('Código Consejo', key=f'wh_codigo_{st.session_state.warehouse_form_counter}', help='Código del consejo regulador')
    zones = ['PENEDÈS', 'ALT CAMP', 'CONCA DE BARBERÀ', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
    zone = st.selectbox('Zona', options=zones, key=f'wh_zone_{st.session_state.warehouse_form_counter}')
    if st.button('Guardar Bodega'):
        if name:
            insert_warehouse(name, codigo_consejo, zone)
            st.success('Bodega guardada exitosamente.')
            st.session_state.warehouse_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete el nombre de la bodega.')

def csv_upload(section):
    st.subheader(f'Carga de {section} desde CSV')
    with st.form(key=f'csv_upload_{section}', clear_on_submit=True):
        uploaded_file = st.file_uploader(f'Seleccione CSV para {section}', type='csv')
        separator = st.selectbox('Separador del CSV', [',', ';'], index=1)  # Cambiar default a punto y coma
        submit = st.form_submit_button('Cargar CSV')
        if submit and uploaded_file is not None:
            try:
                # Intentar detectar automáticamente el separador correcto
                uploaded_file.seek(0)
                sample = uploaded_file.read(1024).decode('utf-8-sig')
                uploaded_file.seek(0)
                
                # Contar separadores en la primera línea
                first_line = sample.split('\n')[0]
                comma_count = first_line.count(',')
                semicolon_count = first_line.count(';')
                
                # Usar el separador que tenga más ocurrencias
                detected_sep = ';' if semicolon_count > comma_count else ','
                
                # Si el separador detectado es diferente al seleccionado, mostrar advertencia
                if detected_sep != separator:
                    st.warning(f'⚠️ Separador detectado automáticamente: "{detected_sep}". Usando separador detectado en lugar de "{separator}".')
                    separator = detected_sep
                
                if section == 'Verificadores':
                    df = pd.read_csv(uploaded_file, sep=separator, encoding='utf-8-sig')
                    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
                    required_columns = ['name', 'surnames']
                    if not all(col in df.columns for col in required_columns):
                        missing_cols = [col for col in required_columns if col not in df.columns]
                        available_cols = list(df.columns)
                        raise ValueError(f'El CSV debe contener las columnas: {", ".join(required_columns)}. Columnas faltantes: {", ".join(missing_cols)}. Columnas disponibles: {", ".join(available_cols)}')
                    load_csv_to_verifiers(uploaded_file, sep=separator)
                elif section == 'Bodegas':
                    df = pd.read_csv(uploaded_file, sep=separator, encoding='utf-8-sig')
                    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
                    required_columns = ['name', 'codigo_consejo']
                    if not all(col in df.columns for col in required_columns):
                        missing_cols = [col for col in required_columns if col not in df.columns]
                        available_cols = list(df.columns)
                        raise ValueError(f'El CSV debe contener las columnas: {", ".join(required_columns)}. Columnas faltantes: {", ".join(missing_cols)}. Columnas disponibles: {", ".join(available_cols)}')
                    load_csv_to_warehouses(uploaded_file, sep=separator)
                st.success(f'{section} cargados exitosamente desde CSV.')
            except Exception as e:
                st.error(f'Error al cargar el CSV: {str(e)}')

def incident_form():
    st.subheader('Alta de Incidencia')
    
    if 'incident_form_counter' not in st.session_state:
        st.session_state.incident_form_counter = 0
    
    # Opción para código personalizado o automático
    col1, col2 = st.columns([1, 3])
    with col1:
        auto_code = st.checkbox('Código automático', value=True, key=f'auto_code_{st.session_state.incident_form_counter}', help='Generar código automáticamente o introducir uno personalizado')
    
    with col2:
        if auto_code:
            # Mostrar el próximo código que se asignará
            from utils.database_supabase import get_supabase_connection
            try:
                client = get_supabase_connection()
                count_result = client.table('incidents').select('count', count='exact').execute()
                next_code = f"{(count_result.count if count_result.count else 0) + 1:03d}"
                st.info(f'Código automático que se asignará: **{next_code}**')
            except:
                st.info('Se generará automáticamente un código secuencial (ej: 001, 002, etc.)')
            custom_code = None
        else:
            custom_code = st.text_input('Código de Incidencia', key=f'inc_code_{st.session_state.incident_form_counter}', help='Introduzca un código único para la incidencia (ej: INC-2025-001)', max_chars=20)
    
    # Campo para tipo de incidencia (descripción corta)
    incident_type = st.text_input('Tipo de Incidencia', key=f'inc_type_{st.session_state.incident_form_counter}', help='Descripción corta del tipo de incidencia (ej: Problema de calidad, Retraso en entrega)', max_chars=100)
    
    # Campo para descripción detallada
    description = st.text_area('Descripción Detallada de la Incidencia', key=f'inc_description_{st.session_state.incident_form_counter}', help='Proporcione una descripción detallada y completa de la incidencia (mínimo 10 caracteres)')
    
    if st.button('Guardar Incidencia'):
        if incident_type and len(incident_type.strip()) >= 3 and description and len(description) >= 10:
            if not auto_code and (not custom_code or len(custom_code.strip()) < 3):
                st.error('Por favor, ingrese un código válido de al menos 3 caracteres o active la generación automática.')
            else:
                code_to_use = custom_code.strip() if not auto_code else None
                # Combinar tipo y descripción para el campo description
                full_description = f"{incident_type.strip()} - {description.strip()}"
                result = insert_incident(full_description, code_to_use)
                if result['success']:
                    st.success(f'Incidencia guardada exitosamente con código: **{result["code"]}**')
                    st.info(f'Tipo: {incident_type.strip()}')
                    st.session_state.incident_form_counter += 1
                    st.rerun()
                else:
                    st.error(result['error'])
        else:
            if not incident_type or len(incident_type.strip()) < 3:
                st.error('Por favor, ingrese un tipo de incidencia con al menos 3 caracteres.')
            if not description or len(description) < 10:
                st.error('Por favor, ingrese una descripción detallada con al menos 10 caracteres.')

def search_incident_form():
    """Formulario para buscar incidencias por código"""
    st.header("🔍 Buscar Incidencia por Código")
    
    # Obtener todas las incidencias disponibles
    incidents = get_incidents()
    if not incidents:
        st.warning('No hay incidencias disponibles en el sistema.')
        return
    
    # Crear opciones para el selectbox con opción en blanco
    incident_options = [None] + incidents
    
    # Selectbox con autocompletado
    selected_incident = st.selectbox(
        "Seleccionar Incidencia",
        options=incident_options,
        format_func=lambda x: "-- Seleccionar una incidencia --" if x is None else x[1],
        help="Seleccione la incidencia que desea consultar. Puede escribir para buscar."
    )
    
    if selected_incident:
        # Extraer el código de la incidencia seleccionada
        incident_code = selected_incident[1].split(' - ')[0]  # Obtener solo el código
        
        # Buscar la incidencia
        incident_result = search_incident_by_code(incident_code)
        
        if incident_result['success']:
            incident = incident_result['incident']
            
            # Mostrar información de la incidencia
            st.success(f"✅ Incidencia encontrada: **{incident['code']}**")
            
            with st.expander("📋 Detalles de la Incidencia", expanded=True):
                st.write(f"**Código:** {incident['code']}")
                st.write(f"**Descripción:** {incident['description']}")
                st.write(f"**Fecha de creación:** {incident.get('created_at', 'No disponible')}")
            
            # Buscar registros asociados
            records_result = get_incident_records_by_incident_code(incident_code)
            
            if records_result['success']:
                records = records_result['records']
                st.subheader(f"📊 Registros Asociados ({len(records)})")
                
                for i, record in enumerate(records, 1):
                    with st.expander(f"Registro #{i} - {record['warehouse']} ({record['status']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Fecha:** {record['date']}")
                            st.write(f"**Almacén:** {record['warehouse']} - {record['warehouse_zone']}")
                            st.write(f"**Estado:** {record['status']}")
                            st.write(f"**Tipo:** {record['incident_type']}")
                        
                        with col2:
                            st.write(f"**Coordinador Registrante:** {record['registering_coordinator']}")
                            st.write(f"**Verificador Causante:** {record['causing_verifier']}")
                            st.write(f"**Coordinador Asignado:** {record['assigned_coordinator']}")
                        
                        if record.get('observations'):
                            st.write(f"**Observaciones:** {record['observations']}")
                        
                        # Mostrar enlace como hipervínculo si existe
                        enlace = record.get('enlace', '')
                        if enlace and enlace.strip():
                            st.write(f"**Enlace:** [{enlace}]({enlace})")
                        else:
                            st.write("**Enlace:** No disponible")
            else:
                st.info("ℹ️ No se encontraron registros asociados a esta incidencia")
                
        else:
            st.error(f"❌ {incident_result['error']}")

def incident_record_form():
    st.subheader('Registro de Incidencia')
    
    if 'incident_record_counter' not in st.session_state:
        st.session_state.incident_record_counter = 0
    
    date = st.date_input('Fecha', datetime.date.today(), key=f'inc_rec_date_{st.session_state.incident_record_counter}', help='Seleccione la fecha de la incidencia')
    try:
        coordinators = get_coordinators()
        if not coordinators:
            st.warning('No hay coordinadores disponibles. Por favor, registre uno primero.')
            st.info('💡 Puede registrar un coordinador desde el menú "Altas" → "Alta Coordinador"')
            return
    except Exception as e:
        st.error(f'Error al cargar coordinadores: {e}')
        st.info('💡 Verifique la conexión a la base de datos')
        return
    
    # Agregar opción en blanco para coordinador que registra
    coordinator_options = [None] + coordinators
    selected_registering_coordinator = st.selectbox(
        'Coordinador que registra', 
        options=coordinator_options, 
        format_func=lambda x: "-- Seleccionar coordinador --" if x is None else f"{x['name']} {x['surnames']}", 
        key=f'inc_rec_reg_coord_{st.session_state.incident_record_counter}'
    )
    registering_coordinator_id = selected_registering_coordinator['id'] if selected_registering_coordinator else None
    try:
        warehouses = get_warehouses()
        if not warehouses:
            st.warning('No hay bodegas disponibles. Por favor, registre una primero.')
            st.info('💡 Puede registrar una bodega desde el menú "Altas" → "Alta Bodega"')
            return
    except Exception as e:
        st.error(f'Error al cargar bodegas: {e}')
        st.info('💡 Verifique la conexión a la base de datos')
        return
    
    # Agregar opción en blanco para bodega
    warehouse_options = [None] + warehouses
    selected_warehouse = st.selectbox(
        'Bodega', 
        options=warehouse_options, 
        format_func=lambda x: "-- Seleccionar bodega --" if x is None else f"{x['name']} - {x['zone']} (Código: {x['codigo_consejo']})", 
        key=f'inc_rec_warehouse_{st.session_state.incident_record_counter}'
    )
    warehouse_id = selected_warehouse['id'] if selected_warehouse else None
    try:
        verifiers = get_verifiers()
        if not verifiers:
            st.warning('No hay verificadores disponibles. Por favor, registre uno primero.')
            st.info('💡 Puede registrar un verificador desde el menú "Altas" → "Alta Verificador"')
            return
    except Exception as e:
        st.error(f'Error al cargar verificadores: {e}')
        st.info('💡 Verifique la conexión a la base de datos')
        return
    
    # Agregar opción en blanco para verificador
    verifier_options = [None] + verifiers
    selected_verifier = st.selectbox(
        'Verificador que provocó la incidencia', 
        options=verifier_options, 
        format_func=lambda x: "-- Seleccionar verificador --" if x is None else f"{x['name']} {x['surnames']}", 
        key=f'inc_rec_verifier_{st.session_state.incident_record_counter}'
    )
    causing_verifier_id = selected_verifier['id'] if selected_verifier else None
    try:
        incidents = get_incidents()
        if not incidents:
            st.warning('No hay incidencias disponibles. Por favor, registre una primero.')
            st.info('💡 Puede registrar una incidencia desde el menú "Altas" → "Alta Incidencia"')
            return
    except Exception as e:
        st.error(f'Error al cargar incidencias: {e}')
        st.info('💡 Verifique la conexión a la base de datos')
        return
    incident_id = st.selectbox('Incidencia', options=incidents, format_func=lambda x: x[1], key=f'inc_rec_incident_{st.session_state.incident_record_counter}')[0]
    # Agregar opción en blanco para coordinador asignado
    assigned_coordinator_options = [None] + coordinators
    selected_assigned_coordinator = st.selectbox(
        'Coordinador asignado', 
        options=assigned_coordinator_options, 
        format_func=lambda x: "-- Seleccionar coordinador asignado --" if x is None else f"{x['name']} {x['surnames']}", 
        key=f'inc_rec_assigned_coord_{st.session_state.incident_record_counter}'
    )
    assigned_coordinator_id = selected_assigned_coordinator['id'] if selected_assigned_coordinator else None
    explanation = st.text_area('Explicación', key=f'inc_rec_explanation_{st.session_state.incident_record_counter}', help='Explique los detalles de la incidencia')
    enlace = st.text_input('Enlace (opcional)', key=f'inc_rec_enlace_{st.session_state.incident_record_counter}', help='URL relacionada con la incidencia (opcional)', placeholder='https://ejemplo.com')
    status = st.selectbox('Status', ['Pendiente', 'En Proceso', 'Solucionado', 'Asignado a Técnicos', 'RRHH'], key=f'inc_rec_status_{st.session_state.incident_record_counter}', help='Seleccione el estado actual')
    responsible = st.selectbox('Responsable', ['Bodega', 'Verificador', 'RRHH', 'Coordinacion', 'Servicios Informáticos'], key=f'inc_rec_responsible_{st.session_state.incident_record_counter}', help='Indique quién es responsable')
    if st.button('Guardar Registro de Incidencia'):
        # Validar que todos los campos obligatorios estén completos
        missing_fields = []
        if not registering_coordinator_id:
            missing_fields.append('Coordinador que registra')
        if not warehouse_id:
            missing_fields.append('Bodega')
        if not causing_verifier_id:
            missing_fields.append('Verificador que provocó la incidencia')
        if not incident_id:
            missing_fields.append('Incidencia')
        if not assigned_coordinator_id:
            missing_fields.append('Coordinador asignado')
        if not status:
            missing_fields.append('Status')
        if not responsible:
            missing_fields.append('Responsable')
        
        if not missing_fields:
            success = insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, enlace, status, responsible)
            if success:
                st.success('Registro de incidencia guardado exitosamente.')
                # Incrementar contador para limpiar formulario
                st.session_state.incident_record_counter += 1
                st.rerun()
            else:
                st.error('Error al guardar el registro de incidencia. Por favor, verifique la conexión a la base de datos e intente nuevamente.')
        else:
            st.error(f'Por favor, complete los siguientes campos obligatorios: {", ".join(missing_fields)}')

def manage_incident_actions_form():
    st.subheader('Gestión de Acciones de Incidencia')
    
    if 'incident_actions_counter' not in st.session_state:
        st.session_state.incident_actions_counter = 0
    
    # Mantener la selección del registro después de guardar una acción
    if 'selected_incident_record_id' not in st.session_state:
        st.session_state.selected_incident_record_id = None
    
    # Preservar el contexto de navegación para evitar redirección al dashboard
    st.session_state.in_manage_actions = True
    st.session_state.force_stay_in_actions = True
    
    # Asegurar que permanecemos en la sección correcta siempre
    st.session_state['main_menu_override'] = 'Incidencias'
    st.session_state['sub_menu_override'] = 'Gestión de Acciones'
    
    # Mostrar indicador si se están cargando muchos datos
    if st.session_state.get('loading_large_dataset', False):
        with st.spinner('Cargando datos... Por favor espere.'):
            import time
            time.sleep(0.5)  # Breve pausa para mostrar el spinner
        st.session_state['loading_large_dataset'] = False
    
    try:
        incident_records = get_incident_records()
        if not incident_records:
            st.warning('No hay registros de incidencias disponibles. Por favor, registre uno primero.')
            st.info('💡 Puede registrar una incidencia desde el menú "Incidencias" → "Registro de Incidencia"')
            return
    except Exception as e:
        st.error(f'Error al cargar registros de incidencias: {e}')
        st.info('💡 Verifique la conexión a la base de datos')
        return
    
    # Encontrar el índice del registro previamente seleccionado
    default_index = 0
    if st.session_state.selected_incident_record_id:
        for i, record in enumerate(incident_records):
            if record[0] == st.session_state.selected_incident_record_id:
                default_index = i
                break
    
    selected_record = st.selectbox(
        'Seleccionar Registro de Incidencia', 
        options=incident_records, 
        format_func=lambda x: x[1], 
        index=default_index,
        key=f'inc_act_record_{st.session_state.incident_actions_counter}'
    )
    incident_record_id = selected_record[0]
    
    # Actualizar el ID seleccionado en session_state
    st.session_state.selected_incident_record_id = incident_record_id
    
    # Botón para cambiar de registro
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button('🔄 Cambiar Registro', help='Permite seleccionar otro registro de incidencia'):
            st.session_state.selected_incident_record_id = None
            st.session_state.incident_actions_counter += 1
            st.rerun()
    
    # Mostrar información original de la incidencia
    details = get_incident_record_details(incident_record_id)
    if details:
        st.subheader('Información Original de la Incidencia')
        
        # Mostrar información en formato más legible
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Fecha:** {details.get('date', 'N/A')}")
            st.write(f"**Estado:** {details.get('status', 'N/A')}")
            st.write(f"**Responsable:** {details.get('responsible', 'N/A')}")
            st.write(f"**Bodega:** {details.get('warehouse', 'N/A')}")
        
        with col2:
            st.write(f"**Coordinador Registrador:** {details.get('registering_coordinator', 'N/A')}")
            st.write(f"**Coordinador Asignado:** {details.get('assigned_coordinator', 'N/A')}")
            st.write(f"**Verificador Causante:** {details.get('causing_verifier', 'N/A')}")
        
        st.write(f"**Explicación:** {details.get('explanation', 'N/A')}")
        
        # Mostrar enlace como hipervínculo si existe
        enlace = details.get('enlace', '')
        if enlace and enlace.strip():
            st.write(f"**Enlace:** [{enlace}]({enlace})")
        else:
            st.write("**Enlace:** No disponible")
    
    actions = get_incident_actions(incident_record_id)
    st.subheader('Historial de Acciones')
    for action in actions:
        st.write(f"Fecha: {action['action_date']}, Descripción: {action['action_description']}, Nuevo Status: {action['new_status'] or 'N/A'}, Realizado por: {action['performed_by']}")
    st.subheader('Añadir Nueva Acción')
    action_date = st.date_input('Fecha de la Acción', datetime.date.today(), key=f'inc_act_date_{st.session_state.incident_actions_counter}', help='Fecha en que se realizó la acción')
    action_description = st.text_area('Descripción de la Acción', key=f'inc_act_desc_{st.session_state.incident_actions_counter}', help='Describa la acción tomada')
    new_status = st.selectbox('Nuevo Status (opcional)', [None, 'Pendiente', 'En Proceso', 'Solucionado', 'Asignado a Técnicos', 'RRHH'], index=0, key=f'inc_act_status_{st.session_state.incident_actions_counter}', help='Actualice el estado si es necesario')
    try:
        coordinators = get_coordinators()
        if not coordinators:
            st.error('No hay coordinadores disponibles para asignar la acción.')
            return
        selected_coordinator = st.selectbox('Realizado por', options=coordinators, format_func=lambda x: f"{x['name']} {x['surnames']}", key=f'inc_act_by_{st.session_state.incident_actions_counter}')
        performed_by = selected_coordinator['id']  # Enviar el ID del coordinador, no el nombre
    except Exception as e:
        st.error(f'Error al cargar coordinadores: {e}')
        return
    if st.button('Guardar Acción'):
        if action_date and action_description and performed_by:
            # Mostrar indicador de carga para operaciones con muchos datos
            with st.spinner('Guardando acción... Por favor espere.'):
                success = insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by)
            
            if success:
                st.success('Acción guardada exitosamente.')
                # Incrementar contador para limpiar formulario
                st.session_state.incident_actions_counter += 1
                st.rerun()
            else:
                st.error('Error al guardar la acción. Por favor, inténtelo de nuevo.')
        else:
            st.error('Por favor, complete fecha, descripción y realizado por.')

# Formularios de edición
def edit_coordinator_form():
    st.subheader('Editar Coordinador')
    
    try:
        coordinators = get_coordinators()
        if not coordinators:
            st.warning('No hay coordinadores registrados.')
            return
    except Exception as e:
        st.error(f'Error al cargar coordinadores: {e}')
        return
    
    # Selector de coordinador
    coord_options = {f"{coord['name']} {coord['surnames']} (ID: {coord['id']})": coord['id'] for coord in coordinators}
    selected_coord = st.selectbox('Seleccionar coordinador a editar:', list(coord_options.keys()))
    
    if selected_coord:
        coord_id = coord_options[selected_coord]
        coord_data = get_coordinator_by_id(coord_id)
        
        if coord_data:
            # Formulario de edición
            new_name = st.text_input('Nombre', value=coord_data['name'], help='Mínimo 2 caracteres')
            new_surnames = st.text_input('Apellidos', value=coord_data['surnames'], help='Mínimo 2 caracteres')
            
            if st.button('Actualizar Coordinador'):
                if new_name and len(new_name) >= 2 and new_surnames and len(new_surnames) >= 2:
                    if update_coordinator(coord_id, new_name, new_surnames):
                        st.success('Coordinador actualizado exitosamente.')
                        st.rerun()
                    else:
                        st.error('Error al actualizar el coordinador.')
                else:
                    st.error('Por favor, complete todos los campos con valores válidos (mínimo 2 caracteres cada uno).')

def edit_verifier_form():
    st.subheader('Editar Verificador')
    
    verifiers = get_verifiers()
    if not verifiers:
        st.warning('No hay verificadores registrados.')
        return
    
    # Selector de verificador
    verif_options = {f"{verif['name']} {verif['surnames']} - {verif['zone']} (ID: {verif['id']})": verif['id'] for verif in verifiers}
    selected_verif = st.selectbox('Seleccionar verificador a editar:', list(verif_options.keys()))
    
    if selected_verif:
        verif_id = verif_options[selected_verif]
        verif_data = get_verifier_by_id(verif_id)
        
        if verif_data:
            # Formulario de edición
            new_name = st.text_input('Nombre', value=verif_data['name'], help='Mínimo 2 caracteres')
            new_surnames = st.text_input('Apellidos', value=verif_data['surnames'], help='Mínimo 2 caracteres')
            new_phone = st.text_input('Teléfono', value=verif_data.get('phone', ''), help='9 dígitos')
            zones = ['PENEDÈS', 'ALT CAMP', 'CONCA DE BARBERÀ', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
            current_zone_index = zones.index(verif_data['zone']) if verif_data['zone'] in zones else 0
            new_zone = st.selectbox('Zona', options=zones, index=current_zone_index)
            
            if st.button('Actualizar Verificador'):
                if new_name and len(new_name) >= 2 and new_surnames and len(new_surnames) >= 2 and (new_phone.isdigit() and len(new_phone) == 9 or not new_phone):
                    if update_verifier(verif_id, new_name, new_surnames, new_phone, new_zone):
                        st.success('Verificador actualizado exitosamente.')
                        st.rerun()
                    else:
                        st.error('Error al actualizar el verificador.')
                else:
                    st.error('Por favor, complete nombre y apellidos con mínimo 2 caracteres, y teléfono con 9 dígitos si se proporciona.')

def edit_warehouse_form():
    st.subheader('Editar Bodega')
    
    warehouses = get_warehouses()
    if not warehouses:
        st.warning('No hay bodegas registradas.')
        return
    
    # Selector de bodega
    warehouse_options = {f"{wh['name']} - {wh['zone']} (ID: {wh['id']})": wh['id'] for wh in warehouses}
    selected_warehouse = st.selectbox('Seleccionar bodega a editar:', list(warehouse_options.keys()))
    
    if selected_warehouse:
        warehouse_id = warehouse_options[selected_warehouse]
        warehouse_data = get_warehouse_by_id(warehouse_id)
        
        if warehouse_data:
            # Formulario de edición
            new_name = st.text_input('Nombre', value=warehouse_data['name'])
            new_codigo_consejo = st.text_input('Código Consejo', value=warehouse_data.get('codigo_consejo', ''))
            zones = ['PENEDÈS', 'ALT CAMP', 'CONCA DE BARBERÀ', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
            current_zone_index = zones.index(warehouse_data['zone']) if warehouse_data['zone'] in zones else 0
            new_zone = st.selectbox('Zona', options=zones, index=current_zone_index)
            
            if st.button('Actualizar Bodega'):
                if new_name:
                    if update_warehouse(warehouse_id, new_name, new_codigo_consejo, new_zone):
                        st.success('Bodega actualizada exitosamente.')
                        st.rerun()
                    else:
                        st.error('Error al actualizar la bodega.')
                else:
                    st.error('Por favor, complete el nombre de la bodega.')

def edit_incident_type_form():
    """Formulario para editar tipos de incidencia (códigos y descripciones)"""
    st.subheader('🏷️ Editar Tipo de Incidencia')
    st.info('Esta opción permite editar los códigos y descripciones de los tipos de incidencia disponibles en el sistema.')
    
    incidents = get_incidents()
    if not incidents:
        st.warning('No hay tipos de incidencia registrados.')
        return
    
    # Selector de incidencia
    # get_incidents() devuelve tuplas (id, descripción_formateada)
    incident_options = {inc[1]: inc[0] for inc in incidents}
    selected_incident = st.selectbox('Seleccionar tipo de incidencia a editar:', list(incident_options.keys()))
    
    if selected_incident:
        incident_id = incident_options[selected_incident]
        incident_data = get_incident_by_id(incident_id)
        
        if incident_data:
            # Formulario de edición
            new_code = st.text_input('Código', value=incident_data['code'])
            new_description = st.text_area('Descripción', value=incident_data['description'])
            
            if st.button('Actualizar Tipo de Incidencia'):
                if new_code and new_description:
                    if update_incident(incident_id, new_code, new_description):
                        st.success('Tipo de incidencia actualizado exitosamente.')
                        st.rerun()
                    else:
                        st.error('Error al actualizar el tipo de incidencia.')
                else:
                    st.error('Por favor, complete código y descripción.')

def edit_incident_record_form():
    """Formulario para editar registros específicos de incidencia"""
    st.subheader('📝 Editar Registro de Incidencia')
    st.info('Esta opción permite editar los detalles de un registro específico de incidencia ya creado.')
    
    # Obtener todos los registros de incidencia
    incident_records = get_incident_records()
    if not incident_records:
        st.warning('No hay registros de incidencias disponibles. Por favor, registre uno primero.')
        return
    
    # Selector de registro de incidencia
    record_options = {rec[1]: rec[0] for rec in incident_records}
    selected_record = st.selectbox('Seleccionar registro de incidencia a editar:', list(record_options.keys()))
    
    if selected_record:
        record_id = record_options[selected_record]
        record_data = get_incident_record_details(record_id)
        
        if record_data:
            st.write(f"**Editando registro ID:** {record_id}")
            
            # Formulario de edición con datos actuales
            col1, col2 = st.columns(2)
            
            with col1:
                # Fecha
                new_date = st.date_input('Fecha', value=pd.to_datetime(record_data['date']).date())
                
                # Bodega
                warehouses = get_warehouses()
                warehouse_options = {f"{w['name']} - {w['zone']}": w['id'] for w in warehouses}
                current_warehouse = f"{record_data['warehouse']} - {record_data['warehouse_zone']}"
                warehouse_index = list(warehouse_options.keys()).index(current_warehouse) if current_warehouse in warehouse_options else 0
                selected_warehouse_key = st.selectbox('Bodega', options=list(warehouse_options.keys()), index=warehouse_index)
                new_warehouse_id = warehouse_options[selected_warehouse_key]
                
                # Verificador causante
                verifiers = get_verifiers()
                verifier_options = {f"{v['name']} {v['surnames']}": v['id'] for v in verifiers}
                current_verifier = record_data['causing_verifier']
                verifier_index = list(verifier_options.keys()).index(current_verifier) if current_verifier in verifier_options else 0
                selected_verifier_key = st.selectbox('Verificador Causante', options=list(verifier_options.keys()), index=verifier_index)
                new_causing_verifier_id = verifier_options[selected_verifier_key]
            
            with col2:
                # Tipo de incidencia
                incidents = get_incidents()
                incident_options = {inc[1]: inc[0] for inc in incidents}
                current_incident = record_data['incident_type']
                # Buscar el incident_id actual
                current_incident_id = None
                for inc_id, inc_desc in incidents:
                    if current_incident in inc_desc:
                        current_incident_id = inc_id
                        break
                incident_index = 0
                if current_incident_id:
                    for i, (inc_id, _) in enumerate(incidents):
                        if inc_id == current_incident_id:
                            incident_index = i
                            break
                selected_incident_key = st.selectbox('Tipo de Incidencia', options=list(incident_options.keys()), index=incident_index)
                new_incident_id = incident_options[selected_incident_key]
                
                # Coordinador asignado
                try:
                    coordinators = get_coordinators()
                    if not coordinators:
                        st.error('No hay coordinadores disponibles.')
                        return
                    coordinator_options = {f"{c['name']} {c['surnames']}": c['id'] for c in coordinators}
                except Exception as e:
                    st.error(f'Error al cargar coordinadores: {e}')
                    return
                current_coordinator = record_data['assigned_coordinator']
                coordinator_index = list(coordinator_options.keys()).index(current_coordinator) if current_coordinator in coordinator_options else 0
                selected_coordinator_key = st.selectbox('Coordinador Asignado', options=list(coordinator_options.keys()), index=coordinator_index)
                new_assigned_coordinator_id = coordinator_options[selected_coordinator_key]
                
                # Estado
                status_options = ['Pendiente', 'En Proceso', 'Solucionado', 'Resuelto']
                current_status_index = status_options.index(record_data['status']) if record_data['status'] in status_options else 0
                new_status = st.selectbox('Estado', options=status_options, index=current_status_index)
                
                # Responsable
                responsible_options = ['Coordinador', 'Verificador']
                current_responsible_index = responsible_options.index(record_data['responsible']) if record_data['responsible'] in responsible_options else 0
                new_responsible = st.selectbox('Responsable', options=responsible_options, index=current_responsible_index)
            
            # Explicación
            new_explanation = st.text_area('Explicación', value=record_data['explanation'], help='Explique los detalles de la incidencia')
            
            # Enlace
            new_enlace = st.text_input('Enlace (opcional)', value=record_data.get('enlace', ''), help='URL relacionada con la incidencia (opcional)', placeholder='https://ejemplo.com')
            
            # Mostrar enlace actual como hipervínculo si existe
            current_enlace = record_data.get('enlace', '')
            if current_enlace and current_enlace.strip():
                st.write(f"**Enlace actual:** [{current_enlace}]({current_enlace})")
            
            # Botón de actualización
            if st.button('Actualizar Registro de Incidencia', type='primary'):
                if new_explanation and len(new_explanation.strip()) >= 10:
                    # El coordinador registrador no se puede cambiar, usar el original
                    registering_coordinator_id = record_data['registering_coordinator_id']
                    
                    if update_incident_record(
                        record_id,
                        str(new_date),
                        new_warehouse_id,
                        new_causing_verifier_id,
                        new_incident_id,
                        new_assigned_coordinator_id,
                        new_explanation.strip(),
                        new_enlace.strip() if new_enlace else '',
                        new_status,
                        new_responsible
                    ):
                        st.success('Registro de incidencia actualizado exitosamente.')
                        st.rerun()
                    else:
                        st.error('Error al actualizar el registro de incidencia.')
                else:
                    st.error('Por favor, proporcione una explicación de al menos 10 caracteres.')