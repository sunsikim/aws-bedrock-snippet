import boto3
from typing import Optional, List
from bedrock_snippet.models.guardrail import *
from bedrock_snippet.models.request import (
    CreateGuardrailRequest,
    UpdateGuardrailRequest,
)


class GuardrailManagementService:

    def __init__(self, guardrail_name: str, session: boto3.Session):
        self._guardrail_name = guardrail_name
        self._session = session
        self._client = session.client("bedrock")

    def create_guardrail(
        self,
        description: str,
        blocked_input_message: str,
        blocked_output_message: str,
        restricted_words: List[str],
    ):
        assert (
            not self._is_guardrail_created()
        ), f"Guardrail with name '{self._guardrail_name}' already exists."
        words_config = GuardrailWordPolicyConfig(
            wordsConfig=[GuardrailWordConfig(text=word) for word in restricted_words]
        )
        request = CreateGuardrailRequest(
            name=self._guardrail_name,
            description=description,
            blockedInputMessaging=blocked_input_message,
            blockedOutputsMessaging=blocked_output_message,
            wordPolicyConfig=words_config,
        )
        self._client.create_guardrail(**request.model_dump(exclude_none=True))

    def create_guardrail_version(self, description: Optional[str] = None):
        if description is None:
            description = self.get_guardrail().get("description", None)
        self._client.create_guardrail_version(
            guardrailIdentifier=self.get_guardrail_id(),
            description=description,
        )

    def get_guardrail(self, version: Optional[int] = None):
        assert (
            self._is_guardrail_created()
        ), f"Prompt '{self._guardrail_name}' is not created"
        if version is None:
            return self._client.get_guardrail(
                guardrailIdentifier=self.get_guardrail_id()
            )
        else:
            assert version > 0, "Guardrail version must be greater than 0"
            return self._client.get_guardrail(
                guardrailIdentifier=self.get_guardrail_id(),
                guardrailVersion=str(version),
            )

    def get_guardrail_id(self) -> str:
        guardrails = self._client.list_guardrails().get("guardrails")
        test_guardrail = [
            g for g in guardrails if g.get("name") == self._guardrail_name
        ]
        assert (
            test_guardrail
        ), f"Guardrail with name '{self._guardrail_name}' doesn't exist"
        return test_guardrail[0].get("id")

    def list_available_guardrail_versions(self):
        result = []
        version = 0
        guardrail_info = self.get_guardrail()
        guardrail_arn = guardrail_info.get("guardrailArn")
        resource_info = self._client.list_tags_for_resource(resourceARN=guardrail_arn)
        result.append(
            {
                "version": version,
                "wordPolicy": resource_info.get("wordPolicy"),
                "tags": resource_info.get("tags"),
            }
        )
        while True:
            version += 1
            try:
                resource_info = self._client.list_tags_for_resource(
                    resourceARN=f"{guardrail_arn}:{version}"
                )
                result.append(
                    {
                        "version": version,
                        "wordPolicy": resource_info.get("wordPolicy"),
                        "tags": resource_info.get("tags"),
                    }
                )
            except self._client.exceptions.ResourceNotFoundException:
                return result

    def update_guardrail(
        self,
        description: Optional[str] = None,
        blocked_input_message: Optional[str] = None,
        blocked_output_message: Optional[str] = None,
        restricted_words: Optional[List[str]] = None,
    ):
        guardrail_info = self.get_guardrail()
        if restricted_words is not None:
            words_config = GuardrailWordPolicyConfig(
                wordsConfig=[
                    GuardrailWordConfig(text=word) for word in restricted_words
                ]
            )
        else:
            words_config = GuardrailWordPolicyConfig(
                wordsConfig=[
                    GuardrailWordConfig(text=word.get("text"))
                    for word in guardrail_info.get("wordPolicy").get("words")
                ]
            )
        request = UpdateGuardrailRequest(
            name=self._guardrail_name,
            description=(
                description
                if description is not None
                else guardrail_info.get("description")
            ),
            guardrailIdentifier=self.get_guardrail_id(),
            blockedInputMessaging=(
                blocked_input_message
                if blocked_input_message is not None
                else guardrail_info.get("blockedInputMessaging")
            ),
            blockedOutputsMessaging=(
                blocked_output_message
                if blocked_output_message is not None
                else guardrail_info.get("blockedOutputsMessaging")
            ),
            wordPolicyConfig=words_config,
        )
        self._client.update_guardrail(**request.model_dump(exclude_none=True))

    def delete_guardrail(self):
        self._client.delete_guardrail(guardrailIdentifier=self.get_guardrail_id())

    def _is_guardrail_created(self) -> bool:
        guardrails = self._client.list_guardrails().get("guardrails")
        for guardrail in guardrails:
            if guardrail.get("name") == self._guardrail_name:
                return True
        return False
