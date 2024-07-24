# Shibumi Store

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-312/)
[![FastAPI Version](https://img.shields.io/badge/fastapi-0.111.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB Version](https://img.shields.io/badge/mongodb-7.0-green.svg)](https://www.mongodb.com/)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=valentyn-malenchak_shibumi-store&metric=coverage)](https://sonarcloud.io/summary/new_code?id=valentyn-malenchak_shibumi-store)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=valentyn-malenchak_shibumi-store&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=valentyn-malenchak_shibumi-store)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Welcome to the "Shibumi Store" Project - a high-performance backend for e-commerce platform. Code name is SHIBU.

## What is Shibumi?
Shibumi (渋み) (noun) or Shibui (渋い) (adjective) are Japanese words which refer to a particular aesthetic or beauty of simple, subtle, and unobtrusive beauty. Shibumi includes the following essential qualities:

- Shibui objects appear to be simple overall, but they include subtle details, such as textures, that balance simplicity with complexity. 
- This balance of simplicity and complexity ensures that one does not tire of a shibumi object but constantly finds new meanings and enriched beauty that cause its aesthetic value to grow over the years.
- Shibui objects are not necessarily imperfect or asymmetrical, though they can include these qualities.
- Shibumi walks a fine line between contrasting aesthetic concepts such as elegant and rough or spontaneous and restrained.

## Technology Stack

- **FastAPI**: Utilizing the FastAPI web framework for high-speed asynchronous API development.
- **MongoDB with Motor**: Efficient and asynchronous data storage.
- **Authentication and Security**: Secure user authentication with pyjwt and password hashing using Argon2.
- **Data Validation and Serialization**: Robust data validation and serialization using Pydantic.
- **Dependency Injection**: Improved code organization and maintainability with the Injector library.
- **Date and Time Handling**: Efficient date and time handling using the Arrow library.
- **Testing**: Comprehensive testing suite with Pytest and Pytest-asyncio for reliable code testing.
- **Database Migrations**: Smooth management of database schema changes using MongoDB Migrations.

## Code Cleanliness
Maintaining clean and readable code is essential. The project uses Ruff as a code formatter and linter, MyPy for static type checking, and SonarQube for additional code quality analysis.

## Project Structure

The project is organized with the following directory structure:

```plaintext
.
├── .github/                                   # GitHub-related configurations
│   └── workflows/                             # GitHub Actions workflows
│       └── ci.yml                             # Continuous Integration workflow
├── app/                                       # Main Application code
│   ├── api/
│   │   ├── v1/                                # API version 1
│   │   │   ├── auth                           # Authentication and Authorization interactions used in services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                    # Authentication and Authorization handlers
│   │   │   │   ├── jwt.py                     # JWT handler
│   │   │   │   └── password.py                # Password handler
│   │   │   ├── dependencies                   # Domain dependencies for determination and validation (using validators) request entities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── models                         # Pydantic models for API and entities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── repositories                   # Database entities interactions used in services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── routers                        # API route handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── health.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── validators                     # Validators for request data
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── services                       # API business logic which uses interactions from repositories and auth   
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   └── ...
│   │   │   ├── __init__.py                    # Collects API routes
│   │   │   └── constants.py                   # Constants for API v1
│   │   └── __init__.py
│   ├── loaders                                # Data loading modules from different sources (environment, JSON files, etc.)
│   │   └── __init__.py
│   ├── services                               # External services used by application
│   │   ├── mongo                              # MongoDB service
│   │   │   ├── __init__.py
│   │   │   ├── client.py                      # MongoDB client handler
│   │   │   ├── constants.py                   # MongoDB constants
│   │   │   ├── service.py                     # MongoDB service (facade used in entity repositories)
│   │   │   └── transaction_manager.py         # MongoDB transaction manager
│   │   ├── ...
│   │   ├── __init__.py                        # Collects all services
│   │   └── base.py                            # Base service abstract class
│   ├── tests/                                 # Unit tests and fixtures
│   │   ├── api
│   │   │   ├── v1                             # Unit tests for API routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_auth.py
│   │   │   │   ├── test_health.py
│   │   │   │   ├── test_user.py
│   │   │   │   └── ...
│   │   │   └── __init__.py
│   │   ├── fixtures                           # Handler JSON file fixtures
│   │   │   ├── json                           # JSON files with entities data
│   │   │   │   ├── users.json
│   │   │   │   └── ...
│   │   │   ├── __init__.py
│   │   │   └── manager.py                     # JSON files fixture manager
│   │   ├── __init__.py
│   │   └── constants.py                       # Constants for unit tests
│   ├── utils/                                 # Utility modules
│   │   ├── __init__.py
│   │   ├── json.py                            # Custom JSON decoder
│   │   └── token.py                           # Verification token component
│   ├── __init__.py
│   ├── app.py                                 # Configures and runs FastAPI application
│   ├── constants.py                           # Application level constants
│   ├── exceptions.py                          # Custom application exceptions
│   └── settings.py                            # Defines application settings
├── migrations/                                # MongoDB migration scripts
│   ├── 20231231132337_create_users_username_index.py
│   └── ...
├── .coveragerc                                # Configuration file for coverage reports
├── .gitignore                                 # Gitignore file to specify ignored files and directories
├── LICENSE                                    # License information for the project
├── mypy.ini                                   # Configuration file for MyPy static type checker
├── poetry.lock                                # Poetry lock file specifying exact package versions
├── pyproject.toml                             # Poetry configuration file
├── README.md                                  # Project README file
├── ruff.toml                                  # Configuration file for Ruff code formatter and linter
├── sonar-project.properties                   # Configuration file for SonarQube code quality analysis
└── tasks.py                                   # Application cli
```

## Getting Started

### 1. Clone the repository:
```bash
git clone https://github.com/valentyn-malenchak/shibumi-store.git
```

### 2. Add environment variables in [docker-compose](docker-compose.yml) marked with appropriate comments.

### 3. Build the application container:
```bash
docker build -t shibumi-store:latest .
```
or
```bash
invoke build
```

### 4. Run the application:
```bash
docker-compose up -d
```
or
```bash
invoke compose
```

## Check out useful [cli commands](tasks.py)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
