# hydro_ui.py
# ================================================================================
#                            H Y D R O   U I
# ================================================================================
#                    Componentes reutilizables de interfaz
# ================================================================================

import streamlit as st
import json
import datetime
import pandas as pd

from hydro_core import (
    TIPOS_OCUPACION_AGUA, UNIDADES_GASTO, DIAMETROS_PAVCO,
    ajustar_cotas_relativas
)
from hydro_utils import cargar_y_aplicar_configuracion, generar_configuracion_json

# ================================================================================
# COMPONENTE: METODOLOGÍA
# ================================================================================

def mostrar_metodologia():
    """Muestra la metodología de cálculo con fórmulas en formato LaTeX"""
    with st.expander("📚 Metodología y Bases de Cálculo", expanded=False):
        st.markdown(r"""
        ### 🔬 Fundamentos del Análisis Hidráulico
        
        El simulador utiliza modelos matemáticos de alta precisión para el diseño de redes hidrosanitarias, 
        superando las limitaciones de ecuaciones empíricas tradicionales.
        
        ---
        
        #### 1. 📐 Pérdidas por Fricción (Darcy-Weisbach)
        
        Utiliza la ecuación universal para un cálculo exacto basado en la conservación de energía y la geometría del tramo:
        
        $$h_f = f \cdot \frac{L}{D} \cdot \frac{v^2}{2g}$$
        
        **Donde:**
        - $h_f$ = Pérdida de carga (mca)
        - $f$ = Factor de fricción (adimensional)
        - $L$ = Longitud de la tubería (m)
        - $D$ = Diámetro interno (m)
        - $v$ = Velocidad del flujo (m/s)
        - $g$ = Aceleración de la gravedad (9.81 m/s²)
        
        ---
        
        #### 2. 🔄 Factor de Fricción (Colebrook-White)
        
        Resuelve dinámicamente el factor de fricción $f$ en régimen turbulento mediante métodos numéricos iterativos (Newton-Raphson):
        
        $$\frac{1}{\sqrt{f}} = -2 \log_{10} \left( \frac{\epsilon}{3.71D} + \frac{2.51}{Re \sqrt{f}} \right)$$
        
        **Donde:**
        - $\epsilon$ = Rugosidad absoluta del PVC (0.0015 mm)
        - $Re$ = Número de Reynolds (calculado en tiempo real)
        - $Re = \frac{v \cdot D}{\nu}$ (con $\nu$ = viscosidad cinemática del agua)
        
        ---
        
        #### 3. 📊 Caudales de Diseño (Método de Hunter)
        
        Asigna caudales probabilísticos mediante un recorrido topológico en árbol (Búsqueda en Anchura - BFS):
        
        $$Q = a \cdot \sqrt{UG} + b$$
        
        **Donde:**
        - $UG$ = Unidades de Gasto acumuladas
        - $a, b$ = Coeficientes según tipo de edificación
        
        | Tipo de Edificación | Coeficiente a | Coeficiente b |
        |---------------------|---------------|---------------|
        | Vivienda Unifamiliar | 0.20 | 0.50 |
        | Vivienda Multifamiliar | 0.25 | 0.60 |
        | Edificio de Oficinas | 0.15 | 0.30 |
        | Hotel / Hostería | 0.18 | 0.40 |
        | Hospital / Clínica | 0.22 | 0.70 |
        | Centro Comercial | 0.12 | 0.40 |
        
        ---
        
        #### 4. 🔧 Pérdidas Localizadas (Longitudes Equivalentes)
        
        Transforma la resistencia de accesorios (codos, tees, válvulas) en Longitudes Equivalentes ($Leq$) que se suman al modelo lineal:
        
        $$Leq = K \cdot \frac{D}{f}$$
        
        | Accesorio | Longitud Equivalente (m) |
        |-----------|--------------------------|
        | Tee | 1.5 |
        | Codo 90° | 0.8 |
        | Codo 45° | 0.5 |
        | Reducción | 0.5 |
        | Válvula Compuerta | 0.3 |
        | Válvula Globo | 1.5 |
        | Válvula Check | 2.5 |
        | Válvula Esfera | 0.2 |
        
        ---
        
        #### 5. 🚪 Estrangulamiento de Válvulas
        
        Modela cierres parciales aplicando una penalización cuadrática a la longitud equivalente de la válvula:
        
        $$Leq_{efectivo} = Leq_{base} \cdot \left(\frac{100}{Apertura}\right)^2$$
        
        **Ejemplo práctico:**
        - Válvula al 100%: Factor = 1.0 (pérdida normal)
        - Válvula al 50%: Factor = 4.0 (pérdida 4x mayor)
        - Válvula al 25%: Factor = 16.0 (pérdida 16x mayor)
        """)

# ================================================================================
# COMPONENTE: CONFIGURACIÓN DE NODOS
# ================================================================================

def panel_configuracion_nodos(red, tipo_ocupacion, presion_entrada, unidad_dibujo):
    """
    Panel de configuración de nodos con carga/guardado de JSON
    y actualización de interfaz
    """
    st.markdown("### 📌 Configuración de Nodos")
    
    # ===== CARGA DE CONFIGURACIÓN =====
    col_load, col_save = st.columns([1, 1])
    
    with col_load:
        config_file = st.file_uploader(
            "📂 Cargar configuración (.json)",
            type=["json"],
            help="Cargue una configuración guardada anteriormente",
            key="config_uploader"
        )
        
        if config_file is not None:
            try:
                config_data = json.load(config_file)
                if cargar_y_aplicar_configuracion(red, config_data):
                    st.success("✅ Configuración cargada exitosamente")
                    st.rerun()
            except Exception as e:
                st.error(f"Error cargando configuración: {e}")
    
    # ===== TABLA DE CONFIGURACIÓN =====
    nodos_ids = list(red.nodos.keys())
    
    # Preparar datos para el DataEditor
    aparatos_list = []
    valvulas_list = []
    aperturas_list = []
    entrada_list = []
    
    for nid in nodos_ids:
        nodo = red.nodos[nid]
        aparatos_list.append(nodo.tipo_aparato or "")
        valvulas_list.append(nodo.valvula_tipo or "")
        aperturas_list.append(nodo.valvula_apertura if nodo.valvula_tipo else 100.0)
        entrada_list.append("✓" if nodo.es_entrada else "")
    
    df_config = pd.DataFrame({
        "ID Nodo": nodos_ids,
        "Entrada": entrada_list,
        "Aparato": aparatos_list,
        "Válvula": valvulas_list,
        "Apertura (%)": aperturas_list
    })
    
    edited_df = st.data_editor(
        df_config,
        column_config={
            "ID Nodo": st.column_config.Column("ID Nodo", disabled=True),
            "Entrada": st.column_config.Column("Entrada", disabled=True),
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
                min_value=0,
                max_value=100,
                step=5
            )
        },
        disabled=["ID Nodo", "Entrada"],
        use_container_width=True,
        hide_index=True,
        key="nodos_editor"
    )
    
    # ===== GUARDAR CONFIGURACIÓN =====
    with col_save:
        if st.button("💾 Guardar Configuración", use_container_width=True, key="save_config"):
            # Aplicar cambios a la red
            for _, row in edited_df.iterrows():
                nid = row["ID Nodo"]
                if nid in red.nodos:
                    red.nodos[nid].tipo_aparato = row["Aparato"] if row["Aparato"] else ""
                    red.nodos[nid].valvula_tipo = row["Válvula"] if row["Válvula"] else ""
                    red.nodos[nid].valvula_apertura = float(row["Apertura (%)"])
            
            # Generar configuración
            config = generar_configuracion_json(red, tipo_ocupacion, presion_entrada, unidad_dibujo)
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            
            # Botón de descarga
            st.download_button(
                label="📥 Descargar JSON",
                data=config_json,
                file_name=f"HydroDomusPy_config_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_config"
            )
            st.success("✅ Configuración guardada")
    
    # ===== ASIGNACIÓN RÁPIDA =====
    st.markdown("---")
    st.markdown("### ⚡ Asignación Rápida")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nodo_seleccionado = st.selectbox(
            "Seleccionar nodo:",
            options=nodos_ids,
            format_func=lambda x: f"Nodo {x}",
            key="nodo_rapido"
        )
    
    with col2:
        tipo_aparato = st.selectbox(
            "Asignar aparato:",
            options=[""] + list(UNIDADES_GASTO.keys()),
            key="aparato_rapido"
        )
        
        if tipo_aparato and st.button("📌 Asignar Aparato", key="btn_aparato"):
            if nodo_seleccionado == red.nodo_entrada_id:
                st.error("⚠️ El nodo de entrada no puede tener aparato")
            else:
                red.nodos[nodo_seleccionado].tipo_aparato = tipo_aparato
                st.success(f"✅ Aparato '{tipo_aparato}' asignado al nodo {nodo_seleccionado}")
                st.rerun()
    
    with col3:
        tipo_valvula = st.selectbox(
            "Asignar válvula:",
            options=["", "Compuerta", "Globo", "Check", "Esfera"],
            key="valvula_rapida"
        )
        apertura = st.slider(
            "Apertura (%)",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
            key="apertura_rapida"
        )
        
        if tipo_valvula and st.button("🔧 Asignar Válvula", key="btn_valvula"):
            red.nodos[nodo_seleccionado].valvula_tipo = tipo_valvula
            red.nodos[nodo_seleccionado].valvula_apertura = apertura
            st.success(f"✅ Válvula '{tipo_valvula}' al {apertura}% asignada al nodo {nodo_seleccionado}")
            st.rerun()
    
    # ===== RESUMEN DE CONFIGURACIÓN =====
    st.markdown("---")
    st.markdown("### 📊 Resumen de Configuración")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        aparatos_asignados = sum(1 for n in red.nodos.values() if n.tipo_aparato)
        st.metric("📌 Aparatos", aparatos_asignados)
    
    with col2:
        valvulas_asignadas = sum(1 for n in red.nodos.values() if n.valvula_tipo)
        st.metric("🔧 Válvulas", valvulas_asignadas)
    
    with col3:
        valvulas_cerradas = sum(1 for n in red.nodos.values() if n.valvula_apertura == 0)
        st.metric("🚫 Válvulas cerradas", valvulas_cerradas)
    
    with col4:
        ug_total = sum(UNIDADES_GASTO.get(n.tipo_aparato, {}).get("ug", 0) 
                      for n in red.nodos.values() if n.tipo_aparato)
        st.metric("📊 UG totales", f"{ug_total:.0f}")
