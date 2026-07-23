#!/bin/bash

echo "============================================================"
echo "              H Y D R O   D O M U S   P Y"
echo "              Configuración del Entorno"
echo "============================================================"
echo ""

# Verificar Python
echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado."
    echo "Por favor, instala Python 3.8 o superior."
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Verificar versión
python3 -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)"
if [ $? -ne 0 ]; then
    echo "❌ Se requiere Python 3.8 o superior."
    echo "Tu version: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Version de Python compatible."
echo ""

# Crear entorno virtual
echo "[2/5] Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "⚠️ El entorno virtual ya existe."
    read -p "¿Deseas recrearlo? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Eliminando entorno anterior..."
        rm -rf venv
        echo "Creando nuevo entorno..."
        python3 -m venv venv
    else
        echo "Usando entorno existente..."
    fi
else
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi
echo "✅ Entorno virtual creado."
echo ""

# Activar entorno virtual
echo "[3/5] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Error al activar el entorno virtual."
    exit 1
fi
echo "✅ Entorno virtual activado."
echo ""

# Actualizar pip
echo "[4/5] Actualizando pip..."
pip install --upgrade pip
echo ""

# Instalar dependencias
echo "[5/5] Instalando dependencias..."
echo "Esto puede tomar unos minutos..."

if [ -f "requirements.txt" ]; then
    echo "Instalando desde requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar las dependencias."
        exit 1
    fi
else
    echo "⚠️ Archivo requirements.txt no encontrado."
    echo "Instalando dependencias principales..."
    pip install streamlit ezdxf numpy networkx scipy plotly openpyxl pandas
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar las dependencias."
        exit 1
    fi
fi
echo "✅ Dependencias instaladas correctamente."
echo ""

# Verificar instalación
echo "Verificando instalación..."
python -c "import streamlit, ezdxf, numpy, networkx, scipy, plotly, openpyxl, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Algunas dependencias no se instalaron correctamente."
    exit 1
fi
echo "✅ Todas las dependencias están instaladas."
echo ""

# Ejecutar la aplicación
echo "============================================================"
echo "  ¡Configuración completada exitosamente!"
echo "  Iniciando Hydro Domus Py..."
echo "============================================================"
echo ""

streamlit run app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error al ejecutar la aplicación."
    echo ""
    echo "Puedes intentar ejecutarla manualmente:"
    echo "1. Activa el entorno: source venv/bin/activate"
    echo "2. Ejecuta: streamlit run app.py"
    echo ""
fi
