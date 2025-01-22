from typing import Optional
from pydantic import BaseModel, Field


class PromptAgentResource(BaseModel):
    agentIdentifier: str = Field(
        ...,
        pattern=r"^arn:aws:bedrock:[a-z0-9-]{1,20}:[0-9]{12}:agent-alias/[0-9a-zA-Z]{10}/[0-9a-zA-Z]{10}$",
        description="The ARN of the agent with which to use the prompt.",
    )


class PromptGenAiResource(BaseModel):
    agent: Optional[PromptAgentResource] = Field(
        None,
        description="Specifies an Amazon Bedrock agent with which to use the prompt.",
    )
