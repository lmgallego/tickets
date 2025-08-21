#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

print('=== DIAGNÓSTICO DE EXPORTACIÓN ===')

try:
    print('1. Probando conexión a Supabase...')
    from utils.database_supabase import get_supabase_connection
    client = get_supabase_connection()
    print('   ✓ Conexión establecida')
    
    print('2. Verificando datos en incident_records...')
    result = client.table('incident_records').select('*').execute()
    print(f'   ✓ Registros encontrados: {len(result.data)}')
    
    if len(result.data) == 0:
        print('   ⚠ No hay datos para exportar')
        sys.exit(0)
    
    print('3. Probando get_all_incident_records_df...')
    from utils.database_supabase import get_all_incident_records_df
    df = get_all_incident_records_df()
    print(f'   ✓ DataFrame: {len(df)} filas, {len(df.columns)} columnas')
    
    print('4. Verificando pandas y openpyxl...')
    import pandas as pd
    import openpyxl
    print('   ✓ Librerías disponibles')
    
    print('5. Probando exportación manual...')
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_export_{timestamp}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test', index=False)
    
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f'   ✓ Archivo creado manualmente: {filename} ({size} bytes)')
    else:
        print('   ✗ Error creando archivo manualmente')
    
    print('6. Probando función export_incidents_to_excel...')
    from utils.database_supabase import export_incidents_to_excel
    result_filename = export_incidents_to_excel()
    
    if result_filename:
        print(f'   ✓ Función ejecutada: {result_filename}')
        if os.path.exists(result_filename):
            size = os.path.getsize(result_filename)
            print(f'   ✓ Archivo confirmado: {size} bytes')
        else:
            print('   ✗ Archivo no encontrado en disco')
    else:
        print('   ✗ Función no retornó nombre de archivo')
    
    print('\n=== DIAGNÓSTICO COMPLETADO ===')
    
except Exception as e:
    print(f'\n✗ ERROR en paso actual: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)