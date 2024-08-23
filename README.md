# Correct Registry Script

This Python script checks and corrects specific registry keys within the Windows Registry for the Fortinet FortiClient SSL VPN settings. It ensures that the specified registry values are correctly set according to predefined expected values and types. If the values do not match, the script updates them accordingly.

## Table of Contents

- [Prerequisites](#prerequisites)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Error Handling](#error-handling)
- [Customizing the Script](#customizing-the-script)
- [Known Issues](#known-issues)
- [License](#license)

## Prerequisites

- **Python 3.x**: Ensure that Python 3.x is installed on your system.
- **Administrator Privileges**: Ideally the script requires administrative privileges to modify the Windows Registry.

## How It Works

### Script Components

- **`is_admin()`**: Checks if the script is running with administrative privileges.
- **`elevate()`**: Re-runs the script with administrative privileges if it is not already elevated.
- **`correct_registry()`**: Sets a registry key to the correct value and type if it is not already set correctly.
- **`show_message()`**: Displays a message box to the user.
- **`check_and_correct_registry()`**: Main function that checks the specified registry keys and corrects them if necessary.
- **`main()`**: The entry point of the script, which checks for administrative privileges and calls the necessary functions.

### Registry Path

The script targets the following registry path: "SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"

### Expected Registry Values

The script checks for the following keys and values:

- `Server`: Expected value is `"vpn.contoso.com:443"` (Type: `REG_SZ`)
- `Sso_enabled`: Expected value is `0` (Type: `REG_DWORD`)
- `DATA1`: Expected value is `"EncLM 65f1d4bc8b4140b3822ea7"` (Type: `REG_SZ`)

If any of these keys are missing or have incorrect values or types, the script will update them accordingly.

## Usage

1. **Run the script**: To use the script, simply run it with Python from your computer:
   ```bash
   python check_and_correct_registry.py

2. **Administrator Privileges**: If the script is not run as an administrator, it will request elevation. The script will re-run with the necessary privileges and continue executing.

3. **Check and Correct Registry**: The script will automatically check the specified registry keys and correct any discrepancies.

### Error Handling

1. **PermissionError**: If the script does not have the required permissions to modify the registry, it will prompt the user to run the script as an administrator.

2. **FileNotFoundError**: If the registry path or specific keys are not found, the script will notify the user but continue executing for other keys.

3. **General Exceptions**: Any other exceptions are caught, and detailed information is provided to the user.

### Considerations 

- OS Compatibility: The script is designed to run on Windows systems. It will not function on non-Windows platforms.