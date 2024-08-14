"""Dependencies package.

Dependency rules:

- Defines and validates (using validators) HTTP request data.
- Recommended name formats: "{Entity}{Operation}Dependency" or
"{RelatedEntity}{Operation}{Entity}Dependency".
- Should use validators and other dependencies.
- Can't use entity services.
- Should be reusable as much as possible.
- Should use 'SingletonMeta' metaclass to make FastAPI Depends() cache works.

"""
