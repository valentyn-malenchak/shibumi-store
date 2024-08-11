"""Contains product domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.product import (
    BaseProductFilter,
    Product,
    ProductData,
    ProductFilter,
)
from app.api.v1.validators.product import (
    ProductByIdStatusValidator,
    ProductFilterValidator,
    ProductParametersValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class ProductDataDependency:
    """Create/update product dependency."""

    async def __call__(
        self,
        product_data: ProductData,
        product_parameters_validator: ProductParametersValidator = Depends(),
    ) -> ProductData:
        """Validates if the product can be created/updated.

        Args:
            product_data (ProductData): New product data.
            product_parameters_validator (ProductParametersValidator): Product parameter
            validator.

        Returns:
            ProductData: Product data.

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
        """Validates if user can get a product from request.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            product_by_id_status_validator (ProductByIdStatusValidator): Product by
            identifier status validator.

        Returns:
            Product: Product object.

        """

        return await product_by_id_status_validator.validate(product_id=product_id)


class ProductFilterDependency:
    """Product filter dependency."""

    async def __call__(
        self,
        filter_: BaseProductFilter = Depends(),
        product_filter_validator: ProductFilterValidator = Depends(),
    ) -> ProductFilter:
        """Validates and formats products list filter.

        Args:
            filter_ (BaseProductFilter): Base products filter.
            product_filter_validator (ProductFilterValidator): Product filter
            validator.

        Returns:
            ProductFilter: Product filter object.

        """

        return await product_filter_validator.validate(
            category_id=filter_.category_id,
            available=filter_.available,
            ids=filter_.ids,
        )
