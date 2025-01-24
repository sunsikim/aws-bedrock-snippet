from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from bedrock_snippet.models.prompt.variant import PromptVariant


class CreatePromptRequest(BaseModel):
    name: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="A name for the prompt.",
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=200, description="A description for the prompt."
    )
    tags: Optional[Dict[str, str]] = Field(
        None, description="Tags to attach to the prompt."
    )
    variants: Optional[List[PromptVariant]] = Field(
        None,
        description="A list of objects, each containing details about a variant of the prompt.",
    )
    defaultVariant: Optional[str] = Field(
        None,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="The name of the default variant for the prompt."
        "This value must match the 'name' field in the relevant PromptVariant object.",
    )
    customerEncryptionKeyArn: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2048,
        pattern=r"^arn:aws(|-cn|-us-gov):kms:[a-zA-Z0-9-]*:[0-9]{12}:key/[a-zA-Z0-9-]{36}$",
        description="The Amazon Resource Name (ARN) of the KMS key to encrypt the prompt.",
    )


class CreatePromptVersionRequest(BaseModel):
    promptIdentifier: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z]{10})|(arn:aws:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:prompt/[0-9a-zA-Z]{10})(?::[0-9]{1,5})?$",
        description="The unique identifier of the prompt that you want to update.",
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=200, description="A description for the prompt."
    )
    tags: Optional[Dict[str, str]] = Field(
        None, description="Tags to attach to the prompt."
    )


class UpdatePromptRequest(BaseModel):
    promptIdentifier: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z]{10})|(arn:aws:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:prompt/[0-9a-zA-Z]{10})(?::[0-9]{1,5})?$",
        description="The unique identifier of the prompt that you want to update.",
    )
    name: str = Field(
        ...,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="A name for the prompt.",
    )
    description: Optional[str] = Field(
        None, min_length=1, max_length=200, description="A description for the prompt."
    )
    variants: Optional[List[PromptVariant]] = Field(
        None,
        description="A list of objects, each containing details about a variant of the prompt.",
    )
    defaultVariant: Optional[str] = Field(
        None,
        pattern=r"^([0-9a-zA-Z][_-]?){1,100}$",
        description="The name of the default variant for the prompt. "
        "This value must match the 'name' field in the relevant PromptVariant object.",
    )
    customerEncryptionKeyArn: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2048,
        pattern=r"^arn:aws(|-cn|-us-gov):kms:[a-zA-Z0-9-]*:[0-9]{12}:key/[a-zA-Z0-9-]{36}$",
        description="The Amazon Resource Name (ARN) of the KMS key to encrypt the prompt.",
    )
