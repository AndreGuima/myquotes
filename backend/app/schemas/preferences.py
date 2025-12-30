from typing import Any, Dict

from pydantic import BaseModel


class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]


class PreferencesResponse(BaseModel):
    category: str
    preferences: Dict[str, Any]
