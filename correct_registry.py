import winreg as reg

def correct_registry():
    try:
        # Path to the registry key
        registry_path = r"SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, registry_path, 0, reg.KEY_WRITE)

        # List of keys to correct
        correct_values = {
            "Server": ("REG_SZ", "vpn.contoso.com:443"),
            "Sso_enabled": ("REG_DWORD", 0),
            "DATA1": ("REG_SZ", "EncLM 65f1d4bc8b4140b3822ea7")
        }

        # Set each key to the correct value
        for key_name, (value_type, value) in correct_values.items():
            if value_type == "REG_SZ":
                reg.SetValueEx(key, key_name, 0, reg.REG_SZ, value)
            elif value_type == "REG_DWORD":
                reg.SetValueEx(key, key_name, 0, reg.REG_DWORD, value)
            print(f"{key_name} set to {value}")

        reg.CloseKey(key)
    except FileNotFoundError:
        print(f"Registry path {registry_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    correct_registry()
