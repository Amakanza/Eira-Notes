from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from the class name."""
        return cls.__name__.lower()

    id: Any


# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)

# Generic types for Pydantic schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseSchema(BaseModel):
    """Base Pydantic model for all schemas."""
    model_config = ConfigDict(from_attributes=True)