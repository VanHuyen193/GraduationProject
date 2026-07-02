@echo off
REM ================================================================
REM train_all.bat - Chạy training tuần tự 3 thuật toán RL
REM ================================================================
REM Yêu cầu:
REM   - Unity Editor đang chạy và mở đúng Scene khi cần
REM   - Conda env 'mlagents' đã được cài đặt
REM
REM Sử dụng:
REM   train_all.bat           <- Chạy tất cả (hỏi xác nhận cho từng môi trường)
REM   train_all.bat football  <- Chỉ chạy Football
REM   train_all.bat crossroad <- Chỉ chạy CrossTheRoad
REM   train_all.bat capture   <- Chỉ chạy CaptureTheFlag
REM ================================================================

setlocal enabledelayedexpansion

SET PYTHON=C:\Users\Admin\miniconda3\envs\mlagents\python.exe
SET MLAGENTS=C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe
SET PROJECT_DIR=%~dp0
SET CONFIG_DIR=%PROJECT_DIR%config
SET RESULTS_DIR=%PROJECT_DIR%results
SET TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%

echo.
echo ================================================================
echo  TRAINING PIPELINE - 3 RL ALGORITHMS
echo ================================================================
echo   1. Football Table    -^> PPO + Self-Play
echo   2. Cross The Road    -^> SAC (Soft Actor-Critic)
echo   3. Capture The Flag  -^> MA-POCA
echo ================================================================
echo.

REM Kiểm tra mlagents-learn
if not exist "%MLAGENTS%" (
    echo [LỖI] Không tìm thấy mlagents-learn tại: %MLAGENTS%
    echo Vui lòng cài đặt conda env 'mlagents' trước.
    pause
    exit /b 1
)

REM ================================================================
REM 1. FOOTBALL TABLE - PPO + Self-Play
REM ================================================================
if "%1"=="" goto run_football
if "%1"=="football" goto run_football
goto skip_football

:run_football
echo.
echo [1/3] FOOTBALL TABLE - PPO + Self-Play
echo ----------------------------------------------------------------
echo Cấu hình: %CONFIG_DIR%\football_ppo.yaml
echo Run ID  : Football_PPO_%TIMESTAMP%
echo.
echo *** Yêu cầu: Mở Unity Editor với Scene: Assets/Football/Football.unity
echo *** Nhấn Play trong Unity Editor trước khi tiếp tục
echo.
pause

"%MLAGENTS%" "%CONFIG_DIR%\football_ppo.yaml" ^
    --run-id="Football_PPO_%TIMESTAMP%" ^
    --results-dir="%RESULTS_DIR%" ^
    --time-scale=20 ^
    --base-port=5005

if errorlevel 1 (
    echo [CẢNH BÁO] Football training kết thúc với lỗi.
) else (
    echo [THÀNH CÔNG] Football training hoàn thành!
)

:skip_football

REM ================================================================
REM 2. CROSS THE ROAD - SAC
REM ================================================================
if "%1"=="" goto run_crossroad
if "%1"=="crossroad" goto run_crossroad
goto skip_crossroad

:run_crossroad
echo.
echo [2/3] CROSS THE ROAD - SAC
echo ----------------------------------------------------------------
echo Cấu hình: %CONFIG_DIR%\crosstheroad_sac.yaml
echo Run ID  : CrossTheRoad_SAC_%TIMESTAMP%
echo.
echo *** Yêu cầu: Mở Unity Editor với Scene: Assets/CrossTheRoad/Scenes/
echo *** Nhấn Play trong Unity Editor trước khi tiếp tục
echo.
pause

"%MLAGENTS%" "%CONFIG_DIR%\crosstheroad_sac.yaml" ^
    --run-id="CrossTheRoad_SAC_%TIMESTAMP%" ^
    --results-dir="%RESULTS_DIR%" ^
    --time-scale=20 ^
    --base-port=5005

if errorlevel 1 (
    echo [CẢNH BÁO] CrossTheRoad training kết thúc với lỗi.
) else (
    echo [THÀNH CÔNG] CrossTheRoad training hoàn thành!
)

:skip_crossroad

REM ================================================================
REM 3. CAPTURE THE FLAG - MA-POCA
REM ================================================================
if "%1"=="" goto run_capture
if "%1"=="capture" goto run_capture
goto skip_capture

:run_capture
echo.
echo [3/3] CAPTURE THE FLAG - MA-POCA
echo ----------------------------------------------------------------
echo Cấu hình: %CONFIG_DIR%\captureflag_poca.yaml
echo Run ID  : CaptureFlag_POCA_%TIMESTAMP%
echo.
echo *** Yêu cầu: Mở Unity Editor với Scene: Assets/Collaboration/Collaboration.unity
echo *** Nhấn Play trong Unity Editor trước khi tiếp tục
echo.
pause

"%MLAGENTS%" "%CONFIG_DIR%\captureflag_poca.yaml" ^
    --run-id="CaptureFlag_POCA_%TIMESTAMP%" ^
    --results-dir="%RESULTS_DIR%" ^
    --time-scale=20 ^
    --base-port=5005

if errorlevel 1 (
    echo [CẢNH BÁO] CaptureTheFlag training kết thúc với lỗi.
) else (
    echo [THÀNH CÔNG] CaptureTheFlag training hoàn thành!
)

:skip_capture

echo.
echo ================================================================
echo  TẤT CẢ TRAINING JOBS ĐÃ HOÀN THÀNH
echo  Xem kết quả tại: %RESULTS_DIR%
echo  Chạy TensorBoard: tensorboard --logdir "%RESULTS_DIR%"
echo ================================================================
echo.
pause
