"""Routers packages.

Router rules:

- Recommended name formats: "{operation}_{entity}".
- Should use dependencies (to define and validate HTTP request data) and entity services
(to execute actions).
- Parameters that don't require validation could be passed directly to route.
- Should have defined response model and status code.
- Each route should have unique authorization permission.

"""
