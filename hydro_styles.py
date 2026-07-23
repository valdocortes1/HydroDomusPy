# hydro_styles.py
# ================================================================================
#                            H Y D R O   S T Y L E S
# ================================================================================
#                    Estilos CSS unificados para la interfaz
# ================================================================================

import streamlit as st

def apply_enhanced_styles():
    """
    Aplica estilos CSS con paleta de colores consistente para cada tema.
    Esta función es llamada desde app.py después de inicializar el tema.
    """
    # Determinar tema desde session_state (ya inicializado en app.py)
    if 'tema' in st.session_state:
        is_dark = st.session_state.tema == "dark"
    else:
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"
    
    # ============================================================
    # PALETA DE COLORES - DEFINICIÓN ÚNICA Y CONSISTENTE
    # ============================================================
    if is_dark:
        # ---------- MODO OSCURO ----------
        BG_PRIMARY = "#0e1117"
        BG_SECONDARY = "#1e2a3a"
        BG_CARD = "#262730"
        BG_INPUT = "#1a2533"
        BG_BUTTON = "rgba(255,255,255,0.08)"
        BG_TAB = "#1a2533"
        BG_TOOLBAR = "#1e2a3a"
        
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#bbbbbb"
        TEXT_INPUT = "#ffffff"
        TEXT_BUTTON = "#ffffff"
        TEXT_TAB = "#bbbbbb"
        
        BORDER = "#3d3d4d"
        BORDER_INPUT = "#3d3d4d"
        
        BTN_HOVER = "rgba(255,255,255,0.15)"
        TAB_ACTIVE = "#3498db"
        HEADER_GRAD = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
        SHADOW = "rgba(0,0,0,0.3)"
    else:
        # ---------- MODO CLARO ----------
        BG_PRIMARY = "#f0f2f6"
        BG_SECONDARY = "#ffffff"
        BG_CARD = "#ffffff"
        BG_INPUT = "#ffffff"
        BG_BUTTON = "#f0f2f6"
        BG_TAB = "#f0f2f6"
        BG_TOOLBAR = "#ffffff"
        
        TEXT_PRIMARY = "#1a1a2e"
        TEXT_SECONDARY = "#4a4a5a"
        TEXT_INPUT = "#1a1a2e"
        TEXT_BUTTON = "#1a1a2e"
        TEXT_TAB = "#4a4a5a"
        
        BORDER = "#d0d0d0"
        BORDER_INPUT = "#d0d0d0"
        
        BTN_HOVER = "#e0e0e0"
        TAB_ACTIVE = "#3498db"
        HEADER_GRAD = "linear-gradient(135deg, #1a5276, #2471a3, #2e86c1)"
        SHADOW = "rgba(0,0,0,0.08)"
    
    # ============================================================
    # APLICAR ESTILOS CSS
    # ============================================================
    st.markdown(f"""
    <style>
        /* ============================================================
           ESTILOS GENERALES
           ============================================================ */
        .stApp {{
            background: {BG_PRIMARY} !important;
        }}
        
        /* Ocultar sidebar */
        .stSidebar {{
            display: none !important;
        }}
        
        /* ============================================================
           HEADER SUPERIOR
           ============================================================ */
        .main-header {{
            background: {HEADER_GRAD} !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            box-shadow: 0 4px 20px {SHADOW} !important;
            flex-wrap: wrap !important;
            gap: 0.8rem !important;
        }}
        
        .main-header * {{
            color: #ffffff !important;
        }}
        
        .main-header .subtitle {{
            color: rgba(255,255,255,0.7) !important;
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
            background: {BG_TOOLBAR} !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 10px !important;
            margin-bottom: 1.2rem !important;
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.6rem !important;
            align-items: center !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 2px 10px {SHADOW} !important;
        }}
        
        .toolbar .divider {{
            width: 1px !important;
            height: 28px !important;
            background: {BORDER} !important;
            margin: 0 0.4rem !important;
        }}
        
        /* ============================================================
           INPUTS Y SELECTORES
           ============================================================ */
        .stSelectbox > div,
        .stNumberInput > div,
        .stTextInput > div,
        .stFileUploader > div,
        .stDateInput > div,
        .stTimeInput > div {{
            background: {BG_INPUT} !important;
            border: 1px solid {BORDER_INPUT} !important;
            border-radius: 8px !important;
        }}
        
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label,
        .stFileUploader label {{
            color: {TEXT_SECONDARY} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] > div {{
            background: {BG_INPUT} !important;
            color: {TEXT_INPUT} !important;
            border: none !important;
        }}
        
        .stSelectbox [data-baseweb="select"] input {{
            color: {TEXT_INPUT} !important;
            background: {BG_INPUT} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] svg {{
            fill: {TEXT_INPUT} !important;
        }}
        
        .stNumberInput input {{
            color: {TEXT_INPUT} !important;
            background: {BG_INPUT} !important;
            border: none !important;
        }}
        
        .stNumberInput button {{
            background: {BG_INPUT} !important;
            color: {TEXT_INPUT} !important;
            border: 1px solid {BORDER_INPUT} !important;
        }}
        
        .stNumberInput button:hover {{
            background: {BTN_HOVER} !important;
        }}
        
        /* File Uploader */
        .stFileUploader > div > div {{
            background: {BG_INPUT} !important;
            border: 1px dashed {BORDER_INPUT} !important;
            border-radius: 8px !important;
        }}
        
        .stFileUploader > div > div > div {{
            color: {TEXT_SECONDARY} !important;
        }}
        
        .stFileUploader button {{
            background: #3498db !important;
            color: white !important;
            border: none !important;
        }}
        
        .stFileUploader button:hover {{
            background: #2980b9 !important;
        }}
        
        /* ============================================================
           BOTONES
           ============================================================ */
        .stButton > button {{
            background: {BG_BUTTON} !important;
            color: {TEXT_BUTTON} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            padding: 0.3rem 0.8rem !important;
            font-size: 0.8rem !important;
        }}
        
        .stButton > button:hover {{
            background: {BTN_HOVER} !important;
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
            background: {BG_CARD} !important;
            padding: 1rem !important;
            border-radius: 12px !important;
            text-align: center !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 2px 8px {SHADOW} !important;
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
            color: {TEXT_SECONDARY} !important;
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
            background: {BG_SECONDARY} !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 2px 8px {SHADOW} !important;
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
            background: {BG_TAB} !important;
            padding: 0.4rem !important;
            border-radius: 10px !important;
            border: 1px solid {BORDER} !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            color: {TEXT_TAB} !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(52,152,219,0.1) !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {TAB_ACTIVE} !important;
            color: white !important;
        }}
        
        /* ============================================================
           DATAFRAMES
           ============================================================ */
        .stDataFrame {{
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        
        .stDataFrame thead tr th {{
            background: {BG_SECONDARY} !important;
            color: {TEXT_PRIMARY} !important;
            font-weight: 600 !important;
        }}
        
        .stDataFrame tbody tr td {{
            color: {TEXT_SECONDARY} !important;
        }}
        
        /* ============================================================
           EXPANDERS
           ============================================================ */
        .streamlit-expanderHeader {{
            color: {TEXT_PRIMARY} !important;
            background: {BG_SECONDARY} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background: rgba(52,152,219,0.05) !important;
        }}
        
        .streamlit-expanderContent {{
            background: {BG_SECONDARY} !important;
            border: 1px solid {BORDER} !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }}
        
        /* ============================================================
           METRICAS DE STREAMLIT
           ============================================================ */
        [data-testid="metric-container"] {{
            background: {BG_CARD} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
            padding: 0.8rem !important;
            box-shadow: 0 2px 8px {SHADOW} !important;
        }}
        
        [data-testid="metric-container"] label {{
            color: {TEXT_SECONDARY} !important;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* ============================================================
           SCROLLBAR
           ============================================================ */
        ::-webkit-scrollbar {{
            width: 6px !important;
            height: 6px !important;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {BG_SECONDARY} !important;
            border-radius: 3px !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #3498db !important;
            border-radius: 3px !important;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #2980b9 !important;
        }}
        
        /* ============================================================
           RESPONSIVE
           ============================================================ */
        @media (max-width: 768px) {{
            .main-header {{
                flex-direction: column !important;
                text-align: center !important;
                gap: 0.8rem !important;
            }}
            .main-header .logo-section {{
                flex-direction: column !important;
            }}
            .toolbar {{
                flex-direction: column !important;
                align-items: stretch !important;
            }}
            .toolbar .divider {{
                display: none !important;
            }}
            .main-header .status-section {{
                justify-content: center !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
