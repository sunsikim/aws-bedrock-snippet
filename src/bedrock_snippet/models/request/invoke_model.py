from typing import List, Annotated, Optional, Self
from pydantic import BaseModel, Field, model_validator
from bedrock_snippet.models.prompt.content import AnthropicMessage


class AnthropicModelRequestBody(BaseModel):
    system: Optional[str] = Field(
        default=None,
        description="The text in the system prompt.",
    )
    messages: List[AnthropicMessage] = (
        Field(..., description="Contains messages in the chat for the prompt."),
    )
    max_tokens: Annotated[
        int,
        Field(
            default=2000,
            ge=0,
            le=4096,
            description="The maximum number of tokens to return in the response.",
        ),
    ]
    stop_sequences: Annotated[
        List[str],
        Field(
            default_factory=list,
            min_length=0,
            max_length=4,
            description="A list of strings that define sequences after which the model will stop generating.",
        ),
    ]
    temperature: Annotated[
        float,
        Field(
            default=1.0,
            ge=0.0,
            le=1.0,
            description="Choose a lower value for more predictable outputs and a higher value for more random outputs.",
        ),
    ]
    top_p: Annotated[
        float,
        Field(
            default=1.0,
            ge=0.0,
            le=1.0,
            description="The percentage of most-likely candidates that the model considers for the next token.",
        ),
    ]
    top_k: Annotated[int, Field(ge=1, le=500)] = Field(
        default=100,
        description="Determines how many of the most likely tokens should be considered when generating a response.",
    )
    anthropic_version: str = Field(
        default="bedrock-2023-05-31", description="Anthropic version"
    )


class AnthropicModelRequest(BaseModel):
    modelId: Annotated[str, Field(min_length=1, max_length=2048)] = Field(
        ...,
        description=(
            "Specifies the model or throughput with which to run inference, or the prompt resource to use in inference."
            "Refer to: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html"
        ),
    )
    body: AnthropicModelRequestBody | str = Field(
        ..., description="Anthropic model request body"
    )
    accept: Optional[str] = Field(
        default="application/json",
        description="The desired MIME type of the inference body in the response.",
    )
    contentType: Optional[str] = Field(
        default="application/json",
        description="The MIME type of the input data in the request. You must specify application/json.",
    )
    guardrailIdentifier: Optional[
        Annotated[
            str,
            Field(
                max_length=2048,
                description="The unique identifier of the guardrail that you want to use. "
                "If you don't provide a value, no guardrail is applied to the invocation.",
                pattern=r"^(([a-z0-9]+)|(arn:aws(-[^:]+)?:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:guardrail/[a-z0-9]+))$",
            ),
        ]
    ] = None
    guardrailVersion: Optional[
        Annotated[
            str,
            Field(
                description="The version number for the guardrail. The value can also be DRAFT.",
                pattern=r"^(([1-9][0-9]{0,7})|(DRAFT))$",
            ),
        ]
    ] = None

    @model_validator(mode="after")
    def encode_body(self) -> Self:
        assert isinstance(
            self.body, AnthropicModelRequestBody
        ), "Pass raw AnthropicModelRequestBody instance without json encode"
        self.body = self.body.model_dump_json(exclude_none=True)
        return self
