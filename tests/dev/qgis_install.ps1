#Requires -RunAsAdministrator

<#
.Synopsis
   Download the OSGeo4W installer then download and install QGIS LTR (through the 'full' meta-package).
.DESCRIPTION
   This script will:
      1. change the current directory to the user downloads folder
      2. download the OSGeo4W installer
      3. launch it passing command-line parameters to DOWNLOAD packages required to QGIS LTR FULL
      4. launch it passing command-line parameters to INSTALL QGIS LTR

    Documentation reference: https://trac.osgeo.org/osgeo4w/wiki/CommandLine
#>

# Save current working directory
$starter_path = Get-Location

# Move into the user download directory
Set-Location -Path "$env:USERPROFILE/Downloads"

# Download installer
Write-Host "= Start downloading the OSGeo4W installer" -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://download.osgeo.org/osgeo4w/osgeo4w-setup-x86_64.exe" -OutFile "osgeo4w-setup-x86_64.exe"

# Download the packages included into the meta-package QGIS LTR FULL
Write-Host "== Installer downloaded into $env:USERPROFILE/Downloads" -ForegroundColor Yellow
Write-Host "== Start downloading the QGIS LTR full meta-package" -ForegroundColor Yellow
.\osgeo4w-setup-x86_64.exe --quiet-mode --download --no-desktop --advanced --arch x86_64 --autoaccept --packages qgis-ltr-full | out-null

# Launch the installation (same command to upgrade with clean up)
Write-Host "=== QGIS packages downloaded into 'C:\OSGeo4W64'" -ForegroundColor Yellow
Write-Host "=== Start installing / upgrading QGIS LTR..." -ForegroundColor Yellow
& .\osgeo4w-setup-x86_64.exe --quiet-mode --delete-orphans --upgrade-also --no-desktop --advanced --arch x86_64 --autoaccept --packages qgis-ltr-full

# Return to the initial directory
Set-Location -Path $starter_path
Write-Host "==== Work is done!" -ForegroundColor Green
