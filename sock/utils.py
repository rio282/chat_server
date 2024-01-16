import os


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
