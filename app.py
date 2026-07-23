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
import math
import traceback

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
# FUNCIÓN PARA DETECTAR SINCRONIZACIÓN DESDE LA INTERFAZ 3D
# ================================================================================

def detectar_sincronizacion_3d():
    """
    Detecta si hay una solicitud de sincronización desde la interfaz 3D.
    """
    query_params = st.query_params
    
    # Verificar si hay un parámetro 'sync' en la URL
    if 'sync' in query_params:
        # Limpiar el parámetro
        st.query_params.clear()
        
        # Intentar obtener la configuración de session_state
        if 'config_3d' in st.session_state and st.session_state.config_3d:
            config = st.session_state.config_3d
            if st.session_state.red:
                for nodo_cfg in config.get("nodos", []):
                    nid = nodo_cfg.get("id")
                    if nid in st.session_state.red.nodos:
                        nodo = st.session_state.red.nodos[nid]
                        nodo.es_entrada = nodo_cfg.get("es_entrada", False)
                        nodo.tipo_aparato = nodo_cfg.get("tipo_aparato", "")
                        nodo.valvula_tipo = nodo_cfg.get("valvula_tipo", "")
                        nodo.valvula_cerrada = nodo_cfg.get("valvula_cerrada", False)
                        nodo.valvula_apertura = nodo_cfg.get("valvula_apertura", 100.0)
                
                if config.get("nodo_entrada") is not None:
                    st.session_state.red.nodo_entrada_id = config["nodo_entrada"]
                
                st.session_state.config_3d = None
                st.session_state.config_actualizada = True
                st.success("✅ ¡Configuración sincronizada desde la interfaz 3D!")
                
                # 👇 IMPORTANTE: Usar st.rerun() en lugar de recargar la página
                st.rerun()
        return True
    
    return False


if detectar_sincronizacion_3d():
    # Si se detectó sincronización, la función ya manejó la actualización
    pass
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
# FUNCIÓN PARA CONFIGURACIÓN 3D INTERACTIVA
# ================================================================================

def generar_html_config(nodos_data, tuberias_data):
    """Genera HTML para la configuración interactiva de nodos con sincronización directa"""
    
    if not nodos_data or not tuberias_data:
        return "<p style='color:red;'>⚠️ Error: No hay datos de red para mostrar</p>"
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Hydro Domus Py - Configuración</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
body{{margin:0;font-family:Segoe UI,sans-serif;background:#1e1e1e;color:#ffffff}}
#header{{background:#2c3e50;color:white;padding:15px;text-align:center}}
#header h1{{margin:0;font-size:1.5em}}
#header p{{margin:5px 0 0;font-size:0.9em}}
#main{{position:fixed;top:80px;left:0;right:200px;bottom:0}}
#sidebar{{position:fixed;top:80px;right:0;width:200px;bottom:0;background:#2d2d2d;padding:12px;overflow-y:auto;font-size:11px;box-shadow:-2px 0 10px rgba(0,0,0,0.3)}}
#sidebar h3{{margin-top:0;color:#3498db;font-size:14px}}
.btn{{background:#3498db;color:white;border:none;padding:6px 10px;border-radius:6px;cursor:pointer;margin:4px;font-size:11px;transition:all 0.3s}}
.btn:hover{{background:#2980b9;transform:scale(1.02)}}
.btn-success{{background:#27ae60}}
.btn-success:hover{{background:#229954}}
.btn-danger{{background:#e74c3c}}
.btn-danger:hover{{background:#c0392b}}
.btn-secondary{{background:#7f8c8d}}
.btn-secondary:hover{{background:#5d6d7e}}
.btn-sync{{background:#8e44ad}}
.btn-sync:hover{{background:#6c3483}}
.btn-sync.active{{background:#27ae60;animation:pulse 1s ease-in-out}}
@keyframes pulse{{0%{{transform:scale(1)}}50%{{transform:scale(1.05)}}100%{{transform:scale(1)}}}}
.badge-entrada{{background:#e74c3c;color:white;padding:2px 8px;border-radius:12px;font-size:10px;display:inline-block;margin:2px}}
.badge-aparato{{background:#3498db;color:white;padding:2px 8px;border-radius:12px;font-size:10px;display:inline-block;margin:2px}}
.badge-valvula{{background:#e67e22;color:white;padding:2px 8px;border-radius:12px;font-size:10px;display:inline-block;margin:2px}}
.info-nodo{{background:#3d3d3d;border-radius:8px;padding:10px;margin-bottom:10px;border:1px solid #444444;color:#ffffff}}
.info-nodo h4{{margin:0 0 6px 0;color:#3498db;font-size:12px}}
.info-nodo p{{margin:4px 0;font-size:10px;color:#aaaaaa}}
select{{font-size:10px;padding:3px;margin:3px 0;width:100%;border-radius:4px;border:1px solid #444444;background:#2d2d2d;color:#ffffff}}
input[type="range"]{{width:100%;margin:5px 0;accent-color:#3498db}}
.file-input{{display:none}}
.upload-area{{border:2px dashed #444;border-radius:8px;padding:8px;text-align:center;cursor:pointer;margin:5px 0;font-size:10px;color:#aaaaaa;transition:all 0.3s}}
.upload-area:hover{{border-color:#3498db;background:rgba(52,152,219,0.1)}}
hr{{margin:8px 0;border-color:#444444}}
label{{color:#ffffff}}
.sync-status{{font-size:9px;color:#888;text-align:center;margin:2px 0}}
</style>
</head>
<body>
<div id="header"><h1>💧 Hydro Domus Py - Configuración Interactiva</h1><p>Haga clic en cualquier nodo para configurarlo</p></div>
<div id="main"></div>
<div id="sidebar">
<h3>📋 Configuración</h3>
<div id="info-panel"><p style="font-size:11px; color:#aaaaaa">✨ Haga clic en un nodo del gráfico 3D</p></div>

<!-- Botón de sincronización directa -->
<div style="margin-top:8px;">
    <button class="btn btn-sync" onclick="sincronizarTablaDirecta()" id="syncBtn" style="width:100%; font-size:11px; padding:6px;">
        🔄 Sincronizar con Tabla Manual
    </button>
    <p class="sync-status" id="syncStatus">Click para actualizar la tabla manual con la configuración actual</p>
</div>

<!-- Área de carga de configuración -->
<div style="margin-top:8px; border:1px solid #444; border-radius:6px; padding:6px;">
    <div style="display:flex; gap:4px; align-items:center; flex-wrap:wrap;">
        <button class="btn btn-secondary" onclick="document.getElementById('fileInput').click()" style="flex:1; font-size:10px; padding:4px 6px;">📂 Cargar JSON</button>
        <input type="file" id="fileInput" class="file-input" accept=".json" onchange="cargarConfiguracion(event)">
        <span style="font-size:8px; color:#666;" id="fileStatus">Ningún archivo cargado</span>
    </div>
</div>

<div style="text-align:center; margin-top:8px">
<button class="btn btn-success" onclick="guardar()" style="width:95%">💾 Guardar Configuración</button>
<button class="btn btn-danger" onclick="resetear()" style="width:95%; margin-top:4px">🔄 Resetear todo</button>
</div>
<hr>
<div id="resumen" style="font-size:11px; background:#3d3d3d; padding:8px; border-radius:6px;"></div>
<p style="font-size:8px; color:#999; text-align:center; margin-top:10px">Hydro Domus Py v1.0.0<br>NTC 1500 - RAS</p>
</div>
<script>
// ============================================================
// DATOS DE LA RED (convertidos a JSON)
// ============================================================
const nodos = {json.dumps(nodos_data)};
const tuberias = {json.dumps(tuberias_data)};
const aparatos = {json.dumps(list(UNIDADES_GASTO.keys()))};

console.log("Nodos cargados:", nodos.length);
console.log("Tuberías cargadas:", tuberias.length);

let entradaId = null;
let nodoSeleccionado = null;
let currentCamera = null;

// ============================================================
// FUNCIÓN PARA SINCRONIZAR DIRECTAMENTE CON LA TABLA MANUAL
// ============================================================
function sincronizarTablaDirecta() {{
    const btn = document.getElementById('syncBtn');
    const status = document.getElementById('syncStatus');
    
    // Crear objeto de configuración actual
    const config = {{
        nodo_entrada: entradaId,
        nodos: nodos.map(n => ({{
            id: n.id,
            es_entrada: n.id === entradaId,
            tipo_aparato: n.tipo_aparato,
            valvula_tipo: n.valvula_tipo,
            valvula_cerrada: n.valvula_cerrada || false,
            valvula_apertura: n.valvula_apertura !== undefined ? n.valvula_apertura : 100
        }}))
    }};
    
    // Guardar en localStorage para que Streamlit lo pueda leer
    try {{
        localStorage.setItem('hydro_config_3d', JSON.stringify(config));
        console.log("✅ Configuración guardada en localStorage");
    }} catch(e) {{
        console.warn("Error guardando en localStorage:", e);
    }}
    
    // Feedback visual
    btn.classList.add('active');
    status.innerHTML = '✅ ¡Configuración sincronizada!';
    status.style.color = '#2ecc71';
    
    // 👇 IMPORTANTE: Recargar la página padre (Streamlit), no el iframe
    setTimeout(() => {{
        try {{
            // Intentar recargar la página padre (Streamlit)
            window.parent.location.reload();
        }} catch(e) {{
            // Fallback: recargar la página actual
            window.location.reload();
        }}
    }}, 300);
}}

// ============================================================
// FUNCIÓN PARA CARGAR CONFIGURACIÓN DESDE JSON (archivo)
// ============================================================
function cargarConfiguracion(event) {{
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {{
        try {{
            const config = JSON.parse(e.target.result);
            document.getElementById('fileStatus').innerHTML = '✅ Cargado: ' + file.name;
            aplicarConfiguracion(config);
        }} catch (error) {{
            alert('❌ Error al leer el archivo JSON: ' + error.message);
        }}
    }};
    reader.readAsText(file);
    event.target.value = '';
}}

function aplicarConfiguracion(config) {{
    entradaId = null;
    for(const n of nodos) {{
        n.es_entrada = false;
        n.tipo_aparato = "";
        n.valvula_tipo = "";
        n.valvula_cerrada = false;
        n.valvula_apertura = 100;
    }}
    
    const nodoEntrada = config.nodo_entrada;
    if (nodoEntrada !== undefined && nodoEntrada !== null) {{
        const entrada = nodos.find(n => n.id === nodoEntrada);
        if(entrada) {{
            entrada.es_entrada = true;
            entradaId = nodoEntrada;
        }}
    }}
    
    for(const nodoConfig of config.nodos) {{
        const nodo = nodos.find(n => n.id === nodoConfig.id);
        if(nodo) {{
            if(nodoConfig.tipo_aparato) nodo.tipo_aparato = nodoConfig.tipo_aparato;
            if(nodoConfig.valvula_tipo) {{
                nodo.valvula_tipo = nodoConfig.valvula_tipo;
                nodo.valvula_cerrada = nodoConfig.valvula_cerrada || false;
                nodo.valvula_apertura = nodoConfig.valvula_apertura !== undefined ? nodoConfig.valvula_apertura : 100;
            }}
            if(nodoConfig.es_entrada) {{
                nodo.es_entrada = true;
                entradaId = nodoConfig.id;
            }}
        }}
    }}
    
    actualizarGrafico();
    actualizarResumen();
    if(nodoSeleccionado) {{
        const nodoActualizado = nodos.find(n => n.id === nodoSeleccionado.id);
        if(nodoActualizado) mostrarPanel(nodoActualizado);
    }}
    
    console.log("✅ Configuración aplicada exitosamente");
}}

// ============================================================
// ACTUALIZAR GRÁFICO 3D
// ============================================================
function actualizarGrafico() {{
    if (nodos.length === 0) {{
        document.getElementById('main').innerHTML = '<p style="color:red;text-align:center;margin-top:50px;">⚠️ No hay nodos para mostrar</p>';
        return;
    }}
    
    const tx=[], ty=[], tz=[];
    for(const t of tuberias) {{
        tx.push(t.x1, t.x2, null);
        ty.push(t.y1, t.y2, null);
        tz.push(t.z1, t.z2, null);
    }}
    
    const nx=[], ny=[], nz=[], col=[], tam=[], labels=[], customdata=[];
    for(const n of nodos) {{
        nx.push(n.x);
        ny.push(n.y);
        nz.push(n.z);
        labels.push(String(n.id));
        customdata.push(n.id);
        
        if(n.id === entradaId) {{
            col.push('#e74c3c');
            tam.push(12);
        }} else if(n.tipo_aparato) {{
            col.push('#3498db');
            tam.push(9);
        }} else if(n.valvula_tipo) {{
            col.push('#e67e22');
            tam.push(9);
        }} else {{
            col.push('#95a5a6');
            tam.push(6);
        }}
    }}
    
    var xs = nodos.map(n => n.x);
    var ys = nodos.map(n => n.y);
    var zs = nodos.map(n => n.z);
    var xRange = Math.max(...xs) - Math.min(...xs) || 1;
    var yRange = Math.max(...ys) - Math.min(...ys) || 1;
    var zRange = Math.max(...zs) - Math.min(...zs) || 1;
    var maxRange = Math.max(xRange, yRange, zRange);
    
    const layout = {{
        scene: {{
            xaxis: {{title: 'X (m)'}},
            yaxis: {{title: 'Y (m)'}},
            zaxis: {{title: 'Z (m)'}},
            aspectmode: 'manual',
            aspectratio: {{x: xRange / maxRange, y: yRange / maxRange, z: zRange / maxRange}},
            camera: currentCamera || {{eye: {{x: 1.5, y: 1.5, z: 1.5}}}},
            bgcolor: '#1e1e1e'
        }},
        margin: {{l: 0, r: 0, t: 40, b: 0}},
        paper_bgcolor: '#1e1e1e',
        plot_bgcolor: '#1e1e1e'
    }};
    
    const traces = [
        {{
            type: 'scatter3d',
            mode: 'lines',
            x: tx,
            y: ty,
            z: tz,
            line: {{color: '#bdc3c7', width: 4}},
            showlegend: false,
            hoverinfo: 'skip'
        }},
        {{
            type: 'scatter3d',
            mode: 'markers+text',
            x: nx,
            y: ny,
            z: nz,
            marker: {{color: col, size: tam, line: {{width: 1, color: 'white'}}}},
            text: labels,
            textposition: 'top center',
            textfont: {{size: 10, color: '#ffffff'}},
            customdata: customdata,
            hoverinfo: 'text',
            hovertext: nodos.map(n => `Nodo ${{n.id}}<br>X: ${{n.x.toFixed(2)}}<br>Y: ${{n.y.toFixed(2)}}<br>Z: ${{n.z.toFixed(2)}}`)
        }}
    ];
    
    Plotly.newPlot('main', traces, layout);
    
    document.getElementById('main').on('plotly_click', function(data) {{
        if(data.points && data.points[0]) {{
            const nodoId = data.points[0].customdata;
            const nodo = nodos.find(n => n.id === nodoId);
            if(nodo) {{
                mostrarPanel(nodo);
            }}
        }}
    }});
}}

// ============================================================
// FUNCIONES DEL PANEL
// ============================================================
function mostrarPanel(nodo) {{
    if (!nodo) return;
    nodoSeleccionado = nodo;
    const esEntrada = (nodo.id === entradaId);
    const tieneAparato = !!nodo.tipo_aparato;
    const tieneValvula = !!nodo.valvula_tipo;
    const valvulaCerrada = nodo.valvula_cerrada || false;
    const apertura = nodo.valvula_apertura !== undefined ? nodo.valvula_apertura : 100;
    
    let html = `<div class="info-nodo"><h4>🔘 Nodo ${{nodo.id}}</h4>
    <p>📍 (${{nodo.x.toFixed(1)}}, ${{nodo.y.toFixed(1)}}, ${{nodo.z.toFixed(1)}})</p>
    <p>📌 Estado: `;
    if(esEntrada) html += '<span class="badge-entrada">🚰 ENTRADA</span>';
    if(tieneAparato) html += `<span class="badge-aparato">📌 ${{nodo.tipo_aparato}}</span>`;
    if(tieneValvula) {{
        const estadoValvula = valvulaCerrada ? 'CERRADA' : `Abierta al ${{apertura}}%`;
        html += `<span class="badge-valvula">🔧 ${{nodo.valvula_tipo}} (${{estadoValvula}})</span>`;
    }}
    if(!esEntrada && !tieneAparato && !tieneValvula) html += '⚪ Sin asignar';
    
    html += `</p><hr>
    <button class="btn" onclick="setEntrada(${{nodo.id}})" ${{esEntrada ? 'disabled' : ''}} style="width:100%">🚰 Hacer ENTRADA</button>
    
    <div style="margin-top:5px"><label>📌 Aparato:</label>
    <select id="selAparato" style="width:100%"><option value="">-- Seleccionar --</option>`;
    for(const a of aparatos) {{
        html += `<option value="${{a}}" ${{nodo.tipo_aparato === a ? 'selected' : ''}}>${{a}}</option>`;
    }}
    html += `</select>
    <button class="btn" onclick="setAparato(${{nodo.id}})" style="width:100%">Aplicar</button></div>
    
    <div style="margin-top:5px"><label>🔧 Válvula:</label>
    <select id="selValvula" style="width:100%">
        <option value="">-- Ninguna --</option>
        <option value="Compuerta" ${{nodo.valvula_tipo === 'Compuerta' ? 'selected' : ''}}>Compuerta (Leq=0.3m)</option>
        <option value="Globo" ${{nodo.valvula_tipo === 'Globo' ? 'selected' : ''}}>Globo (Leq=1.5m)</option>
        <option value="Check" ${{nodo.valvula_tipo === 'Check' ? 'selected' : ''}}>Check (Leq=2.5m)</option>
        <option value="Esfera" ${{nodo.valvula_tipo === 'Esfera' ? 'selected' : ''}}>Esfera (Leq=0.2m)</option>
    </select>
    
    <div style="margin-top:8px;">
        <label style="font-size:10px; color:#aaaaaa;">🔓 Apertura: <span id="aperturaDisplay">${{apertura}}</span>%</label>
        <input type="range" id="selApertura" min="0" max="100" value="${{apertura}}" step="5" 
               style="width:100%; margin:3px 0;" 
               oninput="document.getElementById('aperturaDisplay').innerText = this.value">
    </div>
    
    <div style="margin-top:5px">
        <select id="selEstadoValvula" style="width:100%; margin-top:2px" ${{!tieneValvula ? 'disabled' : ''}}>
            <option value="abierta" ${{!valvulaCerrada ? 'selected' : ''}}>ABIERTA (flujo normal)</option>
            <option value="cerrada" ${{valvulaCerrada ? 'selected' : ''}}>CERRADA (aisla aguas abajo)</option>
        </select>
    </div>
    <button class="btn" onclick="setValvula(${{nodo.id}})" style="width:100%; margin-top:3px">Aplicar</button></div>`;
    
    if(!esEntrada && !tieneAparato && !tieneValvula) {{
        html += `<hr><button class="btn" onclick="limpiarNodo(${{nodo.id}})" style="width:100%">🗑️ Limpiar todo</button>`;
    }}
    html += `</div>`;
    document.getElementById('info-panel').innerHTML = html;
}}

// ============================================================
// FUNCIONES DE CONFIGURACIÓN
// ============================================================
function setEntrada(id) {{
    if(entradaId !== null && entradaId !== undefined) {{
        const old = nodos.find(n => n.id === entradaId);
        if(old) old.es_entrada = false;
    }}
    entradaId = id;
    const nodo = nodos.find(n => n.id === id);
    if(nodo) {{
        nodo.es_entrada = true;
        nodo.tipo_aparato = "";
        nodo.valvula_tipo = "";
        nodo.valvula_cerrada = false;
        nodo.valvula_apertura = 100;
    }}
    actualizarGrafico();
    actualizarResumen();
    if(nodoSeleccionado && nodoSeleccionado.id === id) mostrarPanel(nodo);
}}

function setAparato(id) {{
    const tipo = document.getElementById('selAparato').value;
    if(!tipo) return;
    if(id === entradaId) {{
        alert('La entrada no puede ser aparato');
        return;
    }}
    const nodo = nodos.find(n => n.id === id);
    if(nodo) {{
        nodo.tipo_aparato = tipo;
        nodo.es_entrada = false;
    }}
    actualizarGrafico();
    actualizarResumen();
    if(nodoSeleccionado && nodoSeleccionado.id === id) mostrarPanel(nodo);
}}

function setValvula(id) {{
    const tipo = document.getElementById('selValvula').value;
    const estado = document.getElementById('selEstadoValvula').value;
    const apertura = parseInt(document.getElementById('selApertura').value) || 100;
    const nodo = nodos.find(n => n.id === id);
    if(!nodo) return;
    
    if(!tipo) {{
        nodo.valvula_tipo = "";
        nodo.valvula_cerrada = false;
        nodo.valvula_apertura = 100;
    }} else {{
        nodo.valvula_tipo = tipo;
        nodo.valvula_cerrada = (estado === 'cerrada');
        nodo.valvula_apertura = apertura;
    }}
    actualizarGrafico();
    actualizarResumen();
    if(nodoSeleccionado && nodoSeleccionado.id === id) mostrarPanel(nodo);
}}

function limpiarNodo(id) {{
    const nodo = nodos.find(n => n.id === id);
    if(nodo) {{
        if(nodo.id === entradaId) entradaId = null;
        nodo.es_entrada = false;
        nodo.tipo_aparato = "";
        nodo.valvula_tipo = "";
        nodo.valvula_cerrada = false;
        nodo.valvula_apertura = 100;
    }}
    actualizarGrafico();
    actualizarResumen();
    if(nodoSeleccionado && nodoSeleccionado.id === id) mostrarPanel(nodo);
}}

function resetear() {{
    if(confirm('¿Resetear toda la configuración?')) {{
        entradaId = null;
        for(const n of nodos) {{
            n.es_entrada = false;
            n.tipo_aparato = "";
            n.valvula_tipo = "";
            n.valvula_cerrada = false;
            n.valvula_apertura = 100;
        }}
        actualizarGrafico();
        actualizarResumen();
        document.getElementById('info-panel').innerHTML = '<p style="font-size:11px; color:#aaaaaa">Seleccione un nodo</p>';
    }}
}}

function actualizarResumen() {{
    const entrada = nodos.find(n => n.id === entradaId);
    const aparatosList = nodos.filter(n => n.tipo_aparato);
    const valvulasList = nodos.filter(n => n.valvula_tipo);
    const valvulasCerradas = valvulasList.filter(n => n.valvula_cerrada);
    const totalUG = aparatosList.reduce((sum, n) => {{
        const ugMap = {json.dumps({k:v["ug"] for k,v in UNIDADES_GASTO.items()})};
        return sum + (ugMap[n.tipo_aparato] || 0);
    }}, 0);
    document.getElementById('resumen').innerHTML = `<strong>🚰 Entrada:</strong> ${{entrada !== null && entrada !== undefined ? 'Nodo '+entrada.id : '❌ No'}}<br>
    <strong>📌 Aparatos:</strong> ${{aparatosList.length}}<br>
    <strong>🔧 Válvulas:</strong> ${{valvulasList.length}} (${{valvulasCerradas.length}} cerradas)<br>
    <strong>📊 UG totales:</strong> ${{totalUG}} UG<br>
    <strong>💧 Caudal probable:</strong> ${{(0.2 * Math.sqrt(totalUG) + 0.5).toFixed(2)}} L/s`;
}}

function guardar() {{
    if(entradaId === null || entradaId === undefined) {{
        alert('⚠️ Seleccione un nodo de entrada antes de guardar');
        return;
    }}
    const config = {{
        nodo_entrada: entradaId,
        nodos: nodos.map(n => ({{
            id: n.id,
            es_entrada: n.id === entradaId,
            tipo_aparato: n.tipo_aparato,
            valvula_tipo: n.valvula_tipo,
            valvula_cerrada: n.valvula_cerrada || false,
            valvula_apertura: n.valvula_apertura !== undefined ? n.valvula_apertura : 100
        }}))
    }};
    const blob = new Blob([JSON.stringify(config, null, 2)], {{type: 'application/json'}});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'HydroDomusPy_config.json';
    a.click();
    alert('✅ Configuración guardada exitosamente.');
}}

// ============================================================
// INICIALIZAR
// ============================================================
actualizarGrafico();
actualizarResumen();
</script></body></html>"""
    return html

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
# FUNCIÓN PARA SINCRONIZAR TABLA CON CONFIGURACIÓN CARGADA
# ================================================================================

def actualizar_tabla_desde_config(red, config_data):
    """
    Actualiza la tabla manual con la configuración cargada desde un JSON.
    Retorna los datos para el DataEditor.
    """
    nodos_ids = list(red.nodos.keys())
    default_entrada_idx = 0
    aparatos_list = [""] * len(nodos_ids)
    valvulas_list = [""] * len(nodos_ids)
    aperturas_list = [100.0] * len(nodos_ids)

    if config_data:
        if config_data.get("nodo_entrada") in nodos_ids:
            default_entrada_idx = nodos_ids.index(config_data["nodo_entrada"])
        config_nodos = {n["id"]: n for n in config_data.get("nodos", [])}
        for i, nid in enumerate(nodos_ids):
            if nid in config_nodos:
                aparatos_list[i] = config_nodos[nid].get("tipo_aparato", "")
                valvulas_list[i] = config_nodos[nid].get("valvula_tipo", "")
                aperturas_list[i] = config_nodos[nid].get("valvula_apertura", 100.0)
    
    return nodos_ids, default_entrada_idx, aparatos_list, valvulas_list, aperturas_list

# ================================================================================
# FUNCIÓN PARA RECIBIR MENSAJES DEL COMPONENTE HTML
# ================================================================================

def procesar_mensaje_configuracion():
    """
    Procesa los mensajes enviados desde el componente HTML (interfaz 3D).
    Actualiza la red y el estado de sesión con la configuración recibida.
    """
    # Verificar si hay un mensaje del componente
    query_params = st.query_params
    
    # También podemos usar st.session_state para almacenar la configuración
    if 'config_3d' in st.session_state:
        config = st.session_state.config_3d
        if config and st.session_state.red:
            # Actualizar los nodos con la configuración recibida
            for nodo_cfg in config.get("nodos", []):
                nid = nodo_cfg.get("id")
                if nid in st.session_state.red.nodos:
                    nodo = st.session_state.red.nodos[nid]
                    nodo.es_entrada = nodo_cfg.get("es_entrada", False)
                    nodo.tipo_aparato = nodo_cfg.get("tipo_aparato", "")
                    nodo.valvula_tipo = nodo_cfg.get("valvula_tipo", "")
                    nodo.valvula_cerrada = nodo_cfg.get("valvula_cerrada", False)
                    nodo.valvula_apertura = nodo_cfg.get("valvula_apertura", 100.0)
            
            # Configurar nodo de entrada
            if config.get("nodo_entrada") is not None:
                st.session_state.red.nodo_entrada_id = config["nodo_entrada"]
            
            # Marcar que la configuración ha sido actualizada
            st.session_state.config_actualizada = True
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
    
    # ==========================================
    # OPCIÓN 1: CONFIGURACIÓN 3D INTERACTIVA
    # ==========================================
    with st.expander("🎯 Configuración 3D Interactiva (Recomendado)", expanded=True):
        st.markdown("""
        **💡 Haga clic en cualquier nodo del gráfico 3D para configurarlo.**
        - 🚰 Asigne el nodo de entrada
        - 🚽 Asigne aparatos sanitarios
        - 🔧 Configure válvulas y su apertura
        """)
        
        # Preparar datos para el HTML interactivo
        nodos_data = [{"id": n.id, "x": n.x, "y": n.y, "z": n.z, 
                       "es_entrada": n.es_entrada, "tipo_aparato": n.tipo_aparato, 
                       "valvula_tipo": n.valvula_tipo, "valvula_cerrada": n.valvula_cerrada,
                       "valvula_apertura": getattr(n, 'valvula_apertura', 100)} 
                      for n in red.nodos.values()]
        
        tuberias_data = []
        for t in red.tuberias.values():
            n1, n2 = red.nodos[t.nodo_inicio], red.nodos[t.nodo_fin]
            tuberias_data.append({"id": t.id, "x1": n1.x, "y1": n1.y, "z1": n1.z, 
                                  "x2": n2.x, "y2": n2.y, "z2": n2.z})
        
        # Generar HTML interactivo
        html_content = generar_html_config(nodos_data, tuberias_data)
        
        # Mostrar el componente HTML
        st.components.v1.html(html_content, height=650, scrolling=True)
        
        st.info("💡 Después de configurar en 3D, la tabla manual se actualizará automáticamente.")
    
    # ==========================================
    # OPCIÓN 2: TABLA MANUAL (alternativa)
    # ==========================================
    with st.expander("📋 Configuración Manual (Tabla)", expanded=False):
        st.markdown("**Alternativa: Configure los nodos manualmente usando la tabla.**")
        
        col_load, col_save = st.columns([1, 1])
        
        with col_load:
            config_file = st.file_uploader(
                "📂 Cargar configuración (.json)", 
                type=["json"],
                key="config_uploader"
            )
        
        # Cargar configuración desde archivo
        loaded_config = None
        if config_file is not None:
            try:
                loaded_config = json.load(config_file)
                st.success("✅ Configuración cargada exitosamente")
            except Exception as e:
                st.error(f"Error cargando configuración: {e}")
        
        # Obtener datos de la red actual
        nodos_ids = list(red.nodos.keys())
        default_entrada_idx = 0
        aparatos_list = [""] * len(nodos_ids)
        valvulas_list = [""] * len(nodos_ids)
        aperturas_list = [100.0] * len(nodos_ids)
        
        # Si hay configuración cargada, usarla
        if loaded_config:
            if loaded_config.get("nodo_entrada") in nodos_ids:
                default_entrada_idx = nodos_ids.index(loaded_config["nodo_entrada"])
            config_nodos = {n["id"]: n for n in loaded_config.get("nodos", [])}
            for i, nid in enumerate(nodos_ids):
                if nid in config_nodos:
                    aparatos_list[i] = config_nodos[nid].get("tipo_aparato", "")
                    valvulas_list[i] = config_nodos[nid].get("valvula_tipo", "")
                    aperturas_list[i] = config_nodos[nid].get("valvula_apertura", 100.0)
        else:
            # Usar el estado actual de la red
            for i, nid in enumerate(nodos_ids):
                nodo = red.nodos[nid]
                aparatos_list[i] = nodo.tipo_aparato or ""
                valvulas_list[i] = nodo.valvula_tipo or ""
                aperturas_list[i] = nodo.valvula_apertura if nodo.valvula_tipo else 100.0
                if nodo.es_entrada:
                    default_entrada_idx = i

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
            with st.spinner("Calculando red..."):
                red = st.session_state.red
                
                # Resetear configuración de nodos
                for n in red.nodos.values():
                    n.es_entrada = False
                    n.tipo_aparato = ""
                    n.valvula_tipo = ""
                    n.valvula_apertura = 100.0
                    n.valvula_cerrada = False
                
                # Aplicar configuración de la tabla (si existe)
                if 'edited_df' in locals():
                    for _, row in edited_df.iterrows():
                        nid = row["ID Nodo"]
                        if nid in red.nodos:
                            red.nodos[nid].tipo_aparato = row["Aparato"] if row["Aparato"] else ""
                            red.nodos[nid].valvula_tipo = row["Válvula"] if row["Válvula"] else ""
                            red.nodos[nid].valvula_apertura = float(row["Apertura (%)"])
                            red.nodos[nid].valvula_cerrada = float(row["Apertura (%)"]) == 0
                
                # Configurar nodo de entrada
                red.nodo_entrada_id = nodo_entrada
                red.nodos[nodo_entrada].es_entrada = True
                ajustar_cotas_relativas(red)
                
                # Ejecutar análisis
                analyzer = HydraulicAnalyzer(
                    red, 
                    diametro_maximo=st.session_state.diametro_maximo
                )
                analyzer.ejecutar()
                st.session_state.analyzer = analyzer
                
                # Calcular estadísticas
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
                generate_3d_plot(red, st.session_state.presion_entrada), 
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
