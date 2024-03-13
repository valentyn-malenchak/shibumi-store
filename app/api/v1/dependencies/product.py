"""Contains product domain dependencies."""

from typing import Annotated, Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel, ValidationError, create_model

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.product import (
    BaseProductsFilterModel,
    Product,
    ProductRequestModel,
    ProductsFilterModel,
)
from app.api.v1.services.parameter import ParameterService
from app.api.v1.validators.product import (
    ProductAccessValidator,
    ProductIdValidator,
    ProductParametersValidator,
    ProductsAccessFilterValidator,
)


class ProductDataDependency:
    """Create/update product dependency."""

    async def __call__(
        self,
        product_data: ProductRequestModel,
        product_parameters_validator: ProductParametersValidator = Depends(),
    ) -> ProductRequestModel:
        """Checks if the product can be created/updated.

        Args:
            product_data (ProductRequestModel): New product data.
            product_parameters_validator (ProductParametersValidator): Product parameter
            validator.

        Returns:
            ProductRequestModel: Product data.

        """

        await product_parameters_validator.validate(
            category_id=product_data.category_id,
            requested_parameters=product_data.parameters,
        )

        return product_data


class ProductIdDependency:
    """Product identifier dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        product_id_validator: ProductIdValidator = Depends(),
    ) -> Product:
        """Checks product from request by identifier.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            product_id_validator (ProductIdValidator): Product identifier validator.

        Returns:
            Product: Product object.

        """

        return await product_id_validator.validate(product_id=product_id)


class GetProductDependency:
    """Get product dependency."""

    async def __call__(
        self,
        product: Product = Depends(ProductIdDependency()),
        product_access_validator: ProductAccessValidator = Depends(),
    ) -> Product:
        """Checks if user can get a product from request.

        Args:
            product (Product): Product object.
            product_access_validator (ProductAccessValidator): Product access validator.

        Returns:
            Product: Product object.

        """

        await product_access_validator.validate(product=product)

        return product


class ProductsFilterDependency:
    """Products filter dependency."""

    async def __call__(
        self,
        request: Request,
        filter_: BaseProductsFilterModel = Depends(),
        products_access_filter_validator: ProductsAccessFilterValidator = Depends(),
        parameter_service: ParameterService = Depends(),
    ) -> ProductsFilterModel:
        """Validates and formats products list filter.

        Args:
            request (Request): Current request object.
            filter_ (BaseProductsFilterModel): Base products filter.
            products_access_filter_validator (ProductsAccessFilterValidator): Products
            access filter validator.
            parameter_service (ParameterService): Parameter service.

        Returns:
            ProductsFilterModel: Products filter object.

        Raises:
            HTTPException: If product parameters filter is invalid.

        """

        await products_access_filter_validator.validate(available=filter_.available)

        fields: dict[str, Any] = {
            parameter["machine_name"]: (
                list[getattr(ProductParameterTypesEnum, parameter["type"]).value]  # type: ignore
                if parameter["type"] != ProductParameterTypesEnum.LIST.name
                else list[str],
                None,
            )
            for parameter in await parameter_service.get()
        }

        parameters_model = create_model(
            "ProductsParameters", **fields, __base__=BaseModel
        )

        try:
            query_params = parameters_model(
                **{
                    query_param: request.query_params.getlist(query_param)
                    for query_param in request.query_params.keys()
                }
            ).model_dump(exclude_unset=True)

        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error.errors(),
            )

        return ProductsFilterModel(
            category_id=filter_.category_id,
            available=filter_.available,
            parameters=query_params,
        )
