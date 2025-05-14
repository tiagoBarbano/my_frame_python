import dataclasses
import orjson

from app.infra.database import MongoDB
from app.dto.user_dto import UserRequestDto
from app.models.user_model import UserModel
from app.repository.mongo_repository import MongoRepository
from app.infra.redis import RedisClient


@dataclasses.dataclass(slots=True)
class UserService:
    repository = MongoRepository[UserModel](UserModel)

    async def list_users(self) -> list[UserModel]:
        return await self.repository.find_all(db=MongoDB.get_db())

    async def create_user(self, data: UserRequestDto) -> dict:
        result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
        user = UserModel.create(**result)
        await self.repository.save(model=user, db=MongoDB.get_db())
        return user.to_dict()

    async def get_user_by_id(self, user_id: str) -> dict:
        redis = RedisClient.get()
        key_redis = f"cotador:{id}"
        cached_result = await redis.get(key_redis)

        if cached_result:
            return orjson.loads(cached_result)

        result = await self.repository.find_by_id(id=user_id, db=MongoDB.get_db())

        if not result:
            return None

        await redis.set(key_redis, orjson.dumps(result.to_dict()), ex=15)
        return result.to_dict()

    async def soft_delete_user(self, user_id: str):
        await self.repository.soft_delete(id=user_id, db=MongoDB.get_db())
