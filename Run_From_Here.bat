@echo off
setlocal EnableDelayedExpansion

chcp 65001 >nul
title NediaVision
color 0F

for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"
set "DIM=%ESC%[2m"
set "CYAN=%ESC%[96m"
set "MAGENTA=%ESC%[95m"
set "YELLOW=%ESC%[93m"
set "GREEN=%ESC%[92m"
set "WHITE=%ESC%[97m"
set "RED=%ESC%[91m"
set "MINT=%ESC%[38;2;117;255;178m"
set "SOFTMINT=%ESC%[38;2;188;255;224m"
set "CREAM=%ESC%[38;2;244;232;197m"
set "GOLD=%ESC%[38;2;255;220;120m"
set "LIME=%ESC%[38;2;148;180;59m"
set "CORAL=%ESC%[38;2;255;110;90m"

cd /d "%~dp0sd"

:start_menu
cls
echo %LIME%========================================================================================================%RESET%
echo.
echo %CREAM%%BOLD%guest @ nediavision.ai:$ ~ hello%RESET%
echo.
echo %MINT%%BOLD%NN   NN  EEEEEEE  DDDDDD    IIIII    AAAAA   VV     VV  IIIII   SSSSS   IIIII   OOOOO   NN   NN%RESET%
echo %MINT%%BOLD%NNN  NN  EE       DD   DD     I     AA   AA   VV   VV     I    SS        I    OO   OO  NNN  NN%RESET%
echo %MINT%%BOLD%NN N NN  EEEEE    DD    DD    I     AAAAAAA    VV VV      I     SSSSS     I    OO   OO  NN N NN%RESET%
echo %MINT%%BOLD%NN  NNN  EE       DD   DD     I     AA   AA     VVV       I         SS    I    OO   OO  NN  NNN%RESET%
echo %MINT%%BOLD%NN   NN  EEEEEEE  DDDDDD    IIIII  AA   AA      V      IIIII   SSSSS   IIIII   OOOOO   NN   NN%RESET%
echo.
echo %SOFTMINT%%DIM%by nedia melki   2025-2026%RESET%
echo.
echo %SOFTMINT%Welcome to my %BOLD%FINAL YEAR PROJECT%RESET%%SOFTMINT%.%RESET%
echo.
echo %SOFTMINT%This is %BOLD%NediaVision%RESET%%SOFTMINT%, a terminal-style AI image generation project.%RESET%
echo.
echo %SOFTMINT%GPU is selected automatically when available for faster rendering.%RESET%
echo.
echo %GOLD%Available modes:%RESET%
echo %SOFTMINT%  [1] Text   - create a new image from a text prompt%RESET%
echo %SOFTMINT%  [2] Edit   - transform an existing image with an AI prompt%RESET%
echo %SOFTMINT%  [3] Filter - apply an exact image filter like grayscale or blur%RESET%
echo %SOFTMINT%  [4] Inpaint - regenerate only a masked part of an image%RESET%
echo.
echo %GOLD%Choose a mode first, then follow the instructions shown after that.%RESET%
echo %CREAM%--%RESET%
echo.

set "MODE="
set /p MODE=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ mode %CORAL%^> %RESET%

if /I "%MODE%"=="" set "MODE=text"
if /I "%MODE%"=="1" set "MODE=text"
if /I "%MODE%"=="2" set "MODE=edit"
if /I "%MODE%"=="3" set "MODE=filter"
if /I "%MODE%"=="4" set "MODE=inpaint"
if /I "%MODE%"=="text" goto mode_ok
if /I "%MODE%"=="edit" goto mode_ok
if /I "%MODE%"=="filter" goto mode_ok
if /I "%MODE%"=="inpaint" goto mode_ok

echo.
echo %RED%Invalid mode. Use text, edit, filter, inpaint, 1, 2, 3, or 4.%RESET%
exit /b 1

:mode_ok
echo.

echo.
echo %MINT%Launching NediaVision...%RESET%
echo.

set "PYTHONWARNINGS=ignore:pkg_resources is deprecated as an API"
if /I "%MODE%"=="text" (
    echo %GOLD%Text mode selected.%RESET%
    echo %SOFTMINT%Next step: type a prompt that describes the image you want to create.%RESET%
    echo %SOFTMINT%Example: a realistic black cat, centered composition, detailed fur, sharp focus%RESET%
    echo.
    set "USER_PROMPT="
    set /p USER_PROMPT=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ prompt %CORAL%^> %RESET%
    if "!USER_PROMPT!"=="" (
        echo.
        echo %RED%No prompt entered. Exiting.%RESET%
        exit /b 1
    )
    py -3.11 run.py --prompt "!USER_PROMPT!" --device auto --low-spec
) else if /I "%MODE%"=="filter" (
    echo %GOLD%Filter mode selected.%RESET%
    echo %SOFTMINT%Next step 1: paste the full path of the image you want to modify.%RESET%
    echo %SOFTMINT%Next step 2: choose one of the available filters.%RESET%
    echo.
    set "IMAGEPATH="
    set "FILTERNAME="
    set /p IMAGEPATH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ image-path %CORAL%^> %RESET%
    if "!IMAGEPATH!"=="" (
        echo.
        echo %RED%No image path entered. Exiting.%RESET%
        pause
        exit /b 1
    )

    if not exist "!IMAGEPATH!" (
        echo.
        echo %RED%Image file not found:%RESET%
        echo %CREAM%!IMAGEPATH!%RESET%
        pause
        exit /b 1
    )

    echo.
    echo %GOLD%Available filters:%RESET%
    echo %SOFTMINT%  grayscale  - convert the image to grayscale%RESET%
    echo %SOFTMINT%  blackwhite - strong black and white threshold effect%RESET%
    echo %SOFTMINT%  blur       - soften the image%RESET%
    echo %SOFTMINT%  sharpen    - make the image a little sharper%RESET%
    echo.
    set /p FILTERNAME=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ filter %CORAL%^> %RESET%
    if "!FILTERNAME!"=="" (
        echo.
        echo %RED%No filter entered. Exiting.%RESET%
        pause
        exit /b 1
    )

    py -3.11 run.py --input-image "!IMAGEPATH!" --filter !FILTERNAME!
) else if /I "%MODE%"=="inpaint" (
    echo %GOLD%Inpaint mode selected.%RESET%
    echo %SOFTMINT%Next step 1: type a prompt describing what should appear in the masked area.%RESET%
    echo %SOFTMINT%Next step 2: paste the full path of the base image.%RESET%
    echo %SOFTMINT%Next step 3: paste the full path of a black-and-white mask image.%RESET%
    echo %SOFTMINT%White areas will be regenerated. Black areas will be preserved.%RESET%
    echo %SOFTMINT%Next step 4: choose a strength value for how strongly the masked zone should change.%RESET%
    echo.
    set "IMAGEPATH="
    set "MASKPATH="
    set "STRENGTH="
    set "USER_PROMPT="
    set /p USER_PROMPT=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ prompt %CORAL%^> %RESET%
    if "!USER_PROMPT!"=="" (
        echo.
        echo %RED%No prompt entered. Exiting.%RESET%
        exit /b 1
    )
    set /p IMAGEPATH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ image-path %CORAL%^> %RESET%
    if "!IMAGEPATH!"=="" (
        echo.
        echo %RED%No image path entered. Exiting.%RESET%
        pause
        exit /b 1
    )
    if not exist "!IMAGEPATH!" (
        echo.
        echo %RED%Image file not found:%RESET%
        echo %CREAM%!IMAGEPATH!%RESET%
        pause
        exit /b 1
    )
    set /p MASKPATH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ mask-path %CORAL%^> %RESET%
    if "!MASKPATH!"=="" (
        echo.
        echo %RED%No mask path entered. Exiting.%RESET%
        pause
        exit /b 1
    )
    if not exist "!MASKPATH!" (
        echo.
        echo %RED%Mask file not found:%RESET%
        echo %CREAM%!MASKPATH!%RESET%
        pause
        exit /b 1
    )
    echo.
    echo %SOFTMINT%If you are not sure, type 0.85 as a strong inpainting starting point.%RESET%
    echo %SOFTMINT%Use lower values to keep more of the original masked content and higher values for a fuller redraw.%RESET%
    echo.
    set /p STRENGTH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ strength %CORAL%^> %RESET%
    if "!STRENGTH!"=="" set "STRENGTH=0.85"

    py -3.11 run.py --prompt "!USER_PROMPT!" --input-image "!IMAGEPATH!" --mask-image "!MASKPATH!" --strength !STRENGTH! --device auto --low-spec
) else (
    echo %GOLD%Edit mode selected.%RESET%
    echo %SOFTMINT%Next step 1: type an edit prompt that describes how the image should change.%RESET%
    echo %SOFTMINT%Example: black and white photo, monochrome, high contrast, realistic%RESET%
    echo %SOFTMINT%Next step 2: paste the full path of the image you want to edit.%RESET%
    echo %SOFTMINT%Next step 3: choose a strength value.%RESET%
    echo %SOFTMINT%Recommended: 0.3 to 0.4 for light edits, 0.6 to 0.8 for stronger edits.%RESET%
    echo.
    set "IMAGEPATH="
    set "STRENGTH="
    set "USER_PROMPT="
    set /p USER_PROMPT=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ prompt %CORAL%^> %RESET%
    if "!USER_PROMPT!"=="" (
        echo.
        echo %RED%No prompt entered. Exiting.%RESET%
        exit /b 1
    )
    set /p IMAGEPATH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ image-path %CORAL%^> %RESET%
    if "!IMAGEPATH!"=="" (
        echo.
        echo %RED%No image path entered. Exiting.%RESET%
        pause
        exit /b 1
    )

    if not exist "!IMAGEPATH!" (
        echo.
        echo %RED%Image file not found:%RESET%
        echo %CREAM%!IMAGEPATH!%RESET%
        pause
        exit /b 1
    )

    echo.
    echo %SOFTMINT%If you are not sure, type 0.4 to preserve more of the original image.%RESET%
    echo %SOFTMINT%Type 0.7 or 0.8 if you want a stronger transformation.%RESET%
    echo.
    set /p STRENGTH=%CREAM%%BOLD%guest @ nediavision.ai:$ ~ strength %CORAL%^> %RESET%
    if "!STRENGTH!"=="" set "STRENGTH=0.4"

    py -3.11 run.py --prompt "!USER_PROMPT!" --input-image "!IMAGEPATH!" --strength !STRENGTH! --device auto --low-spec
)

echo.
echo %CREAM%--%RESET%
echo.
echo %MINT%%BOLD%Done.%RESET% %SOFTMINT%Check the output image at:%RESET%
echo %CREAM%%~dp0generatedoutputs\generated X.png%RESET%
echo.
echo %CREAM%%BOLD%guest @ nediavision.ai:$ ~ %CORAL%done%RESET%
echo.
set "EXIT_CHOICE="
set /p EXIT_CHOICE=%CREAM%%BOLD%Do you want to exit? (y/N) %CORAL%^> %RESET%
if /I "!EXIT_CHOICE!"=="y" exit /b 0
goto start_menu
