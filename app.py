import streamlit as st
st.set_page_config(layout="wide", page_title="Gestión de Incidencias")
st.markdown("""
    <style>
        .main {max-width: 100%;}
        @media (max-width: 768px) {
            .main {padding: 0 10px;}
            .stButton > button {width: 100%;}
        }
        section[data-testid="stSidebar"] {
            background-color: #f5f5f5 !important;
            font-size: 0.7rem !important;
        }
        section[data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        section[data-testid="stSidebar"] .block-container {
            background-color: #f5f5f5 !important;
        }
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        /* For option menu */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] .row-widget {
            background-color: #f5f5f5 !important;
            color: #000000 !important;
            font-size: 0.7rem !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] .row-widget button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] a.nav-link {
            background-color: #f5f5f5 !important;
            color: #000000 !important;
        }
        section[data-testid="stSidebar"] a.nav-link.active {
            background-color: #D3D3D3 !important;
            color: #000000 !important;
        }
        /* Estilo específico para el botón de cerrar sesión */
        .logout-button {
            background: linear-gradient(135deg, #dc3545, #c82333) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
        }
        .logout-button:hover {
            background: linear-gradient(135deg, #c82333, #a71e2a) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
        }
        .logout-button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

from streamlit_option_menu import option_menu
from utils.database_unified import init_db
from components.forms import coordinator_form, verifier_form, warehouse_form, csv_upload, incident_form, search_incident_form, incident_record_form, manage_incident_actions_form, edit_coordinator_form, edit_verifier_form, edit_warehouse_form, edit_incident_type_form, edit_incident_record_form
from components.analytics import analytics_incidents, analytics_verifiers, analytics_warehouses
from components.delete import delete_test_data_form, backup_database_form, export_excel_form, restore_database_form
from components.dashboard import dashboard_main, handle_dashboard_navigation
import hashlib
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar la base de datos
logger.info("Initializing database from app.py...")
init_db()
logger.info("Database initialization completed.")

# Inicializar datos por defecto en entornos de deploy
try:
    from config import is_deployed_environment
    if is_deployed_environment():
        from init_default_data import run_default_initialization
        logger.info("Deploy environment detected, checking for default data...")
        run_default_initialization()
except ImportError:
    logger.info("Default data initialization not available")

# Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        stored_hash = hashlib.sha256("Cava1234!".encode()).hexdigest()
        if username == "coordinador" and hashed_password == stored_hash:
            st.session_state.logged_in = True
            st.session_state.role = "coordinador"
            st.rerun()
        elif username == "admin" and hashed_password == stored_hash:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    role = st.session_state.get('role', 'coordinador')
    
    # Manejar navegación desde dashboard
    dashboard_nav = handle_dashboard_navigation()
    if dashboard_nav:
        if dashboard_nav == 'manage_actions':
            st.session_state['main_menu_override'] = 'Incidencias'
            st.session_state['sub_menu_override'] = 'Gestión de Acciones'
        elif dashboard_nav == 'new_incident_record':
            st.session_state['main_menu_override'] = 'Incidencias'
            st.session_state['sub_menu_override'] = 'Registro de Incidencia'
            # Marcar que venimos desde acceso rápido para mantener contexto
            st.session_state['from_quick_access'] = 'new_incident_record'
        elif dashboard_nav == 'new_incident_code':
            st.session_state['main_menu_override'] = 'Altas'
            st.session_state['sub_menu_override'] = 'Alta Incidencia'
            st.session_state['from_quick_access'] = 'new_incident_code'
        elif dashboard_nav == 'analytics':
            st.session_state['main_menu_override'] = 'Consultas y Analítica'
            st.session_state['from_quick_access'] = 'analytics'
        elif dashboard_nav == 'export':
            st.session_state['main_menu_override'] = 'Administración'
            st.session_state['sub_menu_override'] = 'Exportar a Excel'
            st.session_state['from_quick_access'] = 'export'
    
    with st.sidebar:
        # Botón de logout en la parte superior con estilo personalizado
        st.markdown("""
        <style>
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #dc3545, #c82333) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
            width: 100% !important;
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(135deg, #c82333, #a71e2a) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
        }
        div.stButton > button:first-child:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            # Limpiar todas las variables de sesión relacionadas con login
            for key in list(st.session_state.keys()):
                if key in ['logged_in', 'role', 'main_menu_override', 'sub_menu_override', 'in_manage_actions']:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        main_options = ["Dashboard", "Altas", "Edición", "Incidencias", "Consultas y Analítica", "Administración"]
        icons = ["speedometer2", "plus-circle", "pencil", "exclamation-triangle", "bar-chart-line", "gear"]
        
        # Determinar índice por defecto basado en navegación
        default_idx = 0
        if 'main_menu_override' in st.session_state:
            override_menu = st.session_state['main_menu_override']
            if override_menu in main_options:
                default_idx = main_options.index(override_menu)
            del st.session_state['main_menu_override']
        elif 'from_quick_access' in st.session_state:
            # Mantener contexto de navegación desde acceso rápido
            quick_access = st.session_state['from_quick_access']
            if quick_access == 'new_incident_record':
                default_idx = main_options.index('Incidencias')
            elif quick_access == 'new_incident_code':
                default_idx = main_options.index('Altas')
            elif quick_access == 'analytics':
                default_idx = main_options.index('Consultas y Analítica')
            elif quick_access == 'export':
                default_idx = main_options.index('Administración')
        
        main_selected = option_menu(
            menu_title="Menú Principal",
            options=main_options,
            icons=icons,
            menu_icon="cast",
            default_index=default_idx,
        )
    
    # Limpiar contexto de acceso rápido si se navega manualmente a otro menú principal
    if 'from_quick_access' in st.session_state:
        quick_access = st.session_state['from_quick_access']
        # Limpiar si el usuario navega fuera del menú principal correspondiente
        if (quick_access in ['new_incident_record', 'manage_actions'] and main_selected != "Incidencias") or \
           (quick_access == 'new_incident_code' and main_selected != "Altas") or \
           (quick_access == 'analytics' and main_selected != "Consultas y Analítica") or \
           (quick_access == 'export' and main_selected != "Administración"):
            del st.session_state['from_quick_access']
    
    # Limpiar contexto de gestión de acciones si se navega a otra sección
    # PERO solo si no hay una fuerza explícita para permanecer en acciones
    if main_selected != "Incidencias" and 'in_manage_actions' in st.session_state:
        # No limpiar si hay una fuerza explícita para permanecer
        if not st.session_state.get('force_stay_in_actions', False):
            del st.session_state['in_manage_actions']
        else:
            # Si hay fuerza para permanecer, redirigir de vuelta a Incidencias
            # PERO no si estamos en búsqueda por código O si el usuario seleccionó Dashboard explícitamente
            if not st.session_state.get('in_search_mode', False) and main_selected != "Dashboard":
                main_selected = "Incidencias"
            elif main_selected == "Dashboard":
                # Limpiar todas las variables de fuerza si el usuario va al Dashboard
                if 'force_stay_in_actions' in st.session_state:
                    del st.session_state['force_stay_in_actions']
                if 'in_manage_actions' in st.session_state:
                    del st.session_state['in_manage_actions']
                # No establecer overrides cuando el usuario explícitamente va al Dashboard
    
    if main_selected == "Dashboard":
        dashboard_main()
    
    elif main_selected == "Altas":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Alta Coordinador", "Alta Verificador", "Alta Bodega", "Cargar Verificadores CSV", "Cargar Bodegas CSV", "Alta Incidencia"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            
            sub_selected = option_menu(
                menu_title="Altas",
                options=["Alta Coordinador", "Alta Verificador", "Alta Bodega", "Cargar Verificadores CSV", "Cargar Bodegas CSV", "Alta Incidencia"],
                icons=["person", "person-check", "building", "file-earmark-spreadsheet", "file-earmark-spreadsheet", "exclamation-triangle"],
                menu_icon="plus",
                default_index=sub_default_idx,
            )

        if sub_selected == "Alta Coordinador":
            coordinator_form()
        elif sub_selected == "Alta Verificador":
            verifier_form()
        elif sub_selected == "Alta Bodega":
            warehouse_form()
        elif sub_selected == "Cargar Verificadores CSV":
            csv_upload("Verificadores")
        elif sub_selected == "Cargar Bodegas CSV":
            csv_upload("Bodegas")
        elif sub_selected == "Alta Incidencia":
            incident_form()

    elif main_selected == "Edición":
        with st.sidebar:
            sub_selected = option_menu(
                menu_title="Edición",
                options=["Editar Coordinador", "Editar Verificador", "Editar Bodega", "Editar Tipo de Incidencia", "Editar Registro de Incidencia"],
                icons=["person-gear", "person-check-fill", "building-gear", "tag-fill", "clipboard-data-fill"],
                menu_icon="pencil",
                default_index=0,
            )

        if sub_selected == "Editar Coordinador":
            edit_coordinator_form()
        elif sub_selected == "Editar Verificador":
            edit_verifier_form()
        elif sub_selected == "Editar Bodega":
            edit_warehouse_form()
        elif sub_selected == "Editar Tipo de Incidencia":
            edit_incident_type_form()
        elif sub_selected == "Editar Registro de Incidencia":
            edit_incident_record_form()

    elif main_selected == "Incidencias":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Registro de Incidencia", "Gestión de Acciones", "Buscar por Código"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            elif 'from_quick_access' in st.session_state and st.session_state['from_quick_access'] == 'new_incident_record':
                # Mantener contexto para registro de incidencia desde acceso rápido
                sub_options = ["Registro de Incidencia", "Gestión de Acciones", "Buscar por Código"]
                sub_default_idx = sub_options.index("Registro de Incidencia")
            
            sub_selected = option_menu(
                menu_title="Incidencias",
                options=["Registro de Incidencia", "Gestión de Acciones", "Buscar por Código"],
                icons=["clipboard-plus", "pencil-square", "search"],
                menu_icon="exclamation",
                default_index=sub_default_idx,
            )

        # Limpiar contexto de acceso rápido si se navega manualmente a otra subsección
        if 'from_quick_access' in st.session_state:
            quick_access = st.session_state['from_quick_access']
            # Solo limpiar si el usuario navega manualmente fuera de la sección de acceso rápido
            if (quick_access == 'new_incident_record' and sub_selected != "Registro de Incidencia") or \
               (quick_access == 'manage_actions' and sub_selected != "Gestión de Acciones"):
                del st.session_state['from_quick_access']
        
        # Limpiar contexto de gestión de acciones si se navega a otra subsección
        # PERO solo si no hay una fuerza explícita para permanecer en acciones
        if sub_selected != "Gestión de Acciones" and 'in_manage_actions' in st.session_state:
            # No limpiar si hay una fuerza explícita para permanecer
            if not st.session_state.get('force_stay_in_actions', False):
                del st.session_state['in_manage_actions']
            else:
                # Si hay fuerza para permanecer, limpiar la fuerza pero mantener el contexto
                # EXCEPTO si estamos en modo búsqueda
                if 'force_stay_in_actions' in st.session_state and not st.session_state.get('in_search_mode', False):
                    del st.session_state['force_stay_in_actions']
        
        if sub_selected == "Registro de Incidencia":
            incident_record_form()
        elif sub_selected == "Gestión de Acciones":
            manage_incident_actions_form()
        elif sub_selected == "Buscar por Código":
            # Marcar que estamos en modo búsqueda para evitar redirecciones
            st.session_state['in_search_mode'] = True
            search_incident_form()
            # Limpiar el modo búsqueda al final
            if 'in_search_mode' in st.session_state:
                del st.session_state['in_search_mode']

    elif main_selected == "Consultas y Analítica":
        with st.sidebar:
            sub_selected = option_menu(
                menu_title="Consultas y Analítica",
                options=["Analítica de Incidencias", "Analítica de Verificadores", "Analítica de Bodegas"],
                icons=["clipboard-data", "person-lines-fill", "building"],
                menu_icon="graph-up",
                default_index=0,
            )

        if sub_selected == "Analítica de Incidencias":
            analytics_incidents()
        elif sub_selected == "Analítica de Verificadores":
            analytics_verifiers()
        elif sub_selected == "Analítica de Bodegas":
            analytics_warehouses()

    elif main_selected == "Administración":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Copia de Seguridad", "Restaurar Copia", "Exportar a Excel", "Borrar Datos de Prueba"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            
            sub_selected = option_menu(
                menu_title="Administración",
                options=["Copia de Seguridad", "Restaurar Copia", "Exportar a Excel", "Borrar Datos de Prueba"],
                icons=["shield-check", "arrow-clockwise", "file-earmark-excel", "trash"],
                menu_icon="gear",
                default_index=sub_default_idx,
            )

        if sub_selected == "Copia de Seguridad":
            backup_database_form()
        elif sub_selected == "Restaurar Copia":
            restore_database_form()
        elif sub_selected == "Exportar a Excel":
            export_excel_form()
        elif sub_selected == "Borrar Datos de Prueba":
            delete_test_data_form()