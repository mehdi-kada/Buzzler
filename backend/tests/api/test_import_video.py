import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import VideoStatus

client = TestClient(app)


class TestImportVideo:
    """Test cases for the video import endpoint."""

    def test_import_video_success(self, mock_celery_task):
        """Test successful video import initiation."""
        # Use the same example URL as other tests to keep expectations consistent
        response = client.post("/import/import-video", params={
            "url": "https://youtu.be/rnp4-RoRxSo?si=7ZhiDurVKo5E4iDQ",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test_task_id"
        assert data["status"] == VideoStatus.UPLOADING
        assert data["message"] == "Video import has been initiated."
        mock_celery_task.delay.assert_called_once_with(
            "https://example.com/video.mp4", "bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[height>=720][ext=mp4]/best[ext=mp4]/best", None
        )

    def test_import_video_with_custom_filename(self, mock_celery_task):
        """Test video import with custom filename."""
        response = client.post("/import/import-video", params={
            "url": "https://example.com/video.mp4",
            "custom_filename": "my_video"
        })

        assert response.status_code == 200
        mock_celery_task.delay.assert_called_once_with(
            "https://example.com/video.mp4", "bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[height>=720][ext=mp4]/best[ext=mp4]/best", "my_video"
        )

    def test_import_video_server_error(self):
        """Test video import when server error occurs."""
        with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock:
            mock.delay.side_effect = Exception("Connection failed")

            response = client.post("/import/import-video", params={
                "url": "https://example.com/video.mp4",
            })

            assert response.status_code == 500
            data = response.json()
            assert "Failed to start video streaming" in data["detail"]


class TestServerStats:
    """Test cases for the server stats endpoint."""

    def test_get_server_stats_success(self, mock_get_server_stats):
        """Test successful retrieval of server stats."""
        response = client.get("/import/server-stats")

        assert response.status_code == 200
        data = response.json()
        assert "server_stats" in data
        assert data["server_stats"] == {"active_tasks": 0, "available_slots": 5}
        mock_get_server_stats.delay.assert_called_once()


class TestTaskStatus:
    """Test cases for the task status endpoint."""

    def test_get_task_status_from_redis(self, mock_redis_client):
        """Test getting task status from Redis."""
        # Mock Redis response with progress data
        progress_data = '{"task_id": "test_task_id", "status": "uploading", "progress_percentage": 50, "uploaded_bytes": 1024, "current_step": "downloading"}'
        mock_redis_client.get.return_value = progress_data

        response = client.get("/import/task-status/test_task_id")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test_task_id"
        assert data["progress_percentage"] == 50
        assert data["uploaded_bytes"] == 1024
        mock_redis_client.get.assert_called_once_with("video_upload_progress:test_task_id")

    def test_get_task_status_pending_from_celery(self, mock_redis_client):
        """Test getting pending task status from Celery."""
        # Mock no Redis data
        mock_redis_client.get.return_value = None

        # Mock Celery task as pending
        with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock_celery:
            mock_task = Mock()
            mock_task.state = "PENDING"
            mock_celery.AsyncResult.return_value = mock_task

            response = client.get("/import/task-status/test_task_id")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == VideoStatus.PENDING_UPLOAD
            assert data["progress_percentage"] == 0

    def test_get_task_status_failure_from_celery(self, mock_redis_client):
        """Test getting failed task status from Celery."""
        # Mock no Redis data
        mock_redis_client.get.return_value = None

        # Mock Celery task as failure
        with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock_celery:
            mock_task = Mock()
            mock_task.state = "FAILURE"
            mock_task.info = "Download failed"
            mock_celery.AsyncResult.return_value = mock_task

            response = client.get("/import/task-status/test_task_id")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == VideoStatus.FAILED
            assert data["error_message"] == "Download failed"

    def test_get_task_status_other_state_from_celery(self, mock_redis_client):
        """Test getting other task status from Celery."""
        # Mock no Redis data
        mock_redis_client.get.return_value = None

        # Mock Celery task with other state
        with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock_celery:
            mock_task = Mock()
            mock_task.state = "PROCESSING"
            mock_celery.AsyncResult.return_value = mock_task

            response = client.get("/import/task-status/test_task_id")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == VideoStatus.UPLOADING
            assert data["current_step"] == "processing"

    def test_get_task_status_redis_parse_error(self, mock_redis_client):
        """Test getting task status when Redis data can't be parsed."""
        # Mock invalid Redis data
        mock_redis_client.get.return_value = "invalid json"

        # Mock Celery task
        with patch("app.api.endpoints.video.import_video.process_video_upload_streaming") as mock_celery:
            mock_task = Mock()
            mock_task.state = "DOWNLOADING"
            mock_celery.AsyncResult.return_value = mock_task

            response = client.get("/import/task-status/test_task_id")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == VideoStatus.UPLOADING
            assert data["current_step"] == "downloading"

    def test_get_task_status_server_error(self):
        """Test task status endpoint when server error occurs."""
        with patch("app.api.endpoints.video.import_video.redis_client") as mock_redis:
            mock_redis.get.side_effect = Exception("Redis connection failed")

            response = client.get("/import/task-status/test_task_id")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to get progress" in data["detail"]
