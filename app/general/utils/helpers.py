from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # Ensure the value is a valid ObjectId
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return str(value) if isinstance(value, ObjectId) else str(ObjectId(value))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", format="objectid")


def prepare_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list, tuple)):
                prepare_json(value)
    elif isinstance(data, (list, tuple)):
        for i, item in enumerate(data):
            data[i] = prepare_json(item)
    return data
