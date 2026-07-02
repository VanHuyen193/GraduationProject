@echo off
REM ================================================================
REM compare_results.bat - Generate comparison charts and report
REM Run this AFTER all 9 training jobs are complete
REM ================================================================

SET PYTHON=C:\Users\Admin\miniconda3\envs\mlagents\python.exe
SET PROJECT_DIR=%~dp0

echo ================================================================
echo   GENERATING RL COMPARISON REPORT
echo ================================================================
echo.

"%PYTHON%" "%PROJECT_DIR%compare_results.py"

echo.
if errorlevel 1 (
    echo [ERROR] Comparison script failed. Check error above.
) else (
    echo [SUCCESS] Report generated!
    echo.
    echo Output files:
    echo   comparison_charts\01_reward_curves.png
    echo   comparison_charts\02_final_reward_bar.png
    echo   comparison_charts\03_episode_length.png
    echo   comparison_charts\04_policy_loss.png
    echo   comparison_charts\05_entropy.png
    echo   comparison_report.md
)

echo.
pause
