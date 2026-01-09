"""Tests for job queue functionality."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.queue import enqueue_job, get_queue_status
from app.db.models import Job


class TestEnqueueJob:
    """Test cases for enqueue_job function."""
    
    @pytest.mark.asyncio
    async def test_enqueue_job_creates_job_record(self):
        """Test that enqueue_job creates a Job record in the database."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        scan_id = uuid.uuid4()
        user_id = uuid.uuid4()
        file_path = "upload/test-scan.xml"
        
        # Mock the job that gets created
        mock_job = Job(
            id=uuid.uuid4(),
            scan_id=scan_id,
            user_id=user_id,
            job_type='parse_scan',
            status='pending',
            progress=0
        )
        
        async def mock_refresh(obj):
            obj.id = mock_job.id
        
        mock_db.refresh = mock_refresh
        
        # Act
        with patch('app.core.queue.redis_client') as mock_redis:
            job_id = await enqueue_job(
                db=mock_db,
                job_type='parse_scan',
                scan_id=scan_id,
                user_id=user_id,
                file_path=file_path
            )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert job_id is not None
    
    @pytest.mark.asyncio
    async def test_enqueue_job_pushes_to_redis(self):
        """Test that enqueue_job pushes job payload to Redis."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        scan_id = uuid.uuid4()
        user_id = uuid.uuid4()
        file_path = "upload/test-scan.xml"
        
        mock_job_id = uuid.uuid4()
        
        async def mock_refresh(obj):
            obj.id = mock_job_id
        
        mock_db.refresh = mock_refresh
        
        # Act
        with patch('app.core.queue.redis_client') as mock_redis:
            job_id = await enqueue_job(
                db=mock_db,
                job_type='parse_scan',
                scan_id=scan_id,
                user_id=user_id,
                file_path=file_path,
                metadata={'test': 'data'}
            )
            
            # Assert
            mock_redis.rpush.assert_called_once()
            call_args = mock_redis.rpush.call_args
            queue_name = call_args[0][0]
            assert queue_name == 'queue:parse_scan'
    
    @pytest.mark.asyncio
    async def test_enqueue_job_prevents_duplicates(self):
        """Test that enqueue_job returns existing job if already pending."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        
        existing_job_id = uuid.uuid4()
        existing_job = Job(
            id=existing_job_id,
            scan_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            job_type='parse_scan',
            status='pending'
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_job
        mock_db.execute.return_value = mock_result
        
        # Act
        with patch('app.core.queue.redis_client'):
            job_id = await enqueue_job(
                db=mock_db,
                job_type='parse_scan',
                scan_id=existing_job.scan_id,
                user_id=existing_job.user_id,
                file_path='upload/test.xml'
            )
        
        # Assert
        assert job_id == existing_job_id
        mock_db.add.assert_not_called()  # Should not create new job
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_enqueue_job_validates_job_type(self):
        """Test that enqueue_job raises ValueError for invalid job_type."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid job_type"):
            await enqueue_job(
                db=mock_db,
                job_type='invalid_type',
                scan_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                file_path='upload/test.xml'
            )


class TestGetQueueStatus:
    """Test cases for get_queue_status function."""
    
    def test_get_queue_status_returns_all_queues(self):
        """Test that get_queue_status returns status for all job types."""
        # Arrange
        with patch('app.core.queue.redis_client') as mock_redis:
            mock_redis.llen.return_value = 5
            
            # Act
            status = get_queue_status()
            
            # Assert
            assert 'parse_scan' in status
            assert 'ml_analysis' in status
            assert 'jira_creation' in status
            assert 'report_generation' in status
            assert all(v == 5 for v in status.values())
