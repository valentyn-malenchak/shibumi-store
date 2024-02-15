"""Contains product domain dependencies."""

from fastapi import Depends

from app.api.v1.models.product import CreateProductRequestModel
from app.api.v1.validators.product import ProductParametersValidator


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
