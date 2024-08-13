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
    ProductAccessValidator,
    ProductAvailableFilterValidator,
    ProductByIdValidator,
    ProductParametersFilterValidator,
    ProductParametersValidator,
)
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class ProductByIdGetDependency(metaclass=SingletonMeta):
    """Product by identifier get dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        product_by_id_validator: ProductByIdValidator = Depends(),
    ) -> Product:
        """Validates product by its unique identifier.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            product_by_id_validator (ProductByIdValidator): Product by identifier
            validator.

        Returns:
            Product: Product object.

        """
        return await product_by_id_validator.validate(product_id=product_id)


class ProductByIdGetAccessDependency(metaclass=SingletonMeta):
    """Product by identifier get access dependency."""

    async def __call__(
        self,
        product: Product = Depends(ProductByIdGetDependency()),
        product_access_validator: ProductAccessValidator = Depends(),
    ) -> Product:
        """Validates access to specific product.

        Args:
            product (Product): Product object.
            product_access_validator (ProductAccessValidator): Product access validator.

        Returns:
            Product: Product object.

        """
        return await product_access_validator.validate(product=product)


class ProductsFilterDependency(metaclass=SingletonMeta):
    """Products filter dependency."""

    async def __call__(
        self,
        filter_: BaseProductFilter = Depends(),
        available_filter_validator: ProductAvailableFilterValidator = Depends(),
        parameters_filter_validator: ProductParametersFilterValidator = Depends(),
    ) -> ProductFilter:
        """Validates filter for product list.

        Args:
            filter_ (BaseProductFilter): Base product filter.
            available_filter_validator (ProductAvailableFilterValidator): Product
            filter validator.
            parameters_filter_validator (ProductParametersFilterValidator): Product
            parameters filter validator.

        Returns:
            ProductFilter: Product filter object.

        """

        await available_filter_validator.validate(available=filter_.available)

        query_params = await parameters_filter_validator.validate()

        return ProductFilter(
            category_id=filter_.category_id,
            available=filter_.available,
            ids=filter_.ids,
            parameters=query_params,
        )


class ProductDataDependency(metaclass=SingletonMeta):
    """Product data dependency."""

    async def __call__(
        self,
        product_data: ProductData,
        product_parameters_validator: ProductParametersValidator = Depends(),
    ) -> ProductData:
        """Validates product data.

        Args:
            product_data (ProductData): Product data.
            product_parameters_validator (ProductParametersValidator): Product
            parameters validator.

        Returns:
            ProductData: Product data.

        """

        await product_parameters_validator.validate(
            category_id=product_data.category_id,
            requested_parameters=product_data.parameters,
        )

        return product_data
