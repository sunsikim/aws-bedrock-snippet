import json
import pathlib

import boto3
from base64 import b64encode
from typing import Dict, Optional
from bedrock_snippet.models.prompt import (
    PromptVariant,
    AnthropicMessage,
    AnthropicContentBlock,
    AnthropicImageContent,
)
from bedrock_snippet.models.request import (
    AnthropicModelRequestBody,
    AnthropicModelRequest,
)


class PromptInvocationService:

    def __init__(
        self, prompt_name: str, session: boto3.Session, version: Optional[int] = None
    ):
        self._prompt_name = prompt_name
        self._session = session
        self._default_variant = f"{prompt_name}-variant"
        self._bedrock_agent = session.client("bedrock-agent")
        self._bedrock_runtime = session.client("bedrock-runtime")
        variant = PromptVariant(**self.get_prompt(version).get("variants")[0])
        self._model_id = variant.modelId
        self._default_body = self._parse_variant(variant)

    def get_prompt(self, version: Optional[int] = None):
        assert self._is_prompt_created(), f"Prompt '{self._prompt_name}' is not created"
        if version is None:
            return self._bedrock_agent.get_prompt(
                promptIdentifier=self._get_prompt_id()
            )
        else:
            assert version > 0, "Prompt version must be greater than 0"
            return self._bedrock_agent.get_prompt(
                promptIdentifier=self._get_prompt_id(),
                promptVersion=str(version),
            )

    def invoke_multimodal(
        self,
        image_path: pathlib.Path,
        version: Optional[int] = None,
        return_result_only: bool = False,
        guardrail_identifier: Optional[str] = None,
        guardrail_version: Optional[int | str] = "DRAFT",
    ):
        source = AnthropicImageContent(
            media_type=f"image/{image_path.suffix[1:]}",
            data=b64encode(open(image_path, "rb").read()).decode("utf8"),
        )
        image_block = AnthropicContentBlock(type="image", source=source)
        if version is None:
            body = self._default_body.copy()
            model_id = self._model_id
        else:
            variant = PromptVariant(**self.get_prompt(version).get("variants")[0])
            body = self._parse_variant(variant)
            model_id = variant.modelId
        body.messages[0].content.append(image_block)
        if guardrail_identifier is not None:
            request = AnthropicModelRequest(
                modelId=model_id,
                body=body,
                guardrailIdentifier=guardrail_identifier,
                guardrailVersion=str(guardrail_version),
            )
        else:
            request = AnthropicModelRequest(modelId=model_id, body=body)
        response = self._bedrock_runtime.invoke_model(
            **request.model_dump(exclude_none=True)
        )
        result = json.loads(response.get("body").read())
        if return_result_only:
            return result.get("content")[0].get("text")
        else:
            return result

    def invoke_text(
        self, prompt_variables: Dict[str, str], version: Optional[int] = None
    ):
        pass

    def _parse_variant(self, variant: PromptVariant) -> AnthropicModelRequestBody:
        template_config = variant.templateConfiguration.chat
        inference_config = variant.inferenceConfiguration.text
        message = template_config.messages[0]
        message = AnthropicMessage(
            role=message.role,
            content=[AnthropicContentBlock(type="text", text=message.content[0].text)],
        )
        return AnthropicModelRequestBody(
            system=template_config.system[0].text,
            messages=[message],
            top_k=variant.additionalModelRequestFields.get("top_k"),
            max_tokens=inference_config.maxTokens,
            stop_sequences=inference_config.stopSequences,
            temperature=inference_config.temperature,
            top_p=inference_config.topP,
        )

    def _is_prompt_created(self) -> bool:
        prompts = self._bedrock_agent.list_prompts().get("promptSummaries")
        for prompt in prompts:
            if prompt.get("name") == self._prompt_name:
                return True
        return False

    def _get_prompt_id(self) -> str:
        prompts = self._bedrock_agent.list_prompts().get("promptSummaries")
        test_prompt = [p for p in prompts if p.get("name") == self._prompt_name]
        assert test_prompt, f"Prompt with name '{self._prompt_name}' doesn't exist"
        return test_prompt[0].get("id")
