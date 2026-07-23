# app.py
# ================================================================================
#                            H Y D R O   D O M U S   P Y
# ================================================================================
#                    Análisis Hidráulico para Redes Internas
#                          Interfaz Web con Streamlit
# ================================================================================
#                               Versión 1.0.0 - Web
#                          (Interfaz con Sidebar y Flujo Guiado)
# ================================================================================

import streamlit as st
import tempfile
import os
import json
import base64
import datetime
import pandas as pd
import numpy as np
import networkx as nx
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ================================================================================
# CONFIGURACIÓN DE PÁGINA - STREAMLIT
# ================================================================================
st.set_page_config(
    page_title="Hydro Domus Py - Análisis Hidráulico",
    page_icon="💧",
    layout="wide"
)

# ================================================================================
# CONFIGURACIÓN DE UNIDADES DE DIBUJO
# ================================================================================
UNIDADES_DIBUJO = {
    "mm": {"nombre": "Milímetros", "factor": 1000, "icono": "📏"},
    "cm": {"nombre": "Centímetros", "factor": 100, "icono": "📐"},
    "m": {"nombre": "Metros", "factor": 1, "icono": "📏"},
    "in": {"nombre": "Pulgadas", "factor": 0.0254, "icono": "📐"},
    "ft": {"nombre": "Pies", "factor": 0.3048, "icono": "📏"},
}

# ================================================================================
# INICIALIZAR ESTADO DE SESIÓN
# ================================================================================
if 'red' not in st.session_state:
    st.session_state.red = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'presion_entrada' not in st.session_state:
    st.session_state.presion_entrada = 15.0
if 'tipo_ocupacion' not in st.session_state:
    st.session_state.tipo_ocupacion = "Vivienda Unifamiliar"
if 'diametro_maximo' not in st.session_state:
    st.session_state.diametro_maximo = None
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'unidad_dibujo' not in st.session_state:
    st.session_state.unidad_dibujo = "mm"
if 'factor_conversion' not in st.session_state:
    st.session_state.factor_conversion = 1000
if 'vel_min' not in st.session_state:
    st.session_state.vel_min = 0.5
if 'vel_max' not in st.session_state:
    st.session_state.vel_max = 2.0
if 'dxf_loaded' not in st.session_state:
    st.session_state.dxf_loaded = False
if 'tmp_dxf_path' not in st.session_state:
    st.session_state.tmp_dxf_path = None
if 'nodos_raw' not in st.session_state:
    st.session_state.nodos_raw = None

# ================================================================================
# IMPORTACIONES DE MÓDULOS PROPIOS
# ================================================================================
import hydro_core
from hydro_core import (
    DXFReader, normalizar_coordenadas, construir_red,
    RedHidraulica, Nodo, Tuberia, HydraulicAnalyzer, generate_3d_plot,
    TIPOS_OCUPACION_AGUA, UNIDADES_GASTO, DIAMETROS_PAVCO, 
    ajustar_cotas_relativas, PRESION_MIN_NORMA, diametro_a_numero,
    caudal_por_ug
)

from hydro_ui import mostrar_metodologia
from hydro_utils import generar_excel_bytes, generar_configuracion_json

# ================================================================================
# FUNCIONES AUXILIARES DE INTERFAZ
# ================================================================================

def get_status(red):
    if red is None:
        return "🔴 Sin red"
    if red.nodo_entrada_id is None:
        return "🟡 Sin entrada"
    return "🟢 Red lista"

def procesar_dxf(archivo_dxf):
    """Procesa el archivo DXF y construye la red"""
    with st.spinner("🔄 Construyendo red..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
            tmp.write(archivo_dxf.getvalue())
            ruta_tmp = tmp.name

        try:
            reader = DXFReader(ruta_tmp)
            layers_disponibles = reader.obtener_layers()
            
            if not layers_disponibles:
                st.warning("⚠️ No se encontraron layers en el archivo DXF")
                return
            
            layers_seleccionados = st.multiselect(
                "Layers con tuberías:", 
                layers_disponibles, 
                default=layers_disponibles[0] if layers_disponibles else None,
                key="layer_selector_build"
            )
            
            if not layers_seleccionados:
                st.warning("⚠️ Seleccione al menos un layer")
                return
            
            opciones_unidades = {
                "Milímetros (mm)": 1000.0, 
                "Centímetros (cm)": 100.0, 
                "Metros (m)": 1.0, 
                "Pulgadas (in)": 1 / 0.0254, 
                "Pies (ft)": 1 / 0.3048
            }
            factor = opciones_unidades[st.selectbox("Unidades originales", list(opciones_unidades.keys()), key="unidades_select")]
            
            if st.button("🏗️ Construir Red", type="primary", key="btn_build"):
                with st.spinner("Armando topología..."):
                    lineas = normalizar_coordenadas(
                        reader.extraer_lineas(layers_seleccionados), 
                        factor_conversion=factor
                    )
                    nodos_dict, tuberias = construir_red(lineas)
                    
                    red = RedHidraulica()
                    for (x, y, z), nid in nodos_dict.items():
                        red.agregar_nodo(Nodo(id=nid, x=x, y=y, z=z))
                    for t in tuberias:
                        red.agregar_tuberia(t)
                    
                    st.session_state.red = red
                    st.session_state.nodos_raw = nodos_dict
                    
                    if len(red.nodos) > 0:
                        primer_nodo = list(red.nodos.keys())[0]
                        red.nodo_entrada_id = primer_nodo
                        red.nodos[primer_nodo].es_entrada = True
                        ajustar_cotas_relativas(red)
                    
                    st.success(f"✅ Red construida: {len(red.nodos)} nodos, {len(red.tuberias)} tuberías")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error crítico construyendo la red: {e}")
            st.code(traceback.format_exc(), language="python")
        finally:
            if os.path.exists(ruta_tmp):
                os.unlink(ruta_tmp)

def ejecutar_analisis():
    """Ejecuta el análisis hidráulico"""
    with st.spinner("🚀 Ejecutando análisis..."):
        # Actualizar variables globales en hydro_core
        hydro_core.VEL_MIN_MS = st.session_state.vel_min
        hydro_core.VEL_MAX_MS = st.session_state.vel_max
        hydro_core.PRESION_ENTRADA_MCA = st.session_state.presion_entrada
        hydro_core.TIPO_OCUPACION_ACTUAL = st.session_state.tipo_ocupacion
        
        analyzer = HydraulicAnalyzer(
            st.session_state.red,
            st.session_state.diametro_maximo
        )
        analyzer.ejecutar()
        st.session_state.analyzer = analyzer
        
        presiones = [n.presion_mca for n in st.session_state.red.nodos.values() if n.presion_mca is not None]
        ug_acumulada = st.session_state.red.calcular_ug_acumulada()
        ug_total = ug_acumulada.get(st.session_state.red.nodo_entrada_id, 0)
        caudal_total = caudal_por_ug(ug_total, st.session_state.tipo_ocupacion)
        
        st.session_state.resultados = {
            'presiones': presiones,
            'ug_total': ug_total,
            'caudal_total': caudal_total,
            'cumple': min(presiones) >= PRESION_MIN_NORMA if presiones else False
        }
        st.success("✅ Análisis completado")
        st.rerun()

def exportar_resultados():
    """Exporta resultados a Excel"""
    try:
        excel_data = generar_excel_bytes(
            st.session_state.red,
            st.session_state.tipo_ocupacion,
            st.session_state.presion_entrada,
            PRESION_MIN_NORMA
        )
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="HydroDomusPy_Reporte_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx">📥 Descargar Excel</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Excel generado")
    except Exception as e:
        st.error(f"Error exportando: {e}")

def generar_perfil_presiones(red):
    """Genera el perfil de presiones 2D para la ruta más larga desde la entrada."""
    try:
        if red.nodo_entrada_id is None:
            return None
        
        distancias = nx.single_source_dijkstra_path_length(red.grafo, red.nodo_entrada_id)
        if distancias:
            nodo_lejano = max(distancias, key=distancias.get)
            camino = nx.shortest_path(red.grafo, red.nodo_entrada_id, nodo_lejano)
        else:
            camino = list(red.nodos.keys())[:10]
        
        distancias_acum = [0]
        presiones = [red.nodos[camino[0]].presion_mca or 0]
        cotas = [red.nodos[camino[0]].z]
        nodos_ids = [camino[0]]
        
        for i in range(1, len(camino)):
            n_prev = camino[i-1]
            n_curr = camino[i]
            tid = red._find_tuberia(n_prev, n_curr)
            tubo = red.tuberias[tid] if tid else None
            
            dist_acum = distancias_acum[-1] + (tubo.longitud_m if tubo else 0)
            distancias_acum.append(dist_acum)
            presiones.append(red.nodos[n_curr].presion_mca or 0)
            cotas.append(red.nodos[n_curr].z)
            nodos_ids.append(n_curr)
        
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
            subplot_titles=("📉 Gradiente Hidráulico (Presión)", "🏔️ Perfil Físico (Elevación Z)")
        )
        
        fig.add_trace(go.Scatter(
            x=distancias_acum, y=presiones, mode='lines+markers', name='Presión',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8, color='#2980b9', line=dict(width=2, color='white')),
            customdata=nodos_ids,
            hovertemplate="<b>Nodo: %{customdata}</b><br>Presión: %{y:.2f} mca<extra></extra>"
        ), row=1, col=1)
        
        fig.add_hline(
            y=PRESION_MIN_NORMA, line_dash="dash", line_color="#e74c3c",
            annotation_text=f"Mínima Normativa ({PRESION_MIN_NORMA} mca)",
            annotation_position="top right", row=1, col=1
        )
        
        fig.add_trace(go.Scatter(
            x=distancias_acum, y=cotas, mode='lines+markers', name='Elevación',
            fill='tozeroy', fillcolor='rgba(230, 126, 34, 0.15)',
            line=dict(color='#e67e22', width=3),
            marker=dict(size=6, color='#d35400'),
            customdata=nodos_ids,
            hovertemplate="<b>Nodo: %{customdata}</b><br>Cota Z: %{y:.2f} m<extra></extra>"
        ), row=2, col=1)
        
        fig.update_layout(
            height=600,
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_xaxes(title_text="Distancia acumulada desde la entrada (m)", row=2, col=1)
        fig.update_yaxes(title_text="Presión (mca)", row=1, col=1)
        fig.update_yaxes(title_text="Elevación (m)", row=2, col=1)
        
        return fig
    except Exception as e:
        return None

# ================================================================================
# ENCABEZADO Y BOTONES DE APOYO (TOP RIGHT)
# ================================================================================
col_titulo, col_donaciones = st.columns([3.2, 1.8])

with col_titulo:
    st.title("💧 Hydro Domus Py")
    st.markdown("### Análisis Hidráulico para Redes Internas")

with col_donaciones:
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("##### ☕ Apoya este proyecto, ¡Donaciones aquí!")
    
    col_int, col_nac = st.columns(2)
    with col_int:
        st.link_button("🌎 Internacional", "https://paypal.me/eocing", use_container_width=True)
    with col_nac:
        with st.popover("Colombia", use_container_width=True):
            st.markdown("**Bre-B (Nu Bank)**")
            st.markdown("Llave: `@EOC803`")
            st.caption("Transferencia inmediata y sin costo")
            
            if os.path.exists("qr_nubank.jpg"):
                st.image("qr_nubank.jpg", width=250)
            elif os.path.exists("qr_nubank.png"):
                st.image("qr_nubank.png", width=250)
            elif os.path.exists("qr_nubank.jpeg"):
                st.image("qr_nubank.jpeg", width=250)
            else:
                st.warning("Falta la imagen del QR. Guárdala como 'qr_nubank.jpg' en esta carpeta.")

# ================================================================================
# SECCIÓN INFORMATIVA: METODOLOGÍA
# ================================================================================
mostrar_metodologia()

# ================================================================================
# BARRA LATERAL - PARÁMETROS Y CONTROLES
# ================================================================================
with st.sidebar:
    st.header("⚙️ Parámetros de Cálculo")
    
    tipo_ocupacion = st.selectbox(
        "Tipo de Edificación", 
        list(TIPOS_OCUPACION_AGUA.keys()),
        key="tipo_ocup_sidebar"
    )
    st.session_state.tipo_ocupacion = tipo_ocupacion
    
    presion_entrada = st.number_input(
        "Presión de entrada (mca)", 
        value=st.session_state.presion_entrada, 
        min_value=1.0,
        key="presion_sidebar"
    )
    st.session_state.presion_entrada = presion_entrada
    
    col1, col2 = st.columns(2)
    with col1:
        vel_min = st.number_input(
            "Vel. mín (m/s)", 
            value=st.session_state.vel_min,
            min_value=0.1,
            max_value=5.0,
            step=0.1,
            key="vel_min_sidebar"
        )
        st.session_state.vel_min = vel_min
    with col2:
        vel_max = st.number_input(
            "Vel. máx (m/s)", 
            value=st.session_state.vel_max,
            min_value=0.5,
            max_value=10.0,
            step=0.1,
            key="vel_max_sidebar"
        )
        st.session_state.vel_max = vel_max
    
    # Actualizar variables globales en hydro_core
    hydro_core.TIPO_OCUPACION_ACTUAL = st.session_state.tipo_ocupacion
    hydro_core.PRESION_ENTRADA_MCA = st.session_state.presion_entrada
    hydro_core.VEL_MIN_MS = st.session_state.vel_min
    hydro_core.VEL_MAX_MS = st.session_state.vel_max
    
    st.markdown("---")
    st.subheader("📏 Restricción de Diámetro")
    
    restringir_diametro = st.checkbox(
        "Restringir al diámetro de la red matriz", 
        value=False,
        key="restringir_sidebar"
    )
    
    if restringir_diametro:
        diametro_maximo_nom = st.selectbox(
            "Diámetro máximo permitido:", 
            list(DIAMETROS_PAVCO.keys()), 
            index=2,
            key="diam_max_sidebar"
        )
        st.session_state.diametro_maximo = DIAMETROS_PAVCO[diametro_maximo_nom]
    else:
        st.session_state.diametro_maximo = None
        st.caption("✅ Sin restricción")
    
    st.markdown("---")
    st.markdown("### 📊 Estado del Sistema")
    st.info(get_status(st.session_state.red))
    
    if st.session_state.red is not None:
        st.caption(f"🔢 Nodos: {len(st.session_state.red.nodos)}")
        st.caption(f"🔗 Tuberías: {len(st.session_state.red.tuberias)}")
        if st.session_state.red.nodo_entrada_id is not None:
            st.caption(f"🚰 Entrada: Nodo {st.session_state.red.nodo_entrada_id}")
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Desarrollado por:")
    st.markdown("**Ing. Edison Osvaldo Olaya Cortes**")
    st.markdown("📧 olaya.ing.quim@gmail.com")
    st.markdown("© 2026 - Software de Código Abierto")

# ================================================================================
# ÁREA PRINCIPAL - FLUJO DE TRABAJO
# ================================================================================

# ===== PASO 1: CARGA DE GEOMETRÍA =====
st.subheader("1. Cargar Geometría")

archivo_dxf = st.file_uploader(
    "Sube tu plano hidrosanitario (.dxf)", 
    type=['dxf'],
    key="dxf_uploader_main"
)

if archivo_dxf is not None:
    procesar_dxf(archivo_dxf)

# ===== PASO 2: CONFIGURACIÓN DE NODOS (si hay red) =====
if st.session_state.red is not None:
    st.markdown("---")
    st.subheader("2. Configuración de Nodos")
    
    red = st.session_state.red
    
    # Mostrar gráfico 3D de la topología
    st.plotly_chart(
        generate_3d_plot(red, theme="dark"), 
        use_container_width=True, 
        key="grafico_topologia"
    )
    
    # Configuración de nodos
    col_load, col_save = st.columns([1, 1])
    
    with col_load:
        config_file = st.file_uploader(
            "📂 Cargar configuración (.json)", 
            type=["json"],
            key="config_uploader"
        )
    
    loaded_config = json.load(config_file) if config_file else None
    
    nodos_ids = list(red.nodos.keys())
    default_entrada_idx = 0
    aparatos_list = [""] * len(nodos_ids)
    valvulas_list = [""] * len(nodos_ids)
    aperturas_list = [100.0] * len(nodos_ids)

    if loaded_config:
        if loaded_config.get("nodo_entrada") in nodos_ids:
            default_entrada_idx = nodos_ids.index(loaded_config["nodo_entrada"])
        config_nodos = {n["id"]: n for n in loaded_config.get("nodos", [])}
        for i, nid in enumerate(nodos_ids):
            if nid in config_nodos:
                aparatos_list[i] = config_nodos[nid].get("tipo_aparato", "")
                valvulas_list[i] = config_nodos[nid].get("valvula_tipo", "")
                aperturas_list[i] = config_nodos[nid].get("valvula_apertura", 100.0)

    col1, col2 = st.columns([1, 2.5])
    with col1:
        nodo_entrada = st.selectbox(
            "🚰 ID Nodo Entrada:", 
            options=nodos_ids, 
            index=default_entrada_idx,
            key="nodo_entrada_main"
        )
        
    with col2:
        df_config = pd.DataFrame({
            "ID Nodo": nodos_ids, 
            "Aparato": aparatos_list, 
            "Válvula": valvulas_list, 
            "Apertura (%)": aperturas_list
        })
        edited_df = st.data_editor(
            df_config,
            column_config={
                "Aparato": st.column_config.SelectboxColumn(
                    "Aparato", 
                    options=[""] + list(UNIDADES_GASTO.keys())
                ),
                "Válvula": st.column_config.SelectboxColumn(
                    "Válvula", 
                    options=["", "Compuerta", "Globo", "Check", "Esfera"]
                ),
                "Apertura (%)": st.column_config.NumberColumn(
                    "Apertura (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    step=5.0
                )
            },
            disabled=["ID Nodo"], 
            use_container_width=True, 
            hide_index=True,
            key="nodos_editor"
        )

    config_to_save = {
        "nodo_entrada": nodo_entrada, 
        "nodos": []
    }
    for _, row in edited_df.iterrows():
        config_to_save["nodos"].append({
            "id": row["ID Nodo"], 
            "tipo_aparato": row["Aparato"], 
            "valvula_tipo": row["Válvula"], 
            "valvula_apertura": row["Apertura (%)"]
        })
    
    with col_save:
        st.write("<br>", unsafe_allow_html=True)
        st.download_button(
            "💾 Guardar Progreso (.json)", 
            data=json.dumps(config_to_save, indent=2, ensure_ascii=False), 
            file_name="Config.json",
            key="download_config"
        )

    # ===== PASO 3: SIMULACIÓN Y RESULTADOS =====
    st.markdown("---")
    st.subheader("3. Simulación y Resultados")
    
    col_run, col_export = st.columns(2)
    
    with col_run:
        if st.button("🚀 Ejecutar Análisis Hidráulico", type="primary", use_container_width=True):
            red = st.session_state.red
            
            # Resetear configuración de nodos
            for n in red.nodos.values():
                n.es_entrada = False
                n.tipo_aparato = ""
                n.valvula_tipo = ""
                n.valvula_apertura = 100.0
            
            red.nodo_entrada_id = nodo_entrada
            red.nodos[nodo_entrada].es_entrada = True
            
            for _, row in edited_df.iterrows():
                nid = row["ID Nodo"]
                red.nodos[nid].tipo_aparato = row["Aparato"]
                red.nodos[nid].valvula_tipo = row["Válvula"]
                red.nodos[nid].valvula_apertura = float(row["Apertura (%)"])
                    
            analyzer = HydraulicAnalyzer(
                red, 
                diametro_maximo=st.session_state.diametro_maximo
            )
            analyzer.ejecutar()
            st.session_state.analyzer = analyzer
            
            presiones = [n.presion_mca for n in red.nodos.values() if n.presion_mca is not None]
            ug_acumulada = red.calcular_ug_acumulada()
            ug_total = ug_acumulada.get(red.nodo_entrada_id, 0)
            caudal_total = caudal_por_ug(ug_total, st.session_state.tipo_ocupacion)
            
            st.session_state.resultados = {
                'presiones': presiones,
                'ug_total': ug_total,
                'caudal_total': caudal_total,
                'cumple': min(presiones) >= PRESION_MIN_NORMA if presiones else False
            }
            st.success("✅ Análisis completado exitosamente.")
            st.rerun()
    
    with col_export:
        if st.session_state.resultados:
            if st.button("📊 Exportar Reporte Excel", use_container_width=True):
                excel_data = generar_excel_bytes(
                    st.session_state.red,
                    st.session_state.tipo_ocupacion,
                    st.session_state.presion_entrada,
                    PRESION_MIN_NORMA
                )
                b64 = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="HydroDomusPy_Reporte_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx">📥 Descargar Excel</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Excel generado")
    
    # ===== RESULTADOS =====
    if st.session_state.resultados:
        resultados = st.session_state.resultados
        red = st.session_state.red
        
        # Métricas rápidas
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🔢 Nodos", len(red.nodos))
        col2.metric("🔗 Tuberías", len(red.tuberias))
        col3.metric("🔧 Accesorios", len(red.accesorios))
        col4.metric("💧 Caudal", f"{resultados['caudal_total']:.2f} L/s")
        col5.metric("📊 UG totales", f"{resultados['ug_total']:.0f}")
        
        st.divider()
        
        # Pestañas de resultados
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🌐 Modelo 3D", 
            "📈 Ruta Crítica", 
            "📍 Nodos", 
            "📏 Tuberías", 
            "🔧 Accesorios", 
            "📋 Materiales"
        ])
        
        with tab1:
            st.plotly_chart(
                generate_3d_plot(red, theme="dark"), 
                use_container_width=True, 
                key="grafico_resultados"
            )
        
        with tab2:
            st.markdown("#### Perfil de la ruta más alejada desde el nodo de entrada")
            st.info("💡 Pasa el cursor sobre la gráfica para ver simultáneamente la elevación y la presión en cada nodo.")
            fig_perfil = generar_perfil_presiones(red)
            if fig_perfil:
                st.plotly_chart(fig_perfil, use_container_width=True)
            else:
                st.warning("No se pudo generar el perfil. Asegúrese de haber configurado un nodo de entrada válido.")
        
        with tab3:
            datos_nodos = []
            for n in red.nodos.values():
                datos_nodos.append({
                    "ID": n.id,
                    "X (m)": round(n.x, 2),
                    "Y (m)": round(n.y, 2),
                    "Z (m)": round(n.z, 2),
                    "Presión (mca)": round(n.presion_mca, 2) if n.presion_mca else None,
                    "Aparato": n.tipo_aparato or "-",
                    "Válvula": f"{n.valvula_tipo} ({n.valvula_apertura}%)" if n.valvula_tipo else "-"
                })
            st.dataframe(pd.DataFrame(datos_nodos), use_container_width=True, hide_index=True)
        
        with tab4:
            datos_tubos = []
            for t in red.tuberias.values():
                datos_tubos.append({
                    "ID": t.id,
                    "Inicio": t.nodo_inicio,
                    "Fin": t.nodo_fin,
                    "Longitud (m)": round(t.longitud_m, 2),
                    "Diam. Nom.": t.diametro_nominal_pulg,
                    "Caudal (L/s)": round(t.caudal_lps, 3),
                    "Vel (m/s)": round(t.velocidad_ms, 2),
                    "Pérdida (mca)": round(t.perdida_mca, 3)
                })
            st.dataframe(pd.DataFrame(datos_tubos), use_container_width=True, hide_index=True)
        
        with tab5:
            datos_acc = []
            for a in red.accesorios:
                datos_acc.append({
                    "ID": a.id,
                    "Tipo": a.tipo.replace("_", " "),
                    "Nodo": a.nodo_id,
                    "Leq (m)": round(a.longitud_equivalente_m, 2),
                    "Pérdida (mca)": round(a.perdida_mca, 4)
                })
            st.dataframe(pd.DataFrame(datos_acc), use_container_width=True, hide_index=True)
        
        with tab6:
            st.markdown("### 📏 Tuberías PVC")
            longitudes = {}
            for t in red.tuberias.values():
                diam = t.diametro_nominal_pulg
                longitudes[diam] = longitudes.get(diam, 0) + t.longitud_m
            
            tubos_data, total_tramos = [], 0
            for diam in sorted(longitudes.keys(), key=lambda x: diametro_a_numero(x)):
                tramos = int(math.ceil(longitudes[diam] / 6.0))
                total_tramos += tramos
                tubos_data.append({
                    "Diámetro": diam, 
                    "Longitud (m)": round(longitudes[diam], 2), 
                    "Tubos 6m": tramos
                })
            st.dataframe(pd.DataFrame(tubos_data), use_container_width=True, hide_index=True)
            
            st.markdown("### 🔧 Accesorios detectados")
            acc_data = {}
            for a in red.accesorios:
                acc_data[a.tipo] = acc_data.get(a.tipo, 0) + 1
            st.dataframe(
                pd.DataFrame([
                    {"Accesorio": k.replace("_", " "), "Cantidad": v} 
                    for k, v in acc_data.items()
                ]), 
                use_container_width=True, 
                hide_index=True
            )
            
            st.markdown("### 🧴 Consumibles (Basado en Uniones + 10% Seguridad)")
            uniones_acc = sum([3 if 'Tee' in k else 2 for k, v in acc_data.items() for _ in range(v)])
            uniones_tubos = sum([max(0, math.ceil(t.longitud_m / 6.0) - 1) for t in red.tuberias.values()])
            uniones_estimadas = int((uniones_acc + uniones_tubos) * 1.10)
            
            galones_pegamento = max(0.25, uniones_estimadas / 150)
            galones_limpiador = max(0.25, uniones_estimadas / 250)
            
            col_p, col_l = st.columns(2)
            col_p.info(f"**PEGAMENTO PVC**\n\n• Uniones: {uniones_estimadas}\n• Galones: {galones_pegamento:.2f}")
            col_l.warning(f"**LIMPIADOR (Primer)**\n\n• Uniones: {uniones_estimadas}\n• Galones: {galones_limpiador:.2f}")
