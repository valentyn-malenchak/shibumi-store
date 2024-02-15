"""Contains product domain validators."""


from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.services.product import ProductService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.category import LeafCategoryValidator
from app.constants import ValidationErrorMessagesEnum


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
                        "msg": ValidationErrorMessagesEnum.REQUIRED_FIELD.value,
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
