@echo off
IF EXIST "live-telemetry-%1.7z" (
    echo Deleting old files...
    del "live-telemetry-%1.7z"
)
echo Creating new archive file...
"C:\Program Files\7-Zip\7z.exe" a "live-telemetry-%1.7z" apps content -r -x!*.psd 1> 7z.log 2>&1
IF %ERRORLEVEL% NEQ 0 ( 
    type 7z.log
) ELSE (
    echo Done.
)
del 7z.log
@echo on
