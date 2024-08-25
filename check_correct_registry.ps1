# Path to the registry key
$registryPath = "HKLM:\SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"

# Function to check if the current user is an administrator
function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to request elevation if the script is not running as admin
function Invoke-Elevate {
    if (-not (Test-IsAdmin)) {
        Write-Host "Requesting elevation..."
        # Prepare arguments for relaunching the script with elevated privileges
        $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
        # Start a new PowerShell process with elevated privileges
        Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -Verb RunAs -Wait
        # Exit the current process after starting the elevated one
        Write-Host "Elevation requested. Exiting current process."
        exit
    } else {
        Write-Host "Script is running with administrative privileges."
    }
}

# Function to set a registry value
function Set-RegistryValue {
    param (
        [Parameter(Mandatory=$true)]
        [string]$keyName, # The name of the registry value to be set
        
        [Parameter(Mandatory=$true)]
        [string]$valueType, # The type of the registry value (e.g., REG_SZ, REG_DWORD)
        
        [Parameter(Mandatory=$true)]
        $value # The value to set for the registry key
    )

    try {
        # Set the registry value based on the specified type
        if ($valueType -eq "REG_SZ") {
            Set-ItemProperty -Path $registryPath -Name $keyName -Value $value
        } elseif ($valueType -eq "REG_DWORD") {
            Set-ItemProperty -Path $registryPath -Name $keyName -Value $value
        }
        Write-Host "$keyName set to $value"
    } catch {
        # Output an error message if the operation fails
        Write-Host "An error occurred: $_"
    }
}

# Function to check and correct registry values
function Check-AndCorrectRegistry {
    # Check if the registry path exists
    if (-not (Test-Path $registryPath)) {
        Write-Host "Registry path $registryPath not found."
        return
    }

    # Define expected registry values and types
    $expectedValues = @{
        "Server"      = @("REG_SZ", "vpn.contoso.com:443")
        "Sso_enabled" = @("REG_DWORD", 0)
        "DATA1"       = @("REG_SZ", "EncLM 65f1d4bc8b4140b3822ea7")
    }

    # Iterate over each expected registry key and value
    foreach ($keyName in $expectedValues.Keys) {
        $expectedType, $expectedValue = $expectedValues[$keyName]
        try {
            # Get the current value of the registry key
            $actualValue = (Get-ItemProperty -Path $registryPath -Name $keyName).$keyName
            # Determine the type of the current registry value
            $actualType = if ($expectedType -eq "REG_SZ") { "REG_SZ" } elseif ($expectedType -eq "REG_DWORD") { "REG_DWORD" }

            # Check if the current value matches the expected value and type
            if ($actualType -eq $expectedType -and $actualValue -eq $expectedValue) {
                Write-Host "$keyName is correct: $actualValue"
            } else {
                Write-Host "$keyName is incorrect. Expected Value: $expectedValue, Found: $actualValue, Expected Type: $expectedType, Found: $actualType"
                # Correct the registry value if it does not match the expected value
                Set-RegistryValue -keyName $keyName -valueType $expectedType -value $expectedValue
                Write-Host "Correcting registry type and values..."
            }
        } catch {
            # Handle the case where the registry key is not found
            Write-Host "$keyName not found in registry."
        }
    }
}

# Main function to control script execution
function Main {
    # Elevate the script if not running as admin
    Invoke-Elevate

    # Verify if the script is running with administrative privileges
    if (-not (Test-IsAdmin)) {
        Write-Host "Elevation failed. Script is not running with administrative privileges."
        exit
    }

    # Run the function to check and correct the registry
    Check-AndCorrectRegistry
}

# Execute the script
Main
