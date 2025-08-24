import pytest
from unittest.mock import patch, Mock
from src.services.api_client import GeminiAPIClient


@pytest.fixture
def api_client():
    return GeminiAPIClient()


def test_successful_api_call(api_client):
    with patch("src.services.api_client.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Hello, this is a response."}]}}
            ]
        }
        mock_post.return_value = mock_response

        response = api_client.call_api("Test prompt")
        assert response == "Hello, this is a response."


def test_api_call_failure(api_client):
    with patch("src.services.api_client.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="API error: 500"):
            api_client.call_api("Test prompt")


def test_invalid_response_structure(api_client):
    with patch("src.services.api_client.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Invalid response structure"):
            api_client.call_api("Test prompt")
