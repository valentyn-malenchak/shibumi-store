"""Contains product domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel, ValidationError, create_model

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.models.product import Product
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


class ProductByIdValidator(BaseProductValidator):
    """Product by identifier validator."""

    async def validate(self, product_id: ObjectId) -> Product:
        """Validates requested product by identifier.

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


class ProductAccessValidator(BaseProductValidator):
    """Product access validator."""

    async def validate(self, product: Product) -> Product:
        """Validates requested user has access to product.

        Args:
            product: Product object.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If current user don't have access to product.

        """

        current_user = getattr(self.request.state, "current_user", None)

        if (
            current_user is None or current_user.object.is_client
        ) and product.available is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(
                    destination="product"
                ),
            )

        return product


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


class ProductAvailableFilterValidator(BaseProductValidator):
    """Product available filter validator."""

    async def validate(self, available: bool | None) -> None:
        """Validates if the current user has access to not available products.

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
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(
                    destination="not available product"
                ),
            )


class ProductParametersFilterValidator(BaseProductValidator):
    """Product parameters filter validator."""

    def __init__(
        self,
        request: Request,
        product_service: ProductService = Depends(),
        parameter_service: ParameterService = Depends(),
    ):
        """Initializes product parameters filter validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            parameter_service (ParameterService): Parameter service.

        """

        super().__init__(request=request, product_service=product_service)

        self.parameter_service = parameter_service

    async def validate(self) -> dict[str, Any]:
        """Validates product parameters filter.

        Returns:
            dict[str, Any]: Product parameter filter.

        Raises:
            HTTPException: If product parameter filter is invalid.

        """

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
            "ProductParameterFilter", **fields, __base__=BaseModel
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

        return query_params


class ProductQuantityValidator(BaseProductValidator):
    """Product quantity validator."""

    async def validate(self, product: Product, quantity: PositiveInt) -> Product:
        """Validates product quantity.

        Args:
            product (Product): Product object.
            quantity (PositiveInt): Requested product quantity.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If cart product quantity is exceeded the maximum number
            available.

        """

        if product.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.MAXIMUM_PRODUCT_QUANTITY_AVAILABLE,
            )

        return product
