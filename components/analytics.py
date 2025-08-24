import streamlit as st
import pandas as pd
import altair as alt
from utils.database_unified import get_all_incident_records_df, get_all_verifiers_df, get_all_warehouses_df, get_incidents_by_zone, get_incidents_by_verifier, get_incidents_by_warehouse, get_incidents_by_type, get_incidents_by_status, get_assignments_by_verifier

def display_filtered_table(title, df_getter):
    st.subheader(title)
    df = df_getter()
    if df.empty:
        st.warning('No hay datos disponibles.')
        return
    search_term = st.text_input('Búsqueda global', '')
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        df = df[mask]
    
    # Mapeos de nombres amigables para cada tipo de tabla
    friendly_mappings = {
        'Consulta de Incidencias': {
            'ID': 'id',
            'Fecha': 'date',
            'Coordinador Registrador': 'registering_coordinator',
            'Bodega': 'warehouse',
            'Zona de Bodega': 'warehouse_zone',
            'Verificador Causante': 'causing_verifier',
            'Zona de Verificador': 'verifier_zone',
            'Tipo de Incidencia': 'incident_type',
            'Coordinador Asignado': 'assigned_coordinator',
            'Explicación': 'explanation',
            'Enlace': 'enlace',
            'Estado': 'status',
            'Responsable': 'responsible'
        },
        'Consulta de Verificadores': {
            'Nombre': 'name',
            'Apellidos': 'surnames',
            'Teléfono': 'phone',
            'Zona': 'zone'
        },
        'Consulta de Bodegas': {
            'Nombre': 'name',
            'Código Consejo': 'codigo_consejo',
            'Zona': 'zone'
        }
    }
    
    friendly_to_tech = friendly_mappings.get(title, {})
    tech_to_friendly = {v: k for k, v in friendly_to_tech.items()}
    available_tech = list(friendly_to_tech.values())
    selected_tech = st.multiselect('Seleccionar columnas para filtrar', list(friendly_to_tech.keys()), default=[])
    columns = [friendly_to_tech[f] for f in selected_tech]
    
    filters = {}
    for col in columns:
        friendly_col = next((k for k, v in friendly_to_tech.items() if v == col), col)
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = st.slider(f'Filtrar {friendly_col}', float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))
            filters[col] = (min_val, max_val)
        else:
            unique_vals = df[col].unique()
            selected = st.multiselect(f'Filtrar {friendly_col}', unique_vals, unique_vals)
            filters[col] = selected
    filtered_df = df.copy()
    for col, vals in filters.items():
        if isinstance(vals, tuple):
            filtered_df = filtered_df[(filtered_df[col] >= vals[0]) & (filtered_df[col] <= vals[1])]
        else:
            filtered_df = filtered_df[filtered_df[col].isin(vals)]
    filtered_df = filtered_df.rename(columns=tech_to_friendly)
    
    # Ocultar columnas de códigos (asumiendo que son las que terminan en '_id' o 'id')
    display_columns = [col for col in filtered_df.columns if not col.lower().endswith('_id') and col.lower() != 'id']
    
    # Mostrar tabla con funcionalidad especial para enlaces
    display_df = filtered_df[display_columns]
    
    # Formatear enlaces como hipervínculos si existe la columna 'Enlace'
    if 'Enlace' in display_df.columns:
        # Mostrar la tabla
        st.dataframe(display_df, use_container_width=True)
        
        # Mostrar enlaces como hipervínculos debajo de la tabla si hay enlaces
        enlaces_con_datos = display_df[display_df['Enlace'].notna() & (display_df['Enlace'] != '')]
        if not enlaces_con_datos.empty:
            st.subheader("🔗 Enlaces Disponibles")
            for idx, row in enlaces_con_datos.iterrows():
                enlace = row['Enlace']
                if enlace and enlace.strip():
                    # Buscar ID en las columnas disponibles
                    id_value = row.get('ID', idx)
                    st.markdown(f"**ID {id_value}:** [{enlace}]({enlace})")
    else:
        st.dataframe(display_df, use_container_width=True)

def display_chart(title, df_getter, x_col, y_col='count'):
    st.subheader(title)
    df = df_getter()
    if df.empty:
        st.warning('No hay datos disponibles.')
        return
    # Las columnas ya vienen con nombres amigables desde database_supabase.py
    friendly_y = 'Cantidad'
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(x_col, sort='-y', title=x_col),
        y=alt.Y(y_col, title=friendly_y),
        tooltip=[alt.Tooltip(x_col, title=x_col), alt.Tooltip(y_col, title=friendly_y)]
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def analytics_incidents():
    display_filtered_table('Consulta de Incidencias', get_all_incident_records_df)
    display_chart('Incidencias por Zona', get_incidents_by_zone, 'warehouse_zone')
    display_chart('Incidencias por Verificador', get_incidents_by_verifier, 'causing_verifier')
    display_chart('Incidencias por Bodega', get_incidents_by_warehouse, 'warehouse')
    display_chart('Incidencias por Tipo', get_incidents_by_type, 'incident_type')
    display_chart('Incidencias por Estado', get_incidents_by_status, 'status')

def analytics_verifiers():
    display_filtered_table('Consulta de Verificadores', get_all_verifiers_df)
    display_chart('Asignaciones por Verificador', get_assignments_by_verifier, 'causing_verifier')

def analytics_warehouses():
    display_filtered_table('Consulta de Bodegas', get_all_warehouses_df)