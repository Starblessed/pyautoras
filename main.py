from win32com import client

def get_ras_dispatch_string(version: str) -> str:
    """Gets the RAS Dispatch string from the specified RAS version.

    Args:
        version (float): RAS version to use.

    Returns:
        str: RAS Dispatch string.
    """
    
    return f"RAS{version.replace(".", "")}.HECRASController"

def main():
    ras_dstr = get_ras_dispatch_string("7.0")
    
    print(ras_dstr)


if __name__ == "__main__":
    main()
