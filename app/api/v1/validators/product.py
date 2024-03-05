"""Contains product domain validators."""


from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.models.product import Product
from app.api.v1.services.product import ProductService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.category import LeafCategoryValidator
from app.constants import HTTPErrorMessagesEnum, ValidationErrorMessagesEnum


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
        leaf_category_validator: LeafCategoryValidator = Depends(),
    ):
        """Initializes product parameter validator.

        Args:
            request (Request): Current request object.
            product_service (ProductService): Product service.
            leaf_category_validator (LeafCategoryValidator): Leaf category validator.

        """

        super().__init__(request=request, product_service=product_service)

        self.leaf_category_validator = leaf_category_validator

        self._errors: List[Dict[str, Any]] = []

    async def validate(
        self,
        category_id: ObjectId,
        requested_parameters: Dict[str, Any],
    ) -> None:
        """Validates product parameters.

        Args:
            category_id (ObjectId): BSON object identifier of requested category.
            requested_parameters (Dict[str, Any]): Requested product parameters.

        Raises:
            HTTPException: If product parameters are invalid.

        """

        category = await self.leaf_category_validator.validate(category_id=category_id)

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
                        "msg": ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.value.format(  # noqa: E501
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


class ProductIdValidator(BaseProductValidator):
    """Product identifier validator."""

    async def validate(self, product_id: ObjectId) -> Product:
        """Validates requested product by id.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.

        Returns:
            Product: Product object.

        Raises:
            HTTPException: If requested product is not found.

        """

        product = await self.product_service.get_by_id(id_=product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                    entity="Product"
                ),
            )

        return product


class ProductAccessValidator(BaseProductValidator):
    """Product access validator."""

    async def validate(self, product: Product) -> None:
        """Checks if the current user has access to product.

        Args:
            product (Product): Product object.

        Raises:
            HTTPException: If current user don't have access to product.

        """

        current_user = getattr(self.request.state, "current_user", None)

        if (
            current_user is None or current_user.object.is_client
        ) and product.available is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED,
            )


class ProductsAccessFilterValidator(BaseProductValidator):
    """Products access filter validator."""

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
