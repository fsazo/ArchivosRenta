import pandas as pd
import streamlit as st
import plotly.express as px
import glob

GITHUB_RAW_URL_BASE = "https://raw.githubusercontent.com/fsazo/ArchivosRenta/refs/heads/main/RentaFija/ArchivosExcel/"

# Lista de identificadores MMYY
identificadores_mmyy = [
    '1224', '0125', '0225', '0325', '0425',
    '0525', '0625', '0725', '0825', '0925'
]

# GENERAR EL DICCIONARIO DE URLs automáticamente
archivos_urls = {}
for mmyy in identificadores_mmyy:
    nombre_archivo_excel = f"Consolidado_renta_fija_{mmyy}.xlsx"
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

#archivos = glob.glob("Consolidado_renta_fija_*.xlsx")
#df_list = []


@st.cache_data
def cargar_datos(url): # Ahora acepta una URL
    # Extraer la fecha (MMYY) del nombre del archivo en la URL
    try:
        # Se asume que el nombre del archivo es el último segmento de la URL antes de cualquier parámetro
        nombre_archivo = url.split('/')[-1] 
        parte_fecha = nombre_archivo.replace('Consolidado_renta_fija_', '').replace('.xlsx', '')
    except:
        parte_fecha = '0000' # Respaldo

    df = pd.read_excel(
        url, # Lee directamente desde la URL
        sheet_name="Sheet1",
        usecols=['Aseguradora','Nemotecnico','Tipo_de_instrumento','Valor_final B.1','Fecha compra']
    )
    df.columns = df.columns.str.strip()
    df['Fecha compra'] = pd.to_datetime(df['Fecha compra'], errors='coerce')
    # --- Convertir Valor_final a UF según el mes ---
    uf_mes = uf_mensual.get(parte_fecha, 1)  # default 1 si no encuentra
    df['Valor_final B.1'] = df['Valor_final B.1'] / uf_mes
    return df

# @st.cache_data
# def cargar_datos(path):
#     parte_fecha = path.split('_')[-1].replace('.xlsx', '')  # → "0925"

#     df = pd.read_excel(
#         path,
#         sheet_name="Sheet1",
#         usecols=['Aseguradora','Nemotecnico','Tipo_de_instrumento','Valor_final B.1','Fecha compra']
#     )
#     df.columns = df.columns.str.strip()
#     df['Fecha compra'] = pd.to_datetime(df['Fecha compra'], errors='coerce')
#     # --- Convertir Valor_final a UF según el mes ---
#     uf_mes = uf_mensual.get(parte_fecha, 1)  # default 1 si no encuentra
#     df['Valor_final B.1'] = df['Valor_final B.1'] / uf_mes
#     ##df.to_parquet("Consolidado_renta_fija.parquet") ###
#     return df

aseguradoras_filtrar = [
    '4_Life', 'Augustar', 'BICE', 'CN_Life', 'Confuturo',
    'Consorcio', 'Euroamerica', 'Metlife', 'Penta',
    'Principal', 'Renta_Nacional', 'Security'
]

# Diccionario de meses en español
meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

if archivos_urls:
    # Determinar el archivo más reciente (clave MMYY más alta)
    latest_mmyy = max(
        archivos_urls.keys(), 
        key=lambda mmyy: pd.to_datetime(mmyy, format='%m%y')
    )
    latest_file_url = archivos_urls[latest_mmyy] # ESTA ES LA URL COMPLETA
    df = cargar_datos(latest_file_url)
    
    # ⚠️ Definimos 'latest_file' para que el resto del código lo use.
    # Ahora contiene la URL, no la ruta local.
    latest_file = latest_file_url 

    # --- Obtener mes y año legible del archivo más reciente ---
    # nombre_archivo ya es el MMYY más reciente. Se elimina el código obsoleto con os.path.basename
    nombre_archivo = latest_mmyy 
    
    fecha_archivo = pd.to_datetime(nombre_archivo, format='%m%y', errors='coerce')
    mes_actual = meses_es.get(fecha_archivo.month, "")
    año_actual = fecha_archivo.year
    mes_titulo = f"{mes_actual} {año_actual}"

else:
    st.error("⚠️ Error: No se pudo generar la lista de URLs de archivos. Revise GITHUB_RAW_URL_BASE.")
    st.stop()



# if archivos:
#     archivos_parsed = []
#     for f in archivos:
#         mmyy = os.path.basename(f).split('_')[-1].replace('.xlsx', '')
#         fecha = pd.to_datetime(mmyy, format='%m%y', errors='coerce')
#         if pd.notna(fecha):
#             archivos_parsed.append((fecha, f))
#     if archivos_parsed:
#         latest_file = max(archivos_parsed, key=lambda x: x[0])[1]
#         df = cargar_datos(latest_file)


# # --- Obtener mes y año legible del archivo más reciente ---
# nombre_archivo = os.path.basename(latest_file).split('_')[-1].replace('.xlsx', '')
# fecha_archivo = pd.to_datetime(nombre_archivo, format='%m%y', errors='coerce')
# mes_actual = meses_es.get(fecha_archivo.month, "")
# año_actual = fecha_archivo.year
# mes_titulo = f"{mes_actual} {año_actual}"

    

df = df[df['Aseguradora'].isin(aseguradoras_filtrar)]
años_disponibles = sorted(df['Fecha compra'].dt.year.dropna().unique(), reverse=True)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Resumen Renta Fija", layout="wide")



# Filtros laterales
st.sidebar.header("Filtros")
años_disponibles = sorted(df['Fecha compra'].dt.year.dropna().unique(), reverse=True)

with st.sidebar.expander("Seleccionar fecha(s) de compra"):
    años_sel = []   
    meses_sel = []

    # Checkbox general "Todos"
    select_all_años = st.checkbox("Todos", value=True, key="check_all_años")

    if select_all_años:
        años_sel = años_disponibles.copy()
    else:
        for y in años_disponibles:
            if st.checkbox(str(y), key=f"anio_{y}"):
                años_sel.append(y)

                # Mostrar meses solo para años seleccionados individualmente
                df_meses = df[df['Fecha compra'].dt.year == y]
                meses_disponibles = sorted(df_meses['Fecha compra'].dt.month.unique())
                for mes in meses_disponibles:
                    nombre_mes = meses_es[mes]
                    col1, col2 = st.columns([0.1, 0.9])  # agrega un margen visual
                    with col2:
                        if st.checkbox(f" {nombre_mes}", key=f"mes_{y}_{mes}"):
                            meses_sel.append(f"{y}-{mes:02d}")

# --- Filtrar DataFrame según los filtros ---
if años_sel != "Todos":
    df = df[df['Fecha compra'].dt.year.isin(años_sel)]

if meses_sel:
    df = df[df['Fecha compra'].dt.strftime('%Y-%m').isin(meses_sel)]

# --- Crear tabla dinámica ---

st.title("Resumen Renta Fija en UF")

# --- Filtro por aseguradora (en la página, no sidebar) ---
aseguradoras_disponibles_tabla = sorted(df['Aseguradora'].dropna().unique())
with st.expander("Seleccionar aseguradora(s) para la tabla", expanded=True):
    select_all_aseg_tabla = st.checkbox("Todas", value=True, key="check_all_aseg_tabla")
    aseguradoras_sel_tabla = []

    cols_aseg_tabla = st.columns(4)
    if select_all_aseg_tabla:
        aseguradoras_sel_tabla = aseguradoras_disponibles_tabla
    else:
        for i, a in enumerate(aseguradoras_disponibles_tabla):
            with cols_aseg_tabla[i % 4]:
                if st.checkbox(a, key=f"aseg_{a}_tabla"):
                    aseguradoras_sel_tabla.append(a)

# --- Filtrar DataFrame según las aseguradoras seleccionadas ---
if select_all_aseg_tabla or not aseguradoras_sel_tabla:
    df_tabla = df.copy()
else:
    df_tabla = df[df['Aseguradora'].isin(aseguradoras_sel_tabla)]

# Construir título con saltos de línea HTML
titulo_grafico = (
    f"<b>Aseguradora(s) seleccionada(s):</b> {', '.join(aseguradoras_sel_tabla) if not select_all_aseg_tabla else 'Todas'}<br>"
)

# Mostrar título arriba del gráfico
st.markdown(titulo_grafico, unsafe_allow_html=True)


tabla = df_tabla.groupby(['Aseguradora','Tipo_de_instrumento'])['Valor_final B.1'].sum().unstack(fill_value=0)
tabla['Total Aseguradora'] = tabla.sum(axis=1)

# Total general y porcentaje
if not tabla.empty:
    total_general = tabla.sum(axis=0).to_frame().T
    total_general.index = ['TOTAL GENERAL']
    tabla = pd.concat([tabla, total_general])

    total_global = tabla.loc['TOTAL GENERAL', 'Total Aseguradora']
    fila_porcentaje = (tabla / total_global) * 100
    fila_porcentaje = fila_porcentaje.loc['TOTAL GENERAL']
    fila_porcentaje.name = '% del Total'
    tabla = pd.concat([tabla, pd.DataFrame([fila_porcentaje])])

    # Formatear
    def formatear_valor(x):
        if isinstance(x, (int, float)):
            return f"{x:,.0f}".replace(",", ".")
        return x
    
    tabla_formateada = tabla.copy()

    # Separar valores y porcentaje
    valores = tabla_formateada.iloc[:-1].map(lambda x: f"{int(x):,.0f}".replace(",", "."))
    porcentaje = tabla_formateada.iloc[-1].apply(lambda x: f"{x:.2f}%")

    # Unir
    tabla_formateada = pd.concat([valores, pd.DataFrame([porcentaje], index=['% del Total'])])
    st.dataframe(tabla_formateada, width='stretch')
else:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")


# --- Crear gráfico de torta del valor final según tipo de instrumento ---

st.subheader(f"Distribución del Valor Final por Tipo de Instrumento")

# --- Filtro por aseguradora (en la página, no sidebar) ---
aseguradoras_disponibles_torta = sorted(df['Aseguradora'].dropna().unique())
with st.expander("Seleccionar aseguradora(s)", expanded=True):
    select_all_aseg_torta = st.checkbox("Todas", value=True, key="check_all_aseg_torta")
    aseguradoras_sel_torta = []

    cols_aseg_torta = st.columns(4)
    if select_all_aseg_torta:
        aseguradoras_sel_torta = aseguradoras_disponibles_torta
    else:
        for i, a in enumerate(aseguradoras_disponibles_torta):
            with cols_aseg_torta[i % 4]:
                if st.checkbox(a, key=f"aseg_{a}_torta"):
                    aseguradoras_sel_torta.append(a)

# --- Filtrar DataFrame según las aseguradoras seleccionadas ---
if select_all_aseg_torta or not aseguradoras_sel_torta:
    df_filtrado_torta = df.copy()
else:
    df_filtrado_torta = df[df['Aseguradora'].isin(aseguradoras_sel_torta)]

# --- Crear gráfico de torta ---
if not df_filtrado_torta.empty:
    # Agrupar y sumar los valores finales por tipo de instrumento
    df_pie = (
        df_filtrado_torta.groupby('Tipo_de_instrumento')['Valor_final B.1']
        .sum()
        .reset_index()
    )

    df_pie['Valor Final UF'] = df_pie['Valor_final B.1']

    # Construir título con saltos de línea HTML
    titulo_grafico = (
        f"<b>Aseguradora(s) seleccionada(s):</b> {', '.join(aseguradoras_sel_torta) if not select_all_aseg_torta else 'Todas'}<br>"
    )

    # Mostrar título arriba del gráfico
    st.markdown(titulo_grafico, unsafe_allow_html=True)

    fig = px.pie(
        df_pie,
        values='Valor Final UF',
        names='Tipo_de_instrumento',
        hole=0.3,  # tipo dona
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{customdata} UF<br>%{percent:.2%}<extra></extra>',
        customdata=[f"{v:,.0f}".replace(",", ".") for v in df_pie['Valor Final UF']]
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No hay datos para las aseguradoras seleccionadas en el gráfico de torta.")


# --- Crear tabla resumen con las columnas deseadas ---
st.subheader("Detalle de Valores Finales por Nemotécnico")

tabla_resumen = df[['Aseguradora', 'Tipo_de_instrumento', 'Nemotecnico', 'Valor_final B.1']].copy()

# Crear dos subcolumnas para los filtros
col_aseg, col_tipos = st.columns(2)

# --- Filtro por aseguradora (local, no sidebar) ---
aseguradoras_disponibles_tabla = sorted(tabla_resumen['Aseguradora'].dropna().unique())

with col_aseg:
    with st.expander("Seleccionar aseguradora(s)", expanded=True):
        select_all_aseg_tabla = st.checkbox("Todas", value=True, key="check_all_aseg_tabla_nemo")
        aseguradoras_sel_tabla = []

        cols_aseg_tabla = st.columns(3)
        if select_all_aseg_tabla:
            aseguradoras_sel_tabla = aseguradoras_disponibles_tabla
        else:
            for i, a in enumerate(aseguradoras_disponibles_tabla):
                with cols_aseg_tabla[i % 3]:
                    if st.checkbox(a, key=f"aseg_{a}_tabla_nemo"):
                        aseguradoras_sel_tabla.append(a)

# --- Aplicar filtro por aseguradora ---
if aseguradoras_sel_tabla and not select_all_aseg_tabla:
    tabla_resumen = tabla_resumen[tabla_resumen['Aseguradora'].isin(aseguradoras_sel_tabla)]


# --- Filtro adicional por tipo de instrumento ---
tipos_disponibles_tabla = sorted(tabla_resumen['Tipo_de_instrumento'].dropna().astype(str).unique())
with col_tipos:
    with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
        select_all_tipos_tabla = st.checkbox("Todos", value=True, key="check_all_tipos_tabla")
        tipos_sel_tabla = []

        # Crear 6 columnas
        cols = st.columns(3)

        if select_all_tipos_tabla:
            tipos_sel_tabla = tipos_disponibles_tabla  # Selecciona todos
        else:
            # Distribuir los checkboxes en 3 columnas
            for i, t in enumerate(tipos_disponibles_tabla):
                with cols[i % 3]:
                    if st.checkbox(t, key=f"tipo_{t}_tabla"):
                        tipos_sel_tabla.append(t)

# Aplicar filtro a la tabla
if tipos_sel_tabla and not select_all_tipos_tabla:
    tabla_resumen = tabla_resumen[tabla_resumen['Tipo_de_instrumento'].astype(str).isin(tipos_sel_tabla)]

# Renombrar columnas para mayor claridad
tabla_resumen.columns = ['Aseguradora', 'Tipo de Instrumento', 'Nemotécnico', 'Valor Final UF']
tabla_resumen['Valor Final UF'] = tabla_resumen['Valor Final UF'].apply(lambda x: f"{x:,.0f}".replace(",", "."))


# Construir título con saltos de línea HTML
titulo_grafico = (
    f"<b>Aseguradora(s) seleccionada(s):</b> {', '.join(aseguradoras_sel_tabla) if not select_all_aseg_tabla else 'Todas'}<br>"
    f"<b>Tipo(s) de instrumento seleccionado(s):</b> {', '.join(tipos_sel_tabla) if not select_all_tipos_tabla else 'Todos'}"
)

# Mostrar título arriba del gráfico
st.markdown(titulo_grafico, unsafe_allow_html=True)

# Mostrar la tabla en Streamlit
st.dataframe(tabla_resumen, width='stretch')


## --- Gráfico de suma de valores finales por tipo de instrumento ---

st.subheader("Evolución Mensual del Valor Final Total por Tipo de Instrumento (Año 2025)")

# Crear dos subcolumnas para los filtros
col_aseg, col_tipos = st.columns(2)

# --- Filtro por aseguradora (en la página, no sidebar) ---
aseguradoras_disponibles_graf = sorted(df['Aseguradora'].dropna().unique())
with col_aseg:
    with st.expander("Seleccionar aseguradora(s)", expanded=True):
        select_all_aseg = st.checkbox("Todas", value=True, key="check_all_aseg_evolucion")
        aseguradoras_sel_graf = []

        cols_aseg = st.columns(3)
        if select_all_aseg:
            aseguradoras_sel_graf = aseguradoras_disponibles_graf
        else:
            for i, a in enumerate(aseguradoras_disponibles_graf):
                with cols_aseg[i % 3]:
                    if st.checkbox(a, key=f"aseg_{a}_evolucion"):
                        aseguradoras_sel_graf.append(a)


# --- Filtrar tipos de instrumentos según las aseguradoras seleccionadas ---
if select_all_aseg or not aseguradoras_sel_graf:
    df_filtrado_tipos = df.copy()
else:
    df_filtrado_tipos = df[df['Aseguradora'].isin(aseguradoras_sel_graf)]


# --- Filtro por tipo de instrumento en la página (no sidebar) ---
tipos_disponibles = sorted(df_filtrado_tipos['Tipo_de_instrumento'].dropna().unique())
with col_tipos:
    with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
        select_all_tipos = st.checkbox("Todos", value=True, key="check_all_tipos_evolucion")
        tipos_sel = []

        # Crear 6 columnas
        cols = st.columns(3)

        if select_all_tipos:
            tipos_sel = tipos_disponibles  # Selecciona todos
        else:
            # Distribuir los checkboxes en 6 columnas
            for i, t in enumerate(tipos_disponibles):
                with cols[i % 3]:
                    if st.checkbox(t, key=f"tipo_{t}_evolucion"):
                        tipos_sel.append(t)


evolucion_mensual_tipo = []

for archivo in archivos:
    # Extraer mes y año del archivo (asumiendo formato: Consolidado_renta_fija_MMYY.xlsx)
    nombre = archivo.split('_')[-1].replace('.xlsx', '')
    fecha = pd.to_datetime(nombre, format='%m%y')
    
    # Solo considerar archivos del año 2025
    if fecha.year != 2025:
        continue
    
    df_archivo = cargar_datos(archivo)
    df_archivo = df_archivo[df_archivo['Aseguradora'].isin(aseguradoras_filtrar)]

    # --- Aplicar filtros de sidebar sobre este Excel ---
    if años_sel != "Todos":
        df_archivo = df_archivo[df_archivo['Fecha compra'].dt.year.isin(años_sel)]
    if meses_sel:
        df_archivo = df_archivo[df_archivo['Fecha compra'].dt.strftime('%Y-%m').isin(meses_sel)]
    if not select_all_aseg:
        df_archivo = df_archivo[df_archivo['Aseguradora'].isin(aseguradoras_sel_graf)]
    if tipos_sel and not select_all_tipos:
        df_archivo = df_archivo[df_archivo['Tipo_de_instrumento'].isin(tipos_sel)]
    
    #df_list.append(df_archivo)
    # Extraer el mes y año del archivo (asumiendo formato: Consolidado_renta_fija_MMYY.xlsx)
    df_archivo['Mes'] = fecha
    
    # Agrupar por tipo de instrumento y sumar el valor final
    suma_por_tipo = df_archivo.groupby(['Tipo_de_instrumento', 'Aseguradora'])['Valor_final B.1'].sum().reset_index()
    suma_por_tipo['Mes'] = fecha

    for _, row in suma_por_tipo.iterrows():
        evolucion_mensual_tipo.append({
            'Mes': fecha,
            'Tipo_de_instrumento': row['Tipo_de_instrumento'],
            'Aseguradora': row['Aseguradora'],
            'Valor_final B.1': row['Valor_final B.1']
        })

# Crear DataFrame de evolución mensual
df_evolucion_mensual_tipo = pd.DataFrame(evolucion_mensual_tipo)

if not df_evolucion_mensual_tipo.empty:
    # Asegurarse que 'Mes' sea datetime
    df_evolucion_mensual_tipo['Mes'] = pd.to_datetime(df_evolucion_mensual_tipo['Mes'], errors='coerce')
    df_evolucion_mensual_tipo = df_evolucion_mensual_tipo.dropna(subset=['Mes'])
    
    if not df_evolucion_mensual_tipo.empty:
        df_evolucion_mensual_tipo = df_evolucion_mensual_tipo.sort_values('Mes')
        df_evolucion_mensual_tipo['Valor_fmt'] = df_evolucion_mensual_tipo['Valor_final B.1'].apply(lambda x: formatear_valor(x))

        # Construir título con saltos de línea HTML
        titulo_grafico = (
            f"<b>Aseguradora(s):</b> {', '.join(aseguradoras_sel_graf) if not select_all_aseg else 'Todas'}<br>"
            f"<b>Tipo(s) de instrumento:</b> {', '.join(tipos_sel) if not select_all_tipos else 'Todos'}"
        )

        # Mostrar título arriba del gráfico
        st.markdown(titulo_grafico, unsafe_allow_html=True)


        fig = px.line(
            df_evolucion_mensual_tipo,
            x='Mes',
            y='Valor_final B.1',
            color='Aseguradora',
            line_dash='Tipo_de_instrumento',
            markers=True,
            labels={'Valor_final B.1': 'Valor Final (UF)', 'Mes': 'Mes'},
            custom_data=['Valor_fmt', 'Aseguradora', 'Tipo_de_instrumento']
        )

        fig.update_traces(hovertemplate="<b>%{x|%b %Y}</b><br>Aseguradora: %{customdata[1]}<br>Tipo de instrumento: %{customdata[2]}<br>Valor Final: %{customdata[0]} UF<extra></extra>")

        # Formatear ticks como "Ene 2025", "Feb 2025", etc.
        fig.update_xaxes(
            tickformat="%b %Y",
            dtick="M1",  # mostrar cada mes
        )
        
        fig.update_layout(
            xaxis_title="Mes",
            yaxis_tickformat=',.0f',
            template='plotly_white',
            legend_title_text='Tipo de Instrumento',
        )

        # Usar coma como separador decimal y punto como separador de miles
        fig.update_layout(separators=",.")
        # Asegurar formato de ticks numéricos en el eje Y con separador de miles (puntos)
        fig.update_yaxes(tickformat=",.0f")

        st.plotly_chart(fig, use_container_width=True)
    else:
     
        st.warning("⚠️ No hay datos para el gráfico de evolución según los filtros seleccionados.")
else:
    st.warning("⚠️ No hay datos para el gráfico de evolución según los filtros seleccionados.")


# --- Gráfico de barras apiladas del Valor Final por Aseguradora y Tipo de Instrumento ---

st.subheader("Composición del Valor Final por Aseguradora y Tipo de Instrumento")

# Partir del df filtrado por sidebar
df_filtrado_barras = df.copy()


# --- Filtro adicional por tipo de instrumento (propio del gráfico) ---
tipos_disponibles_barras = sorted(df_filtrado_barras['Tipo_de_instrumento'].dropna().astype(str).unique())

with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
    select_all_tipos_barras = st.checkbox("Todos", value=True, key="check_all_tipos_barras")
    tipos_sel_barras = []

    # Crear 6 columnas para organizar los checkboxes
    cols = st.columns(6)

    if select_all_tipos_barras:
        tipos_sel_barras = tipos_disponibles_barras  # Selecciona todos
    else:
        # Distribuir los checkboxes en columnas
        for i, t in enumerate(tipos_disponibles_barras):
            with cols[i % 6]:
                if st.checkbox(t, key=f"tipo_{t}_barras"):
                    tipos_sel_barras.append(t)

# Aplicar filtro de tipo de instrumento
if tipos_sel_barras and not select_all_tipos_barras:
    df_filtrado_barras = df_filtrado_barras[df_filtrado_barras['Tipo_de_instrumento'].astype(str).isin(tipos_sel_barras)]


if not df_filtrado_barras.empty:
    # Agrupar y convertir a miles de pesos (o UF, según prefieras)
    df_barras_apiladas = (
        df_filtrado_barras.groupby(['Aseguradora', 'Tipo_de_instrumento'])['Valor_final B.1']
        .sum()
        .reset_index()
    )

    # Convertir a miles de pesos (si tus valores están en pesos)
    df_barras_apiladas['Valor Final (UF)'] = df_barras_apiladas['Valor_final B.1'] 

    # Crear gráfico de barras apiladas
    fig_barras_apiladas = px.bar(
        df_barras_apiladas,
        y='Aseguradora',
        x='Valor Final (UF)',
        color='Tipo_de_instrumento',
        barmode='stack',  # Apiladas
        orientation='h',
        labels={
            'Valor Final (UF)': 'Valor Final (en UF)',
            'Aseguradora': 'Aseguradora',
            'Tipo_de_instrumento': 'Tipo de Instrumento'
        },
    )

    fig_barras_apiladas.update_layout(
        template='plotly_white',
        xaxis_tickangle=-30,
        legend_title_text='Tipo de Instrumento',
        yaxis_tickformat=',.0f'
    )

    fig_barras_apiladas.update_layout(separators=",.")
    fig_barras_apiladas.update_xaxes(tickformat=",.0f")

    st.plotly_chart(fig_barras_apiladas, use_container_width=True)

else:
    st.warning("⚠️ No hay datos para mostrar el gráfico de barras según los filtros seleccionados.")


# --- Gráfico de barras apiladas: variación por tipo de instrumento ---
st.subheader("Variación de Valor Final en UF (Compras y Ventas) por Tipo de Instrumento")

# Seleccionar los dos archivos más recientes para comparar
if len(archivos) < 2:
    st.warning("⚠️ Se necesitan al menos dos archivos mensuales para comparar compras y ventas.")
else:
    # Ordenar los archivos por fecha en el nombre
    #archivos_ordenados = sorted(archivos, key=lambda x: pd.to_datetime(x.split('_')[-1].replace('.xlsx', ''), format='%m%y'))
    #archivo_anterior, archivo_posterior = archivos_ordenados[-2], archivos_ordenados[-1]

    # Crear un diccionario de archivos por fecha
    archivos_dict = {
        pd.to_datetime(a.split('_')[-1].replace('.xlsx',''), format='%m%y'): a
        for a in archivos
    }

    # Definir meses deseados
    fecha_inicio = pd.Timestamp(year=2024, month=12, day=1)  # dic 2024
    fecha_fin = pd.Timestamp(year=2025, month=9, day=1)       # sept 2025

    # Obtener archivos correspondientes
    archivo_anterior = archivos_dict.get(fecha_inicio)
    archivo_posterior = archivos_dict.get(fecha_fin)

    # Obtener nombres legibles de los meses
    mes_anterior = pd.to_datetime(archivo_anterior.split('_')[-1].replace('.xlsx', ''), format='%m%y').strftime('%b %Y')
    mes_posterior = pd.to_datetime(archivo_posterior.split('_')[-1].replace('.xlsx', ''), format='%m%y').strftime('%b %Y')


    # Cargar ambos archivos
    df_anterior = cargar_datos(archivo_anterior)
    df_posterior = cargar_datos(archivo_posterior)

    # Filtrar aseguradoras relevantes
    df_anterior = df_anterior[df_anterior['Aseguradora'].isin(aseguradoras_filtrar)]
    df_posterior = df_posterior[df_posterior['Aseguradora'].isin(aseguradoras_filtrar)]

    # --- Agrupar antes del merge ---
    df_anterior_sum = df_anterior.groupby(['Aseguradora', 'Nemotecnico', 'Tipo_de_instrumento'], as_index=False)[
        'Valor_final B.1'
    ].sum()

    df_posterior_sum = df_posterior.groupby(['Aseguradora', 'Nemotecnico', 'Tipo_de_instrumento'], as_index=False)[
        'Valor_final B.1'
    ].sum()

    # --- Unir ambos DataFrames por Aseguradora + Nemotécnico ---
    df_comparacion = pd.merge(
        df_anterior_sum,
        df_posterior_sum,
        on=['Aseguradora', 'Nemotecnico', 'Tipo_de_instrumento'],
        how='outer',
        suffixes=(f'_{mes_anterior}', f'_{mes_posterior}')
    )

    # Reemplazar NaN con 0 en los valores finales
    df_comparacion['Valor_final B.1_' + mes_anterior] = df_comparacion['Valor_final B.1_' + mes_anterior].fillna(0)
    df_comparacion['Valor_final B.1_' + mes_posterior] = df_comparacion['Valor_final B.1_' + mes_posterior].fillna(0)

    # Calcular la diferencia de valor final
    df_comparacion['Diferencia'] = df_comparacion['Valor_final B.1_' + mes_posterior] - df_comparacion['Valor_final B.1_' + mes_anterior]

    # Clasificar como Compra / Venta / Sin cambio
    df_comparacion['Movimiento'] = df_comparacion['Diferencia'].apply(
        lambda x: 'Compra' if x > 0 else ('Venta' if x < 0 else 'Sin cambio')
    )

    # Eliminar los que no tuvieron variación
    df_comparacion = df_comparacion[df_comparacion['Movimiento'] != 'Sin cambio']

    # --- Filtros en página ---
    aseguradoras_disp = sorted(df_comparacion['Aseguradora'].unique())
    tipos_disp = sorted(df_comparacion['Tipo_de_instrumento'].unique())

    # Crear dos subcolumnas para los filtros
    col_aseg, col_tipos = st.columns(2)

    with col_aseg:
        with st.expander("Seleccionar aseguradora(s)", expanded=True):
            select_all_aseg = st.checkbox("Todas", value=True, key="check_all_aseg_mov")
            cols_aseg = st.columns(3)
            aseguradoras_sel = []
            if select_all_aseg:
                aseguradoras_sel = aseguradoras_disp
            else:
                for i, a in enumerate(aseguradoras_disp):
                    with cols_aseg[i % 3]:
                        if st.checkbox(a, key=f"aseg_mov_{a}"):
                            aseguradoras_sel.append(a)

    with col_tipos:
        with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
            select_all_tipos = st.checkbox("Todos", value=True, key="check_all_tipos_mov")
            cols_tipos = st.columns(3)
            tipos_sel = []
            if select_all_tipos:
                tipos_sel = tipos_disp
            else:
                for i, t in enumerate(tipos_disp):
                    with cols_tipos[i % 3]:
                        if st.checkbox(t, key=f"tipo_mov_{t}"):
                            tipos_sel.append(t)

    # --- Aplicar filtros ---
    df_filtrado = df_comparacion[
        df_comparacion['Aseguradora'].isin(aseguradoras_sel) &
        df_comparacion['Tipo_de_instrumento'].isin(tipos_sel)
    ]

    if df_filtrado.empty:
        st.warning("⚠️ No hay movimientos de compra o venta para los filtros seleccionados.")
    else:
        # Agrupar por aseguradora, tipo y movimiento
        df_resumen = (
            df_filtrado
            .groupby(['Aseguradora', 'Tipo_de_instrumento', 'Movimiento'], as_index=False)
            .agg({'Diferencia': 'sum'})
        )

        # Dar formato de texto
        df_resumen['Diferencia_fmt'] = df_resumen['Diferencia'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        # --- Título dinámico ---
        titulo_grafico = (
            f"<b>Período:</b> {mes_anterior} → {mes_posterior}<br>"
            f"<b>Aseguradora(s):</b> {', '.join(aseguradoras_sel) if not select_all_aseg else 'Todas'}<br>"
            f"<b>Tipo(s) de instrumento:</b> {', '.join(tipos_sel) if not select_all_tipos else 'Todos'}"
        )
        st.markdown(titulo_grafico, unsafe_allow_html=True)


        # Mostrar gráfico
        fig_var = px.bar(
            df_resumen,
            y='Aseguradora',
            x='Diferencia',
            color='Tipo_de_instrumento',
            orientation='h',
            barmode='relative',
            text='Diferencia_fmt',
            labels={
                'Diferencia': 'Variación (UF)',
                'Aseguradora': 'Aseguradora',
            },
        )

        fig_var.update_layout(
            template="plotly_white",
            xaxis_title="Variación en UF (Compras ↑ / Ventas ↓)",
            yaxis_title="Aseguradora",
            legend_title="Tipo de Instrumento",
            xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black")
        )

        fig_var.update_layout(separators=",.")
        fig_var.update_xaxes(tickformat=",.0f")

        fig_var.update_traces(
            hovertemplate="<b>%{y}</b><br>Tipo: %{customdata[0]}<br>Variación: %{text} UF<extra></extra>",
            customdata=df_resumen[['Tipo_de_instrumento']]
        )


        st.plotly_chart(fig_var, use_container_width=True)


# --- Gráfico de variaciones de Valor Final por Nemotécnico ---
st.subheader("Variación de Valor Final (en UF) por Nemotécnico")

# Crear dos subcolumnas para los filtros
col_aseg, col_tipos = st.columns(2)

# --- Filtro por aseguradora ---
aseguradoras_disp = sorted(df_comparacion['Aseguradora'].dropna().unique())
with col_aseg:
    with st.expander("Seleccionar aseguradora(s)", expanded=True):
        select_all_aseg = st.checkbox("Todas", value=False, key="check_all_aseg_nemotec")
        aseguradoras_sel = []

        cols_aseg = st.columns(3)
        if select_all_aseg:
            aseguradoras_sel = aseguradoras_disp
        else:
            for i, a in enumerate(aseguradoras_disp):
                with cols_aseg[i % 3]:
                    if st.checkbox(a, key=f"aseg_{a}_nemotec"):
                        aseguradoras_sel.append(a)

# --- Determinar tipos disponibles según aseguradora seleccionada ---
if aseguradoras_sel:
    tipos_disp = sorted(
        df_comparacion[df_comparacion['Aseguradora'].isin(aseguradoras_sel)]['Tipo_de_instrumento']
        .dropna()
        .unique()
    )
else:
    tipos_disp = sorted(df_comparacion['Tipo_de_instrumento'].dropna().unique())

with col_tipos:
    with st.expander("Seleccionar tipo(s) de instrumento", expanded=True):
        select_all_tipos = st.checkbox("Todos", value=False, key="check_all_tipo_nemotec")
        tipos_sel = []

        cols_tipos = st.columns(3)
        if select_all_tipos:
            tipos_sel = tipos_disp
        else:
            for i, t in enumerate(tipos_disp):
                with cols_tipos[i % 3]:
                    if st.checkbox(t, key=f"tipo_{t}_nemotec"):
                        tipos_sel.append(t)

# --- Validar selección obligatoria ---
if not aseguradoras_sel or not tipos_sel:
    st.warning("⚠️ Debes seleccionar al menos una aseguradora y un tipo de instrumento.")
else:
    # --- Filtrar según selección ---
    df_plot = df_comparacion[
        df_comparacion['Aseguradora'].isin(aseguradoras_sel) &
        df_comparacion['Tipo_de_instrumento'].isin(tipos_sel)
    ]

    # --- Agrupar por Nemotécnico y Aseguradora para sumar valores por período ---
    df_plot_sumado = (
        df_plot.groupby(['Nemotecnico', 'Aseguradora', 'Tipo_de_instrumento'])
        [[f'Valor_final B.1_{mes_anterior}', f'Valor_final B.1_{mes_posterior}']]
        .sum()
        .reset_index()
    )


    df_plot_sumado['Diferencia UF'] = (
        df_plot_sumado[f'Valor_final B.1_{mes_posterior}'] -
        df_plot_sumado[f'Valor_final B.1_{mes_anterior}']
    )

    # Clasificar Compra / Venta
    df_plot_sumado['Movimiento'] = df_plot_sumado['Diferencia UF'].apply(lambda x: 'Compra' if x > 0 else 'Venta')

    # Ordenar y limitar Top 50
    df_plot = df_plot_sumado.sort_values(by='Diferencia UF', ascending=False).head(50)

    # Formato texto
    df_plot['Diferencia_fmt'] = df_plot['Diferencia UF'].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # --- Ordenar Nemotécnicos de mayor a menor diferencia ---
    nemos_ordenados = df_plot.sort_values('Diferencia UF', ascending=False)['Nemotecnico']

    # --- Título dinámico ---
    titulo_grafico = (
        f"<b>Período:</b> {mes_anterior} → {mes_posterior}<br>"
        f"<b>Aseguradora(s):</b> {', '.join(aseguradoras_sel) if not select_all_aseg else 'Todas'}<br>"
        f"<b>Tipo(s) de instrumento:</b> {', '.join(tipos_sel) if not select_all_tipos else 'Todos'}"
    )
    st.markdown(titulo_grafico, unsafe_allow_html=True)



    # Crear gráfico
    fig_nemotecnicos_valor = px.bar(
        df_plot,
        y='Nemotecnico',
        x='Diferencia UF',
        color='Movimiento',
        text='Diferencia_fmt',
        hover_data=['Aseguradora', 'Tipo_de_instrumento'],
        orientation='h',
        color_discrete_map={'Compra': '#2ca02c', 'Venta': '#d62728'},
        height=max(400, 25 * len(df_plot)),
        category_orders={"Nemotecnico": list(nemos_ordenados)}
    )

    fig_nemotecnicos_valor.update_layout(
        xaxis_title="Variación en Valor Final (UF)",
        yaxis_title="Nemotécnico",
        template="plotly_white",
        bargap=0.15,
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black")
    )

    fig_nemotecnicos_valor.update_layout(separators=",.")
    fig_nemotecnicos_valor.update_xaxes(tickformat=",.0f")

    st.plotly_chart(fig_nemotecnicos_valor, use_container_width=True)


# --- Gráfico Treemap del Valor Final por Aseguradora y Tipo de Instrumento ---
st.subheader("Treemap del Valor Final en UF por Aseguradora y Tipo de Instrumento")

# Filtrar solo datos de septiembre 2025
if not df.empty:
    # Agrupar por aseguradora y tipo de instrumento
    df_treemap = (
        df.groupby(['Aseguradora', 'Tipo_de_instrumento'], as_index=False)['Valor_final B.1']
        .sum()
        .rename(columns={'Valor_final B.1': 'Valor Final UF'})
    )

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

    
    #Crear treemap
    fig_treemap = px.treemap(
        df_treemap,
        path=['Aseguradora', 'Tipo_de_instrumento'],
        values='Valor Final UF',
        color='Aseguradora',
        color_discrete_sequence=colores,
    )

    
    # Ajustes visuales
    fig_treemap.update_traces(
        hovertemplate="<b>%{label}</b><br>Valor Final: %{value:,.0f} UF<extra></extra>",
        marker=dict(
        root=dict(
            # Puedes usar 'lightgrey' o cualquier color para el botón de 'Volver'
            color="lightgrey" 
        )
    )
    )

    fig_treemap.update_layout(
        template='plotly_white',
        margin=dict(t=30, l=0, r=0, b=0),
    )

    st.plotly_chart(fig_treemap, use_container_width=True)
else:
    st.warning("⚠️ No hay datos disponibles para generar el treemap.")




