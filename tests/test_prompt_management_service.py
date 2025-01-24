import boto3
from dotenv import dotenv_values
from bedrock_snippet.services.prompt_management import PromptManagementService

session = boto3.Session(
    aws_access_key_id=dotenv_values().get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=dotenv_values().get("AWS_SECRET_ACCESS_KEY"),
)
service = PromptManagementService("test-prompt", session)


def test_create_prompt():
    service.create_prompt(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        description="dummy description",
        user_prompt="Hello World!",
        system_prompt="You are a helpful assistant that greets user.",
    )
    prompt_info = service.get_prompt()
    messages = (
        prompt_info.get("variants")[0]
        .get("templateConfiguration")
        .get("chat")
        .get("messages")
    )
    content = messages[0].get("content")[0].get("text")
    assert content == "Hello World!"


def test_update_prompt():
    service.update_prompt(
        description="updated dummy description",
        system_prompt="You are a helpful assistant that greets Bedrock user.",
    )
    prompt_info = service.get_prompt()
    description = prompt_info.get("description")
    system_prompt = (
        prompt_info.get("variants")[0]
        .get("templateConfiguration")
        .get("chat")
        .get("system")[0]
        .get("text")
    )
    assert (
        description == "updated dummy description"
        and system_prompt == "You are a helpful assistant that greets Bedrock user."
    )


def test_create_prompt_version():
    service.create_prompt_version(tags={"author": "dummy.kim"})
    new_version = list(
        filter(
            lambda x: x.get("version") == 1, service.list_available_prompt_versions()
        )
    ).pop()
    system_prompt = (
        new_version.get("variant")
        .get("templateConfiguration")
        .get("chat")
        .get("system")[0]
        .get("text")
    )
    assert (
        new_version.get("tags").get("author") == "dummy.kim"
        and system_prompt == "You are a helpful assistant that greets Bedrock user."
    )
    service.delete_prompt()  # resource clean up
