import pytest
from unittest.mock import patch, MagicMock
from src.llm_client import LLMClient

@pytest.fixture
def llm_client():
    return LLMClient(
        base_url="http://test.api/v1",
        model="test-model",
        system_prompt="Ты тестовый ассистент."
    )

def test_get_response(llm_client):
    with patch.object(llm_client.client.chat.completions, 'create') as mock_create:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Тестовый ответ"
        mock_create.return_value = mock_response
        
        messages = [{"role": "user", "content": "Привет"}]
        response = llm_client.get_response(messages)
        
        assert response == "Тестовый ответ"
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args['model'] == "test-model"
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]['role'] == "system"

def test_get_response_error(llm_client):
    with patch.object(llm_client.client.chat.completions, 'create') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        messages = [{"role": "user", "content": "Привет"}]
        with pytest.raises(Exception, match="API Error"):
            llm_client.get_response(messages)

