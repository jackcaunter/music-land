# config_loader.py

from config import CONFIG

try:
    from config_local import CONFIG as LOCAL_CONFIG
    CONFIG.update(LOCAL_CONFIG)
except ImportError:
    pass
