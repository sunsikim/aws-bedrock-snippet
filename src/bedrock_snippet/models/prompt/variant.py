from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bedrock_snippet.models.prompt.configuration import (
    PromptTemplateConfiguration,
    PromptInferenceConfiguration,
)


class PromptVariant(BaseModel):
    """
    Variant means A list of different configurations for the prompt. Among them, user can set default variant
    Since system prompt can only be used in chat prompt template, set template type to be CHAT in this example.
    (reference: https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-create.html)
    """

    name: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="Name must match the pattern ^([0-9a-zA-Z][_-]?){1,100}$.",
    )
    templateType: str = "CHAT"
    templateConfiguration: PromptTemplateConfiguration
    modelId: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        pattern=r"^(arn:aws(-[^:]{1,12})?:(bedrock|sagemaker):[a-z0-9-]{1,20}:([0-9]{12})?:([a-z-]+/)?)?([a-zA-Z0-9.-]{1,63}){0,2}(([:][a-z0-9-]{1,63}){0,2})?(/[a-z0-9]{1,12})?$",
        description="The ARN of the model or inference profile with which to run inference on the prompt.",
    )
    additionalModelRequestFields: Optional[Dict[str, Any]] = None
    inferenceConfiguration: Optional[PromptInferenceConfiguration] = None
