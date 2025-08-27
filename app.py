import streamlit as st
st.set_page_config(layout="wide", page_title="Gestión de Incidencias")

@st.cache_data
def get_main_css():
    """Retorna los estilos CSS principales con cache"""
    return """
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
    """

@st.cache_data
def get_logout_button_css():
    """Retorna los estilos CSS del botón de logout con cache"""
    return """
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
    """

# Aplicar estilos principales
st.markdown(get_main_css(), unsafe_allow_html=True)

# Imports básicos necesarios al inicio
import hashlib
import logging

# Lazy imports - se cargarán cuando sean necesarios
def get_option_menu():
    from streamlit_option_menu import option_menu
    return option_menu

def get_database_functions():
    from utils.database_unified import init_db
    return init_db

def get_form_components():
    from components.forms import (
        coordinator_form, verifier_form, warehouse_form, csv_upload, 
        incident_form, search_incident_form, incident_record_form, 
        manage_incident_actions_form, edit_coordinator_form, 
        edit_verifier_form, edit_warehouse_form, edit_incident_type_form, 
        edit_incident_record_form
    )
    return {
        'coordinator_form': coordinator_form,
        'verifier_form': verifier_form,
        'warehouse_form': warehouse_form,
        'csv_upload': csv_upload,
        'incident_form': incident_form,
        'search_incident_form': search_incident_form,
        'incident_record_form': incident_record_form,
        'manage_incident_actions_form': manage_incident_actions_form,
        'edit_coordinator_form': edit_coordinator_form,
        'edit_verifier_form': edit_verifier_form,
        'edit_warehouse_form': edit_warehouse_form,
        'edit_incident_type_form': edit_incident_type_form,
        'edit_incident_record_form': edit_incident_record_form
    }

def get_analytics_components():
    from components.analytics import analytics_incidents, analytics_verifiers, analytics_warehouses
    return {
        'analytics_incidents': analytics_incidents,
        'analytics_verifiers': analytics_verifiers,
        'analytics_warehouses': analytics_warehouses
    }

def get_delete_components():
    from components.delete import delete_test_data_form, backup_database_form, export_excel_form, restore_database_form
    return {
        'delete_test_data_form': delete_test_data_form,
        'backup_database_form': backup_database_form,
        'export_excel_form': export_excel_form,
        'restore_database_form': restore_database_form
    }

def get_admin_components():
    """Lazy loading para componentes de administración"""
    from components.delete import backup_database_form, restore_database_form, export_excel_form, delete_test_data_form
    
    return {
        'backup_database_form': backup_database_form,
        'restore_database_form': restore_database_form,
        'export_excel_form': export_excel_form,
        'delete_test_data_form': delete_test_data_form
    }

def get_dashboard_components():
    from components.dashboard import dashboard_main, handle_dashboard_navigation
    return {
        'dashboard_main': dashboard_main,
        'handle_dashboard_navigation': handle_dashboard_navigation
    }

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar la base de datos usando lazy loading
logger.info("Initializing database from app.py...")
init_db = get_database_functions()
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

@st.cache_data
def get_session_defaults():
    """Retorna los valores por defecto para session_state"""
    return {
        'logged_in': False,
        'role': 'coordinador',
        'coord_form_counter': 0,
        'verif_form_counter': 0,
        'warehouse_form_counter': 0,
        'incident_form_counter': 0,
        'incident_record_counter': 0,
        'incident_actions_counter': 0
    }

def initialize_session_state():
    """Inicializa session_state solo si es necesario"""
    defaults = get_session_defaults()
    
    # Solo inicializar las claves que no existen
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def clear_session_state():
    """Limpia session_state de manera eficiente al cerrar sesión"""
    # Claves que deben mantenerse después del logout
    keys_to_keep = set()
    
    # Claves que deben eliminarse
    keys_to_remove = {
        'logged_in', 'role', 'main_menu_override', 'sub_menu_override', 
        'in_manage_actions', 'force_stay_in_actions', 'in_search_mode',
        'from_quick_access', 'selected_incident_record_id', 'navigate_to_actions',
        'navigate_to', 'last_created_record_id', 'loading_large_dataset'
    }
    
    # Eliminar solo las claves específicas
    for key in list(st.session_state.keys()):
        if key in keys_to_remove:
            del st.session_state[key]
    
    # Reinicializar valores por defecto
    st.session_state.logged_in = False

# Inicializar session_state de manera eficiente
initialize_session_state()

if not st.session_state.logged_in:
    # CSS personalizado para la pantalla de login
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 450px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .login-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .login-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .login-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.9) !important;
        border: 2px solid transparent !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76,175,80,0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 12px rgba(76,175,80,0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #45a049, #3d8b40) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 16px rgba(76,175,80,0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(76,175,80,0.3) !important;
    }
    
    .login-footer {
        margin-top: 2rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
    }
    
    .user-roles {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .role-item {
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    /* Animación de entrada */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-container {
        animation: slideIn 0.6s ease-out;
    }
    
    /* Ocultar elementos de Streamlit */
    .stApp > header {
        background-color: transparent;
    }
    
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Crear el contenedor de login centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-icon">🔐</div>
            <h1 class="login-title">CAVA CRM</h1>
            <p class="login-subtitle">Sistema de Gestión de Incidencias</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario de login con espaciado
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingrese su contraseña")
            

            
            if st.button("🚀 Iniciar Sesión"):
                if not username or not password:
                    st.error("⚠️ Por favor, complete todos los campos")
                else:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    stored_hash = hashlib.sha256("Cava1234!".encode()).hexdigest()
                    
                    if username == "coordinador" and hashed_password == stored_hash:
                        st.success("✅ ¡Bienvenido, Coordinador!")
                        st.session_state.logged_in = True
                        st.session_state.role = "coordinador"
                        st.balloons()
                        st.rerun()
                    elif username == "admin" and hashed_password == stored_hash:
                        st.success("✅ ¡Bienvenido, Administrador!")
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.balloons()
                        st.rerun()
                    else:
                         st.error("❌ Usuario o contraseña incorrectos")
                         st.warning("🔒 Acceso denegado. Contacte al administrador del sistema.")
        

else:
    role = st.session_state.get('role', 'coordinador')
    
    # Manejar navegación desde dashboard usando lazy loading
    dashboard_components = get_dashboard_components()
    dashboard_nav = dashboard_components['handle_dashboard_navigation']()
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
        st.markdown(get_logout_button_css(), unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            clear_session_state()
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
        
        # Generar key dinámico para forzar re-renderización cuando hay override
        menu_key = "main_menu"
        if 'main_menu_override' in st.session_state:
            menu_key = f"main_menu_force_{st.session_state['main_menu_override']}"
        
        option_menu = get_option_menu()
        main_selected = option_menu(
            menu_title="Menú Principal",
            options=main_options,
            icons=icons,
            menu_icon="cast",
            default_index=default_idx,
            key=menu_key  # Key dinámico fuerza re-renderización
        )
    
    # Limpiar main_menu_override después de procesar la selección
    # Solo eliminar si no hay una bandera de "recién establecido"
    if 'main_menu_override' in st.session_state:
        # Si hay una bandera de recién establecido, no eliminar aún
        if not st.session_state.get('_override_just_set', False):
            del st.session_state['main_menu_override']
        else:
            # Limpiar la bandera para la próxima ejecución
            del st.session_state['_override_just_set']
    
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
        dashboard_components = get_dashboard_components()
        dashboard_components['dashboard_main']()
    
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

        # Cargar componentes de formularios usando lazy loading
        form_components = get_form_components()
        
        if sub_selected == "Alta Coordinador":
            form_components['coordinator_form']()
        elif sub_selected == "Alta Verificador":
            form_components['verifier_form']()
        elif sub_selected == "Alta Bodega":
            form_components['warehouse_form']()
        elif sub_selected == "Cargar Verificadores CSV":
            form_components['csv_upload']("Verificadores")
        elif sub_selected == "Cargar Bodegas CSV":
            form_components['csv_upload']("Bodegas")
        elif sub_selected == "Alta Incidencia":
            form_components['incident_form']()

    elif main_selected == "Edición":
        with st.sidebar:
            sub_selected = option_menu(
                menu_title="Edición",
                options=["Editar Coordinador", "Editar Verificador", "Editar Bodega", "Editar Tipo de Incidencia", "Editar Registro de Incidencia"],
                icons=["person-gear", "person-check-fill", "building-gear", "tag-fill", "clipboard-data-fill"],
                menu_icon="pencil",
                default_index=0,
            )

        # Cargar componentes de formularios usando lazy loading
        form_components = get_form_components()
        
        if sub_selected == "Editar Coordinador":
            form_components['edit_coordinator_form']()
        elif sub_selected == "Editar Verificador":
            form_components['edit_verifier_form']()
        elif sub_selected == "Editar Bodega":
            form_components['edit_warehouse_form']()
        elif sub_selected == "Editar Tipo de Incidencia":
            form_components['edit_incident_type_form']()
        elif sub_selected == "Editar Registro de Incidencia":
            form_components['edit_incident_record_form']()

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
        
        # Cargar componentes de formularios usando lazy loading
        form_components = get_form_components()
        
        if sub_selected == "Registro de Incidencia":
            form_components['incident_record_form']()
        elif sub_selected == "Gestión de Acciones":
            form_components['manage_incident_actions_form']()
        elif sub_selected == "Buscar por Código":
            # Marcar que estamos en modo búsqueda para evitar redirecciones
            st.session_state['in_search_mode'] = True
            form_components['search_incident_form']()
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

        # Cargar componentes de analítica usando lazy loading
        analytics_components = get_analytics_components()
        
        if sub_selected == "Analítica de Incidencias":
            analytics_components['analytics_incidents']()
        elif sub_selected == "Analítica de Verificadores":
            analytics_components['analytics_verifiers']()
        elif sub_selected == "Analítica de Bodegas":
            analytics_components['analytics_warehouses']()

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

        # Cargar componentes de administración usando lazy loading
        admin_components = get_admin_components()
        
        if sub_selected == "Copia de Seguridad":
            admin_components['backup_database_form']()
        elif sub_selected == "Restaurar Copia":
            admin_components['restore_database_form']()
        elif sub_selected == "Exportar a Excel":
            admin_components['export_excel_form']()
        elif sub_selected == "Borrar Datos de Prueba":
            admin_components['delete_test_data_form']()