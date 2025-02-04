from pydantic import BaseModel, Field
from typing import Optional, Annotated, List


class Tag(BaseModel):
    key: str = Field(
        ...,
        min_length=1,
        max_length=128,
        pattern=r"^[a-zA-Z0-9\s._:/=+@-]*$",
        description="Key for the tag",
    )
    value: str = Field(
        ...,
        min_length=0,
        max_length=256,
        pattern=r"^[a-zA-Z0-9\s._:/=+@-]*$",
        description="Value for the tag",
    )


class GuardrailWordConfig(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Text of the word configured for the guardrail to block.",
    )


class GuardrailWordPolicyConfig(BaseModel):
    wordsConfig: Optional[
        Annotated[
            List[GuardrailWordConfig],
            Field(
                min_items=1,
                max_items=10000,
                description="A list of words to configure for the guardrail.",
            ),
        ]
    ] = None
