import pandas as pd
import streamlit as st
import plotly.express as px
import glob

GITHUB_RAW_URL_BASE = "https://raw.githubusercontent.com/fsazo/ArchivosRenta/refs/heads/main/RentaVariable/ArchivosExcel/"

# Lista de identificadores MMYY
identificadores_mmyy = [
    '1224', '0125', '0225', '0325', '0425',
    '0525', '0625', '0725', '0825', '0925'
]

# GENERAR EL DICCIONARIO DE URLs automáticamente
archivos_urls = {}
for mmyy in identificadores_mmyy:
    nombre_archivo_excel = f"Consolidado_renta_variable_{mmyy}.xlsx"
    # El enlace es simplemente: Base + Nombre del archivo
    url_completa = f"{GITHUB_RAW_URL_BASE}{nombre_archivo_excel}"
    archivos_urls[mmyy] = url_completa


# Inicializar las variables para el resto del script
archivos_fechas = sorted(archivos_urls.keys())
archivos = [archivos_urls[mmyy] for mmyy in archivos_fechas] # Lista de URLs para la evolución



uf_1224 = 38416.69 / 1000
uf_0125 = 38384.41 / 1000
uf_0225 = 38647.94 / 1000
uf_0325 = 38894.11 / 1000
uf_0425 = 39075.41 / 1000
uf_0525 = 39189.45 / 1000
uf_0625 = 39267.07 / 1000
uf_0725 = 39179.01 / 1000
uf_0825 = 39383.07 / 1000
uf_0925 = 39485.65 / 1000


# Diccionario UF por mes
uf_mensual = {
    '1224': uf_1224,
    '0125': uf_0125,
    '0225': uf_0225,
    '0325': uf_0325,
    '0425': uf_0425,
    '0525': uf_0525,
    '0625': uf_0625,
    '0725': uf_0725,
    '0825': uf_0825,
    '0925': uf_0925
}

#archivos = sorted(glob.glob("Consolidado_renta_variable_*.xlsx"))

# Función para formatear cualquier valor numérico sin decimales
def formatear_sin_decimales(val):
    if isinstance(val, (int, float)):
        return "{:,.0f}".format(val).replace(",", ".")
    return val  # "No aplica" se deja igual

# Crear texto para título según selección y opción "Todas"
def texto_titulo_seleccion(lista, select_all, max_items=3):
    if select_all:
        return "Todo(a)s"
    elif not lista:
        return "Ninguno"
    elif len(lista) <= max_items:
        return ",\u00A0".join(lista)
    else:
        return ",\u00A0".join(lista[:max_items]) + f" +{len(lista)-max_items} más"


# @st.cache_data
# def cargar_datos(path):
#     # Extraer MMYY del nombre del archivo
#     parte_fecha = path.split('_')[-1].replace('.xlsx','')  # ej: "0925"

#     df = pd.read_excel(
#         path, 
#         sheet_name="Sheet1",
#         usecols=['Aseguradora', 'Tipo Instrumento', 'Nemotecnico', 'Unidades', 'Valor_final']
#     )
#     df.columns = df.columns.str.strip()

#     # --- Agrupar por Nemotecnico, Aseguradora y Tipo Instrumento ---
#     df_agrupado = df.groupby(
#         ['Aseguradora', 'Tipo Instrumento', 'Nemotecnico'],
#         as_index=False
#     ).agg({'Unidades':'sum', 'Valor_final':'sum'})

#     # --- Convertir Valor_final a UF según el mes ---
#     uf_mes = uf_mensual.get(parte_fecha, 1)  # default 1 si no encuentra
#     df_agrupado['Valor_final'] = df_agrupado['Valor_final'] / uf_mes

#     return df_agrupado


@st.cache_data
def cargar_datos(url): # Ahora acepta una URL
    # Extraer la fecha (MMYY) del nombre del archivo en la URL
    try:
        # Se asume que el nombre del archivo es el último segmento de la URL antes de cualquier parámetro
        nombre_archivo = url.split('/')[-1] 
        parte_fecha = nombre_archivo.replace('Consolidado_renta_variable_', '').replace('.xlsx', '')
    except:
        parte_fecha = '0000' # Respaldo

    df = pd.read_excel(
        url, # Lee directamente desde la URL
        sheet_name="Sheet1",
        usecols=['Aseguradora', 'Tipo Instrumento', 'Nemotecnico', 'Unidades', 'Valor_final']
    )
    df.columns = df.columns.str.strip()
    # --- Agrupar por Nemotecnico, Aseguradora y Tipo Instrumento ---
    df_agrupado = df.groupby(
        ['Aseguradora', 'Tipo Instrumento', 'Nemotecnico'],
        as_index=False
    ).agg({'Unidades':'sum', 'Valor_final':'sum'})

    # --- Convertir Valor_final a UF según el mes ---
    uf_mes = uf_mensual.get(parte_fecha, 1)  # default 1 si no encuentra
    df_agrupado['Valor_final'] = df_agrupado['Valor_final'] / uf_mes
    return df_agrupado


# --- Función para convertir MMYY a nombre de mes ---
def obtener_nombre_mes_desde_archivo(nombre_archivo):
    """Extrae 'MMYY' del nombre del archivo y devuelve el nombre del mes en español."""
    parte_fecha = nombre_archivo.split('_')[-1].replace('.xlsx', '')
    fecha = pd.to_datetime(parte_fecha, format='%m%y')
    nombre_mes = fecha.strftime('%B %Y').capitalize()

    # Traducir nombre del mes a español si es necesario
    meses = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    for eng, esp in meses.items():
        nombre_mes = nombre_mes.replace(eng, esp)
    return nombre_mes


# --- Cargar los archivos y obtener los nombres de mes automáticamente ---
#archivo_anterior = "Consolidado_renta_variable_1224.xlsx"
#archivo_posterior = "Consolidado_renta_variable_0925.xlsx"

#mes_anterior = obtener_nombre_mes_desde_archivo(archivo_anterior)
#mes_posterior = obtener_nombre_mes_desde_archivo(archivo_posterior)

# Usar las claves MMYY para buscar las URLs
clave_anterior = '1224'
clave_posterior = '0925'

# Obtener las URLs de descarga
archivo_anterior_url = archivos_urls.get(clave_anterior)
archivo_posterior_url = archivos_urls.get(clave_posterior)

# Obtener nombres legibles de los meses (usando las claves MMYY)
mes_anterior = pd.to_datetime(clave_anterior, format='%m%y').strftime('%B %Y').capitalize()
mes_posterior = pd.to_datetime(clave_posterior, format='%m%y').strftime('%B %Y').capitalize()

# Cargar los DataFrames usando las URLs
df_anterior = cargar_datos(archivo_anterior_url) # USAR URL
df_posterior = cargar_datos(archivo_posterior_url) # USAR URL

#df_anterior = cargar_datos(archivo_anterior)
#df_posterior = cargar_datos(archivo_posterior)

aseguradoras_filtrar = [
    '4_Life', 'Augustar', 'BICE', 'CN_Life', 'Confuturo',
    'Consorcio', 'Euroamerica', 'Metlife', 'Penta',
    'Principal', 'Renta_Nacional', 'Security'
]

df_anterior = df_anterior[df_anterior['Aseguradora'].isin(aseguradoras_filtrar)] 
df_posterior = df_posterior[df_posterior['Aseguradora'].isin(aseguradoras_filtrar)]

# Unir los DataFrames por columnas clave
df_comparacion = pd.merge(
    df_anterior, df_posterior, 
    on=['Aseguradora', 'Tipo Instrumento', 'Nemotecnico'], 
    suffixes=(f' {mes_anterior}', f' {mes_posterior}'), 
    how='outer'
)

# --- Calcular diferencias de unidades ---
def calc_dif_unidades(row):
    unidades_ant = row[f'Unidades {mes_anterior}'] if pd.notna(row[f'Unidades {mes_anterior}']) else 0
    unidades_post = row[f'Unidades {mes_posterior}'] if pd.notna(row[f'Unidades {mes_posterior}']) else 0
    return unidades_post - unidades_ant

df_comparacion['Diferencia en Unidades'] = df_comparacion.apply(calc_dif_unidades, axis=1)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Renta Variable", layout="wide")
st.title("Comparación Renta Variable")

st.subheader(f"Comparación entre {mes_anterior} y {mes_posterior}")


# Crear dos subcolumnas para los filtros
col_aseg, col_tipos = st.columns(2)

# --- Filtro local por aseguradora (no sidebar) ---
aseguradoras_disponibles_local = sorted(df_comparacion['Aseguradora'].unique())
with col_aseg:
    with st.expander("Seleccionar aseguradora(s) para la tabla", expanded=True):
        select_all_local = st.checkbox("Todas", value=True, key="check_all_aseg_local")
        aseguradoras_sel_local = []

        # Crear 4 columnas para distribuir checkboxes si la lista es larga
        cols_aseg = st.columns(3)

        if select_all_local:
            aseguradoras_sel_local = aseguradoras_disponibles_local
        else:
            for i, a in enumerate(aseguradoras_disponibles_local):
                with cols_aseg[i % 3]:
                    if st.checkbox(a, key=f"aseg_{a}_local"):
                        aseguradoras_sel_local.append(a)

# --- Filtro local por tipo de instrumento (no sidebar) ---
tipos_disponibles_local = sorted(df_comparacion['Tipo Instrumento'].unique())
with col_tipos:
    with st.expander("Seleccionar tipo(s) de instrumento para la tabla", expanded=True):
        select_all_tipos_local = st.checkbox("Todos", value=True, key="check_all_tipos_local")
        tipos_sel_local = []

        # Crear 3 columnas para distribuir checkboxes
        cols_tipos = st.columns(3)

        if select_all_tipos_local:
            tipos_sel_local = tipos_disponibles_local
        else:
            for i, t in enumerate(tipos_disponibles_local):
                with cols_tipos[i % 3]:
                    if st.checkbox(t, key=f"tipo_{t}_local"):
                        tipos_sel_local.append(t)

# --- Filtrar ---
df_filtrado = df_comparacion[
    df_comparacion['Aseguradora'].isin(aseguradoras_sel_local) &
    df_comparacion['Tipo Instrumento'].isin(tipos_sel_local)
]

# --- Revisar si hay datos después del filtro ---
if df_filtrado.empty or not aseguradoras_sel_local or not tipos_sel_local:
    st.warning("⚠️ No hay datos para mostrar. Selecciona al menos una aseguradora y un tipo de instrumento.")
else:

    df_filtrado = df_filtrado.sort_values(by=["Aseguradora", "Tipo Instrumento", "Nemotecnico"]).reset_index(drop=True)

    # Seleccionar columnas numéricas
    columnas_numericas = df_filtrado.select_dtypes(include=['int64', 'float64']).columns

    # Calcular la fila de totales
    fila_total = df_filtrado[columnas_numericas].sum()

    no_numericas = pd.Series({
        'Aseguradora': 'Totales',
        'Tipo Instrumento': '',
        'Nemotecnico': ''
    })

    fila_total = pd.concat([fila_total, no_numericas])

    # Agregar la fila al DataFrame
    df_filtrado = pd.concat([df_filtrado, pd.DataFrame([fila_total])], ignore_index=True)


    def resaltar_diferencia(val):
        if pd.notna(val) and isinstance(val, (int, float)) and val != 0:
            return 'background-color: yellow'  # resalta solo si es número distinto de 0
        return ''  # no resalta nada si es 0 o no es número


    tabla_estilizada = df_filtrado.style.map(
        resaltar_diferencia,
        subset=['Diferencia en Unidades']
        ).format(formatear_sin_decimales)


    st.dataframe(tabla_estilizada)

    df_resumen = df_comparacion[
        (df_comparacion['Diferencia en Unidades'] != 0) & 
        (df_comparacion['Diferencia en Unidades'] != "No aplica") 
    ].copy()


    # --- Seleccionar solo las columnas necesarias ---
    df_resumen = df_resumen[['Aseguradora', 'Tipo Instrumento', 'Nemotecnico', 'Diferencia en Unidades']]

    # --- Mostrar en Streamlit ---
    st.subheader(f"Resumen de cambios en unidades por Nemotécnico ({mes_anterior} vs {mes_posterior})")

    
    # Crear dos subcolumnas para los filtros
    col_aseg, col_tipos = st.columns(2)

    # --- Filtro por aseguradora para el resumen ---
    aseguradoras_disponibles_unidades = sorted(df_resumen['Aseguradora'].dropna().unique())
    with col_aseg:
        with st.expander("Seleccionar aseguradora(s) para el resumen", expanded=True):
            select_all_aseg_unidades = st.checkbox("Todas", value=True, key="check_all_aseg_unidades")
            aseguradoras_sel_unidades = []

            # Crear 4 columnas internas para distribuir las aseguradoras si la lista es larga
            cols_aseg = st.columns(3)

            if select_all_aseg_unidades:
                aseguradoras_sel_unidades = aseguradoras_disponibles_unidades
            else:
                for i, a in enumerate(aseguradoras_disponibles_unidades):
                    with cols_aseg[i % 3]:
                        if st.checkbox(a, key=f"aseg_{a}_unidades"):
                            aseguradoras_sel_unidades.append(a)

        
    # --- Filtro local por tipo de instrumento (no sidebar) ---
    tipos_disponibles_unidades = sorted(df_resumen['Tipo Instrumento'].unique())
    with col_tipos:
        with st.expander("Seleccionar tipo(s) de instrumento para el resumen", expanded=True):
            select_all_tipos_unidades = st.checkbox("Todos", value=True, key="check_all_tipos_unidades")
            tipos_sel_unidades = []

            # Crear 4 columnas para distribuir checkboxes
            cols_tipos = st.columns(3)

            if select_all_tipos_unidades:
                tipos_sel_unidades = tipos_disponibles_unidades
            else:
                for i, t in enumerate(tipos_disponibles_unidades):
                    with cols_tipos[i % 3]:
                        if st.checkbox(t, key=f"tipo_{t}_unidades"):
                            tipos_sel_unidades.append(t)


    df_resumen_filtrado = df_resumen.copy()

    # --- Aplicar filtro por aseguradora ---
    if not select_all_aseg_unidades:
        df_resumen_filtrado = df_resumen_filtrado[df_resumen_filtrado['Aseguradora'].isin(aseguradoras_sel_unidades)]
    if not select_all_tipos_unidades:
        df_resumen_filtrado = df_resumen_filtrado[df_resumen_filtrado['Tipo Instrumento'].isin(tipos_sel_unidades)]


    if df_resumen_filtrado.empty:
        st.warning("⚠️ No hay datos para mostrar en el resumen de cambios en unidades.")
    else:
        st.dataframe(
            df_resumen_filtrado.style.format({'Diferencia en Unidades': formatear_sin_decimales})
        )


    # --- Gráfico de pastel: distribución del Valor Final (UF) por tipo de instrumento ---
    st.subheader(f"Distribución del Valor Final (UF) por Tipo de Instrumento - {mes_posterior}")

    # --- Filtrar DataFrame según aseguradoras seleccionadas, excluyendo Totales ---
    df_filtrado_pie = df_comparacion[df_comparacion['Aseguradora'] != 'Totales'].copy()
    
    # --- Filtro por aseguradora para el gráfico de pastel ---
    aseguradoras_disponibles_pie = sorted([
        a for a in df_filtrado_pie['Aseguradora'].dropna().unique()
        if str(a).strip().lower() not in ['totales', 'total']
    ])
    with st.expander("Seleccionar aseguradora(s) para el gráfico", expanded=True):
        select_all_aseg_pie = st.checkbox("Todas", value=True, key="check_all_aseg_pie")
        aseguradoras_sel_pie = []

        # Crear 5 columnas internas para distribuir las aseguradoras si la lista es larga
        cols_aseg = st.columns(6)

        if select_all_aseg_pie:
            aseguradoras_sel_pie = aseguradoras_disponibles_pie
        else:
            for i, a in enumerate(aseguradoras_disponibles_pie):
                with cols_aseg[i % 6]:
                    if st.checkbox(a, key=f"aseg_{a}_pie"):
                        aseguradoras_sel_pie.append(a)

    if not select_all_aseg_pie:
        df_filtrado_pie = df_comparacion[
            (df_comparacion['Aseguradora'].isin(aseguradoras_sel_pie)) &
            (df_comparacion['Aseguradora'] != 'Totales')
        ]
    else:
        df_filtrado_pie = df_comparacion[df_comparacion['Aseguradora'] != 'Totales'].copy()


    # --- Agrupar para el gráfico ---
    df_grafico = df_filtrado_pie.groupby('Tipo Instrumento', as_index=False)[f'Valor_final {mes_posterior}'].sum()
    df_grafico['Valor_final_fmt'] = df_grafico[f'Valor_final {mes_posterior}'].apply(lambda x: f"{int(x):,}".replace(",", "."))

    # Construir título con saltos de línea HTML
    titulo_grafico = (
        f"<b>Aseguradora(s) seleccionada(s):</b> {texto_titulo_seleccion(aseguradoras_sel_pie, select_all_aseg_pie)}<br>"
    )

    st.markdown(titulo_grafico, unsafe_allow_html=True)

    fig = px.pie(
        df_grafico,  # excluye la fila total
        values=f'Valor_final {mes_posterior}',
        names='Tipo Instrumento',
        hole=0.3  # si quieres tipo "dona"
    )

    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label', 
        hovertemplate='%{label}<br>Valor Final (UF): %{customdata}<extra></extra>',
        customdata=df_grafico['Valor_final_fmt']
    )

    st.plotly_chart(fig, use_container_width=True)



    # --- Gráfico de evolución mensual del número total de unidades por tipo de instrumento ---
    st.subheader("Evolución Mensual del Número Total de Unidades por Tipo de Instrumento (Año 2025)")

    evolucion_mensual_unidades = []

    for archivo in archivos:
        # Extraer mes y año desde el nombre del archivo (ej: Consolidado_renta_variable_0925.xlsx)
        try:
            nombre = archivo.split('_')[-1].replace('.xlsx', '')
            fecha = pd.to_datetime(nombre, format='%m%y')
        except Exception:
            continue

        # Solo considerar archivos del año 2025
        if fecha.year != 2025:
            continue

        df_mes = cargar_datos(archivo)
        df_mes = df_mes[df_mes['Aseguradora'].isin(aseguradoras_filtrar)]

        # Agrupar total de unidades por tipo de instrumento
        suma_unidades = (
            df_mes.groupby(['Aseguradora', 'Tipo Instrumento'], as_index=False)['Unidades']
            .sum()
            .assign(Mes=fecha)
        )

        evolucion_mensual_unidades.append(suma_unidades)

    # Unir todos los meses
    if evolucion_mensual_unidades:
        df_evolucion = pd.concat(evolucion_mensual_unidades, ignore_index=True)
        df_evolucion['Mes'] = pd.to_datetime(df_evolucion['Mes'])
        df_evolucion = df_evolucion.sort_values('Mes')

        # --- Filtros interactivos ---
        col_aseg, col_tipos = st.columns(2)

        # Filtro por aseguradora
        aseguradoras_disponibles = sorted(df_evolucion['Aseguradora'].unique())
        with col_aseg:
            with st.expander("Seleccionar aseguradora(s)", expanded=True):
                select_all_aseg_evo = st.checkbox("Todas", value=True, key="check_all_aseg_evo")
                aseguradoras_sel_evo = []
                cols_aseg = st.columns(3)
                if select_all_aseg_evo:
                    aseguradoras_sel_evo = aseguradoras_disponibles
                else:
                    for i, a in enumerate(aseguradoras_disponibles):
                        with cols_aseg[i % 3]:
                            if st.checkbox(a, key=f"aseg_{a}_evo"):
                                aseguradoras_sel_evo.append(a)

        # --- Filtrar tipos de instrumentos según las aseguradoras seleccionadas ---
        if select_all_aseg_evo or not aseguradoras_sel_evo:
            df_filtrado_tipos = df_evolucion.copy()
        else:
            df_filtrado_tipos = df_evolucion[df_evolucion['Aseguradora'].isin(aseguradoras_sel_evo)]

        # Filtro por tipo de instrumento
        tipos_disponibles = sorted(df_filtrado_tipos['Tipo Instrumento'].unique())
        with col_tipos:
            with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
                select_all_tipos_evo = st.checkbox("Todos", value=True, key="check_all_tipos_evo")
                tipos_sel_evo = []
                cols_tipos = st.columns(3)
                if select_all_tipos_evo:
                    tipos_sel_evo = tipos_disponibles
                else:
                    for i, t in enumerate(tipos_disponibles):
                        with cols_tipos[i % 3]:
                            if st.checkbox(t, key=f"tipo_{t}_evo"):
                                tipos_sel_evo.append(t)

        # Filtrar según selección
        if not select_all_aseg_evo:
            df_evolucion = df_evolucion[df_evolucion['Aseguradora'].isin(aseguradoras_sel_evo)]
        if not select_all_tipos_evo:
            df_evolucion = df_evolucion[df_evolucion['Tipo Instrumento'].isin(tipos_sel_evo)]

        
        # Construir título con saltos de línea HTML
        titulo_grafico = (
            f"<b>Aseguradora(s) seleccionada(s):</b> {texto_titulo_seleccion(aseguradoras_sel_evo, select_all_aseg_evo)}<br>"
            f"<b>Tipo(s) de instrumento seleccionado(s):</b> {texto_titulo_seleccion(tipos_sel_evo, select_all_tipos_evo)}"
        )

        st.markdown(titulo_grafico, unsafe_allow_html=True)

        # --- Crear gráfico ---
        if not df_evolucion.empty:
            fig_evolucion = px.line(
                df_evolucion,
                x='Mes',
                y='Unidades',
                color='Aseguradora',
                line_dash='Tipo Instrumento',
                markers=True,
                labels={'Unidades': 'Número total de unidades', 'Mes': 'Mes'},
                custom_data=['Tipo Instrumento', 'Unidades']
            )

            fig_evolucion.update_traces(
                hovertemplate="<b>%{x|%b %Y}</b><br>Tipo: %{customdata[0]}<br>Unidades: %{customdata[1]:,.0f}<extra></extra>"
            )

            fig_evolucion.update_xaxes(
                tickformat="%b %Y",
                dtick="M1"
            )
            fig_evolucion.update_layout(
                xaxis_title="Mes",
                yaxis_tickformat=',.0f',
                template='plotly_white',
                legend_title_text='Tipo de Instrumento'
            )
            fig_evolucion.update_layout(separators=",.")
            fig_evolucion.update_yaxes(tickformat=",.0f")

            st.plotly_chart(fig_evolucion, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos para mostrar según los filtros seleccionados.")
    else:
        st.warning("⚠️ No se encontraron archivos válidos para generar la evolución mensual.")



    
    # --- Gráfico de evolución mensual del Valor Final por tipo de instrumento ---
    st.subheader("Evolución Mensual del Valor Final (UF) por Tipo de Instrumento (Año 2025)")

    evolucion_mensual_valor = []

    for archivo in archivos:
        # Extraer mes y año desde el nombre del archivo
        try:
            nombre = archivo.split('_')[-1].replace('.xlsx', '')
            fecha = pd.to_datetime(nombre, format='%m%y')
        except Exception:
            continue

        if fecha.year != 2025:
            continue

        df_mes = cargar_datos(archivo)
        df_mes = df_mes[df_mes['Aseguradora'].isin(aseguradoras_filtrar)]

        # Agrupar total de Valor_final por tipo de instrumento y aseguradora
        suma_valor = (
            df_mes.groupby(['Aseguradora', 'Tipo Instrumento'], as_index=False)['Valor_final']
            .sum()
            .assign(Mes=fecha)
        )

        evolucion_mensual_valor.append(suma_valor)

    # Unir todos los meses
    if evolucion_mensual_valor:
        df_evolucion_valor = pd.concat(evolucion_mensual_valor, ignore_index=True)
        df_evolucion_valor['Mes'] = pd.to_datetime(df_evolucion_valor['Mes'])
        df_evolucion_valor = df_evolucion_valor.sort_values('Mes')

        # --- Filtros interactivos ---
        col_aseg, col_tipos = st.columns(2)

        # Filtro por aseguradora
        aseguradoras_disponibles = sorted(df_evolucion_valor['Aseguradora'].unique())
        with col_aseg:
            with st.expander("Seleccionar aseguradora(s)", expanded=True):
                select_all_aseg_valor = st.checkbox("Todas", value=True, key="check_all_aseg_valor")
                aseguradoras_sel_valor = []
                cols_aseg = st.columns(3)
                if select_all_aseg_valor:
                    aseguradoras_sel_valor = aseguradoras_disponibles
                else:
                    for i, a in enumerate(aseguradoras_disponibles):
                        with cols_aseg[i % 3]:
                            if st.checkbox(a, key=f"aseg_{a}_valor"):
                                aseguradoras_sel_valor.append(a)

        # --- Filtrar tipos de instrumentos según las aseguradoras seleccionadas ---
        if select_all_aseg_valor or not aseguradoras_sel_valor:
            df_filtrado_tipos_valor = df_evolucion_valor.copy()
        else:
            df_filtrado_tipos_valor = df_evolucion_valor[df_evolucion_valor['Aseguradora'].isin(aseguradoras_sel_valor)]

        # Filtro por tipo de instrumento
        tipos_disponibles = sorted(df_filtrado_tipos_valor['Tipo Instrumento'].unique())
        with col_tipos:
            with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
                select_all_tipos_valor = st.checkbox("Todos", value=True, key="check_all_tipos_valor")
                tipos_sel_valor = []
                cols_tipos = st.columns(3)
                if select_all_tipos_valor:
                    tipos_sel_valor = tipos_disponibles
                else:
                    for i, t in enumerate(tipos_disponibles):
                        with cols_tipos[i % 3]:
                            if st.checkbox(t, key=f"tipo_{t}_valor"):
                                tipos_sel_valor.append(t)

        # Filtrar según selección
        if not select_all_aseg_valor:
            df_evolucion_valor = df_evolucion_valor[df_evolucion_valor['Aseguradora'].isin(aseguradoras_sel_valor)]
        if not select_all_tipos_valor:
            df_evolucion_valor = df_evolucion_valor[df_evolucion_valor['Tipo Instrumento'].isin(tipos_sel_valor)]

        # Construir título
        titulo_grafico = (
            f"<b>Aseguradora(s) seleccionada(s):</b> {texto_titulo_seleccion(aseguradoras_sel_valor, select_all_aseg_valor)}<br>"
            f"<b>Tipo(s) de instrumento seleccionado(s):</b> {texto_titulo_seleccion(tipos_sel_valor, select_all_tipos_valor)}"
        )
        st.markdown(titulo_grafico, unsafe_allow_html=True)

        # --- Crear gráfico ---
        if not df_evolucion_valor.empty:
            fig_evolucion_valor = px.line(
                df_evolucion_valor,
                x='Mes',
                y='Valor_final',
                color='Aseguradora',
                line_dash='Tipo Instrumento',
                markers=True,
                labels={'Valor_final': 'Valor Final (UF)', 'Mes': 'Mes'},
                custom_data=['Tipo Instrumento', 'Valor_final']
            )

            fig_evolucion_valor.update_traces(
                hovertemplate="<b>%{x|%b %Y}</b><br>Tipo: %{customdata[0]}<br>Valor Final (UF): %{customdata[1]:,.0f}<extra></extra>"
            )

            fig_evolucion_valor.update_xaxes(tickformat="%b %Y", dtick="M1")
            fig_evolucion_valor.update_layout(
                xaxis_title="Mes",
                yaxis_tickformat=',.0f',
                template='plotly_white',
                legend_title_text='Tipo de Instrumento'
            )
            fig_evolucion_valor.update_layout(separators=",.")
            fig_evolucion_valor.update_yaxes(tickformat=",.0f")

            st.plotly_chart(fig_evolucion_valor, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos para mostrar según los filtros seleccionados.")



    # --- Gráfico de barras apiladas: variación por tipo de instrumento ---
    st.subheader("Variación de Unidades (Compras y Ventas) por Tipo de Instrumento")

    
    # Crear dos subcolumnas para los filtros
    col_aseg, col_tipos = st.columns(2)

    # Expander para aseguradoras
    df_filtrado_aseg = df_comparacion[df_comparacion['Diferencia en Unidades'] != 0]
    aseguradoras_disponibles = sorted(df_filtrado_aseg['Aseguradora'].unique())
    with col_aseg:
        with st.expander("Seleccionar aseguradora(s)", expanded=True):
            # Checkbox general "Todas"
            select_all_aseg = st.checkbox("Todas", value=True, key="check_all_aseg_total")
            aseguradoras_sel = []

            cols_aseg_tabla = st.columns(3)
            if select_all_aseg:
                aseguradoras_sel = aseguradoras_disponibles # Selecciona todos
            else:
                # Distribuir los checkboxes en 3 columnas
                for i, a in enumerate(aseguradoras_disponibles):
                    with cols_aseg_tabla[i % 3]:
                        if st.checkbox(a, key=f"aseg_{a}_total"):
                            aseguradoras_sel.append(a)

    # --- Filtrar tipos de instrumentos según aseguradoras seleccionadas ---
    df_filtrado_tipos = df_comparacion[
        (df_comparacion['Diferencia en Unidades'] != 0) &
        (df_comparacion['Aseguradora'].isin(aseguradoras_sel))
    ]

    # Expander para tipos de instrumento
    tipos_disponibles = sorted(df_filtrado_tipos['Tipo Instrumento'].unique())
    with col_tipos:
        with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
            select_all_tipos = st.checkbox("Todos", value=True, key="check_all_tipos_total")
            tipos_sel = []
            col_tipos_tabla = st.columns(3)
            if select_all_tipos:
                tipos_sel = tipos_disponibles # Selecciona todos
            else:
                for i, t in enumerate(tipos_disponibles):
                    with col_tipos_tabla[i % 3]:    
                        if st.checkbox(t, key=f"tipo_{t}_total"):
                            tipos_sel.append(t)


    # Calcular variaciones de unidades entre los dos meses
    df_movimientos = df_comparacion.copy()
    df_movimientos['Diferencia en Unidades'] = (
        df_movimientos[f'Unidades {mes_posterior}'].fillna(0) -
        df_movimientos[f'Unidades {mes_anterior}'].fillna(0)
    )

    # Clasificar compra / venta
    df_movimientos['Movimiento'] = df_movimientos['Diferencia en Unidades'].apply(
        lambda x: 'Compra' if x > 0 else ('Venta' if x < 0 else 'Sin cambio')
    )

    # Filtrar solo filas relevantes
    df_movimientos = df_movimientos[
        (df_movimientos['Movimiento'] != 'Sin cambio') &
        (df_movimientos['Aseguradora'].isin(aseguradoras_sel)) &
        (df_movimientos['Tipo Instrumento'].isin(tipos_sel))
    ]

    # Agrupar por aseguradora, tipo de instrumento y tipo de movimiento
    df_resumen_mov = (
        df_movimientos
        .groupby(['Aseguradora', 'Tipo Instrumento', 'Movimiento'], as_index=False)
        .agg({'Diferencia en Unidades': 'sum'})
    )

    df_resumen_mov['Diferencia en Unidades'] = df_resumen_mov['Diferencia en Unidades'].astype(float)

    if df_resumen_mov.empty:
        st.warning("⚠️ No hay movimientos de compra o venta para mostrar.")
    else:
        # Convertir valores a texto con puntos
        df_resumen_mov['Diferencia_fmt'] = df_resumen_mov['Diferencia en Unidades'].apply(lambda x: f"{int(x):,}".replace(",", "."))

        # Construir título con saltos de línea HTML
        titulo_grafico = (
            f"<b>Período:</b> {mes_anterior} → {mes_posterior}<br>"
            f"<b>Aseguradora(s) seleccionada(s):</b> {texto_titulo_seleccion(aseguradoras_sel, select_all_aseg)}<br>"
            f"<b>Tipo(s) de instrumento seleccionado(s):</b> {texto_titulo_seleccion(tipos_sel, select_all_tipos)}"
        )

        st.markdown(titulo_grafico, unsafe_allow_html=True)


        # Gráfico de barras apiladas con Plotly
        fig_mov = px.bar(
            df_resumen_mov,
            y='Aseguradora',
            x='Diferencia en Unidades',
            color='Tipo Instrumento',
            barmode='relative',
            orientation='h', #barras horizontales
            text='Diferencia_fmt'  #
        )

        fig_mov.update_layout(
            yaxis_title="Aseguradora",
            xaxis_title="Variación en Unidades",
            legend_title="Tipo de Instrumento",
            #xaxis_tickformat=",",
            bargap=0.2,
            xaxis=dict(
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="black",
            ),
            template="plotly_white",
        )

        fig_mov.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Variación: %{text} unidades<extra></extra>"
        )
        )

        fig_mov.update_layout(separators=",.")
        fig_mov.update_xaxes(tickformat=",.0f")

        st.plotly_chart(fig_mov, use_container_width=True)


    # --- Gráfico de variaciones por Nemotécnico ---
    st.subheader("Variación de Unidades por Nemotécnico")

    # Crear dos subcolumnas para los filtros
    col_aseg, col_tipos = st.columns(2)

    # Expander para aseguradoras
    df_filtrado_aseg = df_comparacion[df_comparacion['Diferencia en Unidades'] != 0]
    aseguradoras_disponibles = sorted(df_filtrado_aseg['Aseguradora'].unique())
    with col_aseg:
        with st.expander("Seleccionar aseguradora(s)", expanded=True):
            # Checkbox general "Todas"
            select_all_aseg = st.checkbox("Todas", value=True, key="check_all_aseg_nemo")
            aseguradoras_sel = []

            # Crear 2 columnas
            cols = st.columns(3)

            if select_all_aseg:
                aseguradoras_sel = aseguradoras_disponibles # Selecciona todos
            else:
                # Distribuir los checkboxes en 2 columnas
                for i, t in enumerate(aseguradoras_disponibles):
                    with cols[i % 3]:
                        if st.checkbox(t, key=f"aseg_{t}_nemo"):
                            aseguradoras_sel.append(t)

    # --- Filtrar tipos de instrumentos según aseguradoras seleccionadas ---
    df_filtrado_tipos = df_comparacion[
        (df_comparacion['Diferencia en Unidades'] != 0) &
        (df_comparacion['Aseguradora'].isin(aseguradoras_sel))
    ]

    # Expander para tipos de instrumento
    tipos_disponibles = sorted(df_filtrado_tipos['Tipo Instrumento'].unique())
    with col_tipos:
        with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
            select_all_tipos = st.checkbox("Todos", value=True, key="check_all_tipos_nemo")
            tipos_sel = []
            cols_tipos = st.columns(3)
            if select_all_tipos:
                tipos_sel = tipos_disponibles # Selecciona todos    
            else:
                for i, t in enumerate(tipos_disponibles):
                    with cols_tipos[i % 3]:
                        if st.checkbox(t, key=f"tipo_{t}_nemo"):
                            tipos_sel.append(t)


    # Filtrar solo los que tuvieron variación real
    df_nemotecnicos = df_comparacion[
        (df_comparacion['Diferencia en Unidades'] != 0) &
        (df_comparacion['Aseguradora'].isin(aseguradoras_sel)) &
        (df_comparacion['Tipo Instrumento'].isin(tipos_sel))
    ].copy()

    # Clasificar compra/venta
    df_nemotecnicos['Movimiento'] = df_nemotecnicos['Diferencia en Unidades'].apply(
        lambda x: 'Compra' if x > 0 else 'Venta'
    )

    # Formatear texto de unidades
    df_nemotecnicos['Diferencia_fmt'] = df_nemotecnicos['Diferencia en Unidades'].apply(
        lambda x: f"{int(x):,}".replace(",", ".")
    )

    # Ordenar por magnitud de variación
    df_nemotecnicos = df_nemotecnicos.sort_values(by='Diferencia en Unidades', ascending=False)

    # Construir título con saltos de línea HTML
    titulo_grafico = (
        f"<b>Período:</b> {mes_anterior} → {mes_posterior}<br>"
        f"<b>Aseguradora(s) seleccionada(s):</b> {texto_titulo_seleccion(aseguradoras_sel, select_all_aseg)}<br>"
        f"<b>Tipo(s) de instrumento seleccionado(s):</b> {texto_titulo_seleccion(tipos_sel, select_all_tipos)}"
    )

    # Mostrar título arriba del gráfico
    st.markdown(titulo_grafico, unsafe_allow_html=True)


    # Crear gráfico
    fig_nemotecnicos = px.bar(
        df_nemotecnicos,
        y='Nemotecnico',
        x='Diferencia en Unidades',
        color='Movimiento',
        text='Diferencia_fmt',
        hover_data=['Aseguradora', 'Tipo Instrumento'],
        orientation='h',
        color_discrete_map={'Compra': '#2ca02c', 'Venta': '#d62728'},  # verde / rojo
    )

    altura = max(700, 10 * len(df_nemotecnicos))  

    fig_nemotecnicos.update_layout(
        xaxis_title="Variación en Unidades",
        yaxis_title="Nemotécnico",
        template="plotly_white",
        bargap=0.15,
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
        height=700  ##revisar altura fija porque no se ven todos los nemotécnicos
    )

    fig_nemotecnicos.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Variación: %{text} unidades<br>"
            "Aseguradora: %{customdata[0]}<br>"
            "Tipo: %{customdata[1]}<extra></extra>"
        )
    )

    fig_nemotecnicos.update_layout(separators=",.")
    fig_nemotecnicos.update_xaxes(tickformat=",.0f")

    st.plotly_chart(fig_nemotecnicos, use_container_width=True)


    # --- Gráfico Treemap: distribución de unidades ---
    st.subheader(f"Treemap de Valor Final (UF) por Aseguradora y Tipo de Instrumento - {mes_posterior}")

    # Filtrar solo datos relevantes (evitar Totales y sin movimientos)
    df_treemap = df_posterior.copy()
    df_treemap = df_treemap[df_treemap['Aseguradora'] != 'Totales']

    # Agrupar por aseguradora, tipo de instrumento y nemotécnico
    df_treemap = df_treemap.groupby(
        ['Aseguradora', 'Tipo Instrumento', 'Nemotecnico'],
        as_index=False
    ).agg({'Valor_final': 'sum'})


    # Reemplazar NaN por 0 en unidades para evitar errores
    df_treemap['Valor_final'] = df_treemap['Valor_final'].fillna(0)

    # Formatear unidades como texto
    df_treemap['Valor_final_fmt'] = df_treemap['Valor_final'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # Lista de colores tipo pastel (puedes cambiar los hex)
    colores = [
        "#8c564b",  # marrón
        "#A1C935",  # verde claro
        "#1f77b4",  # azul
        "#17becf",  # turquesa
        "#d62728",  # rojo
        "#ff7f0e",  # naranja
        "#FFD700",  # dorado
        "#9467bd",  # morado
        "#e377c2",  # rosa fuerte
        "#2ca02c",  # verde
    ]


    # Treemap
    fig_treemap = px.treemap(
        df_treemap,
        path=['Aseguradora', 'Tipo Instrumento', 'Nemotecnico'],  # jerarquía
        values='Valor_final',                       # tamaño de los bloques
        color='Aseguradora',
        color_discrete_sequence=colores 
    )

    fig_treemap.update_traces(
        hovertemplate="""
        <b>%{label}</b><br>
        Valor Final (UF): %{value:,.0f}<extra></extra>
        """
    )

    fig_treemap.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        template="plotly_white"
    )

    st.plotly_chart(fig_treemap, use_container_width=True)


    