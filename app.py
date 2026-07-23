# app.py
# ================================================================================
#                            H Y D R O   D O M U S   P Y
# ================================================================================
#                    Análisis Hidráulico para Redes Internas
#                          Interfaz Web con Streamlit
# ================================================================================
#                               Versión 1.0.0 - Web
#                          (Interfaz de Pantalla Completa)
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
    layout="wide",
    initial_sidebar_state="collapsed"
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

# ================================================================================
# SELECTOR DE TEMA
# ================================================================================
if 'tema' not in st.session_state:
    tema_sistema = st.get_option("theme.base")
    st.session_state.tema = tema_sistema if tema_sistema else "dark"

# ================================================================================
# APLICAR ESTILOS CSS (VERSIÓN DEFINITIVA CON SELECTORES ESPECÍFICOS)
# ================================================================================
def apply_styles():
    """Aplica estilos CSS según el tema seleccionado - Versión corregida"""
    is_dark = st.session_state.tema == "dark"
    
    # Colores según tema
    if is_dark:
        bg = "#0e1117"
        card = "#262730"
        border = "#3d3d4d"
        text = "#ffffff"
        text_sec = "#bbbbbb"
        input_bg = "#1a2533"
        input_text = "#ffffff"
        input_border = "#3d3d4d"
        btn_bg = "rgba(255,255,255,0.08)"
        btn_text = "#ffffff"
        btn_hover = "rgba(255,255,255,0.15)"
        tab_bg = "#1a2533"
        tab_text = "#bbbbbb"
        header_grad = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    else:
        bg = "#f0f2f6"
        card = "#ffffff"
        border = "#d0d0d0"
        text = "#1a1a2e"
        text_sec = "#4a4a5a"
        input_bg = "#ffffff"
        input_text = "#1a1a2e"
        input_border = "#d0d0d0"
        btn_bg = "#f0f2f6"
        btn_text = "#1a1a2e"
        btn_hover = "#e0e0e0"
        tab_bg = "#f0f2f6"
        tab_text = "#4a4a5a"
        header_grad = "linear-gradient(135deg, #1a5276, #2471a3, #2e86c1)"

    st.markdown(f"""
    <style>
        /* ============================================================
           ESTILOS GENERALES
           ============================================================ */
        .stApp {{
            background: {bg} !important;
        }}
        
        /* ============================================================
           INPUTS Y SELECTORES - CORREGIDO CON SELECTORES ESPECÍFICOS
           ============================================================ */
        /* Contenedor principal de inputs */
        .stSelectbox > div,
        .stNumberInput > div,
        .stTextInput > div,
        .stFileUploader > div,
        .stDateInput > div,
        .stTimeInput > div {{
            background: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
        }}
        
        /* Selectores desplegables - EL MÁS IMPORTANTE */
        .stSelectbox [data-baseweb="select"] > div {{
            background: {input_bg} !important;
            color: {input_text} !important;
            border: none !important;
        }}
        
        .stSelectbox [data-baseweb="select"] input {{
            color: {input_text} !important;
            background: {input_bg} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] svg {{
            fill: {input_text} !important;
        }}
        
        /* Labels de inputs */
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label,
        .stFileUploader label {{
            color: {text_sec} !important;
        }}
        
        /* Inputs numéricos */
        .stNumberInput input {{
            color: {input_text} !important;
            background: {input_bg} !important;
            border: none !important;
        }}
        
        /* Botones de incremento/decremento en NumberInput */
        .stNumberInput button {{
            background: {input_bg} !important;
            color: {input_text} !important;
            border: 1px solid {input_border} !important;
        }}
        
        .stNumberInput button:hover {{
            background: {btn_hover} !important;
        }}
        
        /* File Uploader */
        .stFileUploader > div > div {{
            background: {input_bg} !important;
            border: 1px dashed {input_border} !important;
            border-radius: 8px !important;
        }}
        
        .stFileUploader > div > div > div {{
            color: {text_sec} !important;
        }}
        
        /* Botón del File Uploader */
        .stFileUploader button {{
            background: #3498db !important;
            color: white !important;
            border: none !important;
        }}
        
        .stFileUploader button:hover {{
            background: #2980b9 !important;
        }}
        
        /* ============================================================
           BARRA DE HERRAMIENTAS
           ============================================================ */
        .toolbar {{
            background: {card} !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 10px !important;
            margin-bottom: 1.2rem !important;
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.6rem !important;
            align-items: center !important;
            border: 1px solid {border} !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        }}
        
        .toolbar .divider {{
            width: 1px !important;
            height: 28px !important;
            background: {border} !important;
            margin: 0 0.4rem !important;
        }}
        
        /* ============================================================
           BOTONES
           ============================================================ */
        .stButton > button {{
            background: {btn_bg} !important;
            color: {btn_text} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
            padding: 0.3rem 0.8rem !important;
            font-size: 0.8rem !important;
        }}
        
        .stButton > button:hover {{
            background: {btn_hover} !important;
            border-color: #3498db !important;
        }}
        
        .stButton > button.primary {{
            background: #3498db !important;
            color: white !important;
            border-color: #3498db !important;
        }}
        
        .stButton > button.primary:hover {{
            background: #2980b9 !important;
            border-color: #2980b9 !important;
        }}
        
        /* ============================================================
           TARJETAS DE MÉTRICAS
           ============================================================ */
        .metric-card {{
            background: {card} !important;
            padding: 1rem !important;
            border-radius: 12px !important;
            text-align: center !important;
            border: 1px solid {border} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            min-height: 80px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        
        .metric-card .metric-value {{
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #3498db !important;
        }}
        
        .metric-card .metric-label {{
            font-size: 0.75rem !important;
            color: {text_sec} !important;
            margin-top: 0.2rem !important;
        }}
        
        .metric-card:hover {{
            border-color: #3498db !important;
            transform: translateY(-2px) !important;
        }}
        
        /* ============================================================
           SECCIONES DE CONFIGURACIÓN
           ============================================================ */
        .config-section {{
            background: {card} !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            border: 1px solid {border} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }}
        
        .config-section .section-title {{
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #3498db !important;
            margin-bottom: 0.8rem !important;
        }}
        
        /* ============================================================
           PESTAÑAS
           ============================================================ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.3rem !important;
            background: {tab_bg} !important;
            padding: 0.4rem !important;
            border-radius: 10px !important;
            border: 1px solid {border} !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            color: {tab_text} !important;
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: #3498db !important;
            color: white !important;
        }}
        
        /* ============================================================
           HEADER SUPERIOR
           ============================================================ */
        .main-header {{
            background: {header_grad} !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
            flex-wrap: wrap !important;
            gap: 0.8rem !important;
        }}
        
        .main-header * {{
            color: #ffffff !important;
        }}
        
        .main-header .subtitle {{
            color: rgba(255,255,255,0.7) !important;
        }}
        
        /* ============================================================
           DATAFRAMES
           ============================================================ */
        .stDataFrame {{
            border: 1px solid {border} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        
        /* ============================================================
           EXPANDERS
           ============================================================ */
        .streamlit-expanderHeader {{
            background: {card} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
        }}
        
        .streamlit-expanderContent {{
            background: {card} !important;
            border: 1px solid {border} !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }}
        
        /* ============================================================
           SCROLLBAR
           ============================================================ */
        ::-webkit-scrollbar {{ width: 6px !important; height: 6px !important; }}
        ::-webkit-scrollbar-track {{ background: {card} !important; border-radius: 3px !important; }}
        ::-webkit-scrollbar-thumb {{ background: #3498db !important; border-radius: 3px !important; }}
        
        /* ============================================================
           RESPONSIVE
           ============================================================ */
        @media (max-width: 768px) {{
            .main-header {{ flex-direction: column !important; text-align: center !important; }}
            .toolbar {{ flex-direction: column !important; align-items: stretch !important; }}
            .toolbar .divider {{ display: none !important; }}
        }}
    </style>
    """, unsafe_allow_html=True)

# Ejecutar estilos
apply_styles()

# ================================================================================
# IMPORTACIONES DE MÓDULOS PROPIOS
# ================================================================================
from hydro_core import (
    DXFReader, normalizar_coordenadas, construir_red,
    RedHidraulica, Nodo, Tuberia, HydraulicAnalyzer,
    generate_3d_plot,
    TIPOS_OCUPACION_AGUA, UNIDADES_GASTO, DIAMETROS_PAVCO,
    ajustar_cotas_relativas, PRESION_MIN_NORMA,
    caudal_por_ug
)

from hydro_ui import mostrar_metodologia, panel_configuracion_nodos
from hydro_utils import generar_excel_bytes, generar_configuracion_json

# ================================================================================
# FUNCIONES AUXILIARES DE INTERFAZ
# ================================================================================

def get_status(red):
    if red is None:
        return "dot-gray", "⏳ Sin red"
    if red.nodo_entrada_id is None:
        return "dot-yellow", "⚙️ Sin entrada"
    return "dot-green", "✅ Red lista"

def procesar_dxf(dxf_file):
    """Procesa el archivo DXF y construye la red"""
    with st.spinner("🔄 Construyendo red..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
            tmp.write(dxf_file.getvalue())
            tmp_path = tmp.name
            st.session_state.tmp_dxf_path = tmp_path
        
        try:
            reader = DXFReader(tmp_path)
            layers = reader.obtener_layers()
            
            if layers:
                st.info(f"📋 {len(layers)} layers encontrados")
                selected = st.multiselect(
                    "Seleccionar layers:",
                    options=layers,
                    default=layers[:3] if len(layers) >= 3 else layers,
                    key="layer_selector_build"
                )
                
                if selected:
                    lineas_raw = reader.extraer_lineas(selected)
                    if lineas_raw:
                        factor = st.session_state.factor_conversion
                        lineas = normalizar_coordenadas(lineas_raw, factor_conversion=factor)
                        nodos_dict, tuberias = construir_red(lineas)
                        
                        red = RedHidraulica()
                        for (x, y, z), nid in nodos_dict.items():
                            red.agregar_nodo(Nodo(id=nid, x=x, y=y, z=z))
                        for t in tuberias:
                            red.agregar_tuberia(t)
                        
                        st.session_state.red = red
                        
                        if len(red.nodos) > 0:
                            primer_nodo = list(red.nodos.keys())[0]
                            red.nodo_entrada_id = primer_nodo
                            red.nodos[primer_nodo].es_entrada = True
                            ajustar_cotas_relativas(red)
                        
                        st.success(f"✅ Red construida: {len(red.nodos)} nodos, {len(red.tuberias)} tuberías")
                        st.rerun()
                    else:
                        st.error("❌ No se encontraron líneas en los layers seleccionados")
            else:
                st.warning("⚠️ No se encontraron layers en el archivo DXF")
                
        except Exception as e:
            st.error(f"❌ Error leyendo DXF: {e}")
        finally:
            if st.session_state.tmp_dxf_path and os.path.exists(st.session_state.tmp_dxf_path):
                try:
                    os.unlink(st.session_state.tmp_dxf_path)
                    st.session_state.tmp_dxf_path = None
                except:
                    pass

def ejecutar_analisis():
    """Ejecuta el análisis hidráulico"""
    with st.spinner("🚀 Ejecutando análisis..."):
        import hydro_core
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

def mostrar_welcome():
    """Muestra la pantalla de bienvenida"""
    is_dark = st.session_state.tema == "dark"
    text_color = "#ffffff" if is_dark else "#1a1a2e"
    muted_color = "rgba(255,255,255,0.5)" if is_dark else "rgba(0,0,0,0.5)"
    
    st.markdown(f"""
    <div style="text-align:center; padding:2rem 0;">
        <h1 style="font-size:3rem; margin:0;">💧</h1>
        <h2 style="color:#3498db;">Hydro Domus Py</h2>
        <p style="color:{text_color}; font-size:1.1rem;">
            Análisis Hidráulico para Redes Internas de Agua Potable
        </p>
        <p style="color:{muted_color};">
            Cargue un archivo DXF en la barra de herramientas para comenzar
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("📁", "Lectura DXF", "Soporta LINE, LWPOLYLINE, POLYLINE y 3DPOLYLINE"),
        ("🔧", "Análisis Hidráulico", "Caudales, presiones y pérdidas (Darcy-Weisbach)"),
        ("📊", "Visualización 3D", "Gráficos interactivos con Plotly"),
        ("📋", "Reportes", "Exportación a Excel con materiales")
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:2.5rem;">{icon}</div>
                <div style="font-weight:600;margin:0.5rem 0;">{title}</div>
                <div style="font-size:0.85rem;color:{muted_color};">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

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

def generar_reporte_materiales(red):
    """Genera un reporte de materiales en formato DataFrame."""
    from hydro_core import diametro_a_numero
    
    longitudes = {}
    for t in red.tuberias.values():
        diam = t.diametro_nominal_pulg
        longitudes[diam] = longitudes.get(diam, 0) + t.longitud_m
    
    tramos = {d: int(np.ceil(l / 6.0)) for d, l in longitudes.items()}
    
    accesorios = {}
    for acc in red.accesorios:
        nombre = acc.tipo.replace("_", " ")
        if "Valvula" in nombre:
            nombre = nombre.replace("Valvula ", "Válvula ")
        accesorios[nombre] = accesorios.get(nombre, 0) + 1
    
    df_tuberias = pd.DataFrame([
        {
            "Diámetro": d,
            "DI (mm)": DIAMETROS_PAVCO.get(d.replace("-", "_"), 0),
            "Longitud total (m)": round(l, 2),
            "Tramos de 6m": tramos[d]
        }
        for d, l in sorted(longitudes.items(), key=lambda x: diametro_a_numero(x[0]))
    ])
    
    df_accesorios = pd.DataFrame([
        {"Tipo": t, "Cantidad": c}
        for t, c in sorted(accesorios.items(), key=lambda x: -x[1])
    ])
    
    total_long = sum(longitudes.values())
    total_tramos = sum(tramos.values())
    total_acc = sum(accesorios.values())
    
    return df_tuberias, df_accesorios, total_long, total_tramos, total_acc

# ================================================================================
# HEADER SUPERIOR CON SELECTOR DE TEMA
# ================================================================================
col_titulo, col_selector = st.columns([3, 1])

with col_titulo:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 2rem;">💧</span>
        <div>
            <h1 style="margin: 0; font-size: 1.8rem;">Hydro Domus Py</h1>
            <p style="margin: 0; font-size: 0.85rem; color: rgba(255,255,255,0.7);">
                Análisis Hidráulico para Redes Internas • NTC 1500 - RAS
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_selector:
    tema_seleccionado = st.selectbox(
        "🎨 Tema",
        options=["🌙 Oscuro", "☀️ Claro"],
        index=0 if st.session_state.tema == "dark" else 1,
        label_visibility="collapsed",
        key="selector_tema"
    )
    
    nuevo_tema = "dark" if "Oscuro" in tema_seleccionado else "light"
    
    if nuevo_tema != st.session_state.tema:
        st.session_state.tema = nuevo_tema
        st.rerun()

# ================================================================================
# ESTADO DE LA RED (Header)
# ================================================================================
status_color, status_text = get_status(st.session_state.red)
nodos_count = len(st.session_state.red.nodos) if st.session_state.red else 0
tuberias_count = len(st.session_state.red.tuberias) if st.session_state.red else 0
entrada_text = f"🚰 Entrada: Nodo {st.session_state.red.nodo_entrada_id}" if st.session_state.red and st.session_state.red.nodo_entrada_id else ""

st.markdown(f"""
<div class="main-header">
    <div class="logo-section">
        <span class="logo-icon">💧</span>
        <div>
            <h1 class="title">Hydro Domus Py</h1>
            <p class="subtitle">Análisis Hidráulico para Redes Internas • NTC 1500 - RAS</p>
        </div>
    </div>
    <div class="status-section">
        <span class="status-badge">
            <span class="dot {status_color}"></span>
            {status_text}
        </span>
        <span class="status-badge">🔢 {nodos_count} nodos</span>
        <span class="status-badge">🔗 {tuberias_count} tuberías</span>
        {f'<span class="status-badge">{entrada_text}</span>' if entrada_text else ''}
    </div>
</div>
""", unsafe_allow_html=True)

# ================================================================================
# METODOLOGÍA (Desplegable)
# ================================================================================
mostrar_metodologia()

# ================================================================================
# BARRA DE HERRAMIENTAS
# ================================================================================
st.markdown('<div class="toolbar">', unsafe_allow_html=True)

col_upload, col_units = st.columns([2.5, 2])

with col_upload:
    dxf_file = st.file_uploader(
        "Cargar DXF",
        type=['dxf'],
        label_visibility="collapsed",
        key="dxf_uploader_top",
        help="Seleccione un archivo DXF del plano hidrosanitario"
    )

with col_units:
    unidad_seleccionada = st.selectbox(
        "Unidades del dibujo",
        options=list(UNIDADES_DIBUJO.keys()),
        format_func=lambda x: f"{UNIDADES_DIBUJO[x]['icono']} {UNIDADES_DIBUJO[x]['nombre']}",
        key="unidad_select_top"
    )
    st.session_state.unidad_dibujo = unidad_seleccionada
    st.session_state.factor_conversion = UNIDADES_DIBUJO[unidad_seleccionada]["factor"]

col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([1, 1, 1, 1, 0.8])

with col_btn1:
    if st.button("🚀 Construir Red", use_container_width=True, key="btn_build"):
        if dxf_file is not None:
            procesar_dxf(dxf_file)
        else:
            st.warning("⚠️ Cargue un archivo DXF primero")

with col_btn2:
    if st.button("🎯 Configurar 3D", use_container_width=True, key="btn_config"):
        if st.session_state.red is not None:
            st.session_state.show_config = True
        else:
            st.warning("⚠️ Construya la red primero")

with col_btn3:
    if st.button("🚀 Ejecutar", type="primary", use_container_width=True, key="btn_run"):
        if st.session_state.red is not None and st.session_state.red.nodo_entrada_id is not None:
            ejecutar_analisis()
        else:
            st.warning("⚠️ Configure la red primero")

with col_btn4:
    if st.button("📊 Exportar", use_container_width=True, key="btn_export"):
        if st.session_state.red is not None and st.session_state.resultados:
            exportar_resultados()
        else:
            st.warning("⚠️ Ejecute el análisis primero")

with col_btn5:
    if st.button("🔄 Reset", use_container_width=True, key="btn_reset"):
        st.session_state.red = None
        st.session_state.analyzer = None
        st.session_state.resultados = None
        st.session_state.dxf_loaded = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ================================================================================
# PARÁMETROS DE CÁLCULO
# ================================================================================
st.markdown("""
<div class="config-section">
    <div class="section-title">⚙️ Parámetros de Cálculo</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    presion = st.number_input(
        "Presión entrada (mca)",
        value=st.session_state.presion_entrada,
        min_value=1.0,
        max_value=50.0,
        step=0.5,
        key="presion_main"
    )
    st.session_state.presion_entrada = presion

with col2:
    tipo_ocup = st.selectbox(
        "Tipo de edificación",
        options=list(TIPOS_OCUPACION_AGUA.keys()),
        index=list(TIPOS_OCUPACION_AGUA.keys()).index(st.session_state.tipo_ocupacion) 
             if st.session_state.tipo_ocupacion in TIPOS_OCUPACION_AGUA else 0,
        key="tipo_ocup_main"
    )
    st.session_state.tipo_ocupacion = tipo_ocup
    info_ocup = TIPOS_OCUPACION_AGUA.get(tipo_ocup, {})
    st.caption(f"📐 {info_ocup.get('formula', '')}")

with col3:
    col_vel1, col_vel2 = st.columns(2)
    with col_vel1:
        vel_min = st.number_input(
            "Vel. mín (m/s)",
            value=st.session_state.vel_min,
            min_value=0.1,
            max_value=5.0,
            step=0.1,
            key="vel_min_main"
        )
        st.session_state.vel_min = vel_min
    with col_vel2:
        vel_max = st.number_input(
            "Vel. máx (m/s)",
            value=st.session_state.vel_max,
            min_value=0.5,
            max_value=10.0,
            step=0.1,
            key="vel_max_main"
        )
        st.session_state.vel_max = vel_max

with col4:
    restringir = st.checkbox("Restringir diámetro máximo", key="restringir_main")
    if restringir:
        diam_max = st.selectbox(
            "Diámetro máximo",
            options=list(DIAMETROS_PAVCO.keys()),
            key="diam_max_main"
        )
        st.session_state.diametro_maximo = DIAMETROS_PAVCO[diam_max]
    else:
        st.session_state.diametro_maximo = None
        st.caption("✅ Sin restricción")

st.markdown('</div>', unsafe_allow_html=True)

# ================================================================================
# ÁREA PRINCIPAL
# ================================================================================
if st.session_state.red is None:
    mostrar_welcome()
else:
    red = st.session_state.red
    resultados = st.session_state.resultados
    
    # MÉTRICAS RÁPIDAS
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(red.nodos)}</div>
            <div class="metric-label">🔢 Nodos</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(red.tuberias)}</div>
            <div class="metric-label">🔗 Tuberías</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(red.accesorios)}</div>
            <div class="metric-label">🔧 Accesorios</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        caudal = resultados['caudal_total'] if resultados else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{caudal:.2f}</div>
            <div class="metric-label">💧 Caudal (L/s)</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        ug = resultados['ug_total'] if resultados else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{ug:.0f}</div>
            <div class="metric-label">📊 UG totales</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # PESTAÑAS
    tabs = st.tabs([
        "🔧 Configuración 3D",
        "📊 Resumen",
        "🌐 Visualización 3D",
        "📈 Perfil",
        "📋 Tablas",
        "📦 Materiales"
    ])
    
    # Pestaña 1: Configuración 3D
    with tabs[0]:
        panel_configuracion_nodos(
            red, 
            st.session_state.tipo_ocupacion,
            st.session_state.presion_entrada,
            st.session_state.unidad_dibujo
        )
    
    # Pestaña 2: Resumen
    with tabs[1]:
        st.subheader("📊 Resumen del Análisis")
        
        if resultados:
            presiones = resultados['presiones']
            if presiones:
                p_min, p_max = min(presiones), max(presiones)
                p_prom = sum(presiones) / len(presiones)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💪 Presión entrada", f"{st.session_state.presion_entrada:.1f} mca")
                col2.metric("⬆️ Presión máxima", f"{p_max:.2f} mca")
                col3.metric("⬇️ Presión mínima", f"{p_min:.2f} mca")
                col4.metric("📊 Presión promedio", f"{p_prom:.2f} mca")
                
                if resultados['cumple']:
                    st.success(f"✅ CUMPLE NORMA NTC 1500 (Presión mínima ≥ {PRESION_MIN_NORMA} mca)")
                else:
                    st.error(f"❌ NO CUMPLE NORMA NTC 1500 (Presión mínima: {p_min:.2f} mca < {PRESION_MIN_NORMA} mca)")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Exportar a Excel", use_container_width=True):
                    exportar_resultados()
            with col2:
                if st.button("💾 Guardar Configuración", use_container_width=True):
                    config = generar_configuracion_json(
                        red,
                        st.session_state.tipo_ocupacion,
                        st.session_state.presion_entrada,
                        st.session_state.unidad_dibujo
                    )
                    config_json = json.dumps(config, indent=2, ensure_ascii=False)
                    b64 = base64.b64encode(config_json.encode()).decode()
                    href = f'<a href="data:application/json;base64,{b64}" download="HydroDomusPy_config_{datetime.datetime.now().strftime("%Y%m%d")}.json">📥 Descargar Configuración</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ Configuración lista")
        else:
            st.info("Ejecute el análisis para ver los resultados")
    
    # Pestaña 3: Visualización 3D
    with tabs[2]:
        st.subheader("🌐 Visualización 3D de Resultados")
        if st.session_state.analyzer:
            fig = generate_3d_plot(red, st.session_state.presion_entrada)
            st.plotly_chart(fig, use_container_width=True, height=700)
        else:
            st.info("Ejecute el análisis para ver la visualización 3D")
    
    # Pestaña 4: Perfil
    with tabs[3]:
        st.subheader("📈 Perfil de Presiones")
        if st.session_state.analyzer and red.nodo_entrada_id is not None:
            fig = generar_perfil_presiones(red)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se pudo generar el perfil")
        else:
            st.info("Ejecute el análisis para ver el perfil de presiones")
    
    # Pestaña 5: Tablas
    with tabs[4]:
        st.subheader("📋 Datos de la Red")
        tabla = st.selectbox("Seleccionar tabla:", ["Nodos", "Tuberías", "Accesorios"])
        
        if tabla == "Nodos":
            data = [{"ID": n.id, "X": round(n.x, 2), "Y": round(n.y, 2), "Z": round(n.z, 2),
                     "Presión": round(n.presion_mca, 2) if n.presion_mca else None,
                     "Aparato": n.tipo_aparato or "-",
                     "Válvula": f"{n.valvula_tipo} ({n.valvula_apertura}%)" if n.valvula_tipo else "-",
                     "Entrada": "✓" if n.es_entrada else ""}
                    for n in red.nodos.values()]
            st.dataframe(data, use_container_width=True, height=400)
        elif tabla == "Tuberías":
            data = [{"ID": t.id, "Desde": t.nodo_inicio, "Hasta": t.nodo_fin,
                     "Longitud": round(t.longitud_m, 2), "Diámetro": t.diametro_nominal_pulg,
                     "DI (mm)": round(t.diametro_mm, 2), "Caudal": round(t.caudal_lps, 3),
                     "Velocidad": round(t.velocidad_ms, 2), "Pérdida": round(t.perdida_mca, 3)}
                    for t in red.tuberias.values()]
            st.dataframe(data, use_container_width=True, height=400)
        else:
            data = []
            for acc in red.accesorios:
                diam = "N/A"
                for t in red.tuberias.values():
                    if t.nodo_inicio == acc.nodo_id or t.nodo_fin == acc.nodo_id:
                        diam = t.diametro_nominal_pulg
                        break
                data.append({"ID": acc.id, "Tipo": acc.tipo.replace("_", " "),
                            "Nodo": acc.nodo_id, "DN": diam,
                            "Leq": round(acc.longitud_equivalente_m, 2),
                            "Pérdida": round(acc.perdida_mca, 4)})
            st.dataframe(data, use_container_width=True, height=400)
    
    # Pestaña 6: Materiales
    with tabs[5]:
        st.subheader("📦 Estimación de Materiales")
        if st.session_state.analyzer:
            df_tuberias, df_accesorios, total_long, total_tramos, total_acc = generar_reporte_materiales(red)
            
            st.markdown("### 📏 Tuberías PVC")
            st.dataframe(df_tuberias, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📐 Longitud total", f"{total_long:.2f} m")
            with col2:
                st.metric("🔗 Tramos de 6m", f"{total_tramos}")
            
            st.divider()
            st.markdown("### 🔧 Accesorios")
            st.dataframe(df_accesorios, use_container_width=True)
            st.metric("📊 Total accesorios", f"{total_acc}")
        else:
            st.info("Ejecute el análisis para ver la estimación de materiales")

# ================================================================================
# FOOTER
# ================================================================================
st.markdown("""
<div style="text-align:center; padding:1.5rem 0; margin-top:2rem; border-top:1px solid rgba(255,255,255,0.05);">
    <span style="color:rgba(255,255,255,0.3); font-size:0.8rem;">
        Hydro Domus Py v1.0.0 • Desarrollado por Ing. Edison Osvaldo Olaya Cortes • © 2026
    </span>
</div>
""", unsafe_allow_html=True)
