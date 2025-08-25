import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_celery_task():
    with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock:
        mock_task = Mock()
        mock_task.id = "test_task_id"
        mock.delay.return_value = mock_task
        yield mock


@pytest.fixture
def mock_get_server_stats():
    with patch("app.api.endpoints.video.import_video.get_server_stats") as mock:
        mock_task = Mock()
        mock_task.get.return_value = {"active_tasks": 0, "available_slots": 5}
        mock.delay.return_value = mock_task
        yield mock


@pytest.fixture
def mock_redis_client():
    with patch("app.api.endpoints.video.import_video.redis_client") as mock:
        yield mock