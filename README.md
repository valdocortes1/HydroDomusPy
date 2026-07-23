# 💧 Hydro Domus Py
**Simulador Mecanicista de Análisis Hidráulico para Redes Internas**

Hydro Domus Py es una aplicación web de código abierto desarrollada en Python para el diseño, simulación y análisis de redes hidrosanitarias internas. A diferencia de las herramientas que utilizan aproximaciones empíricas simples, este software implementa un motor de cálculo basado en principios físicos fundamentales, integrando la lectura directa de geometrías desde archivos CAD y la generación de reportes técnicos automatizados.

---

## ✨ Características Principales
* **🔌 Integración CAD Directa:** Lectura y extracción automática de topologías desde archivos `.dxf` (AutoCAD/DraftSight).
* **🌐 Topología Inteligente:** Reconstrucción de la red en grafos mediante `NetworkX` para detectar nodos, tramos, accesorios y la ruta crítica de manera automatizada.
* **📊 Visualización 3D Interactiva:** Renderizado del sistema isométrico y los perfiles de presión utilizando `Plotly`.
* **📑 Reportes de Ingeniería:** Exportación automatizada a hojas de cálculo (Excel) con memoria de cálculo, cantidades de obra (tuberías, uniones, pegamento) y validación de presiones.

---

## ⚙️ Fundamentos Matemáticos y Normativos

El motor matemático (`hydro_core.py`) ejecuta un análisis iterativo basándose en los siguientes modelos mecanicistas:

### 1. Cálculo de Pérdidas de Energía (Fricción)
* **Ecuación de Darcy-Weisbach:** Se utiliza como la fórmula universal para determinar las pérdidas de carga lineales garantizando la conservación de energía, evaluando dinámicamente la carga de velocidad y la geometría de cada tramo ($L/D$).
* **Factor de Fricción Dinámico (Colebrook-White):** En lugar de asumir factores constantes, el software evalúa el régimen de flujo calculando el Número de Reynolds en tiempo real y resuelve el factor $f$ para régimen turbulento mediante métodos numéricos no lineales (`scipy.optimize.fsolve`), considerando la rugosidad absoluta de las tuberías de PVC.

### 2. Caudales de Diseño
* **Método Probabilístico de Hunter:** La asignación de los caudales máximos probables simultáneos se realiza mediante un recorrido topológico en árbol (Búsqueda en Anchura - BFS) desde los aparatos hasta la acometida, acumulando las Unidades de Gasto (UG) según el tipo de edificación.

### 3. Resistencia Localizada
* **Longitudes Equivalentes ($Leq$):** Detección de cambios de dirección geométrica para asignar automáticamente codos y tees, transformando su coeficiente de resistencia en longitudes equivalentes sumadas al modelo de fricción.
* **Estrangulamiento de Válvulas:** Modelamiento avanzado de cierres parciales de flujo a través de una penalización cuadrática sobre el área transversal.

### 4. Parámetros Normativos
* El sistema evalúa gradientes hidráulicos validando que la presión en los nodos más desfavorables (ruta crítica) cumpla con los estándares técnicos y normativos vigentes (e.g., presiones mínimas de la NTC 1500).

---

## 🛠️ Requisitos del Sistema y Prerrequisitos

El entorno de ejecución requiere **Python 3.8 o superior**. Las dependencias principales están listadas en el archivo `requirements.txt`:

* `streamlit` (Interfaz web de usuario)
* `pandas` (Estructuración de datos de tablas)
* `networkx` (Análisis de grafos y teoría de redes)
* `plotly` (Motor de renderizado 3D y gráficos)
* `openpyxl` (Generación de hojas de cálculo)
* `ezdxf` (Procesamiento de vectores CAD)
* `scipy` (Resolución de ecuaciones no lineales complejas)

---

## 🚀 Instalación y Uso Local

Sigue estos pasos para desplegar el simulador en tu máquina local:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/hydro-domus-py.git](https://github.com/TU_USUARIO/hydro-domus-py.git)
   cd hydro-domus-py