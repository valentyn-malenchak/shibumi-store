"""Module that contains category repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum, SortingTypesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class CategoryRepository(BaseRepository):
    """Category repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORIES.value

    async def get(
        self,
        *_: Any,
        path: str | None = None,
        leafs: bool = False,
        session: AsyncIOMotorClientSession | None = None,
        **__: Any,
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of categories based on parameters.

        Args:
            _ (Any): Parameters for list searching, sorting and pagination.
            path (str | None): Category tree path filtering. Defaults to None.
            leafs (bool): Defines if only leaf categories will be returned.
            Defaults to False.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            __ (Any): Parameters for list filtering.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of categories.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=await self._get_list_query_filter(path=path, leafs=leafs),
            projection=self._get_list_query_projection(),
            sort=self._get_list_sorting(sort_by="_id", sort_order=SortingTypesEnum.ASC),
            session=session,
        )

    async def _get_list_query_filter(
        self,
        *_: Any,
        path: str | None = None,
        leafs: bool = False,
        **__: Any,
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list searching.
            path (str | None): Category tree path filtering. Defaults to None.
            leafs (bool): Defines if only leaf categories will be returned.
            Defaults to False.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: Dict[str, Any] = {}

        if path is not None:
            query_filter["path"] = {"$regex": f"^{path}"}

        if leafs is True:
            parent_ids = await self._mongo_service.distinct(
                self._collection_name, "parent_id", filter_={"parent_id": {"$ne": None}}
            )

            query_filter["_id"] = {"$nin": parent_ids}

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {"parameters": ProjectionValuesEnum.EXCLUDE.value}

    async def count(
        self,
        *_: Any,
        path: str | None = None,
        leafs: bool = False,
        session: AsyncIOMotorClientSession | None = None,
        **__: Any,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            _ (Any): Parameters for list searching.
            path (str | None): Category tree path filtering. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            leafs (bool): Defines if only leaf categories will be returned.
            Defaults to False.
            __ (Any): Parameters for list filtering.

        Returns:
            int: Count of documents.

        """
        return await self._mongo_service.count_documents(
            collection=self._collection_name,
            filter_=await self._get_list_query_filter(path=path, leafs=leafs),
            session=session,
        )

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves a category with related data from the repository by its unique
        identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved category.

        """

        result = await self._mongo_service.aggregate(
            collection=self._collection_name,
            pipeline=[
                {"$match": {"_id": id_}},
                {
                    "$lookup": {
                        "from": MongoCollectionsEnum.PARAMETERS.value,
                        "localField": "parameters",
                        "foreignField": "_id",
                        "as": "parameters",
                    }
                },
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "_id",
                        "foreignField": "parent_id",
                        "as": "children",
                    }
                },
                {"$addFields": {"has_children": {"$gt": [{"$size": "$children"}, 0]}}},
            ],
            session=session,
        )

        return result[0] if result else None
