"""Contains product domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.product import (
    BaseProductsFilterModel,
    Product,
    ProductRequestModel,
    ProductsFilterModel,
)
from app.api.v1.validators.product import (
    ProductByIdStatusValidator,
    ProductParametersValidator,
    ProductsFilterValidator,
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


class ProductByIdStatusDependency:
    """Product by identifier status dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        product_by_id_status_validator: ProductByIdStatusValidator = Depends(),
    ) -> Product:
        """Checks if user can get a product from request.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            product_by_id_status_validator (ProductByIdStatusValidator): Product by
            identifier status validator.

        Returns:
            Product: Product object.

        """

        return await product_by_id_status_validator.validate(product_id=product_id)


class ProductsFilterDependency:
    """Products filter dependency."""

    async def __call__(
        self,
        filter_: BaseProductsFilterModel = Depends(),
        products_filter_validator: ProductsFilterValidator = Depends(),
    ) -> ProductsFilterModel:
        """Validates and formats products list filter.

        Args:
            filter_ (BaseProductsFilterModel): Base products filter.
            products_filter_validator (ProductsFilterValidator): Products filter
            validator.

        Returns:
            ProductsFilterModel: Products filter object.

        """

        return await products_filter_validator.validate(
            category_id=filter_.category_id, available=filter_.available
        )
