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
        # Fallback al tema del sistema
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"
    
    # Paleta de colores según tema
    if is_dark:
        bg_primary = "#0e1117"
        bg_secondary = "#1e2a3a"
        card_bg = "#262730"
        border_color = "#3d3d4d"
        shadow_color = "rgba(0,0,0,0.3)"
        text_primary = "#ffffff"
        text_secondary = "#bbbbbb"
        text_muted = "#888888"
        header_grad = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    else:
        bg_primary = "#f0f2f6"
        bg_secondary = "#ffffff"
        card_bg = "#ffffff"
        border_color = "#e0e0e0"
        shadow_color = "rgba(0,0,0,0.08)"
        text_primary = "#1a1a2e"
        text_secondary = "#555555"
        text_muted = "#888888"
        header_grad = "linear-gradient(135deg, #1a5276, #2471a3, #2e86c1)"
    
    st.markdown(f"""
    <style>
        /* ============================================================
           ESTILOS GENERALES
           ============================================================ */
        .stApp {{
            background: {bg_primary};
        }}
        
        /* Ocultar sidebar */
        .stSidebar {{
            display: none !important;
        }}
        
        /* ============================================================
           HEADER SUPERIOR
           ============================================================ */
        .main-header {{
            background: {header_grad};
            padding: 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px {shadow_color};
            flex-wrap: wrap;
            gap: 0.8rem;
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
            color: {text_primary};
            font-size: 1.6rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        
        .main-header .subtitle {{
            color: rgba(255,255,255,0.7);
            font-size: 0.8rem;
            margin: 0;
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
            color: {text_primary};
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
            background: {bg_secondary};
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            margin-bottom: 1.2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            align-items: center;
            box-shadow: 0 2px 10px {shadow_color};
            border: 1px solid {border_color};
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
            background: {border_color};
            margin: 0 0.4rem;
        }}
        
        .toolbar .tool-label {{
            color: {text_secondary};
            font-size: 0.8rem;
        }}
        
        /* ============================================================
           TARJETAS DE MÉTRICAS
           ============================================================ */
        .metric-card {{
            background: {card_bg};
            padding: 1rem 1.2rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid {border_color};
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px {shadow_color};
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .metric-card:hover {{
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px {shadow_color};
        }}
        
        .metric-card .metric-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #3498db;
        }}
        
        .metric-card .metric-label {{
            font-size: 0.75rem;
            color: {text_secondary};
            margin-top: 0.2rem;
        }}
        
        /* ============================================================
           SECCIONES DE CONFIGURACIÓN
           ============================================================ */
        .config-section {{
            background: {bg_secondary};
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            border: 1px solid {border_color};
            box-shadow: 0 2px 8px {shadow_color};
        }}
        
        .config-section .section-title {{
            font-size: 1rem;
            font-weight: 600;
            color: #3498db;
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
            background: {bg_secondary};
            padding: 0.4rem;
            border-radius: 10px;
            border: 1px solid {border_color};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            color: {text_secondary};
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(52,152,219,0.1);
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: #3498db;
            color: white;
        }}
        
        /* ============================================================
           DATAFRAMES Y TABLAS
           ============================================================ */
        .stDataFrame {{
            border: 1px solid {border_color};
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .stDataFrame table {{
            font-size: 0.85rem;
        }}
        
        .stDataFrame thead tr th {{
            background: {bg_secondary} !important;
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}
        
        /* ============================================================
           INPUTS Y CONTROLES
           ============================================================ */
        .stSelectbox > div, .stNumberInput > div {{
            background: {bg_secondary};
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        .stSelectbox label, .stNumberInput label {{
            color: {text_secondary} !important;
        }}
        
        /* ============================================================
           TEXTOS Y COLORES
           ============================================================ */
        .text-primary {{
            color: {text_primary};
        }}
        
        .text-secondary {{
            color: {text_secondary};
        }}
        
        .text-muted {{
            color: {text_muted};
        }}
        
        /* ============================================================
           BOTONES EN TOOLBAR
           ============================================================ */
        .stButton > button {{
            font-size: 0.8rem;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
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
            background: {bg_secondary};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #3498db;
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #2980b9;
        }}
    </style>
    """, unsafe_allow_html=True)
