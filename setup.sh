#!/bin/bash

echo "============================================================"
echo "              H Y D R O   D O M U S   P Y"
echo "              Configuración del Entorno"
echo "============================================================"
echo ""

# Verificar Python
echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado."
    echo "Por favor, instala Python 3.8 o superior."
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Verificar pip
echo "[2/4] Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip no está instalado. Instalando..."
    python3 -m ensurepip --upgrade
fi
echo "✅ pip disponible"

# Instalar dependencias
echo "[3/4] Instalando dependencias..."
if [ -f "requirements.txt" ]; then
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    pip3 install streamlit ezdxf numpy networkx scipy plotly openpyxl pandas
fi
echo "✅ Dependencias instaladas"

# Verificar instalación
echo "[4/4] Verificando instalación..."
python3 -c "import streamlit, ezdxf, numpy, networkx, scipy, plotly, openpyxl, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error en la instalación de dependencias."
    exit 1
fi
echo "✅ Todas las dependencias están instaladas."

# Ejecutar
echo ""
echo "============================================================"
echo "  ¡Configuración completada!"
echo "  Iniciando Hydro Domus Py..."
echo "============================================================"
echo ""

streamlit run app.py
