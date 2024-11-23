TORTOISE_CONFIG = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

SECRET_KEY = '3773073fb36f449e35f1fbf11da4564471b75fa45bdff5a6a3f0465d841529262dcb15ff7f2c7cd21e274394595b0fe4500596bf68c7db20284d862f7c0c6137'