@echo off
SET VERSION=%1
IF "%VERSION%"=="" SET VERSION=1.7.1
echo Packaging Live Telemetry %VERSION%...
IF EXIST "live-telemetry-%VERSION%.7z" (
    echo Deleting old files...
    del "live-telemetry-%VERSION%.7z"
)
echo Creating new archive file...
"C:\Program Files\7-Zip\7z.exe" a "live-telemetry-%VERSION%.7z" apps content -r -x!*.psd -x!*.svg 1> 7z.log 2>&1
IF %ERRORLEVEL% NEQ 0 (
    type 7z.log
) ELSE (
    echo Done.
)
del 7z.log
@echo on
