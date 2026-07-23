@echo off
title Hydro Domus Py - Configuración
echo ============================================================
echo              H Y D R O   D O M U S   P Y
echo              Configuración del Entorno
echo ============================================================
echo.

:: Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado.
    echo.
    echo Por favor, instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegurate de marcar la opcion "Add Python to PATH"
    echo durante la instalacion.
    echo.
    pause
    exit /b 1
)

:: Mostrar versión de Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python encontrado: %PYTHON_VERSION%

:: Verificar versión de Python (3.8+)
python -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Se requiere Python 3.8 o superior.
    echo Tu version: %PYTHON_VERSION%
    echo.
    echo Por favor, actualiza Python desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo ✅ Version de Python compatible.
echo.

:: Verificar pip
echo [2/4] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no esta instalado.
    echo Instalando pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ❌ Error al instalar pip.
        echo.
        pause
        exit /b 1
    )
)
echo ✅ pip disponible.
echo.

:: Instalar dependencias
echo [3/4] Instalando dependencias...
echo Esto puede tomar unos minutos...

if exist requirements.txt (
    echo Instalando desde requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error al instalar las dependencias.
        echo.
        echo Puedes intentar instalar manualmente:
        echo pip install streamlit ezdxf numpy networkx scipy plotly openpyxl pandas
        echo.
        pause
        exit /b 1
    )
) else (
    echo ⚠️ Archivo requirements.txt no encontrado.
    echo Instalando dependencias principales...
    pip install streamlit ezdxf numpy networkx scipy plotly openpyxl pandas
    if errorlevel 1 (
        echo ❌ Error al instalar las dependencias.
        echo.
        pause
        exit /b 1
    )
)
echo ✅ Dependencias instaladas correctamente.
echo.

:: Verificar instalación
echo [4/4] Verificando instalacion...
python -c "import streamlit, ezdxf, numpy, networkx, scipy, plotly, openpyxl, pandas" >nul 2>&1
if errorlevel 1 (
    echo ❌ Algunas dependencias no se instalaron correctamente.
    echo.
    echo Puedes intentar instalarlas manualmente:
    echo pip install streamlit ezdxf numpy networkx scipy plotly openpyxl pandas
    echo.
    pause
    exit /b 1
)
echo ✅ Todas las dependencias estan instaladas.
echo.

:: Ejecutar la aplicación
echo ============================================================
echo  ¡Configuracion completada exitosamente!
echo  Iniciando Hydro Domus Py...
echo ============================================================
echo.

streamlit run app.py

:: Si streamlit no se ejecuta correctamente
if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicacion.
    echo.
    echo Puedes intentar ejecutarla manualmente:
    echo streamlit run app.py
    echo.
    pause
)
