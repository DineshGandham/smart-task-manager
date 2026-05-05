# -----------------------------------------------------------
# BASE REPOSITORY (ABSTRACT + GENERIC)
# -----------------------------------------------------------
# Purpose:
# - Define a common contract (CRUD operations) for all repositories
# - Ensure consistency across different data sources (JSON, DB, etc.)
# - Use Generics to make the repository reusable for any entity (Task, Note, etc.)
# -----------------------------------------------------------

from abc import ABC, abstractmethod  # Used to create abstract base classes
from typing import Generic, Optional, TypeVar  # Generic typing support

# -----------------------------------------------------------
# TYPE VARIABLE (GENERIC PLACEHOLDER)
# -----------------------------------------------------------
# T represents the entity type (e.g., Task, Note, User)
# This allows the repository to be reusable for different models
# -----------------------------------------------------------
T = TypeVar("T")


# -----------------------------------------------------------
# ABSTRACT BASE REPOSITORY
# -----------------------------------------------------------
# - Cannot be instantiated directly
# - Enforces implementation of all abstract methods in child classes
# - Generic[T] makes it type-safe for different entities
# -----------------------------------------------------------
class BaseRepository(ABC, Generic[T]):

    # -------------------------------------------------------
    # GET ALL RECORDS
    # -------------------------------------------------------
    # Returns a list of all entities of type T
    # Example: list[Task]
    # -------------------------------------------------------
    @abstractmethod
    def get_all(self) -> list[T]:
        ...

    # -------------------------------------------------------
    # GET BY ID
    # -------------------------------------------------------
    # Returns a single entity if found, else None
    # Optional[T] means it can return T or None
    # -------------------------------------------------------
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        ...

    # -------------------------------------------------------
    # CREATE RECORD
    # -------------------------------------------------------
    # Accepts raw data (dict) and returns created entity
    # -------------------------------------------------------
    @abstractmethod
    def create(self, data: dict) -> T:
        ...

    # -------------------------------------------------------
    # UPDATE RECORD
    # -------------------------------------------------------
    # Updates entity by ID
    # Returns updated entity or None if not found
    # -------------------------------------------------------
    @abstractmethod
    def update(self, id: str, data: dict) -> Optional[T]:
        ...

    # -------------------------------------------------------
    # DELETE RECORD
    # -------------------------------------------------------
    # Deletes entity by ID
    # Returns True if successful, False otherwise
    # -------------------------------------------------------
    @abstractmethod
    def delete(self, id: str) -> bool:
        ...