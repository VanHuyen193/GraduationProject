@echo off
if "%~1"=="-Z1" (
  tar -tf "%~2"
  exit /b
)
echo This compatibility shim only supports: unzip -Z1 file.pptx 1>&2
exit /b 2
