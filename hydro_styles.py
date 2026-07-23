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
    """
    # ============================================================
    # DETERMINAR TEMA - CON FALLBACK SEGURO
    # ============================================================
    # Intentar obtener el tema de session_state
    if 'tema' in st.session_state:
        is_dark = st.session_state.tema == "dark"
    else:
        # Fallback: intentar obtener del sistema
        try:
            theme = st.get_option("theme.base")
            is_dark = theme == "dark"
        except:
            is_dark = True  # Por defecto, oscuro
    
    # ============================================================
    # PALETA DE COLORES
    # ============================================================
    if is_dark:
        # MODO OSCURO
        bg_primary = "#0e1117"
        bg_secondary = "#1a2533"
        card_bg = "#262730"
        border_color = "#3d3d4d"
        shadow = "0 2px 10px rgba(0,0,0,0.3)"
        text_primary = "#ffffff"
        text_secondary = "#bbbbbb"
        text_muted = "#888888"
        input_bg = "#1a2533"
        input_text = "#ffffff"
        input_border = "#3d3d4d"
        btn_bg = "rgba(255,255,255,0.08)"
        btn_text = "#ffffff"
        btn_hover = "rgba(255,255,255,0.15)"
        tab_bg = "#1a2533"
        tab_text = "#bbbbbb"
        tab_active = "#3498db"
        header_grad = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
        header_text = "#ffffff"
        header_sub = "rgba(255,255,255,0.7)"
        metric_color = "#3498db"
    else:
        # MODO CLARO
        bg_primary = "#f0f2f6"
        bg_secondary = "#ffffff"
        card_bg = "#ffffff"
        border_color = "#d0d0d0"
        shadow = "0 2px 10px rgba(0,0,0,0.08)"
        text_primary = "#1a1a2e"
        text_secondary = "#4a4a5a"
        text_muted = "#7a7a8a"
        input_bg = "#ffffff"
        input_text = "#1a1a2e"
        input_border = "#d0d0d0"
        btn_bg = "#f0f2f6"
        btn_text = "#1a1a2e"
        btn_hover = "#e0e0e0"
        tab_bg = "#f0f2f6"
        tab_text = "#4a4a5a"
        tab_active = "#3498db"
        header_grad = "linear-gradient(135deg, #1a5276, #2471a3, #2e86c1)"
        header_text = "#ffffff"
        header_sub = "rgba(255,255,255,0.85)"
        metric_color = "#3498db"
    
    # ============================================================
    # APLICAR ESTILOS CSS - CON !important PARA SOBRESCRIBIR
    # ============================================================
    st.markdown(f"""
    <style>
        /* ============================================================
           ESTILOS GENERALES
           ============================================================ */
        .stApp {{
            background: {bg_primary} !important;
        }}
        
        .stApp * {{
            color: {text_primary} !important;
        }}
        
        /* Excepción para elementos que deben mantener su color */
        .stApp .dot-green {{ background: #2ecc71; color: white !important; }}
        .stApp .dot-yellow {{ background: #f1c40f; color: white !important; }}
        .stApp .dot-red {{ background: #e74c3c; color: white !important; }}
        .stApp .dot-gray {{ background: #7f8c8d; color: white !important; }}
        
        /* Ocultar sidebar */
        .stSidebar {{
            display: none !important;
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
            color: {header_text} !important;
        }}
        
        .main-header .logo-section {{
            display: flex !important;
            align-items: center !important;
            gap: 1rem !important;
        }}
        
        .main-header .logo-icon {{
            font-size: 2.5rem !important;
            background: rgba(255,255,255,0.1) !important;
            padding: 0.2rem 1rem !important;
            border-radius: 10px !important;
        }}
        
        .main-header .title {{
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }}
        
        .main-header .subtitle {{
            font-size: 0.8rem !important;
            margin: 0 !important;
            color: {header_sub} !important;
        }}
        
        .main-header .status-section {{
            display: flex !important;
            align-items: center !important;
            gap: 1.2rem !important;
            background: rgba(255,255,255,0.08) !important;
            padding: 0.4rem 1.2rem !important;
            border-radius: 10px !important;
            flex-wrap: wrap !important;
        }}
        
        .main-header .status-badge {{
            display: flex !important;
            align-items: center !important;
            gap: 0.4rem !important;
            font-size: 0.8rem !important;
        }}
        
        /* ============================================================
           BARRA DE HERRAMIENTAS
           ============================================================ */
        .toolbar {{
            background: {bg_secondary} !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 10px !important;
            margin-bottom: 1.2rem !important;
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.6rem !important;
            align-items: center !important;
            box-shadow: {shadow} !important;
            border: 1px solid {border_color} !important;
        }}
        
        .toolbar .tool-group {{
            display: flex !important;
            gap: 0.5rem !important;
            align-items: center !important;
            flex-wrap: wrap !important;
        }}
        
        .toolbar .divider {{
            width: 1px !important;
            height: 28px !important;
            background: {border_color} !important;
            margin: 0 0.4rem !important;
        }}
        
        /* ============================================================
           INPUTS Y SELECTORES - CORREGIDO
           ============================================================ */
        /* Contenedor de inputs */
        .stSelectbox > div,
        .stNumberInput > div,
        .stTextInput > div,
        .stTextArea > div,
        .stFileUploader > div,
        .stDateInput > div,
        .stTimeInput > div {{
            background: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
            color: {input_text} !important;
        }}
        
        /* Labels de inputs */
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label,
        .stFileUploader label {{
            color: {text_secondary} !important;
            font-weight: 500 !important;
        }}
        
        /* Selectores desplegables */
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
            fill: {text_secondary} !important;
        }}
        
        /* Inputs numéricos */
        .stNumberInput input {{
            color: {input_text} !important;
            background: {input_bg} !important;
            border: none !important;
        }}
        
        /* File Uploader */
        .stFileUploader > div > div {{
            background: {input_bg} !important;
            border: 1px dashed {input_border} !important;
            border-radius: 8px !important;
        }}
        
        .stFileUploader > div > div > div {{
            color: {text_secondary} !important;
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
           TARJETAS DE MÉTRICAS
           ============================================================ */
        .metric-card {{
            background: {card_bg} !important;
            padding: 1rem 1.2rem !important;
            border-radius: 12px !important;
            text-align: center !important;
            border: 1px solid {border_color} !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            min-height: 80px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        
        .metric-card .metric-value {{
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: {metric_color} !important;
        }}
        
        .metric-card .metric-label {{
            font-size: 0.75rem !important;
            color: {text_secondary} !important;
            margin-top: 0.2rem !important;
        }}
        
        .metric-card:hover {{
            border-color: {metric_color} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
        }}
        
        /* ============================================================
           SECCIONES DE CONFIGURACIÓN
           ============================================================ */
        .config-section {{
            background: {bg_secondary} !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            border: 1px solid {border_color} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }}
        
        .config-section .section-title {{
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: {metric_color} !important;
            margin-bottom: 0.8rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }}
        
        /* ============================================================
           PESTAÑAS
           ============================================================ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.3rem !important;
            background: {tab_bg} !important;
            padding: 0.4rem !important;
            border-radius: 10px !important;
            border: 1px solid {border_color} !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            color: {tab_text} !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(52,152,219,0.1) !important;
            color: {text_primary} !important;
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {tab_active} !important;
            color: white !important;
        }}
        
        /* ============================================================
           DATAFRAMES Y TABLAS
           ============================================================ */
        .stDataFrame {{
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        
        .stDataFrame thead tr th {{
            background: {bg_secondary} !important;
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}
        
        .stDataFrame tbody tr td {{
            color: {text_secondary} !important;
        }}
        
        /* ============================================================
           BOTONES
           ============================================================ */
        .stButton > button {{
            font-size: 0.8rem !important;
            padding: 0.3rem 0.8rem !important;
            border-radius: 8px !important;
            background: {btn_bg} !important;
            color: {btn_text} !important;
            border: 1px solid {border_color} !important;
        }}
        
        .stButton > button:hover {{
            background: {btn_hover} !important;
            border-color: {metric_color} !important;
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
           EXPANDERS
           ============================================================ */
        .streamlit-expanderHeader {{
            color: {text_primary} !important;
            background: {bg_secondary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background: rgba(52,152,219,0.05) !important;
        }}
        
        .streamlit-expanderContent {{
            background: {bg_secondary} !important;
            border: 1px solid {border_color} !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }}
        
        /* ============================================================
           METRICAS DE STREAMLIT
           ============================================================ */
        [data-testid="metric-container"] {{
            background: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
            padding: 0.8rem !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }}
        
        [data-testid="metric-container"] label {{
            color: {text_secondary} !important;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            color: {text_primary} !important;
        }}
        
        /* ============================================================
           SELECTOR DE TEMA
           ============================================================ */
        .stSelectbox[data-baseweb="select"] {{
            background: {input_bg} !important;
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
        
        /* ============================================================
           SCROLLBAR PERSONALIZADA
           ============================================================ */
        ::-webkit-scrollbar {{
            width: 6px !important;
            height: 6px !important;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {bg_secondary} !important;
            border-radius: 3px !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {metric_color} !important;
            border-radius: 3px !important;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #2980b9 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Guardar estado de estilos aplicados
    st.session_state.style_applied = True
