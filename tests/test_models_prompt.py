import pytest
import boto3
from dotenv import dotenv_values
from pydantic import ValidationError
from bedrock_snippet.models.prompt import *

_session = boto3.Session(
    aws_access_key_id=dotenv_values().get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=dotenv_values().get("AWS_SECRET_ACCESS_KEY"),
)
_bedrock_agent = _session.client("bedrock-agent")
_prompt_name = "dummy-prompt"


def test_prompt_message():
    content = ContentBlock(text="Hello World!")

    # check if ValueError is raised if invalid input is passed to Message
    with pytest.raises(ValueError):
        _ = Message(role="client", content=content)

    # check if valid role input is enforced to lowercase
    message = Message(role="USER", content=[content])
    assert message.role == "user"


def test_prompt_template_config():
    content = ContentBlock(text="Hello World!")
    message = Message(role="user", content=[content])
    system = SystemContentBlock(text="You are a helpful assistant that greets user.")
    variable = PromptInputVariable(name="dummy")

    # check if ValidationError is raised when message is not wrapped with list
    with pytest.raises(ValidationError):
        _ = ChatPromptTemplateConfiguration(
            messages=message,
            system=[system],
            inputVariables=[variable],
        )
    with pytest.raises(ValidationError):
        _ = ChatPromptTemplateConfiguration(
            messages=[message],
            system=system,
            inputVariables=[variable],
        )
    with pytest.raises(ValidationError):
        _ = ChatPromptTemplateConfiguration(
            messages=[message],
            system=[system],
            inputVariables=variable,
        )


def test_prompt_model_inference_config():
    default = PromptModelInferenceConfiguration()
    # check if stopSequences field is empty list by default
    assert isinstance(default.stopSequences, list) and len(default.stopSequences) == 0

    # check if ValidationError is raised when temperature value is out of range
    with pytest.raises(ValidationError):
        _ = PromptModelInferenceConfiguration(temperature=1.5)
    with pytest.raises(ValidationError):
        _ = PromptModelInferenceConfiguration(temperature=-1.5)


def test_create_prompt_request():
    variant = _define_dummy_variant(name="test-variant")
    create_prompt_request = CreatePromptRequest(
        name=_prompt_name,
        description="dummy description",
        variants=[variant],
        defaultVariant="test-variant",
    ).model_dump(exclude_none=True)
    response = _bedrock_agent.create_prompt(**create_prompt_request)
    status = response.get("ResponseMetadata").get("HTTPStatusCode")
    assert status == 201


def test_update_prompt_request():
    prompts = _bedrock_agent.list_prompts().get("promptSummaries")
    test_prompt = [p for p in prompts if p.get("name") == _prompt_name][0]
    prompt_id = test_prompt.get("id")
    variant = _define_dummy_variant(
        name="test-variant",
        message_text="Hello Bedrock World!",
        system_text="You are a helpful assistant that greets Bedrock user.",
    )
    update_prompt_request = UpdatePromptRequest(
        promptIdentifier=prompt_id,
        name=_prompt_name,
        description="another dummy description",
        variants=[variant],
    ).model_dump(exclude_none=True)
    response = _bedrock_agent.update_prompt(**update_prompt_request)
    status = response.get("ResponseMetadata").get("HTTPStatusCode")
    variant = PromptVariant(**response.get("variants")[0])
    message = variant.templateConfiguration.chat.messages[0]
    assert status == 200 and message.content[0].text == "Hello Bedrock World!"
    _bedrock_agent.delete_prompt(promptIdentifier=prompt_id)  # test resource clean-up


def _define_dummy_variant(
    name: str,
    message_text: str = "Hello World!",
    system_text: str = "You are a helpful assistant that greets user.",
) -> PromptVariant:
    content = ContentBlock(text=message_text)
    message = Message(role="user", content=[content])
    system = SystemContentBlock(text=system_text)
    template_config = PromptTemplateConfiguration(
        chat=ChatPromptTemplateConfiguration(messages=[message], system=[system])
    )
    inference_config = PromptInferenceConfiguration(
        text=PromptModelInferenceConfiguration()
    )
    variant = PromptVariant(
        name=name,
        templateConfiguration=template_config,
        inferenceConfiguration=inference_config,
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
    )
    return variant
