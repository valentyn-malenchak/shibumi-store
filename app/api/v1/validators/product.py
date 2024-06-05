"""Contains product domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel, ValidationError, create_model

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.models.product import (
    Product,
    ProductsFilterModel,
)
from app.api.v1.services.parameter import ParameterService
from app.api.v1.services.product import ProductService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.category import CategoryLeafValidator
from app.constants import HTTPErrorMessagesEnum, ValidationErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError
from app.utils.pydantic import PositiveInt


class BaseProductValidator(BaseValidator):
    """Base product validator."""

    def __init__(self, request: Request, product_service: ProductService = Depends()):
        """Initializes base product validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.

        """

        super().__init__(request=request)

        self.product_service = product_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class ProductParametersValidator(BaseProductValidator):
    """Product parameters validator."""

    def __init__(
        self,
        request: Request,
        product_service: ProductService = Depends(),
        category_leaf_validator: CategoryLeafValidator = Depends(),
    ):
        """Initializes product parameters validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            category_leaf_validator (CategoryLeafValidator): Category leaf validator.

        """

        super().__init__(request=request, product_service=product_service)

        self.category_leaf_validator = category_leaf_validator

        self._errors: list[dict[str, Any]] = []

    async def validate(
        self,
        category_id: ObjectId,
        requested_parameters: dict[str, Any],
    ) -> None:
        """Validates product parameters.

        Args:
            category_id (ObjectId): BSON object identifier of requested category.
            requested_parameters (dict[str, Any]): Requested product parameters.

        Raises:
            HTTPException: If product parameters are invalid.

        """

        category = await self.category_leaf_validator.validate(category_id=category_id)

        for parameter in category.parameters:
            # each of category parameters is required to set
            if parameter.machine_name not in requested_parameters:
                self._errors.append(
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "parameters",
                            parameter.machine_name,
                        ],
                        "msg": ValidationErrorMessagesEnum.REQUIRED_FIELD,
                    }
                )

                continue

            value = requested_parameters[parameter.machine_name]

            # if parameter is set as None, just skip type validation
            if value is None:
                continue

            type_ = getattr(ProductParameterTypesEnum, parameter.type)

            # parameter value should have an appropriate type
            if not isinstance(value, type_.value):
                self._errors.append(
                    {
                        "type": "invalid_type",
                        "loc": [
                            "body",
                            "parameters",
                            parameter.machine_name,
                        ],
                        "msg": ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.format(
                            type_=type_.value.__name__
                        ),
                        "input": value,
                    }
                )

        # HTTPException in case list of errors is not empty
        if self._errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=self._errors,
            )


class ProductByIdValidator(BaseProductValidator):
    """Product by identifier validator."""

    async def validate(self, product_id: ObjectId) -> Product:
        """Validates requested product by id.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If requested product is not found.

        """

        try:
            product = await self.product_service.get_by_id(id_=product_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                    entity="Product"
                ),
            )

        return product


class ProductByIdStatusValidator(BaseProductValidator):
    """Product by identifier status validator."""

    def __init__(
        self,
        request: Request,
        product_service: ProductService = Depends(),
        product_by_id_validator: ProductByIdValidator = Depends(),
    ):
        """Initializes product by identifier status validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            product_by_id_validator (ProductByIdValidator): Product by identifier
            validator.

        """

        super().__init__(request=request, product_service=product_service)

        self.product_by_id_validator = product_by_id_validator

    async def validate(self, product_id: ObjectId) -> Product:
        """Checks product and user's access to it.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If current user don't have access to product.

        """

        product = await self.product_by_id_validator.validate(product_id=product_id)

        current_user = getattr(self.request.state, "current_user", None)

        if (
            current_user is None or current_user.object.is_client
        ) and product.available is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED,
            )

        return product


class ProductsAvailableFilterValidator(BaseProductValidator):
    """Products available filter validator."""

    async def validate(self, available: bool | None) -> None:
        """Checks if the current user has access to not available products.

        Args:
            available (available: bool | None): Product availability filter.

        Raises:
            HTTPException: If current user don't have access to not available filter
            products.

        """

        current_user = getattr(self.request.state, "current_user", None)

        if (
            current_user is None or current_user.object.is_client
        ) and available is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PRODUCTS_NOT_AVAILABLE_ACCESS_DENIED,
            )


class ProductsFilterValidator(BaseProductValidator):
    """Products filter validator."""

    def __init__(
        self,
        request: Request,
        product_service: ProductService = Depends(),
        parameter_service: ParameterService = Depends(),
        products_available_filter_validator: ProductsAvailableFilterValidator = Depends(),  # noqa: E501
    ):
        """Initializes products filter validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            parameter_service (ParameterService): Parameter service.
            products_available_filter_validator (ProductsAvailableFilterValidator):
            Products available filter validator.

        """

        super().__init__(request=request, product_service=product_service)

        self.parameter_service = parameter_service

        self.products_available_filter_validator = products_available_filter_validator

    async def validate(
        self,
        category_id: ObjectId | None,
        available: bool | None,
        ids: list[ObjectId] | None,
    ) -> ProductsFilterModel:
        """Validates and formats products list filter.

        Args:
            category_id (ObjectId | None): Category identifier filter.
            available (bool | None): Product availability filter.
            ids (list[ObjectId] | None): Filter by list of product identifiers.

        Returns:
            ProductsFilterModel: Products filter object.

        Raises:
            HTTPException: If product parameters filter is invalid.

        """

        await self.products_available_filter_validator.validate(available=available)

        fields: dict[str, Any] = {
            parameter["machine_name"]: (
                list[getattr(ProductParameterTypesEnum, parameter["type"]).value]  # type: ignore
                if parameter["type"] != ProductParameterTypesEnum.LIST.name
                else list[str],
                None,
            )
            for parameter in await self.parameter_service.get()
        }

        parameters_model = create_model(
            "ProductsParameters", **fields, __base__=BaseModel
        )

        try:
            query_params = parameters_model(
                **{
                    query_param: self.request.query_params.getlist(query_param)
                    for query_param in self.request.query_params.keys()
                }
            ).model_dump(exclude_unset=True)

        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error.errors(),
            )

        return ProductsFilterModel(
            category_id=category_id,
            available=available,
            ids=ids,
            parameters=query_params,
        )


class ProductQuantityValidator(BaseProductValidator):
    """Product quantity validator."""

    def __init__(
        self,
        request: Request,
        product_service: ProductService = Depends(),
        product_by_id_status_validator: ProductByIdStatusValidator = Depends(),
    ):
        """Initializes product quantity validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            product_by_id_status_validator (ProductByIdStatusValidator): Product by
            identifier status validator.

        """

        super().__init__(request=request, product_service=product_service)

        self.product_by_id_status_validator = product_by_id_status_validator

    async def validate(self, product_id: ObjectId, quantity: PositiveInt) -> Product:
        """Validates product.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Requested product quantity.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If cart product quantity is exceeded the maximum number
            available.

        """

        product = await self.product_by_id_status_validator.validate(
            product_id=product_id
        )

        if product.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.MAXIMUM_PRODUCT_QUANTITY_AVAILABLE,
            )

        return product
