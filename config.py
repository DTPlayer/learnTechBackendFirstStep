TORTOISE_CONFIG = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

SECRET_KEY = 'ef460dfca73e40a51dc42c4ca36963e'