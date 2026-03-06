import json
import os

CONFIG_FILE = "config.json"

def load():
    """Load configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    # Return default configuration
    return {
        "default_quality": "90",
        "default_format": "JPEG",
        "default_width": "800",
        "default_height": "600"
    }

def save(data):
    """Save configuration to file"""
    try:
        config = load()
        config.update(data)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config
    except Exception as e:
        print(f"Error saving config: {e}")
        return load()
