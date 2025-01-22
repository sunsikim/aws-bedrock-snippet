import pytest
from pydantic import ValidationError
from bedrock_snippet.models.prompt import *


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
        _ = PromptModelInferenceConfiguration(
            temperature=1.5
        )
    with pytest.raises(ValidationError):
        _ = PromptModelInferenceConfiguration(
            temperature=-1.5
        )


def test_prompt_variant():
    content = ContentBlock(text="Hello World!")
    message = Message(role="user", content=[content])
    system = SystemContentBlock(text="You are a helpful assistant that greets user.")
    template_config = PromptTemplateConfiguration(
        chat=ChatPromptTemplateConfiguration(
            messages=[message],
            system=[system]
        )
    )
    inference_config = PromptInferenceConfiguration(text=PromptModelInferenceConfiguration())
    variant = PromptVariant(
        name="test-variant",
        templateConfiguration=template_config,
        inferenceConfiguration=inference_config,
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"
    )
