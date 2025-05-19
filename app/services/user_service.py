import dataclasses

from app.dto.user_dto import UserRequestDto
from app.models.user_model import UserModel
from app.repository.mongo_repository import MongoRepository
from app.infra.redis import redis_cache


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

    @redis_cache(
        ttl=60,
        key_prefix="user",
        key_fn=lambda user_id, **_: f"id:{user_id}",
        use_cache=False,
    )
    async def get_user_by_id(self, user_id: str) -> dict:
        result = await self.repository.find_by_id(id=user_id)

        return result

    async def soft_delete_user(self, user_id: str):
        await self.repository.soft_delete(id=user_id)
