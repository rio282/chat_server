import os
import re


def get_downloads_path():
    # platform-independent way to get the user's home dir
    home_dir = os.path.expanduser("~")

    # check operating system &  build path to the downloads folder
    if os.name == "posix":  # Linux, Unix, macOS
        downloads_path = os.path.join(home_dir, "Downloads")
    elif os.name == "nt":  # Windows
        downloads_path = os.path.join(home_dir, "Downloads")
    else:
        # Unsupported OS
        raise NotImplementedError("Unsupported operating system")

    return downloads_path


def is_valid_ipv4(ip: str):
    if ip == "localhost":
        return True

    ipv4_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    return bool(ipv4_pattern.match(ip))


def is_valid_port(port: int | str):
    try:
        port = int(port)
    except ValueError:
        return False

    return 0 < port < 65535
