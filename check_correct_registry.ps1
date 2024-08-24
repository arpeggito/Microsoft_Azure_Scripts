# Path to the registry key
$registryPath = "HKLM:\SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"

function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-Elevate {
    if (-not (Test-IsAdmin)) {
        Write-Host "Requesting elevation..."
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
        Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -Verb RunAs -Wait
        Write-Host "Elevation requested. Exiting current process."
        exit
    } else {
        Write-Host "Script is running with administrative privileges."
    }
}

function Set-RegistryValue {
    param (
        [Parameter(Mandatory=$true)]
        [string]$keyName,
        
        [Parameter(Mandatory=$true)]
        [string]$valueType,
        
        [Parameter(Mandatory=$true)]
        $value
    )

    try {
        if ($valueType -eq "REG_SZ") {
            Set-ItemProperty -Path $registryPath -Name $keyName -Value $value
        } elseif ($valueType -eq "REG_DWORD") {
            Set-ItemProperty -Path $registryPath -Name $keyName -Value $value
        }
        Write-Host "$keyName set to $value"
    } catch {
        Write-Host "An error occurred: $_"
    }
}

function Check-AndCorrectRegistry {
    if (-not (Test-Path $registryPath)) {
        Write-Host "Registry path $registryPath not found."
        return
    }

    $expectedValues = @{
        "Server"      = @("REG_SZ", "vpn.contoso.com:443")
        "Sso_enabled" = @("REG_DWORD", 0)
        "DATA1"       = @("REG_SZ", "EncLM 65f1d4bc8b4140b3822ea7")
    }

    foreach ($keyName in $expectedValues.Keys) {
        $expectedType, $expectedValue = $expectedValues[$keyName]
        try {
            $actualValue = (Get-ItemProperty -Path $registryPath -Name $keyName).$keyName
            $actualType = if ($expectedType -eq "REG_SZ") { "REG_SZ" } elseif ($expectedType -eq "REG_DWORD") { "REG_DWORD" }

            if ($actualType -eq $expectedType -and $actualValue -eq $expectedValue) {
                Write-Host "$keyName is correct: $actualValue"
            } else {
                Write-Host "$keyName is incorrect. Expected Value: $expectedValue, Found: $actualValue, Expected Type: $expectedType, Found: $actualType"
                Set-RegistryValue -keyName $keyName -valueType $expectedType -value $expectedValue
                Write-Host "Correcting registry type and values..."
            }
        } catch {
            Write-Host "$keyName not found in registry."
        }
    }
}

function Main {
    # Elevate if not running as admin
    Invoke-Elevate

    # Verify elevation
    if (-not (Test-IsAdmin)) {
        Write-Host "Elevation failed. Script is not running with administrative privileges."
        exit
    }

    # Run the function to check and correct the registry
    Check-AndCorrectRegistry
}

# Execute the script
Main
