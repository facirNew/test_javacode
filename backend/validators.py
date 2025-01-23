import uuid


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value, version=4)
        return True
    except ValueError:
        return False
