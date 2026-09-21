# backend/app/models/base.py
from pydantic import BaseModel, Field, ConfigDict, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any, Annotated
from bson import ObjectId


class _ObjectIdPydanticAnnotation:
    """
    Custom Pydantic annotation for MongoDB ObjectId.
    Provides full Pydantic v2 compatibility with proper schema generation.
    """
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Define how to validate and serialize ObjectId.
        """
        def validate_object_id(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
            raise ValueError(f'Invalid ObjectId: {value}')

        return core_schema.no_info_plain_validator_function(
            validate_object_id,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """
        Define the JSON schema for ObjectId (shows as string in OpenAPI docs).
        """
        return {'type': 'string'}


# This is the type alias to use throughout the codebase
PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]


class MongoBaseModel(BaseModel):
    """
    Base model for MongoDB documents with Pydantic v2 compatibility.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")