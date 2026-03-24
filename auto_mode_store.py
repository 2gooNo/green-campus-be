from datetime import datetime

from config import settings_collection


_AUTO_MODE_DOC_ID = "auto_mode"
_DEFAULT_AUTO_MODE = True


def get_auto_mode():
    # Read persisted auto-mode state, create default if missing.
    state = settings_collection.find_one({"_id": _AUTO_MODE_DOC_ID})
    if state is None:
        settings_collection.update_one(
            {"_id": _AUTO_MODE_DOC_ID},
            {
                "$set": {
                    "auto_mode": _DEFAULT_AUTO_MODE,
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return _DEFAULT_AUTO_MODE

    return state.get("auto_mode", _DEFAULT_AUTO_MODE)


def set_auto_mode(value):
    # Persist and return normalized boolean mode value.
    settings_collection.update_one(
        {"_id": _AUTO_MODE_DOC_ID},
        {"$set": {"auto_mode": bool(value), "updated_at": datetime.utcnow()}},
        upsert=True,
    )
    return bool(value)
