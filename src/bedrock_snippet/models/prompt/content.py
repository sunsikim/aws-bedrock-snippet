from typing import List
from pydantic import BaseModel, Field, field_validator


class ContentBlock(BaseModel):
    text: str = Field(..., description="The text in the message.")


class Message(BaseModel):
    role: str = Field(
        ..., pattern=r"^(user|assistant)$", description="The message's role."
    )
    content: List[ContentBlock] = Field(..., description="The content in the message.")

    @field_validator("role", mode="before")
    @classmethod
    def enforce_lower(cls, value: str) -> str:
        role = value.lower()
        if role not in ["user", "assistant"]:
            raise ValueError("Value of role must be one of ('user', 'assistant').")
        else:
            return role


class PromptInputVariable(BaseModel):
    name: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="The name of the variable.",
    )


class SystemContentBlock(BaseModel):
    text: str = Field(..., description="The text in the system prompt.")
