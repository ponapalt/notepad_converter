@echo off

setlocal enabledelayedexpansion

goto begin

:: Function to display error and loop back to the beginning
:error_handler
echo [ERROR] %1
goto end

:begin
echo.
echo ========================
echo Executing common setup...
echo ========================
:: Check for Python virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        call :error_handler "Failed to create a virtual environment. Error code: %ERRORLEVEL%"
    )
)

echo.
echo ========================
echo Activating virtual environment...
echo ========================

endlocal
call venv\Scripts\activate
setlocal enabledelayedexpansion

if %ERRORLEVEL% neq 0 (
    call :error_handler "Failed to activate the virtual environment. Error code: %ERRORLEVEL%"
)

echo ========================
echo Upgrading pip...
echo ========================

python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    call :error_handler "Failed to upgrade pip. Error code: %ERRORLEVEL%"
    goto end
)

echo.
echo ========================
echo Installing dependencies...
echo ========================
pip install -U -r requirements.txt
if %ERRORLEVEL% neq 0 (
    call :error_handler "Failed to install dependencies. Error code: %ERRORLEVEL%"
)

echo.
echo ========================
echo Starting app...
echo ========================

endlocal

python app.py %*

setlocal enabledelayedexpansion

if %ERRORLEVEL% neq 0 (
    echo Failed to start the application.
    exit /b 1
)

:end
echo Script finished. Press any key to exit...
pause
exit