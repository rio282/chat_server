from typing import Dict, Final
import os


def _convert_to_correct_type(value):
    try:
        return int(value)
    except ValueError:
        return value


def load_settings() -> Dict:
    settings = {}
    with open(file=settings_file_path, mode="r") as settings_file:
        for line in settings_file:
            setting = line.strip()
            if setting.count("=") > 1:
                raise Exception("Invalid settings file.")

            key, value = setting.split("=")
            settings[key] = _convert_to_correct_type(value)

    return settings


def locate_server_settings() -> str:
    default_server_settings_path = "./server.settings"

    if os.path.exists(default_server_settings_path):
        return default_server_settings_path
    else:
        for root, dirs, files in os.walk(os.getcwd()):
            if "server.settings" in files:
                return os.path.join(root, "server.settings")

    # Return None if the file is not found
    return ""


settings_file_path: Final[str] = locate_server_settings()
