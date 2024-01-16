"""Module that collects all services."""

from app.services.mongo.client import MongoDBClient
from app.services.mongo.service import MongoDBService
from app.services.redis.client import RedisClient
from app.services.redis.service import RedisService
from app.services.send_grid.client import SendGridClient

SERVICES = [MongoDBService, RedisService]

SERVICE_CLIENTS = [RedisClient, MongoDBClient, SendGridClient]
