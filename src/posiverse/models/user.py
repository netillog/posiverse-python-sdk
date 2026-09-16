"""User record and mutable UserPut schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class User(PosiverseModel):
    """A data record class that contains data for user"""

    id: Optional[str] = Field(None, description="UUID of user")
    name: Optional[str] = Field(None, description="Short name for user")
    description: Optional[str] = Field(None, description="Area to keep notes on user")
    state: Optional[str] = Field(
        None, description='current state one of ("active", "disabled", "deleted")'
    )
    stateStartDate: Optional[int] = Field(
        None,
        description="The date the user entered its current state, in UTC millis from 1970-01-01",
    )
    language_id: Optional[str] = Field(
        None,
        description='Current language assigned to user, one of ("en", "es") where en = English and es = Spanish',
    )
    units: Optional[str] = Field(
        None, description='Units to display measurement, one of "us-std", "uk-imp", "metric"'
    )
    lastActivityDate: Optional[int] = Field(
        None,
        description="The last time the user interacted with the system, in UTC millis from 1970-01-01",
    )
    modifiedDate: Optional[int] = Field(
        None, description="The last time the user was modified, in UTC millis from 1970-01-01"
    )
    createdDate: Optional[int] = Field(
        None, description="The date user was created, in UTC millis from 1970-01-01"
    )


class UserPut(PosiverseModel):
    """The data record containing fields that can be modified on a group"""

    name: Optional[str] = Field(None, description="Short name for user")
    description: Optional[str] = Field(None, description="Area to keep notes on user")
