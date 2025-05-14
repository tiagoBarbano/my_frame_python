from app.models.model_base import MongoModel


class UserModel(MongoModel):
    __collection__ = "users"

    empresa: str
    cotacao_final: float
