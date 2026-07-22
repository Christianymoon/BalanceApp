@echo off

echo Building APK...
echo Continue to build the APK using Flet. This may take a few moments...
echo Press any key to continue...

pause 

flet build apk
if errorlevel 1 (
    echo Build failed. Exiting.
    pause
    exit /b 1
)

color 0A
echo Installing APK...

adb devices 

@REM echo if your device is not listed, please connect it and try again.
@REM echo Press any key to continue...

@REM pause 

adb install -r ./build/apk/app-release.apk

echo "APK installed successfully!"