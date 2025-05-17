import dataclasses

import orjson

from app.dto.user_dto import UserRequestDto
from app.models.user_model import UserModel
from app.repository.mongo_repository import MongoRepository
from app.infra.redis import RedisClient


@dataclasses.dataclass(slots=True)
class UserService:
    repository = MongoRepository[UserModel](UserModel)

    async def list_users(self, page: int, limit: int) -> list[UserModel]:
        return await self.repository.find_all(page=page, limit=limit)

    async def create_user(self, data: UserRequestDto) -> dict:
        result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
        user = UserModel.create(**result)
        await self.repository.save(model=user)
        return user.to_dict()

    async def get_user_by_id(self, user_id: str) -> dict:
        redis = RedisClient.get()
        key_redis = f"cotador:{id}"
        cached_result = await redis.get(key_redis)

        if cached_result:
            return orjson.loads(cached_result)

        result = await self.repository.find_by_id(id=user_id)

        if not result:
            return None

        await redis.set(key_redis, orjson.dumps(result), ex=15)
        return result

    async def soft_delete_user(self, user_id: str):
        await self.repository.soft_delete(id=user_id)
