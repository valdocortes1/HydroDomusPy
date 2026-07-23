# hydro_styles.py
# ================================================================================
#                            H Y D R O   S T Y L E S
# ================================================================================
#                    Estilos CSS unificados para la interfaz
# ================================================================================

import streamlit as st

def apply_enhanced_styles():
    """
    Aplica estilos CSS mejorados con adaptación automática a modo oscuro/claro.
    Prioriza el tema seleccionado por el usuario en session_state.
    """
    # Intentar obtener el tema de session_state, si no, del sistema
    if 'tema' in st.session_state:
        is_dark = st.session_state.tema == "dark"
    else:
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"
    
    # ============================================================
    # PALETA DE COLORES SEGÚN TEMA - DEFINICIÓN CLARA Y PRECISA
    # ============================================================
    if is_dark:
        # ===== MODO OSCURO =====
        COLORS = {
            "bg_primary": "#0e1117",
            "bg_secondary": "#1e2a3a",
            "card_bg": "#262730",
            "border_color": "#3d3d4d",
            "shadow_color": "rgba(0,0,0,0.3)",
            "text_primary": "#ffffff",
            "text_secondary": "#bbbbbb",
            "text_muted": "#888888",
            "text_header": "#ffffff",
            "text_header_sub": "rgba(255,255,255,0.7)",
            "input_bg": "#1a2533",
            "input_text": "#ffffff",
            "input_border": "#3d3d4d",
            "btn_bg": "rgba(255,255,255,0.08)",
            "btn_hover": "rgba(255,255,255,0.15)",
            "btn_text": "#ffffff",
            "btn_primary_bg": "#3498db",
            "btn_primary_hover": "#2980b9",
            "btn_primary_text": "#ffffff",
            "tab_bg": "#1e2a3a",
            "tab_text": "#bbbbbb",
            "tab_active_bg": "#3498db",
            "tab_active_text": "#ffffff",
            "header_grad": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
            "metric_value": "#3498db",
            "section_title": "#3498db",
            "expander_bg": "#1e2a3a",
            "expander_text": "#ffffff",
        }
    else:
        # ===== MODO CLARO =====
        COLORS = {
            "bg_primary": "#f0f2f6",
            "bg_secondary": "#ffffff",
            "card_bg": "#ffffff",
            "border_color": "#d0d0d0",
            "shadow_color": "rgba(0,0,0,0.08)",
            "text_primary": "#1a1a2e",
            "text_secondary": "#4a4a5a",
            "text_muted": "#7a7a8a",
            "text_header": "#ffffff",
            "text_header_sub": "rgba(255,255,255,0.85)",
            "input_bg": "#ffffff",
            "input_text": "#1a1a2e",
            "input_border": "#d0d0d0",
            "btn_bg": "#f0f2f6",
            "btn_hover": "#e0e0e0",
            "btn_text": "#1a1a2e",
            "btn_primary_bg": "#3498db",
            "btn_primary_hover": "#2980b9",
            "btn_primary_text": "#ffffff",
            "tab_bg": "#f0f2f6",
            "tab_text": "#4a4a5a",
            "tab_active_bg": "#3498db",
            "tab_active_text": "#ffffff",
            "header_grad": "linear-gradient(135deg, #1a5276, #2471a3, #2e86c1)",
            "metric_value": "#3498db",
            "section_title": "#3498db",
            "expander_bg": "#ffffff",
            "expander_text": "#1a1a2e",
        }
    
    # ============================================================
    # APLICAR ESTILOS CSS
    # ============================================================
    st.markdown(f"""
    <style>
        /* ============================================================
           ESTILOS GENERALES
           ============================================================ */
        .stApp {{
            background: {COLORS["bg_primary"]};
        }}
        
        /* ============================================================
           HEADER SUPERIOR
           ============================================================ */
        .main-header {{
            background: {COLORS["header_grad"]};
            padding: 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px {COLORS["shadow_color"]};
            flex-wrap: wrap;
            gap: 0.8rem;
        }}
        
        .main-header * {{
            color: {COLORS["text_header"]} !important;
        }}
        
        .main-header .logo-section {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .main-header .logo-icon {{
            font-size: 2.5rem;
            background: rgba(255,255,255,0.1);
            padding: 0.2rem 1rem;
            border-radius: 10px;
        }}
        
        .main-header .title {{
            font-size: 1.6rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        
        .main-header .subtitle {{
            font-size: 0.8rem;
            margin: 0;
            color: {COLORS["text_header_sub"]} !important;
        }}
        
        .main-header .status-section {{
            display: flex;
            align-items: center;
            gap: 1.2rem;
            background: rgba(255,255,255,0.08);
            padding: 0.4rem 1.2rem;
            border-radius: 10px;
            flex-wrap: wrap;
        }}
        
        .main-header .status-badge {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
        }}
        
        .main-header .status-badge .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}
        
        .dot-green {{ background: #2ecc71; }}
        .dot-yellow {{ background: #f1c40f; }}
        .dot-red {{ background: #e74c3c; }}
        .dot-gray {{ background: #7f8c8d; }}
        
        /* ============================================================
           BARRA DE HERRAMIENTAS
           ============================================================ */
        .toolbar {{
            background: {COLORS["bg_secondary"]};
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            margin-bottom: 1.2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            align-items: center;
            box-shadow: 0 2px 10px {COLORS["shadow_color"]};
            border: 1px solid {COLORS["border_color"]};
        }}
        
        .toolbar .tool-group {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .toolbar .divider {{
            width: 1px;
            height: 28px;
            background: {COLORS["border_color"]};
            margin: 0 0.4rem;
        }}
        
        /* ============================================================
           INPUTS Y SELECTORES - CORREGIDO PARA MODO CLARO
           ============================================================ */
        /* Contenedor de inputs */
        .stSelectbox > div, 
        .stNumberInput > div,
        .stTextInput > div,
        .stDateInput > div,
        .stTimeInput > div,
        .stTextArea > div,
        .stFileUploader > div {{
            background: {COLORS["input_bg"]} !important;
            border: 1px solid {COLORS["input_border"]} !important;
            border-radius: 8px !important;
        }}
        
        /* Labels de inputs */
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label,
        .stFileUploader label {{
            color: {COLORS["text_secondary"]} !important;
            font-weight: 500 !important;
        }}
        
        /* Selectores desplegables */
        .stSelectbox [data-baseweb="select"] > div {{
            background: {COLORS["input_bg"]} !important;
            color: {COLORS["input_text"]} !important;
            border: none !important;
        }}
        
        .stSelectbox [data-baseweb="select"] input {{
            color: {COLORS["input_text"]} !important;
            background: {COLORS["input_bg"]} !important;
        }}
        
        /* Inputs numéricos */
        .stNumberInput input {{
            color: {COLORS["input_text"]} !important;
            background: {COLORS["input_bg"]} !important;
            border: none !important;
        }}
        
        /* File Uploader */
        .stFileUploader > div > div {{
            background: {COLORS["input_bg"]} !important;
            border: 1px dashed {COLORS["input_border"]} !important;
            border-radius: 8px !important;
        }}
        
        .stFileUploader > div > div > div {{
            color: {COLORS["text_secondary"]} !important;
        }}
        
        .stFileUploader button {{
            background: {COLORS["btn_primary_bg"]} !important;
            color: {COLORS["btn_primary_text"]} !important;
            border: none !important;
        }}
        
        .stFileUploader button:hover {{
            background: {COLORS["btn_primary_hover"]} !important;
        }}
        
        /* ============================================================
           TARJETAS DE MÉTRICAS
           ============================================================ */
        .metric-card {{
            background: {COLORS["card_bg"]};
            padding: 1rem 1.2rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid {COLORS["border_color"]};
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px {COLORS["shadow_color"]};
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .metric-card .metric-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {COLORS["metric_value"]} !important;
        }}
        
        .metric-card .metric-label {{
            font-size: 0.75rem;
            color: {COLORS["text_secondary"]} !important;
            margin-top: 0.2rem;
        }}
        
        .metric-card:hover {{
            border-color: {COLORS["metric_value"]};
            transform: translateY(-2px);
            box-shadow: 0 4px 15px {COLORS["shadow_color"]};
        }}
        
        /* ============================================================
           SECCIONES DE CONFIGURACIÓN
           ============================================================ */
        .config-section {{
            background: {COLORS["bg_secondary"]};
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            border: 1px solid {COLORS["border_color"]};
            box-shadow: 0 2px 8px {COLORS["shadow_color"]};
        }}
        
        .config-section .section-title {{
            font-size: 1rem;
            font-weight: 600;
            color: {COLORS["section_title"]} !important;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* ============================================================
           PESTAÑAS
           ============================================================ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.3rem;
            background: {COLORS["tab_bg"]};
            padding: 0.4rem;
            border-radius: 10px;
            border: 1px solid {COLORS["border_color"]};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            color: {COLORS["tab_text"]} !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(52,152,219,0.1);
            color: {COLORS["text_primary"]} !important;
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {COLORS["tab_active_bg"]};
            color: {COLORS["tab_active_text"]} !important;
        }}
        
        /* ============================================================
           DATAFRAMES Y TABLAS
           ============================================================ */
        .stDataFrame {{
            border: 1px solid {COLORS["border_color"]};
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .stDataFrame table {{
            font-size: 0.85rem;
        }}
        
        .stDataFrame thead tr th {{
            background: {COLORS["bg_secondary"]} !important;
            color: {COLORS["text_primary"]} !important;
            font-weight: 600 !important;
        }}
        
        .stDataFrame tbody tr td {{
            color: {COLORS["text_secondary"]} !important;
        }}
        
        /* ============================================================
           BOTONES
           ============================================================ */
        .stButton > button {{
            font-size: 0.8rem;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
            background: {COLORS["btn_bg"]};
            color: {COLORS["btn_text"]} !important;
            border: 1px solid {COLORS["border_color"]};
        }}
        
        .stButton > button:hover {{
            background: {COLORS["btn_hover"]};
            border-color: {COLORS["metric_value"]};
        }}
        
        .stButton > button.primary {{
            background: {COLORS["btn_primary_bg"]};
            color: {COLORS["btn_primary_text"]} !important;
            border-color: {COLORS["btn_primary_bg"]};
        }}
        
        .stButton > button.primary:hover {{
            background: {COLORS["btn_primary_hover"]};
            border-color: {COLORS["btn_primary_hover"]};
        }}
        
        /* ============================================================
           EXPANDERS
           ============================================================ */
        .streamlit-expanderHeader {{
            color: {COLORS["expander_text"]} !important;
            background: {COLORS["expander_bg"]} !important;
            border: 1px solid {COLORS["border_color"]} !important;
            border-radius: 8px !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background: rgba(52,152,219,0.05) !important;
        }}
        
        .streamlit-expanderContent {{
            background: {COLORS["bg_secondary"]} !important;
            border: 1px solid {COLORS["border_color"]} !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }}
        
        /* ============================================================
           METRICAS DE STREAMLIT
           ============================================================ */
        [data-testid="metric-container"] {{
            background: {COLORS["card_bg"]};
            border: 1px solid {COLORS["border_color"]};
            border-radius: 10px;
            padding: 0.8rem;
            box-shadow: 0 2px 8px {COLORS["shadow_color"]};
        }}
        
        [data-testid="metric-container"] label {{
            color: {COLORS["text_secondary"]} !important;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* ============================================================
           SELECTOR DE TEMA
           ============================================================ */
        .stSelectbox[data-baseweb="select"] {{
            background: {COLORS["input_bg"]} !important;
        }}
        
        /* ============================================================
           RESPONSIVE
           ============================================================ */
        @media (max-width: 768px) {{
            .main-header {{
                flex-direction: column;
                text-align: center;
                gap: 0.8rem;
            }}
            .main-header .logo-section {{
                flex-direction: column;
            }}
            .toolbar {{
                flex-direction: column;
                align-items: stretch;
            }}
            .toolbar .divider {{
                display: none;
            }}
            .main-header .status-section {{
                justify-content: center;
            }}
        }}
        
        /* ============================================================
           SCROLLBAR PERSONALIZADA
           ============================================================ */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS["bg_secondary"]};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS["metric_value"]};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS["btn_primary_hover"]};
        }}
    </style>
    """, unsafe_allow_html=True)
