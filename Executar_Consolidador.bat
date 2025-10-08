@echo off
chcp 65001 > nul
title Consolidador Fluxo de Caixa
color 0A

echo.
echo ========================================
echo    CONSOLIDADOR FLUXO DE CAIXA
echo ========================================
echo.
echo Iniciando aplicacao...
echo.

cd /d "%~dp0"

:: Tentar executar
python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERRO: Nao foi possivel iniciar a aplicacao!
    echo ========================================
    echo.
    echo Possiveis solucoes:
    echo 1. Verifique se o Python esta instalado
    echo 2. Execute: pip install -r requirements.txt
    echo 3. Verifique se o arquivo app.py existe
    echo.
)

pause