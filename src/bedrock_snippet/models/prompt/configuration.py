from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from bedrock_snippet.models.prompt.content import (
    Message,
    PromptInputVariable,
    SystemContentBlock,
)


class ChatPromptTemplateConfiguration(BaseModel):
    messages: Annotated[
        List[Message],
        Field(description="Contains messages in the chat for the prompt."),
    ]
    system: Optional[
        Annotated[
            List[SystemContentBlock],
            Field(
                description="Contains system prompts to provide context to the model or to describe its behavior."
            ),
        ]
    ] = None
    inputVariables: Optional[
        Annotated[
            List[PromptInputVariable],
            Field(
                min_length=0,
                max_length=5,
                description="An array of the variables in the prompt template.",
            ),
        ]
    ] = []


class PromptTemplateConfiguration(BaseModel):
    chat: ChatPromptTemplateConfiguration = Field(
        ...,
        description="Contains configurations to use the prompt in a conversational format",
    )


class PromptModelInferenceConfiguration(BaseModel):
    maxTokens: Annotated[int, Field(ge=0, le=4096)] = Field(
        2000, description="The maximum number of tokens to return in the response."
    )
    stopSequences: Annotated[List[str], Field(min_length=0, max_length=4)] = Field(
        [],
        description="A list of strings that define sequences after which the model will stop generating.",
    )
    temperature: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        1.0,
        description="Choose a lower value for more predictable outputs and a higher value for more surprising outputs.",
    )
    topP: Optional[Annotated[float, Field(ge=0.0, le=1.0)]] = Field(
        1.0,
        description="The percentage of most-likely candidates that the model considers for the next token.",
    )


class PromptInferenceConfiguration(BaseModel):
    text: PromptModelInferenceConfiguration = Field(
        ..., description="Contains inference configurations for a text prompt."
    )
