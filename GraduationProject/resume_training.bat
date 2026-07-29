@echo off
REM ===================================================================
REM resume_training.bat
REM
REM Chay tiep luot huan luyen 15 job sau khi tat may / mat dien / Ctrl-C.
REM Bam doi vao file nay la du, khong can go lenh.
REM
REM   * Job da xong (co <behavior>.onnx cuoi)  -> bo qua
REM   * Job dang do dang                        -> chay TIEP tu checkpoint
REM                                                (moi 500.000 buoc mot lan luu)
REM   * Job chua chay                           -> chay tu dau
REM ===================================================================
setlocal
cd /d "%~dp0"

REM --- Do tim python cua env 'mlagents' -------------------------------
REM Khong hardcode duong dan: repo nay chay tren nhieu may (Admin, vanhu, ...).
REM Thu tu uu tien giong _find_conda_env() trong train_all.py.
set "PY="
if defined MLAGENTS_ENV if exist "%MLAGENTS_ENV%\python.exe" set "PY=%MLAGENTS_ENV%\python.exe"
if not defined PY if defined CONDA_PREFIX if exist "%CONDA_PREFIX%\python.exe" set "PY=%CONDA_PREFIX%\python.exe"
if not defined PY if exist "%USERPROFILE%\miniconda3\envs\mlagents\python.exe" set "PY=%USERPROFILE%\miniconda3\envs\mlagents\python.exe"
if not defined PY if exist "%USERPROFILE%\anaconda3\envs\mlagents\python.exe" set "PY=%USERPROFILE%\anaconda3\envs\mlagents\python.exe"

if not defined PY (
    echo [LOI] Khong tim thay python cua conda env 'mlagents'.
    echo.
    echo Da thu:
    echo   - bien moi truong MLAGENTS_ENV
    echo   - env conda dang kich hoat ^(CONDA_PREFIX^)
    echo   - %%USERPROFILE%%\miniconda3\envs\mlagents
    echo   - %%USERPROFILE%%\anaconda3\envs\mlagents
    echo.
    echo Cach xu ly: mo Anaconda Prompt, chay "conda activate mlagents"
    echo roi chay lai file nay; hoac dat MLAGENTS_ENV tro toi thu muc env.
    pause
    exit /b 1
)
echo Dung python: %PY%

REM --- Chot chan: khong cho chay hai luot cung luc ---------------------
REM Hai tien trinh train_all.py se tranh cong 5005 va cung ghi vao mot
REM run-id, hong ca hai. Dem xem da co tien trinh nao dang chay chua.
powershell -NoProfile -Command "exit (@(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*train_all.py*' }).Count)"
if errorlevel 1 (
    echo.
    echo [LOI] Da co mot luot train_all.py DANG CHAY.
    echo       Dong no truoc roi hay chay lai file nay.
    echo       Xem tien do:  type training_logs\full_run.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Chay tiep luot huan luyen (ngan sach full, 26.500.000 buoc).
echo Job da xong se duoc bo qua. Ctrl-C de dung bat cu luc nao.
echo.

"%PY%" train_all.py --mode build --budget full --resume --force

echo.
echo Da ket thuc. Xem tong ket o tren, hoac trong training_logs\.
pause
