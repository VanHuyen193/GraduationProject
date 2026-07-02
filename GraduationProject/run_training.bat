@echo off
REM ================================================================
REM run_training.bat - Run a specific training job
REM
REM Usage:
REM   run_training.bat ctf_poca    <- Run Capture The Flag + POCA
REM   run_training.bat ctf_ppo     <- Run Capture The Flag + PPO
REM   run_training.bat ctf_sac     <- Run Capture The Flag + SAC
REM   run_training.bat ctr_ppo     <- Run Cross The Road + PPO
REM   run_training.bat ctr_sac     <- Run Cross The Road + SAC
REM   run_training.bat ctr_poca    <- Run Cross The Road + MA-POCA
REM   run_training.bat football_ppo  <- Run Football + PPO
REM   run_training.bat football_sac  <- Run Football + SAC
REM   run_training.bat football_poca <- Run Football + MA-POCA
REM
REM After all runs done, run compare:
REM   compare_results.bat
REM ================================================================

setlocal enabledelayedexpansion

SET MLAGENTS=C:\Users\Admin\miniconda3\envs\mlagents\Scripts\mlagents-learn.exe
SET PROJECT_DIR=%~dp0
SET CONFIG_DIR=%PROJECT_DIR%config
SET RESULTS_DIR=%PROJECT_DIR%results

if "%1"=="" (
    echo Usage: run_training.bat [job_name]
    echo.
    echo Available jobs:
    echo   ctf_poca    - Capture The Flag with MA-POCA ^(RECOMMENDED FIRST^)
    echo   ctf_ppo     - Capture The Flag with PPO
    echo   ctf_sac     - Capture The Flag with SAC
    echo   ctr_ppo     - Cross The Road with PPO
    echo   ctr_sac     - Cross The Road with SAC
    echo   ctr_poca    - Cross The Road with MA-POCA
    echo   football_ppo  - Football Table with PPO
    echo   football_sac  - Football Table with SAC
    echo   football_poca - Football Table with MA-POCA
    echo.
    echo Run order for complete experiment:
    echo   1. ctf_poca  ^(Scene: Assets/Collaboration/Collaboration.unity^)
    echo   2. ctf_ppo   ^(Scene: Assets/Collaboration/Collaboration.unity^)
    echo   3. ctf_sac   ^(Scene: Assets/Collaboration/Collaboration.unity^)
    echo   4. ctr_ppo   ^(Scene: Assets/CrossTheRoad/Scenes/^)
    echo   5. ctr_sac   ^(Scene: Assets/CrossTheRoad/Scenes/^)
    echo   6. ctr_poca  ^(Scene: Assets/CrossTheRoad/Scenes/^)
    echo   7. football_ppo  ^(Scene: Assets/Football/Football.unity^)
    echo   8. football_sac  ^(Scene: Assets/Football/Football.unity^)
    echo   9. football_poca ^(Scene: Assets/Football/Football.unity^)
    goto :end
)

REM Map job name to config and scene
if "%1"=="ctf_poca" (
    SET CONFIG=ctf_poca.yaml
    SET RUN_ID=ctf_poca_v1
    SET SCENE=Assets/Collaboration/Collaboration.unity
)
if "%1"=="ctf_ppo" (
    SET CONFIG=ctf_ppo.yaml
    SET RUN_ID=ctf_ppo_v1
    SET SCENE=Assets/Collaboration/Collaboration.unity
)
if "%1"=="ctf_sac" (
    SET CONFIG=ctf_sac.yaml
    SET RUN_ID=ctf_sac_v1
    SET SCENE=Assets/Collaboration/Collaboration.unity
)
if "%1"=="ctr_ppo" (
    SET CONFIG=ctr_ppo.yaml
    SET RUN_ID=ctr_ppo_v1
    SET SCENE=Assets/CrossTheRoad/Scenes/
)
if "%1"=="ctr_sac" (
    SET CONFIG=ctr_sac.yaml
    SET RUN_ID=ctr_sac_v1
    SET SCENE=Assets/CrossTheRoad/Scenes/
)
if "%1"=="ctr_poca" (
    SET CONFIG=ctr_poca.yaml
    SET RUN_ID=ctr_poca_v1
    SET SCENE=Assets/CrossTheRoad/Scenes/
)
if "%1"=="football_ppo" (
    SET CONFIG=football_ppo.yaml
    SET RUN_ID=football_ppo_v1
    SET SCENE=Assets/Football/Football.unity
)
if "%1"=="football_sac" (
    SET CONFIG=football_sac.yaml
    SET RUN_ID=football_sac_v1
    SET SCENE=Assets/Football/Football.unity
)
if "%1"=="football_poca" (
    SET CONFIG=football_poca.yaml
    SET RUN_ID=football_poca_v1
    SET SCENE=Assets/Football/Football.unity
)

if not defined CONFIG (
    echo ERROR: Unknown job '%1'
    goto :end
)

echo.
echo ================================================================
echo   TRAINING JOB: %1
echo   Config : %CONFIG%
echo   Run ID : %RUN_ID%
echo ================================================================
echo.
echo *** IMPORTANT: Before pressing ENTER:
echo *** 1. Open Unity Editor
echo *** 2. Load Scene: %SCENE%
echo *** 3. Make sure Behavior Parameters are set to "Default"
echo *** 4. Press PLAY in Unity Editor
echo.
pause

echo.
echo Starting training... (mlagents-learn will connect to Unity)
echo.

"%MLAGENTS%" "%CONFIG_DIR%\%CONFIG%" ^
    --run-id=%RUN_ID% ^
    --results-dir="%RESULTS_DIR%" ^
    --time-scale=20 ^
    --base-port=5005 ^
    --timeout-wait=120 ^
    --force

echo.
if errorlevel 1 (
    echo [FAILED] Training ended with error.
) else (
    echo [SUCCESS] Training completed!
    echo Results saved to: %RESULTS_DIR%\%RUN_ID%
)

:end
pause
