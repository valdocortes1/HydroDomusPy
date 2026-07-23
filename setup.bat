@echo off
title Hydro Domus Py - Configuración
echo ============================================================
echo              H Y D R O   D O M U S   P Y
echo              Configuración del Entorno
echo ============================================================
echo.

:: Verificar Python
echo [1/5] Verificando Python...
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

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python encontrado: %PYTHON_VERSION%

python -c "import sys; exit(0) if sys.version_info >= (3,8) else exit(1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Se requiere Python 3.8 o superior.
    echo Tu version: %PYTHON_VERSION%
    echo.
    pause
    exit /b 1
)
echo ✅ Version de Python compatible.
echo.

:: Crear entorno virtual
echo [2/5] Creando entorno virtual...
if exist venv (
    echo ⚠️ El entorno virtual ya existe.
    choice /C SN /M "¿Deseas recrearlo? (S/N)"
    if errorlevel 2 (
        echo Usando entorno existente...
    ) else (
        echo Eliminando entorno anterior...
        rmdir /s /q venv
        echo Creando nuevo entorno...
        python -m venv venv
    )
) else (
    echo Creando entorno virtual...
    python -m venv venv
)
echo ✅ Entorno virtual creado.
echo.

:: Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error al activar el entorno virtual.
    echo.
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado.
echo.

:: Actualizar pip
echo [4/5] Actualizando pip...
python -m pip install --upgrade pip
echo.

:: Instalar dependencias
echo [5/5] Instalando dependencias...
echo Esto puede tomar unos minutos...

if exist requirements.txt (
    echo Instalando desde requirements.txt...
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
echo Verificando instalacion...
python -c "import streamlit, ezdxf, numpy, networkx, scipy, plotly, openpyxl, pandas" >nul 2>&1
if errorlevel 1 (
    echo ❌ Algunas dependencias no se instalaron correctamente.
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
    echo 1. Activa el entorno: venv\Scripts\activate
    echo 2. Ejecuta: streamlit run app.py
    echo.
    pause
)
