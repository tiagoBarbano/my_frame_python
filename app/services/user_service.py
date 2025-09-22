import dataclasses

import msgspec

from app.core.logger import log
from app.dto.user_dto import UserListResponse, UserRequestDto, UserResponseDto
from app.models.user_model import UserModel
from app.repository.mongo_repository import MongoRepository
from app.infra.redis import RedisClient


@dataclasses.dataclass(slots=True)
class UserService:
    repository: MongoRepository[UserModel] = dataclasses.field(init=False)

    def __post_init__(self):
        self.repository = MongoRepository(UserModel)

    async def list_users(self, page: int, limit: int) -> list[UserModel]:
        data, total_items = await self.repository.find_all(page=page, limit=limit)
        items = [
            UserResponseDto(
                _id=doc["_id"],
                empresa=doc["empresa"],
                cotacao_final=doc["cotacao_final"],
            ).encode_dict()
            for doc in data
        ]

        total_pages = (total_items + limit - 1) // limit

        return UserListResponse(
            data=items,
            page=page,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
        ).encode_dict()

    async def create_user(self, data: UserRequestDto) -> dict:
        result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
        user = UserModel.create(**result)
        await self.repository.save(model=user)
        return user.to_dict()

    # @redis_cache(
    #     ttl=60,
    #     key_prefix="user",
    #     key_fn=lambda user_id, **_: f"id:{user_id}", #"id:{user_id}",
    #     use_cache=True,
    # )
    async def get_user_by_id(self, user_id: str) -> dict:
        redis_key = f"user:id:{user_id}"
        async with RedisClient.connection() as redis:        
            cached = await redis.get(redis_key)
            if cached:
                return msgspec.json.decode(cached)
            
            result = await self.repository.find_by_id(id=user_id)
            
            if result is not None:
                await redis.set(redis_key, msgspec.json.encode(result), ex=60)

            return result

    async def soft_delete_user(self, user_id: str):
        await self.repository.soft_delete(id=user_id)
