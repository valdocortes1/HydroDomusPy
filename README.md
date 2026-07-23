# 💧 Hydro Domus Py

### Análisis Hidráulico para Redes Internas de Agua Potable

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hydrodomuspy.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io)

</div>

---

## 📋 Descripción

**Hydro Domus Py** es una aplicación web de código abierto desarrollada en Python para el diseño, simulación y análisis de redes hidrosanitarias internas. A diferencia de las herramientas que utilizan aproximaciones empíricas simples, este software implementa un **motor de cálculo basado en principios físicos fundamentales**, integrando la lectura directa de geometrías desde archivos CAD y la generación de reportes técnicos automatizados.

### 🎯 ¿Qué hace Hydro Domus Py?

- **📁 Lee planos hidrosanitarios** desde archivos DXF (AutoCAD/DraftSight)
- **🔧 Construye la red topológica** identificando nodos, tuberías y accesorios
- **💧 Calcula caudales** usando el método probabilístico de Hunter
- **📊 Analiza presiones** y pérdidas con ecuaciones mecanicistas (Darcy-Weisbach, Colebrook-White)
- **🌐 Visualiza en 3D** la red con colores según velocidades y presiones
- **📋 Genera reportes técnicos** en Excel con cantidades de obra y materiales
- **🔧 Permite configurar** aparatos sanitarios, válvulas y restricciones de diámetro

### 📐 Normativas Aplicadas

- **NTC 1500** - Norma Técnica Colombiana para instalaciones hidrosanitarias
- **RAS** - Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico

---

## ⚙️ Fundamentos Matemáticos

El motor matemático de Hydro Domus Py ejecuta un análisis iterativo basándose en modelos mecanicistas de alta precisión:

### 1. 📐 Pérdidas por Fricción (Darcy-Weisbach)

Utiliza la ecuación universal para un cálculo exacto basado en la conservación de energía y la geometría del tramo:

$$h_f = f \cdot \frac{L}{D} \cdot \frac{v^2}{2g}$$

### 2. 🔄 Factor de Fricción (Colebrook-White)

Resuelve dinámicamente el factor de fricción $f$ en régimen turbulento mediante métodos numéricos iterativos:

$$\frac{1}{\sqrt{f}} = -2 \log_{10} \left( \frac{\epsilon}{3.71D} + \frac{2.51}{Re \sqrt{f}} \right)$$

### 3. 📊 Caudales de Diseño (Método de Hunter)

Asigna caudales probabilísticos mediante un recorrido topológico en árbol (BFS) que acumula las Unidades de Gasto (UG) según el tipo de edificación:

$$Q = a \cdot \sqrt{UG} + b$$

| Tipo de Edificación | Coeficiente a | Coeficiente b |
|---------------------|---------------|---------------|
| Vivienda Unifamiliar | 0.20 | 0.50 |
| Vivienda Multifamiliar / Apartamentos | 0.25 | 0.60 |
| Edificio de Oficinas | 0.15 | 0.30 |
| Hotel / Hostería | 0.18 | 0.40 |
| Hospital / Clínica | 0.22 | 0.70 |
| Centro Comercial | 0.12 | 0.40 |

### 4. 🔧 Pérdidas Localizadas (Longitudes Equivalentes)

Transforma la resistencia de accesorios (codos, tees, válvulas) en Longitudes Equivalentes ($Leq$) que se suman al modelo lineal.

### 5. 🚪 Estrangulamiento de Válvulas

Modela cierres parciales aplicando una penalización cuadrática a la longitud equivalente de la válvula:

$$Leq_{efectivo} = Leq_{base} \cdot \left(\frac{100}{Apertura}\right)^2$$

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Función |
|------------|---------|
| **[Streamlit](https://streamlit.io/)** | Interfaz web de usuario |
| **[ezdxf](https://ezdxf.mozman.at/)** | Lectura de archivos DXF |
| **[NetworkX](https://networkx.org/)** | Análisis de grafos y topología |
| **[Plotly](https://plotly.com/python/)** | Visualización 3D interactiva |
| **[NumPy](https://numpy.org/)** | Cálculos numéricos |
| **[SciPy](https://scipy.org/)** | Optimización (fsolve) |
| **[OpenPyXL](https://openpyxl.readthedocs.io/)** | Exportación a Excel |

---

## 🚀 Demo en Vivo

Puedes probar la aplicación sin instalar nada en:

[https://hydrodomuspy.streamlit.app](https://hydrodomuspy.streamlit.app)

---

## 📦 Instalación Local

### Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar el repositorio**

```bash
git clone https://github.com/valdocortes1/HydroDomusPy.git
cd HydroDomusPy
