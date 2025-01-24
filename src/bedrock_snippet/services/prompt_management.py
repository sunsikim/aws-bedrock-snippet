import boto3
import pandas as pd
from typing import Optional
from bedrock_snippet.models.prompt import *


class PromptManagementService:
    """
    Method for CRUD operations on prompt object with certain name
    """

    def __init__(self, name: str, session: boto3.Session):
        self._prompt_name = name
        self._session = session
        self._default_variant = f"{name}-variant"
        self._client = session.client("bedrock-agent")

    def create_prompt(
        self,
        model_id: str,
        description: str,
        system_prompt: str,
        user_prompt: str,
        top_p: float = 1.0,
        max_tokens: int = 2000,
        temperature: float = 1.0,
        top_k: int = 15,
        input_variables: Optional[list[dict[str, str]]] = None,
        tags: Optional[dict[str, str]] = None,
        stop_sequences: Optional[list[str]] = None,
    ):
        assert not self._is_prompt_created(), f"Prompt '{self._prompt_name}' exists."
        prompt_config = self._create_prompt_template_config(
            user_prompt, system_prompt, input_variables
        )
        inference_config = self._create_prompt_inference_config(
            max_tokens, temperature, top_p, stop_sequences
        )
        variant = PromptVariant(
            name=self._default_variant,
            templateConfiguration=prompt_config,
            modelId=model_id,
            additionalModelRequestFields={"top_k": top_k},
            inferenceConfiguration=inference_config,
        )
        request = CreatePromptRequest(
            name=self._prompt_name,
            description=description,
            tags=tags,
            variants=[variant],
            defaultVariant=self._default_variant,
        )
        self._client.create_prompt(**request.model_dump(exclude_none=True))

    def create_prompt_version(
        self, description: Optional[str] = None, tags: Optional[dict[str, str]] = None
    ):
        prompt_info = self.get_prompt()
        request = CreatePromptVersionRequest(
            promptIdentifier=prompt_info.get("id"), description=description, tags=tags
        )
        self._client.create_prompt_version(**request.model_dump(exclude_none=True))

    def get_prompt(self, version: Optional[int] = None):
        assert self._is_prompt_created(), f"Prompt '{self._prompt_name}' is not created"
        if version is None:
            return self._client.get_prompt(promptIdentifier=self._get_prompt_id())
        else:
            assert version > 0, "Prompt version must be greater than 0"
            return self._client.get_prompt(
                promptIdentifier=self._get_prompt_id(),
                promptVersion=str(version),
            )

    def list_available_prompt_versions(self):
        result = []
        version = 0
        prompt_info = self.get_prompt()
        prompt_arn = prompt_info.get("arn")
        resource_info = self._client.list_tags_for_resource(resourceArn=prompt_arn)
        result.append(
            {
                "version": version,
                "variant": prompt_info.get("variants")[0],
                "tags": resource_info.get("tags"),
            }
        )
        while True:
            version += 1
            try:
                prompt_info = self.get_prompt(version)
                resource_info = self._client.list_tags_for_resource(
                    resourceArn=f"{prompt_arn}:{version}"
                )
                result.append(
                    {
                        "version": version,
                        "variant": prompt_info.get("variants")[0],
                        "tags": resource_info.get("tags"),
                    }
                )
            except self._client.exceptions.ResourceNotFoundException:
                return result

    def list_available_foundation_models(self) -> pd.DataFrame:
        bedrock_client = self._session.client("bedrock")
        models = bedrock_client.list_foundation_models().get("modelSummaries")
        models = pd.DataFrame(models)
        return models[["modelId", "inputModalities", "outputModalities"]]

    def update_prompt(
        self,
        model_id: Optional[str] = None,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        input_variables: Optional[list[dict[str, str]]] = None,
        stop_sequences: Optional[list[str]] = None,
    ):
        prompt_info = self.get_prompt()
        existing_variant = PromptVariant(**prompt_info.get("variants")[0])
        prompt_config = self._update_prompt_template_config(
            prompt_config=existing_variant.templateConfiguration,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            input_variables=input_variables,
        )
        inference_config = self._update_prompt_inference_config(
            inference_config=existing_variant.inferenceConfiguration,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_sequences=stop_sequences,
        )
        variant = PromptVariant(
            name=self._default_variant,
            templateConfiguration=prompt_config,
            modelId=model_id if model_id is not None else existing_variant.modelId,
            additionalModelRequestFields={
                "top_k": (
                    top_k
                    if top_k is not None
                    else existing_variant.additionalModelRequestFields.get("top_k")
                )
            },
            inferenceConfiguration=inference_config,
        )
        request = UpdatePromptRequest(
            promptIdentifier=self._get_prompt_id(),
            name=self._prompt_name,
            description=(
                description
                if description is not None
                else prompt_info.get("description")
            ),
            variants=[variant],
            defaultVariant=self._default_variant,
        )
        self._client.update_prompt(**request.model_dump(exclude_none=True))

    def delete_prompt(self):
        self._client.delete_prompt(promptIdentifier=self._get_prompt_id())

    def _create_prompt_template_config(
        self,
        user_prompt: str,
        system_prompt: str,
        input_variables: Optional[list[str]] = None,
    ) -> PromptTemplateConfiguration:
        user_message = Message(role="user", content=[ContentBlock(text=user_prompt)])
        chat_prompt_template_config = ChatPromptTemplateConfiguration(
            messages=[user_message],
            system=[SystemContentBlock(text=system_prompt)],
            inputVariables=[] if input_variables is None else input_variables,
        )
        return PromptTemplateConfiguration(chat=chat_prompt_template_config)

    def _create_prompt_inference_config(
        self,
        max_tokens: int,
        temperature: float,
        top_p: float,
        stop_sequences: Optional[list[str]] = None,
    ) -> PromptInferenceConfiguration:
        inference_config = PromptModelInferenceConfiguration(
            maxTokens=max_tokens,
            temperature=temperature,
            topP=top_p,
            stopSequences=[] if stop_sequences is None else stop_sequences,
        )
        return PromptInferenceConfiguration(text=inference_config)

    def _update_prompt_template_config(
        self,
        prompt_config: PromptTemplateConfiguration,
        user_prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        input_variables: Optional[list[str]] = None,
    ) -> PromptTemplateConfiguration:
        user_message = (
            prompt_config.chat.messages[0]
            if user_prompt is None
            else Message(role="user", content=[ContentBlock(text=user_prompt)])
        )
        system_message = (
            prompt_config.chat.system[0]
            if system_prompt is None
            else SystemContentBlock(text=system_prompt)
        )
        chat_prompt_template_config = ChatPromptTemplateConfiguration(
            messages=[user_message],
            system=[system_message],
            inputVariables=(
                prompt_config.chat.inputVariables
                if input_variables is None
                else input_variables
            ),
        )
        return PromptTemplateConfiguration(chat=chat_prompt_template_config)

    def _update_prompt_inference_config(
        self,
        inference_config: PromptInferenceConfiguration,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[list[str]] = None,
    ) -> PromptInferenceConfiguration:
        inference_config = PromptModelInferenceConfiguration(
            maxTokens=(
                inference_config.text.maxTokens if max_tokens is None else max_tokens
            ),
            temperature=(
                inference_config.text.temperature
                if temperature is None
                else temperature
            ),
            topP=(inference_config.text.topP if top_p is None else top_p),
            stopSequences=(
                inference_config.text.stopSequences
                if stop_sequences is None
                else stop_sequences
            ),
        )
        return PromptInferenceConfiguration(text=inference_config)

    def _is_prompt_created(self) -> bool:
        prompts = self._client.list_prompts().get("promptSummaries")
        for prompt in prompts:
            if prompt.get("name") == self._prompt_name:
                return True
        return False

    def _get_prompt_id(self) -> str:
        prompts = self._client.list_prompts().get("promptSummaries")
        test_prompt = [p for p in prompts if p.get("name") == self._prompt_name]
        assert test_prompt, f"Prompt with name '{self._prompt_name}' doesn't exist"
        return test_prompt[0].get("id")
