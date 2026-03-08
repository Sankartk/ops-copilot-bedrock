@echo off
setlocal EnableExtensions

REM ==========================================================
REM Ops Copilot Runner (Windows CMD)
REM ==========================================================

cd /d "%~dp0"

echo.
echo ==========================================================
echo [1/8] Create / activate virtual environment
echo ==========================================================
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo.
echo ==========================================================
echo [2/8] Install dependencies
echo ==========================================================
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo ==========================================================
echo [3/8] Ensure data folder exists
echo ==========================================================
if not exist "data" (
    echo Creating data folder
    mkdir data
) else (
    echo data folder exists
)

echo.
echo ==========================================================
echo [4/8] Build FAISS index
echo ==========================================================
python -m src.build_index --data-dir data --index-dir index
if errorlevel 1 goto :fail

echo.
echo ==========================================================
echo [5/8] Run evaluation
echo ==========================================================
if exist "eval\run_eval.py" (
    python -m eval.run_eval
    if errorlevel 1 (
        echo WARN: eval failed ^(continuing^)
    )
) else (
    echo WARN: eval\run_eval.py not found, skipping
)

echo.
echo ==========================================================
echo [6/8] Check Ollama
echo ==========================================================
where ollama >nul 2>&1
if errorlevel 1 (
    echo WARN: Ollama not found on PATH
) else (
    echo Ollama found
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo WARN: Ollama server not running
    ) else (
        echo Ollama server reachable
    )
)

echo.
echo ==========================================================
echo [7/8] Optional AWS SAM build/deploy
echo ==========================================================
if /I "%DEPLOY_SAM%"=="1" (
    where sam >nul 2>&1
    if errorlevel 1 (
        echo WARN: SAM CLI not installed
        goto :after_sam
    )

    where aws >nul 2>&1
    if errorlevel 1 (
        echo WARN: AWS CLI not installed
        goto :after_sam
    )

    if not exist "infra\template.yaml" (
        echo WARN: infra\template.yaml missing
        goto :after_sam
    )

    echo --- Checking AWS credentials
    aws sts get-caller-identity >nul 2>&1
    if errorlevel 1 (
        echo WARN: AWS credentials not configured
        goto :after_sam
    )

    echo --- SAM validate
    sam validate --template-file "infra\template.yaml"
    if errorlevel 1 (
        echo WARN: SAM validate failed
        goto :after_sam
    )

    echo --- SAM build
    sam build --template-file "infra\template.yaml"
    if errorlevel 1 (
        echo WARN: SAM build failed
        goto :after_sam
    )

    if exist "infra\samconfig.toml" (
        echo --- SAM deploy using samconfig
        sam deploy --config-file "infra\samconfig.toml"
    ) else (
        echo --- First deploy guided
        sam deploy --guided --template-file ".aws-sam\build\template.yaml"
    )
) else (
    echo DEPLOY_SAM is not 1. Skipping SAM deploy.
)

:after_sam
echo.
echo ==========================================================
echo [8/8] Start Streamlit
echo ==========================================================
echo Opening Streamlit UI at http://localhost:8501
streamlit run app.py
goto :end

:fail
echo.
echo ==========================================================
echo FAILED
echo ==========================================================

:end
endlocal