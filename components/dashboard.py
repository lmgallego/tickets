import streamlit as st
import pandas as pd
import altair as alt
from utils.database_unified import get_dashboard_stats, get_pending_incidents_summary, get_recent_actions, get_coordinators, get_pending_incidents_by_coordinator, get_filtered_pending_incidents
from datetime import datetime

def dashboard_main():
    """Pantalla principal del dashboard con estadísticas y accesos directos"""
    st.title("📊 Dashboard - Gestión de Incidencias")
    st.markdown("---")
    
    # Obtener estadísticas
    try:
        stats = get_dashboard_stats()
        pending_incidents = get_pending_incidents_summary()
        recent_actions = get_recent_actions()
    except Exception as e:
        st.error(f"Error al cargar datos del dashboard: {e}")
        return
    
    # Sección de métricas principales
    st.subheader("📈 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Incidencias",
            value=stats['total_incidents'],
            help="Número total de incidencias registradas"
        )
    
    with col2:
        st.metric(
            label="Pendientes",
            value=stats['pending_incidents'],
            delta=f"-{stats['resolved_incidents']} resueltas",
            delta_color="inverse",
            help="Incidencias que requieren atención"
        )
    
    with col3:
        st.metric(
            label="Resueltas",
            value=stats['resolved_incidents'],
            help="Incidencias completamente resueltas"
        )
    
    with col4:
        st.metric(
            label="Últimos 7 días",
            value=stats['recent_incidents'],
            help="Incidencias registradas en la última semana"
        )
    
    st.markdown("---")
    
    # Layout en dos columnas
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Sección de incidencias pendientes
        st.subheader("🚨 Incidencias Pendientes")
        
        # Filtros múltiples
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            # Filtro por coordinador
            coordinators = get_coordinators()
            coordinator_options = [(None, "Todos los coordinadores")] + [(coord['id'], f"{coord['name']} {coord['surnames']}") for coord in coordinators]
            
            selected_coordinator = st.selectbox(
                "Coordinador asignado:",
                options=coordinator_options,
                format_func=lambda x: x[1],
                key="coordinator_filter"
            )
        
        with col_filter2:
            # Filtro por estado
            status_options = [
                (None, "Todos los estados"),
                ("Pendiente", "Pendiente"),
                ("En Proceso", "En Proceso"),
                ("Solucionado", "Solucionado")
            ]
            
            selected_status = st.selectbox(
                "Estado:",
                options=status_options,
                format_func=lambda x: x[1],
                key="status_filter"
            )
        
        with col_filter3:
            # Filtro por fecha (últimos N días)
            days_options = [
                (None, "Todas las fechas"),
                (7, "Últimos 7 días"),
                (15, "Últimos 15 días"),
                (30, "Últimos 30 días")
            ]
            
            selected_days = st.selectbox(
                "Período:",
                options=days_options,
                format_func=lambda x: x[1],
                key="days_filter"
            )
            
            
            selected_date = st.date_input(
                "Fecha específica",
                format="DD/MM/YYYY",
                value=None,
                key="specific_date_filter"
            )
        
        # Obtener incidencias filtradas con múltiples criterios
        coordinator_id = selected_coordinator[0] if selected_coordinator[0] is not None else None
        status_filter = selected_status[0] if selected_status[0] is not None else None
        days_filter = selected_days[0] if selected_days[0] is not None else None
        
        filtered_incidents = get_filtered_pending_incidents(
            coordinator_id, 
            status_filter, 
            days_filter, 
            selected_date
        )
        
        
        if filtered_incidents.empty:
            if coordinator_id:
                st.success(f"🎉 ¡Excelente! No hay incidencias pendientes para {selected_coordinator[1]}.")
            else:
                st.success("🎉 ¡Excelente! No hay incidencias pendientes.")
        else:
            if coordinator_id:
                st.info(f"Se muestran las {len(filtered_incidents)} incidencias pendientes para {selected_coordinator[1]}.")
            else:
                st.info(f"Se muestran las {len(filtered_incidents)} incidencias más recientes pendientes de resolución.")
            
            # Mostrar tabla de incidencias pendientes
            for idx, incident in filtered_incidents.iterrows():
                with st.container():
                    # Crear un expander para cada incidencia
                    status_color = {
                        'Pendiente': '🔴',
                        'En Proceso': '🟡',
                        'Solucionado': '🟠',
                        'Resuelto': '🟢'
                    }.get(incident['status'], '⚪')
                    
                    with st.expander(
                        f"{status_color} ID {incident['id']} - {incident['warehouse']} - {incident['incident_type']}",
                        expanded=False
                    ):
                        col_info, col_action = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**📅 Fecha:** {incident['date']}")
                            st.write(f"**🏢 Bodega:** {incident['warehouse']} ({incident['warehouse_zone']})")
                            st.write(f"**👤 Verificador:** {incident['causing_verifier']}")
                            st.write(f"**👨‍💼 Coordinador Asignado:** {incident['assigned_coordinator']}")
                            st.write(f"**📋 Estado:** {incident['status']}")
                            st.write(f"**👥 Responsable:** {incident['responsible']}")
                        
                        with col_action:
                            # Botón de acceso directo a gestión de acciones
                            if st.button(
                                "⚡ Gestionar",
                                key=f"manage_{incident['id']}",
                                help="Ir a Gestión de Acciones para esta incidencia",
                                type="primary"
                            ):
                                # Guardar el ID de la incidencia en session_state para navegación
                                st.session_state['selected_incident_record_id'] = incident['id']
                                st.session_state['navigate_to_actions'] = True
                                st.rerun()
    
    with col_right:
        # Gráfico de distribución por estado
        st.subheader("📊 Distribución por Estado")
        
        if not stats['by_status'].empty:
            # Crear gráfico de barras
            chart = alt.Chart(stats['by_status']).mark_bar(color='steelblue').encode(
                x=alt.X('count:Q', title='Cantidad'),
                y=alt.Y('status:N', title='Estado', sort='-x'),
                tooltip=['status:N', 'count:Q']
            ).properties(
                width=300,
                height=200
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")
        
        # Acciones recientes en desplegable
        st.subheader("🔄 Acciones Recientes")
        
        if recent_actions.empty:
            st.info("No hay acciones recientes")
        else:
            # Obtener todas las acciones para el desplegable
            try:
                all_recent_actions = get_recent_actions(limit=50)  # Obtener hasta 50 acciones
            except:
                all_recent_actions = recent_actions
            
            with st.expander(f"📋 Ver todas las acciones ({len(all_recent_actions)} disponibles)", expanded=False):
                if all_recent_actions.empty:
                    st.info("No hay acciones disponibles")
                else:
                    for idx, action in all_recent_actions.iterrows():
                        with st.container():
                            # Formatear fecha
                            try:
                                formatted_date = pd.to_datetime(action['action_date']).strftime('%d/%m/%Y %H:%M')
                            except:
                                formatted_date = action['action_date']
                            
                            # Crear un diseño más limpio
                            col_date, col_content = st.columns([1, 3])
                            
                            with col_date:
                                st.markdown(f"**📅 {formatted_date}**")
                                st.markdown(f"🏢 {action['warehouse']}")
                            
                            with col_content:
                                st.markdown(f"**ID:** {action['incident_id']} | **Por:** {action['performed_by']}")
                                st.markdown(f"📝 {action['action_description']}")
                                if pd.notna(action['new_status']) and action['new_status']:
                                    st.markdown(f"➡️ **Estado:** {action['new_status']}")
                            
                            st.markdown("---")
        

    
    # Sección de accesos rápidos
    st.markdown("---")
    st.subheader("🚀 Accesos Rápidos")
    
    col_quick1, col_quick2, col_quick3, col_quick4, col_quick5 = st.columns(5)
    
    with col_quick1:
        if st.button("📝 Nuevo Registro", use_container_width=True, type="secondary", key="quick_new_record"):
            st.session_state['navigate_to'] = 'new_incident_record'
            st.rerun()
    
    with col_quick2:
        if st.button("🏷️ Nuevo Código", use_container_width=True, type="secondary", key="quick_new_code"):
            st.session_state['navigate_to'] = 'new_incident_code'
            st.rerun()
    
    with col_quick3:
        if st.button("⚡ Gestión de Acciones", use_container_width=True, type="secondary", key="quick_actions"):
            st.session_state['navigate_to'] = 'manage_actions'
            st.rerun()
    
    with col_quick4:
        if st.button("📊 Analítica Completa", use_container_width=True, type="secondary", key="quick_analytics"):
            st.session_state['navigate_to'] = 'analytics'
            st.rerun()
    
    with col_quick5:
        if st.button("📋 Exportar Excel", use_container_width=True, type="secondary", key="quick_export"):
            st.session_state['navigate_to'] = 'export'
            # Agregar un pequeño delay para asegurar que el estado se establezca correctamente
            import time
            time.sleep(0.1)
            st.rerun()
    
    # Información adicional
    st.markdown("---")
    with st.expander("ℹ️ Información del Dashboard"):
        st.markdown("""
        **¿Qué puedes hacer desde aquí?**
        
        - **Ver estadísticas generales** de todas las incidencias
        - **Revisar incidencias pendientes** que requieren atención
        - **Acceder directamente** a la gestión de acciones de cualquier incidencia
        - **Monitorear acciones recientes** realizadas por el equipo
        - **Navegar rápidamente** a las funciones más utilizadas
        
        **Accesos Rápidos:**
        - 📝 **Nuevo Registro**: Registrar una nueva incidencia específica
        - 🏷️ **Nuevo Código**: Crear un nuevo tipo/código de incidencia
        - ⚡ **Gestión de Acciones**: Administrar acciones de incidencias existentes
        - 📊 **Analítica Completa**: Ver reportes y estadísticas detalladas
        - 📋 **Exportar Excel**: Generar reportes en formato Excel
        
        **Estados de incidencias:**
        - 🔴 **Pendiente**: Recién registrada, requiere asignación
        - 🟡 **En Proceso**: Se está trabajando en la resolución
        - 🟠 **Solucionado**: Incidencias que han sido solucionadas
        - 🟢 **Resuelto**: Incidencia completamente resuelta
        """)

def handle_dashboard_navigation():
    """Maneja la navegación desde el dashboard"""
    # Verificar si hay navegación pendiente
    if 'navigate_to_actions' in st.session_state and st.session_state['navigate_to_actions']:
        st.session_state['navigate_to_actions'] = False
        return 'manage_actions'
    
    if 'navigate_to' in st.session_state:
        destination = st.session_state['navigate_to']
        del st.session_state['navigate_to']
        return destination
    
    return None