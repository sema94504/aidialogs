from unittest.mock import MagicMock, patch

import pytest

from src.llm_client import LLMClient


@pytest.fixture
def llm_client(temp_prompt_file):
    return LLMClient(
        base_url="http://test.api/v1", model="test-model", system_prompt_file=temp_prompt_file
    )


@pytest.fixture
def temp_prompt_file(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Ты тестовый ассистент из файла.")
    return str(prompt_file)


def test_get_response(llm_client):
    with patch.object(llm_client.client.chat.completions, "create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Тестовый ответ"
        mock_create.return_value = mock_response

        messages = [{"role": "user", "content": "Привет"}]
        response = llm_client.get_response(messages)

        assert response == "Тестовый ответ"
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "test-model"
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][0]["role"] == "system"


def test_get_response_error(llm_client):
    with patch.object(llm_client.client.chat.completions, "create") as mock_create:
        mock_create.side_effect = Exception("API Error")

        messages = [{"role": "user", "content": "Привет"}]
        with pytest.raises(Exception, match="API Error"):
            llm_client.get_response(messages)


def test_llm_client_reads_prompt_from_file(temp_prompt_file):
    client = LLMClient(
        base_url="http://test.api/v1", model="test-model", system_prompt_file=temp_prompt_file
    )
    assert client.system_prompt == "Ты тестовый ассистент из файла."


def test_llm_client_file_not_found():
    with pytest.raises(FileNotFoundError):
        LLMClient(
            base_url="http://test.api/v1",
            model="test-model",
            system_prompt_file="nonexistent_file.txt",
        )
