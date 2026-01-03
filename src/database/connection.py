"""
Neo4j async connection management.
Handles driver lifecycle and connection pooling.
"""

import logging
from typing import Optional
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.core.config import neo4j

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Async Neo4j connection manager."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncGraphDatabase.driver] = None

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connection
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    def session(self):
        """Get a new async session from the driver."""
        if not self.driver:
            raise RuntimeError("Driver not initialized. Call connect() first.")
        return self.driver.session()


# Global connection instance
_connection: Optional[Neo4jConnection] = None


async def get_connection() -> Neo4jConnection:
    """Get or create the global Neo4j connection."""
    global _connection
    if _connection is None:
        _connection = Neo4jConnection(
            uri=neo4j.uri,
            user=neo4j.user,
            password=neo4j.password
        )
        await _connection.connect()
    return _connection


async def close_connection() -> None:
    """Close the global Neo4j connection."""
    global _connection
    if _connection:
        await _connection.close()
        _connection = None
