"""Contains product domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.product import CreateProductRequestModel, Product
from app.api.v1.validators.product import (
    ProductAccessValidator,
    ProductIdValidator,
    ProductParametersValidator,
)


class CreateProductDependency:
    """Create product dependency."""

    async def __call__(
        self,
        product_data: CreateProductRequestModel,
        product_parameters_validator: ProductParametersValidator = Depends(),
    ) -> CreateProductRequestModel:
        """Checks if the product can be created.

        Args:
            product_data (CreateProductRequestModel): New product data.
            product_parameters_validator (ProductParametersValidator): Product parameter
            validator.

        Returns:
            CreateProductRequestModel: Product data.

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
