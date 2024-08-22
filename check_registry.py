import winreg as reg

def check_registry():
    try:
        # Path to the registry key
        registry_path = r"SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\contoso"
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, registry_path, 0, reg.KEY_READ)

        # List of keys to check
        expected_values = {
            "Server": ("REG_SZ", "vpn.contoso.com:443"),
            "Sso_enabled": ("REG_DWORD", 0),
            "DATA1": ("REG_SZ", "EncLM 65f1d4bc8b4140b3822ea7")
        }

        # Check each key
        for key_name, (expected_type, expected_value) in expected_values.items():
            try:
                value, reg_type = reg.QueryValueEx(key, key_name)
                if reg_type == getattr(reg, expected_type) and value == expected_value:
                    print(f"{key_name} is correct: {value}")
                else:
                    print(f"{key_name} is incorrect. Expected: {expected_value}, Found: {value}")
            except FileNotFoundError:
                print(f"{key_name} not found in registry.")

        reg.CloseKey(key)
    except FileNotFoundError:
        print(f"Registry path {registry_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_registry()