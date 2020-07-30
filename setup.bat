REM <#
copy %0 %0.ps1
PowerShell.exe -ExecutionPolicy Unrestricted -NoProfile -Command "&{Set-Alias REM Write-Host; %0.ps1}"
del %0.ps1
REM #>

### Your PowerShell script goes below here.
[Environment]::SetEnvironmentVariable("PANGUI_TOPDIR", "C:\Users\Mu2e\Desktop\mu2e-tracker-factory\", "PROCESS")
[Environment]::SetEnvironmentVariable("PANGUI_TOPDIR", "C:\Users\Mu2e\Desktop\mu2e-tracker-factory\", "USER")
