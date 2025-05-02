from bson import ObjectId

class OID:
    def __init__(self, value: str | ObjectId | None = None):
        self.value = ObjectId(value) if value else ObjectId()

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return str(self) == str(other)

    def to_bson(self):
        return self.value

    def __repr__(self):
        return f"OID('{self.value}')"
