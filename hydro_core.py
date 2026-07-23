"""
================================================================================
                            H Y D R O   C O R E
================================================================================
        Motor de Análisis Hidráulico, Topología y Extracción Geométrica
================================================================================
"""

import ezdxf
import numpy as np
import networkx as nx
from scipy.optimize import fsolve
import plotly.graph_objects as go
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import math

# ==================== CONFIGURACIÓN GLOBAL ====================
UNIDADES_GASTO = {
    "LAVAMANOS": {"ug": 1, "caudal_unitario": 0.1, "color": "#3498db", "icono": "🚰"},
    "LAVADERO": {"ug": 3, "caudal_unitario": 0.3, "color": "#2ecc71", "icono": "🧺"},
    "SANITARIO": {"ug": 3, "caudal_unitario": 0.3, "color": "#e67e22", "icono": "🚽"},
    "DUCHA": {"ug": 2, "caudal_unitario": 0.2, "color": "#1abc9c", "icono": "🚿"},
    "LAVADORA": {"ug": 3, "caudal_unitario": 0.3, "color": "#9b59b6", "icono": "👕"},
    "TANQUE": {"ug": 5, "caudal_unitario": 0.5, "color": "#f39c12", "icono": "🗄️"},
    "LAVAPLATOS": {"ug": 2, "caudal_unitario": 0.2, "color": "#e74c3c", "icono": "🍽️"},
    "GRIFO_JARDIN": {"ug": 2, "caudal_unitario": 0.2, "color": "#27ae60", "icono": "🌿"},
}

DIAMETROS_PAVCO = {
    "1/2": 18.18,
    "3/4": 23.63,
    "1": 30.20,
    "1_1/2": 43.68,
    "2": 55.68,
    "3": 82.04,
    "4": 103.42,
}

EPSILON_PVC_MM = 0.0015
GRAVEDAD = 9.81
VISCOSIDAD_AGUA = 1e-6
VEL_MIN_MS = 0.5
VEL_MAX_MS = 2.0
PRESION_ENTRADA_MCA = 15.0
PRESION_MIN_NORMA = 5.0
TOLERANCIA_CONEXION_M = 0.01

LEQ_ACCESORIOS = {
    'Tee': 1.5,
    'Codo_90': 0.8,
    'Codo_45': 0.5,
    'Reduccion': 0.5,
    'Valvula_Compuerta': 0.3,
    'Valvula_Globo': 1.5,
    'Valvula_Check': 2.5,
    'Valvula_Esfera': 0.2,
}

TIPOS_OCUPACION_AGUA = {
    "Vivienda Unifamiliar": {
        "descripcion": "Casas, residencias unifamiliares",
        "formula": "Q = 0.2 * √UG + 0.5",
        "coeficiente_a": 0.20,
        "coeficiente_b": 0.50,
        "color": "#3498db"
    },
    "Vivienda Multifamiliar": {
        "descripcion": "Edificios de apartamentos (hasta 20 unidades)",
        "formula": "Q = 0.25 * √UG + 0.6",
        "coeficiente_a": 0.25,
        "coeficiente_b": 0.60,
        "color": "#2ecc71"
    },
    "Edificio de Oficinas": {
        "descripcion": "Oficinas, edificios administrativos",
        "formula": "Q = 0.15 * √UG + 0.3",
        "coeficiente_a": 0.15,
        "coeficiente_b": 0.30,
        "color": "#e67e22"
    },
    "Hotel / Hostería": {
        "descripcion": "Hoteles, hostales, alojamientos",
        "formula": "Q = 0.18 * √UG + 0.4",
        "coeficiente_a": 0.18,
        "coeficiente_b": 0.40,
        "color": "#f39c12"
    },
    "Hospital / Clínica": {
        "descripcion": "Centros médicos, hospitales",
        "formula": "Q = 0.22 * √UG + 0.7",
        "coeficiente_a": 0.22,
        "coeficiente_b": 0.70,
        "color": "#e74c3c"
    },
    "Centro Comercial": {
        "descripcion": "Centros comerciales, tiendas",
        "formula": "Q = 0.12 * √UG + 0.4",
        "coeficiente_a": 0.12,
        "coeficiente_b": 0.40,
        "color": "#9b59b6"
    },
    "Colegio / Universidad": {
        "descripcion": "Instituciones educativas",
        "formula": "Q = 0.13 * √UG + 0.35",
        "coeficiente_a": 0.13,
        "coeficiente_b": 0.35,
        "color": "#1abc9c"
    },
    "Restaurante / Cafetería": {
        "descripcion": "Establecimientos de comida",
        "formula": "Q = 0.16 * √UG + 0.45",
        "coeficiente_a": 0.16,
        "coeficiente_b": 0.45,
        "color": "#e84393"
    },
    "Gimnasio / Deportivo": {
        "descripcion": "Centros deportivos, gimnasios",
        "formula": "Q = 0.20 * √UG + 0.55",
        "coeficiente_a": 0.20,
        "coeficiente_b": 0.55,
        "color": "#00cec9"
    },
    "Ancianato / Geriátrico": {
        "descripcion": "Residencias de ancianos",
        "formula": "Q = 0.17 * √UG + 0.4",
        "coeficiente_a": 0.17,
        "coeficiente_b": 0.40,
        "color": "#fd79a8"
    }
}

TIPO_OCUPACION_ACTUAL = "Vivienda Unifamiliar"

# ==================== FUNCIONES AUXILIARES ====================
def caudal_por_ug(ug_total: float, tipo_ocupacion: str = None) -> float:
    if ug_total <= 0:
        return 0.0
    
    if tipo_ocupacion is None:
        tipo_ocupacion = TIPO_OCUPACION_ACTUAL
    
    config = TIPOS_OCUPACION_AGUA.get(tipo_ocupacion, TIPOS_OCUPACION_AGUA["Vivienda Unifamiliar"])
    a = config.get("coeficiente_a", 0.2)
    b = config.get("coeficiente_b", 0.5)
    return a * (ug_total ** 0.5) + b

def diametro_a_numero(diam):
    mapeo = {'1/2': 0.5, '3/4': 0.75, '1': 1.0, '1-1/2': 1.5, '2': 2.0, '3': 3.0, '4': 4.0}
    return mapeo.get(diam, 999)

# ==================== MODELOS DE DATOS ====================
@dataclass
class Nodo:
    id: int
    x: float
    y: float
    z: float
    es_entrada: bool = False
    tipo_aparato: str = ""
    valvula_tipo: str = ""
    valvula_cerrada: bool = False
    valvula_apertura: float = 100.0
    demanda_lps: float = 0.0
    presion_mca: Optional[float] = None

@dataclass
class Accesorio:
    id: int
    tipo: str
    nodo_id: int
    longitud_equivalente_m: float = 0.0
    perdida_mca: float = 0.0
    
    def calcular_perdida(self, f_friccion: float, diametro_m: float, velocidad_ms: float) -> float:
        if self.longitud_equivalente_m > 0 and velocidad_ms > 0:
            self.perdida_mca = f_friccion * (self.longitud_equivalente_m / diametro_m) * (velocidad_ms**2 / (2 * GRAVEDAD))
        return self.perdida_mca

@dataclass
class Tuberia:
    id: int
    nodo_inicio: int
    nodo_fin: int
    longitud_m: float
    diametro_mm: float = 21.0
    caudal_lps: float = 0.0
    velocidad_ms: float = 0.0
    perdida_mca: float = 0.0
    f_friccion: float = 0.02
    
    @property
    def diametro_m(self): return self.diametro_mm / 1000.0
    @property
    def diametro_pulg(self): return self.diametro_mm / 25.4
    @property
    def diametro_nominal_pulg(self):
        mapeo = {18.18: "1/2", 23.63: "3/4", 30.20: "1", 43.68: "1-1/2", 55.68: "2", 82.04: "3", 103.42: "4"}
        if self.diametro_mm in mapeo:
            return mapeo[self.diametro_mm]
        cercano = min(mapeo.keys(), key=lambda x: abs(x - self.diametro_mm))
        return mapeo[cercano]
    @property
    def area_m2(self): return np.pi * (self.diametro_m / 2) ** 2
    
    def calcular_velocidad(self):
        if self.caudal_lps > 0:
            self.velocidad_ms = (self.caudal_lps / 1000.0) / self.area_m2
        return self.velocidad_ms
    
    def colebrook_white(self, Re):
        epsilon = EPSILON_PVC_MM / 1000.0
        D = self.diametro_m
        def ecuacion(f):
            return 1/np.sqrt(f) + 2 * np.log10(epsilon/(3.71*D) + 2.51/(Re*np.sqrt(f)))
        try:
            f_solution = fsolve(ecuacion, 0.02)[0]
            return max(0.008, min(0.05, f_solution))
        except:
            return 0.02
    
    def calcular_perdida(self, accesorios_por_nodo: Dict[int, List[Accesorio]] = None) -> float:
        if self.caudal_lps == 0:
            self.perdida_mca = 0.0
            return 0.0
        
        V = self.velocidad_ms
        D = self.diametro_m
        Re = V * D / VISCOSIDAD_AGUA
        f = self.colebrook_white(Re)
        self.f_friccion = f
        
        hf_friccion = f * (self.longitud_m / D) * (V**2 / (2 * GRAVEDAD))
        hf_accesorios = 0.0
        if accesorios_por_nodo:
            for acc in accesorios_por_nodo.get(self.nodo_inicio, []):
                hf_accesorios += acc.calcular_perdida(f, D, V)
            for acc in accesorios_por_nodo.get(self.nodo_fin, []):
                hf_accesorios += acc.calcular_perdida(f, D, V)
        
        self.perdida_mca = hf_friccion + hf_accesorios
        return self.perdida_mca

# ==================== CLASE RED HIDRÁULICA ====================
class RedHidraulica:
    def __init__(self):
        self.nodos: Dict[int, Nodo] = {}
        self.tuberias: Dict[int, Tuberia] = {}
        self.accesorios: List[Accesorio] = []
        self.grafo = nx.Graph()
        self.nodo_entrada_id = None
    
    def agregar_nodo(self, nodo):
        self.nodos[nodo.id] = nodo
        self.grafo.add_node(nodo.id)
    
    def agregar_tuberia(self, tubo):
        self.tuberias[tubo.id] = tubo
        self.grafo.add_edge(tubo.nodo_inicio, tubo.nodo_fin)
    
    def _find_tuberia(self, n1, n2):
        for tid, t in self.tuberias.items():
            if (t.nodo_inicio == n1 and t.nodo_fin == n2) or (t.nodo_inicio == n2 and t.nodo_fin == n1):
                return tid
        return None

    def calcular_ug_acumulada(self, alcanzables=None):
        if self.nodo_entrada_id is None:
            return {}
        
        if alcanzables is None:
            alcanzables = set(self.nodos.keys())
        
        ug_por_nodo = {}
        for nid, nodo in self.nodos.items():
            ug = 0
            if nid in alcanzables and nodo.tipo_aparato and nodo.tipo_aparato in UNIDADES_GASTO:
                ug = UNIDADES_GASTO[nodo.tipo_aparato]["ug"]
            ug_por_nodo[nid] = ug
        
        padres = {self.nodo_entrada_id: None}
        orden_bfs = [self.nodo_entrada_id]
        cola = deque([self.nodo_entrada_id])
        
        while cola:
            nodo = cola.popleft()
            if nodo not in alcanzables:
                continue
            for vecino in self.grafo.neighbors(nodo):
                if vecino not in padres and vecino in alcanzables:
                    padres[vecino] = nodo
                    orden_bfs.append(vecino)
                    cola.append(vecino)
        
        ug_acumulada = ug_por_nodo.copy()
        for nodo in reversed(orden_bfs):
            if nodo == self.nodo_entrada_id:
                continue
            padre = padres.get(nodo)
            if padre is not None:
                ug_acumulada[padre] = ug_acumulada.get(padre, 0) + ug_acumulada[nodo]
        
        return ug_acumulada
    
    def calcular_angulo_entre_tuberias(self, tuberia1, tuberia2, nodo_comun):
        nodo = self.nodos[nodo_comun]
        otro1 = tuberia1.nodo_fin if tuberia1.nodo_inicio == nodo_comun else tuberia1.nodo_inicio
        otro2 = tuberia2.nodo_fin if tuberia2.nodo_inicio == nodo_comun else tuberia2.nodo_inicio
        n1, n2 = self.nodos[otro1], self.nodos[otro2]
        v1 = np.array([n1.x - nodo.x, n1.y - nodo.y, n1.z - nodo.z])
        v2 = np.array([n2.x - nodo.x, n2.y - nodo.y, n2.z - nodo.z])
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        v1, v2 = v1 / norm1, v2 / norm2
        angulo_deg = np.degrees(np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0)))
        return angulo_deg if angulo_deg <= 90 else 180 - angulo_deg
        
    def detectar_accesorios(self):
        self.accesorios = []
        next_id = 0
        
        for nid in self.nodos.keys():
            tuberias_conectadas = [t for t in self.tuberias.values() 
                                   if t.nodo_inicio == nid or t.nodo_fin == nid]
            grado = len(tuberias_conectadas)
            
            if grado >= 3:
                self.accesorios.append(Accesorio(id=next_id, tipo='Tee', nodo_id=nid,
                                                  longitud_equivalente_m=LEQ_ACCESORIOS['Tee']))
                next_id += 1
            
            if grado >= 2:
                for i in range(len(tuberias_conectadas)):
                    for j in range(i + 1, len(tuberias_conectadas)):
                        if tuberias_conectadas[i].diametro_mm != tuberias_conectadas[j].diametro_mm:
                            self.accesorios.append(Accesorio(id=next_id, tipo='Reduccion', nodo_id=nid,
                                                              longitud_equivalente_m=LEQ_ACCESORIOS['Reduccion']))
                            next_id += 1
                            break
                    else:
                        continue
                    break
            
            if grado == 2:
                d1, d2 = tuberias_conectadas[0].diametro_mm, tuberias_conectadas[1].diametro_mm
                if d1 == d2:
                    angulo = self.calcular_angulo_entre_tuberias(tuberias_conectadas[0], tuberias_conectadas[1], nid)
                    
                    if 35 <= angulo <= 55:
                        tipo_codo, leq = 'Codo_45', LEQ_ACCESORIOS['Codo_45']
                    elif 70 <= angulo <= 110:
                        tipo_codo, leq = 'Codo_90', LEQ_ACCESORIOS['Codo_90']
                    else:
                        continue
                    
                    self.accesorios.append(Accesorio(id=next_id, tipo=tipo_codo, nodo_id=nid, longitud_equivalente_m=leq))
                    next_id += 1
        
        for nid, nodo in self.nodos.items():
            if nodo.valvula_tipo and not nodo.valvula_cerrada and nodo.valvula_apertura > 0:
                leq_base = LEQ_ACCESORIOS.get(f'Valvula_{nodo.valvula_tipo}', 0.5)
                factor = (100.0 / nodo.valvula_apertura)**2 if nodo.valvula_apertura < 100 else 1.0
                leq_efectivo = leq_base * factor
                
                if not any(a.nodo_id == nid and 'Valvula' in a.tipo for a in self.accesorios):
                    self.accesorios.append(Accesorio(id=next_id, tipo=f'Valvula_{nodo.valvula_tipo}',
                                                      nodo_id=nid, longitud_equivalente_m=leq_efectivo))
                    next_id += 1
        
        return self.accesorios

# ==================== CLASE ANALIZADOR HIDRÁULICO ====================
class HydraulicAnalyzer:
    def __init__(self, red, diametro_maximo=None):
        self.red = red
        self.diam_comerciales_original = sorted(DIAMETROS_PAVCO.values())
        self.diametro_maximo = diametro_maximo
        
        if self.diametro_maximo is not None:
            self.diam_comerciales = [d for d in self.diam_comerciales_original if d <= self.diametro_maximo]
        else:
            self.diam_comerciales = self.diam_comerciales_original.copy()
        
        if not self.diam_comerciales:
            self.diam_comerciales = [min(self.diam_comerciales_original)]
        
        diam_max = max(self.diam_comerciales)
        for t in self.red.tuberias.values():
            if t.diametro_mm > diam_max:
                t.diametro_mm = diam_max
    
    def asignar_caudales(self):
        if self.red.nodo_entrada_id is None:
            return
        
        alcanzables = set()
        cola = deque([self.red.nodo_entrada_id])
        
        while cola:
            nodo_actual = cola.popleft()
            if nodo_actual in alcanzables:
                continue
            alcanzables.add(nodo_actual)
            
            nodo_obj = self.red.nodos.get(nodo_actual)
            if nodo_obj and (nodo_obj.valvula_cerrada or getattr(nodo_obj, 'valvula_apertura', 100) == 0):
                continue
            
            for vecino in self.red.grafo.neighbors(nodo_actual):
                if vecino not in alcanzables:
                    cola.append(vecino)
        
        ug_acumulada = self.red.calcular_ug_acumulada(alcanzables=alcanzables)
        
        for t in self.red.tuberias.values():
            try:
                dist_inicio = nx.shortest_path_length(self.red.grafo, self.red.nodo_entrada_id, t.nodo_inicio)
                dist_fin = nx.shortest_path_length(self.red.grafo, self.red.nodo_entrada_id, t.nodo_fin)
            except:
                dist_inicio, dist_fin = 0, 1
            
            nodo_aguas_abajo = t.nodo_fin if dist_fin > dist_inicio else t.nodo_inicio
            
            if nodo_aguas_abajo not in alcanzables:
                t.caudal_lps = 0
            else:
                t.caudal_lps = caudal_por_ug(ug_acumulada.get(nodo_aguas_abajo, 0), TIPO_OCUPACION_ACTUAL)
    
    def optimizar_diametros(self):
        diam_min, diam_max = min(self.diam_comerciales), max(self.diam_comerciales)
        
        for t in self.red.tuberias.values():
            if t.diametro_mm > diam_max:
                t.diametro_mm = diam_max
            
            caudal = t.caudal_lps
            if caudal > 4.0:
                diam_min_sugerido = 55.68
            elif caudal > 2.5:
                diam_min_sugerido = 43.68
            elif caudal > 1.5:
                diam_min_sugerido = 30.20
            elif caudal > 0.8:
                diam_min_sugerido = 23.63
            else:
                diam_min_sugerido = 18.18
            
            cercano = min(self.diam_comerciales, key=lambda x: abs(x - diam_min_sugerido))
            diam_min_sugerido = min(cercano, diam_max)
            
            if t.diametro_mm < diam_min_sugerido:
                t.diametro_mm = diam_min_sugerido
        
        for iteracion in range(15):
            cambios = False
            for t in self.red.tuberias.values():
                v = t.calcular_velocidad()
                d_actual = t.diametro_mm
                
                if v < VEL_MIN_MS and d_actual > diam_min:
                    idx = self.diam_comerciales.index(d_actual)
                    nuevo_diam = self.diam_comerciales[max(0, idx-1)]
                    if nuevo_diam != d_actual:
                        t.diametro_mm = nuevo_diam
                        cambios = True
                elif v > VEL_MAX_MS and d_actual < diam_max:
                    idx = self.diam_comerciales.index(d_actual)
                    nuevo_diam = self.diam_comerciales[min(len(self.diam_comerciales)-1, idx+1)]
                    if nuevo_diam != d_actual:
                        t.diametro_mm = nuevo_diam
                        cambios = True
            
            if not cambios:
                break
    
    def calcular_presiones(self):
        if self.red.nodo_entrada_id is None:
            return
        
        entrada_id = self.red.nodo_entrada_id
        
        alcanzables = set()
        cola = deque([entrada_id])
        
        while cola:
            nodo_actual = cola.popleft()
            if nodo_actual in alcanzables:
                continue
            alcanzables.add(nodo_actual)
            
            nodo_obj = self.red.nodos.get(nodo_actual)
            if nodo_obj and nodo_obj.valvula_cerrada:
                continue
            
            for vecino in self.red.grafo.neighbors(nodo_actual):
                if vecino not in alcanzables:
                    cola.append(vecino)
        
        self.red.detectar_accesorios()
        
        accesorios_por_nodo = {}
        for acc in self.red.accesorios:
            accesorios_por_nodo.setdefault(acc.nodo_id, []).append(acc)
        
        for t in self.red.tuberias.values():
            t.calcular_velocidad()
            t.calcular_perdida(accesorios_por_nodo)
        
        for nodo in self.red.nodos.values():
            nodo.presion_mca = None
        
        self.red.nodos[entrada_id].presion_mca = PRESION_ENTRADA_MCA
        
        queue = deque([entrada_id])
        visitados = set()
        
        while queue:
            nodo_actual = queue.popleft()
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            p_act = self.red.nodos[nodo_actual].presion_mca
            
            if p_act is None:
                continue
            
            nodo_obj = self.red.nodos.get(nodo_actual)
            if nodo_obj and nodo_obj.valvula_cerrada:
                continue
            
            for vecino in self.red.grafo.neighbors(nodo_actual):
                if vecino in visitados:
                    continue
                
                tid = self.red._find_tuberia(nodo_actual, vecino)
                if tid is None:
                    continue
                
                t = self.red.tuberias[tid]
                hf = t.calcular_perdida(accesorios_por_nodo)
                dz = self.red.nodos[vecino].z - self.red.nodos[nodo_actual].z
                p_vecino = p_act - hf - dz
                
                self.red.nodos[vecino].presion_mca = p_vecino
                queue.append(vecino)
    
    def ejecutar(self):
        self.asignar_caudales()
        self.optimizar_diametros()
        self.red.detectar_accesorios()
        self.calcular_presiones()

# ==================== CLASE LECTOR DXF ====================
class DXFReader:
    def __init__(self, archivo):
        self.doc = ezdxf.readfile(archivo)
        self.msp = self.doc.modelspace()
    
    def obtener_layers(self):
        return [layer.dxf.name for layer in self.doc.layers]
    
    def extraer_lineas(self, layers):
        lineas = []
        layers_set = set(layers)
        
        for entity in self.msp:
            dxftype = entity.dxftype()
            
            if dxftype not in ('LINE', 'LWPOLYLINE', 'POLYLINE', '3DPOLYLINE'):
                continue
            
            if entity.dxf.layer not in layers_set:
                continue
            
            if dxftype == 'LINE':
                s = entity.dxf.start
                e = entity.dxf.end
                lineas.append((
                    s.x, s.y, getattr(s, 'z', 0),
                    e.x, e.y, getattr(e, 'z', 0)
                ))
            
            elif dxftype == 'LWPOLYLINE':
                elevation = getattr(entity.dxf, 'elevation', 0)
                pts = []
                
                try:
                    with entity.points() as p_list:
                        pts = [(p[0], p[1]) for p in p_list]
                except Exception:
                    try:
                        p_list = entity.get_points('xy')
                        pts = [(p[0], p[1]) for p in p_list]
                    except Exception:
                        pass
                
                if pts:
                    for i in range(len(pts) - 1):
                        lineas.append((
                            pts[i][0], pts[i][1], elevation,
                            pts[i+1][0], pts[i+1][1], elevation
                        ))
                    if getattr(entity, 'closed', False) and len(pts) > 2:
                        lineas.append((
                            pts[-1][0], pts[-1][1], elevation,
                            pts[0][0], pts[0][1], elevation
                        ))
            
            elif dxftype in ('POLYLINE', '3DPOLYLINE'):
                pts = []
                
                try:
                    pts = [(v.dxf.location.x, v.dxf.location.y, v.dxf.location.z) for v in entity.vertices]
                except Exception:
                    try:
                        with entity.points() as p_list:
                            pts = [(p[0], p[1], p[2] if len(p) > 2 else 0) for p in p_list]
                    except Exception:
                        pass
                        
                if pts:
                    for i in range(len(pts) - 1):
                        lineas.append((
                            pts[i][0], pts[i][1], pts[i][2],
                            pts[i+1][0], pts[i+1][1], pts[i+1][2]
                        ))
                    if getattr(entity, 'is_closed', False) and len(pts) > 2:
                        lineas.append((
                            pts[-1][0], pts[-1][1], pts[-1][2],
                            pts[0][0], pts[0][1], pts[0][2]
                        ))
                        
        return lineas

def normalizar_coordenadas(lineas, factor_conversion=1000):
    if not lineas:
        return lineas
    
    todos_puntos = []
    for l in lineas:
        todos_puntos.extend([(l[0], l[1]), (l[3], l[4])])
    
    min_x = min(p[0] for p in todos_puntos)
    min_y = min(p[1] for p in todos_puntos)
    
    lineas_norm = []
    for x1, y1, z1, x2, y2, z2 in lineas:
        lineas_norm.append((
            (x1 - min_x) / factor_conversion,
            (y1 - min_y) / factor_conversion,
            z1 / factor_conversion,
            (x2 - min_x) / factor_conversion,
            (y2 - min_y) / factor_conversion,
            z2 / factor_conversion
        ))
    
    return lineas_norm

def construir_red(lineas):
    nodos_dict = {}
    tuberias = []
    next_id_nodo, next_id_tubo = 0, 0
    
    diametro_inicial = min(DIAMETROS_PAVCO.values())
    
    def get_nodo(x, y, z):
        nonlocal next_id_nodo
        for (xp, yp, zp), nid in nodos_dict.items():
            if abs(x-xp)<TOLERANCIA_CONEXION_M and abs(y-yp)<TOLERANCIA_CONEXION_M and abs(z-zp)<TOLERANCIA_CONEXION_M:
                return nid
        nodos_dict[(x, y, z)] = next_id_nodo
        next_id_nodo += 1
        return next_id_nodo - 1
    
    for x1,y1,z1,x2,y2,z2 in lineas:
        n1, n2 = get_nodo(x1, y1, z1), get_nodo(x2, y2, z2)
        L = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        tuberias.append(Tuberia(id=next_id_tubo, nodo_inicio=n1, nodo_fin=n2, longitud_m=L, diametro_mm=diametro_inicial))
        next_id_tubo += 1
    return nodos_dict, tuberias

def ajustar_cotas_relativas(red):
    if red.nodo_entrada_id is None:
        return
    
    z_entrada = red.nodos[red.nodo_entrada_id].z
    for nodo in red.nodos.values():
        nodo.z = nodo.z - z_entrada

# ==================== GENERACIÓN DE GRÁFICO 3D ====================
def generate_3d_plot(red, presion_entrada=15.0):
    """
    Genera el gráfico 3D completo con Plotly.
    Versión mejorada con leyenda más clara y símbolos descriptivos.
    """
    fig = go.Figure()
    
    # ============================================================
    # 1. TUBERÍAS (con colores según velocidad)
    # ============================================================
    diametros = [t.diametro_mm for t in red.tuberias.values() if t.diametro_mm > 0]
    if diametros:
        diam_min, diam_max = min(diametros), max(diametros)
    else:
        diam_min, diam_max = 21, 114
    
    for t in red.tuberias.values():
        if t.nodo_inicio not in red.nodos or t.nodo_fin not in red.nodos:
            continue
        n1, n2 = red.nodos[t.nodo_inicio], red.nodos[t.nodo_fin]
        v = t.velocidad_ms
        
        if v < VEL_MIN_MS:
            color, estado = '#74b9ff', 'Velocidad baja'
        elif v <= VEL_MAX_MS:
            color, estado = '#55efc4', 'Velocidad normal'
        else:
            color, estado = '#ff7675', 'Velocidad alta'
        
        if diam_max > diam_min:
            ancho = 4 + (t.diametro_mm - diam_min) / (diam_max - diam_min) * 6
        else:
            ancho = 6
        ancho = max(4, min(10, ancho))
        
        fig.add_trace(go.Scatter3d(
            x=[n1.x, n2.x], y=[n1.y, n2.y], z=[n1.z, n2.z],
            mode='lines',
            line=dict(color=color, width=ancho),
            name=f'Tubería {t.id}',
            showlegend=False,
            hovertext=f"<b>Tubería {t.id}</b><br>"
                     f"📏 Longitud: {t.longitud_m:.2f} m<br>"
                     f"⚙️ Diámetro: {t.diametro_mm:.0f} mm ({t.diametro_nominal_pulg}\")<br>"
                     f"💧 Caudal: {t.caudal_lps:.2f} L/s<br>"
                     f"⚡ Velocidad: {t.velocidad_ms:.2f} m/s ({estado})<br>"
                     f"📉 Pérdida: {t.perdida_mca:.2f} mca",
            hoverinfo='text'
        ))
    
    # ============================================================
    # 2. ACCESORIOS CON SÍMBOLOS MEJORADOS
    # ============================================================
    tipos_accesorios = {}
    for acc in red.accesorios:
        if acc.nodo_id not in red.nodos:
            continue
        if acc.tipo not in tipos_accesorios:
            tipos_accesorios[acc.tipo] = []
        tipos_accesorios[acc.tipo].append(acc)
    
    # Configuración de símbolos mejorada
    config_tipos = {
        'Tee': {'simbolo': 'T', 'color': '#f39c12', 'nombre': '🔧 Tee', 'size': 10},
        'Codo_90': {'simbolo': 'L', 'color': '#9b59b6', 'nombre': '🔀 Codo 90°', 'size': 8},
        'Codo_45': {'simbolo': 'V', 'color': '#8e44ad', 'nombre': '🔄 Codo 45°', 'size': 8},
        'Reduccion': {'simbolo': 'O', 'color': '#e67e22', 'nombre': '📏 Reducción', 'size': 7},
    }
    
    for tipo, accesorios in tipos_accesorios.items():
        if tipo not in config_tipos:
            if 'Valvula' in tipo:
                nombre_valvula = tipo.split("_")[1]
                nombres_valvulas = {
                    'Compuerta': 'Válvula Compuerta',
                    'Globo': 'Válvula Globo', 
                    'Check': 'Válvula Check',
                    'Esfera': 'Válvula Esfera'
                }
                nombre = f'🔧 {nombres_valvulas.get(nombre_valvula, nombre_valvula)}'
                simbolo = 'D'  # Diamante para válvulas
                color = '#e67e22'
                size = 9
            else:
                continue
        else:
            cfg = config_tipos[tipo]
            nombre = cfg['nombre']
            simbolo = cfg['simbolo']
            color = cfg['color']
            size = cfg['size']
        
        xs = [red.nodos[acc.nodo_id].x for acc in accesorios]
        ys = [red.nodos[acc.nodo_id].y for acc in accesorios]
        zs = [red.nodos[acc.nodo_id].z for acc in accesorios]
        
        hover_texts = []
        for acc in accesorios:
            # Obtener diámetro del accesorio
            diam = "N/A"
            for t in red.tuberias.values():
                if t.nodo_inicio == acc.nodo_id or t.nodo_fin == acc.nodo_id:
                    diam = t.diametro_nominal_pulg
                    break
            hover_texts.append(
                f"<b>{nombre}</b><br>📍 Nodo {acc.nodo_id}<br>"
                f"📐 Leq: {acc.longitud_equivalente_m:.2f} m<br>"
                f"📉 Pérdida: {acc.perdida_mca:.4f} mca<br>"
                f"📏 DN: {diam}"
            )
        
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode='markers',
            marker=dict(
                size=size, 
                symbol=simbolo, 
                color=color, 
                line=dict(width=1.5, color='white')
            ),
            name=nombre,
            showlegend=True,
            hovertext=hover_texts,
            hoverinfo='text'
        ))
    
    # ============================================================
    # 3. NODOS CON LEYENDA MEJORADA
    # ============================================================
    alcanzables = set()
    if red.nodo_entrada_id is not None:
        cola = deque([red.nodo_entrada_id])
        while cola:
            nodo_actual = cola.popleft()
            if nodo_actual in alcanzables:
                continue
            alcanzables.add(nodo_actual)
            
            nodo_obj = red.nodos.get(nodo_actual)
            if nodo_obj and nodo_obj.valvula_cerrada:
                continue
            
            for vecino in red.grafo.neighbors(nodo_actual):
                if vecino not in alcanzables:
                    cola.append(vecino)
    
    ug_acumulada = red.calcular_ug_acumulada(alcanzables=alcanzables)
    tipo_ocupacion = st.session_state.get('tipo_ocupacion', "Vivienda Unifamiliar")
    
    # --- CAPAS PARA NODOS CON LEYENDA MEJORADA ---
    capas = {
        'Entrada': {'x': [], 'y': [], 'z': [], 'color': [], 'size': [], 'symbol': [], 'text': []},
        'Aparatos': {'x': [], 'y': [], 'z': [], 'color': [], 'size': [], 'symbol': [], 'text': [], 'labels': []},
        'Nodos': {'x': [], 'y': [], 'z': [], 'color': [], 'size': [], 'symbol': [], 'text': []}
    }
    
    for n in red.nodos.values():
        presion_val = n.presion_mca if n.presion_mca is not None else 0
        
        # Determinar a qué capa pertenece
        if n.es_entrada:
            grupo = 'Entrada'
            simbolo, tamano = 'star', 12
        elif n.tipo_aparato:
            grupo = 'Aparatos'
            simbolo, tamano = 'square', 9
            # Guardar el nombre del aparato para la leyenda
            capas[grupo]['labels'].append(f"{UNIDADES_GASTO.get(n.tipo_aparato, {}).get('icono', '📌')} {n.tipo_aparato}")
        else:
            grupo = 'Nodos'
            simbolo, tamano = 'circle', 5
        
        demanda_unitaria = UNIDADES_GASTO[n.tipo_aparato]["caudal_unitario"] if n.tipo_aparato in UNIDADES_GASTO else 0
        
        if n.id in alcanzables:
            ug_nodo = ug_acumulada.get(n.id, 0)
            caudal_hunter = caudal_por_ug(ug_nodo, tipo_ocupacion)
            caudal_texto = f"{caudal_hunter:.3f} L/s"
        else:
            caudal_texto = "N/A (Aislado por válvula)"
        
        z_signo = '+' if n.z > 0 else ''
        texto = f"<b>Nodo {n.id}</b><br>📍 ({n.x:.2f}, {n.y:.2f}, {z_signo}{n.z:.2f})<br>"
        
        if n.es_entrada:
            texto += "🚰 <b>ENTRADA (Cota 0)</b><br>"
        if n.tipo_aparato:
            ug = UNIDADES_GASTO.get(n.tipo_aparato, {}).get("ug", 0)
            texto += f"📌 {n.tipo_aparato} (UG: {ug})<br>"
            texto += f"💧 Demanda unitaria: {demanda_unitaria:.2f} L/s<br>"
        if n.valvula_tipo:
            estado_valvula = "CERRADA" if n.valvula_cerrada else f"Abierta al {n.valvula_apertura}%"
            texto += f"🔧 Válvula: {n.valvula_tipo} ({estado_valvula})<br>"
        
        texto += f"📊 Caudal Hunter en nodo: {caudal_texto}<br>"
        texto += f"💪 Presión: {n.presion_mca:.2f} mca" if n.presion_mca else "💪 Presión: N/A"
        if n.presion_mca and n.presion_mca < PRESION_MIN_NORMA:
            texto += "\n⚠️ <b>PRESIÓN BAJA</b>"
        
        # Añadir a su respectiva capa
        capas[grupo]['x'].append(n.x)
        capas[grupo]['y'].append(n.y)
        capas[grupo]['z'].append(n.z)
        capas[grupo]['color'].append(presion_val)
        capas[grupo]['size'].append(tamano)
        capas[grupo]['symbol'].append(simbolo)
        capas[grupo]['text'].append(texto)
    
    # --- AÑADIR TRAZAS SEPARADAS ---
    # 1. Entrada
    if capas['Entrada']['x']:
        fig.add_trace(go.Scatter3d(
            x=capas['Entrada']['x'], y=capas['Entrada']['y'], z=capas['Entrada']['z'],
            mode='markers',
            marker=dict(
                size=12, symbol='star', color='#e74c3c',
                line=dict(width=2, color='white')
            ),
            text=capas['Entrada']['text'], hoverinfo='text',
            name='🚰 Entrada', showlegend=True
        ))
    
    # 2. Aparatos (con nombres en la leyenda)
    if capas['Aparatos']['x']:
        # Crear una traza por cada tipo de aparato para mostrar en la leyenda
        aparatos_unicos = {}
        for i, n in enumerate(red.nodos.values()):
            if n.tipo_aparato and n.tipo_aparato not in aparatos_unicos:
                aparatos_unicos[n.tipo_aparato] = {
                    'x': [], 'y': [], 'z': [], 'text': [], 'color': []
                }
        
        for n in red.nodos.values():
            if n.tipo_aparato and n.tipo_aparato in aparatos_unicos:
                aparatos_unicos[n.tipo_aparato]['x'].append(n.x)
                aparatos_unicos[n.tipo_aparato]['y'].append(n.y)
                aparatos_unicos[n.tipo_aparato]['z'].append(n.z)
                aparatos_unicos[n.tipo_aparato]['text'].append(
                    f"<b>Nodo {n.id}</b><br>📌 {n.tipo_aparato}<br>💪 Presión: {n.presion_mca:.2f} mca" if n.presion_mca else f"<b>Nodo {n.id}</b><br>📌 {n.tipo_aparato}"
                )
                aparatos_unicos[n.tipo_aparato]['color'].append(n.presion_mca if n.presion_mca else 0)
        
        for aparato, data in aparatos_unicos.items():
            if data['x']:
                icono = UNIDADES_GASTO.get(aparato, {}).get('icono', '📌')
                fig.add_trace(go.Scatter3d(
                    x=data['x'], y=data['y'], z=data['z'],
                    mode='markers',
                    marker=dict(
                        size=9, symbol='square',
                        color=data['color'],
                        colorscale='RdYlGn',
                        showscale=False,
                        line=dict(width=1.5, color='white'),
                        cmin=0, cmax=presion_entrada
                    ),
                    text=data['text'], hoverinfo='text',
                    name=f"{icono} {aparato}", showlegend=True
                ))
    
    # 3. Nodos de paso (sin aparatos ni entrada)
    if capas['Nodos']['x']:
        fig.add_trace(go.Scatter3d(
            x=capas['Nodos']['x'], y=capas['Nodos']['y'], z=capas['Nodos']['z'],
            mode='markers',
            marker=dict(
                size=5, symbol='circle',
                color=capas['Nodos']['color'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Presión (mca)", x=0.85, len=0.5, thickness=15),
                line=dict(width=1, color='white'),
                cmin=0, cmax=presion_entrada
            ),
            text=capas['Nodos']['text'], hoverinfo='text',
            name='⚪ Nodos de Paso', showlegend=True
        ))
    
    # ============================================================
    # 4. CONFIGURACIÓN DEL GRÁFICO
    # ============================================================
    fig.update_layout(
        title=dict(
            text="💧 Hydro Domus Py - Resultados del Análisis Hidráulico<br>"
                 "<sup>Cotas relativas al nodo de entrada (cota = 0)</sup>",
            font=dict(size=16),
            x=0.5,
            xanchor='center'
        ),
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title=dict(text="Altura relativa (m)", font=dict(size=12)),
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        ),
        width=1200,
        height=700,
        legend=dict(
            x=0.02,
            y=0.98,
            traceorder='normal',
            font=dict(size=10)
        ),
        margin=dict(l=0, r=20, t=70, b=0),
        hoverlabel=dict(bgcolor='white', font_size=11)
    )
    
    return fig
