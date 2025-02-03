from typing import List, Optional, Self
from pydantic import BaseModel, Field, field_validator, model_validator


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


class AnthropicImageContent(BaseModel):
    type: str = "base64"
    media_type: str = Field(..., pattern="^image/(jpg|png|webp|gif)$")
    data: str = Field(..., description="The base64 encoded image.")


class AnthropicContentBlock(BaseModel):
    type: str = Field(..., pattern="^(image|text)$", description="The type of content.")
    text: Optional[str] = Field(None, description="Text content of a prompt")
    source: Optional[AnthropicImageContent] = Field(
        None, description="information on base64 encoded image which is utf8 decoded"
    )

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        if self.type == "text" and (self.source is not None or self.text is None):
            raise ValueError(
                "Content type is set to 'text' but source field is not None or text field is None"
            )
        elif self.type == "image" and (self.source is None or self.text is not None):
            raise ValueError(
                "Content type is set to 'image' but source field is None or text field is not None"
            )
        return self


class AnthropicMessage(Message):
    content: List[AnthropicContentBlock] = Field(
        ..., description="The content in the message."
    )


class PromptInputVariable(BaseModel):
    name: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="The name of the variable.",
    )


class SystemContentBlock(BaseModel):
    text: str = Field(..., description="The text in the system prompt.")
