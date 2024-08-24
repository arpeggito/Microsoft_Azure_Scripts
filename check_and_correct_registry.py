import winreg as reg
import ctypes
import sys
import traceback
import os


REGISTRY_PATH = r"SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"


def is_admin():
    """Check if the script is running with administrative privileges."""
    return ctypes.windll.shell32.IsUserAnAdmin()


def elevate():
    """Rerun the script with administrative privileges."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

def correct_registry(registry_key, key_name, value, value_type):
    try:
        # Key is a global constant
        # Set each key to the correct value
        if value_type == "REG_SZ":
            reg.SetValueEx(registry_key, key_name, 0, reg.REG_SZ, value)
        elif value_type == "REG_DWORD":
            reg.SetValueEx(registry_key, key_name, 0, reg.REG_DWORD, value)
        print(f"{key_name} set to {value}")

    except PermissionError:
        print(f"Access denied. Please run the script as an administrator.")
    except Exception as e:
        print(f"An error occurred: {e}")


def check_and_correct_registry():
    try:
        # Path to the registry key
        registry_key = reg.OpenKey(
            reg.HKEY_LOCAL_MACHINE, REGISTRY_PATH, 0, reg.KEY_READ | reg.KEY_SET_VALUE
        )

        # List of keys to check
        expected_values = {
            "Server": ("REG_SZ", "vpn.contoso.com:443"),
            "Sso_enabled": ("REG_DWORD", 0),
            "DATA1": ("REG_SZ", "EncLM 65f1d4bc8b4140b3822ea7"),
        }

        # Check each key
        for key_name, (expected_type, expected_value) in expected_values.items():
            try:
                value, reg_type = reg.QueryValueEx(registry_key, key_name)
                if reg_type == getattr(reg, expected_type) and value == expected_value:
                    print(f"{key_name} is correct: {value}")
                else:
                    print(
                        f"{key_name} is incorrect. Expected Value: {expected_value}, Found: {value}, Expected Type: {expected_type}, Found: {reg_type}"
                    )

                    correct_registry(
                        registry_key, key_name, expected_value, expected_type
                    )
                    print("Correcting registry type and values...")

            except FileNotFoundError:
                print(f"{key_name} not found in registry.")

        reg.CloseKey(registry_key)
    except FileNotFoundError:
        print(f"Registry path {REGISTRY_PATH} not found.")
    except Exception as e:
        print(traceback.format_exc())
        print(f"An error occurred: {e}")


def main():
    if not is_admin():
        print("The script is not running with administrative privileges.")
        print("Requesting elevation...")
        elevate()
        sys.exit(0)  # Exit the non-admin instance after requesting elevation.

    # Run the function to check and correct the registry
    check_and_correct_registry()


if __name__ == "__main__":
    main()
