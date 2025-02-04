from pydantic import BaseModel, Field
from typing import Optional, Annotated, List
from bedrock_snippet.models.guardrail import GuardrailWordPolicyConfig, Tag


class CreateGuardrailRequest(BaseModel):
    name: str = Field(..., description="The name of the guardrail.")
    blockedInputMessaging: Annotated[str, Field(min_length=1, max_length=500)] = Field(
        ..., description="The message to return when the guardrail blocks a prompt."
    )
    blockedOutputsMessaging: Annotated[str, Field(min_length=1, max_length=500)] = (
        Field(
            ...,
            description="The message to return when the guardrail blocks a model response.",
        )
    )
    description: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=200,
                description="A description of the guardrail.",
            ),
        ]
    ] = None
    tags: Optional[List[Tag]] = Field(
        default=None, description="A list of tags to associate with the guardrail."
    )
    wordPolicyConfig: Optional[GuardrailWordPolicyConfig] = Field(
        default=None, description="Configuration for word filters."
    )


class UpdateGuardrailRequest(BaseModel):
    name: str = Field(..., description="The name of the guardrail.")
    guardrailIdentifier: str = Field(
        ...,
        min_length=0,
        max_length=2048,
        pattern=r"^(([a-z0-9]+)|(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:guardrail/[a-z0-9]+))$",
        description="The guardrail identifier.",
    )
    blockedInputMessaging: Annotated[str, Field(min_length=1, max_length=500)] = Field(
        ..., description="The message to return when the guardrail blocks a prompt."
    )
    blockedOutputsMessaging: Annotated[str, Field(min_length=1, max_length=500)] = (
        Field(
            ...,
            description="The message to return when the guardrail blocks a model response.",
        )
    )
    description: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=200,
                description="A description of the guardrail.",
            ),
        ]
    ] = None
    tags: Optional[List[Tag]] = Field(
        default=None, description="A list of tags to associate with the guardrail."
    )
    wordPolicyConfig: Optional[GuardrailWordPolicyConfig] = Field(
        default=None, description="Configuration for word filters."
    )
