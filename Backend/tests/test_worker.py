"""Tests for background worker functionality."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.worker import parse_scan, process_scan_file, update_job_status
from app.db.models import Job, Scan


class TestUpdateJobStatus:
    """Test cases for update_job_status function."""
    
    @pytest.mark.asyncio
    async def test_update_job_status_marks_running(self):
        """Test that update_job_status marks job as running and sets started_at."""
        # Arrange
        mock_db = AsyncMock()
        job_id = uuid.uuid4()
        
        mock_job = Job(
            id=job_id,
            scan_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            job_type='parse_scan',
            status='pending',
            progress=0
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_db.execute.return_value = mock_result
        
        # Act
        await update_job_status(mock_db, job_id, 'running', progress=10)
        
        # Assert
        assert mock_job.status == 'running'
        assert mock_job.progress == 10
        assert mock_job.started_at is not None
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_job_status_marks_completed(self):
        """Test that update_job_status marks job as completed and sets completed_at."""
        # Arrange
        mock_db = AsyncMock()
        job_id = uuid.uuid4()
        
        mock_job = Job(
            id=job_id,
            scan_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            job_type='parse_scan',
            status='running',
            progress=50,
            started_at=datetime.utcnow()
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_db.execute.return_value = mock_result
        
        result_data = {'vulnerabilities_found': 5}
        
        # Act
        await update_job_status(
            mock_db, 
            job_id, 
            'completed', 
            progress=100,
            result_data=result_data
        )
        
        # Assert
        assert mock_job.status == 'completed'
        assert mock_job.progress == 100
        assert mock_job.completed_at is not None
        assert mock_job.result_data == result_data
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_job_status_handles_failure(self):
        """Test that update_job_status records error message on failure."""
        # Arrange
        mock_db = AsyncMock()
        job_id = uuid.uuid4()
        
        mock_job = Job(
            id=job_id,
            scan_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            job_type='parse_scan',
            status='running',
            started_at=datetime.utcnow()
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_db.execute.return_value = mock_result
        
        error_msg = "FileNotFoundError: File not found"
        
        # Act
        await update_job_status(
            mock_db,
            job_id,
            'failed',
            error_message=error_msg
        )
        
        # Assert
        assert mock_job.status == 'failed'
        assert mock_job.error_message == error_msg
        assert mock_job.completed_at is not None
        mock_db.commit.assert_called_once()


class TestProcessScanFile:
    """Test cases for process_scan_file function."""
    
    @pytest.mark.asyncio
    async def test_process_scan_file_updates_progress(self):
        """Test that process_scan_file updates progress throughout processing."""
        # Arrange
        mock_db = AsyncMock()
        job_id = uuid.uuid4()
        
        # Mock the job for progress updates
        mock_job = Job(
            id=job_id,
            scan_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            job_type='parse_scan',
            status='running'
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_db.execute.return_value = mock_result
        
        # Create a temporary test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<scan></scan>')
            temp_file = f.name
        
        try:
            # Act
            with patch('scripts.worker.Path') as mock_path:
                mock_file = MagicMock()
                mock_file.exists.return_value = True
                mock_file.stat.return_value.st_size = 1024
                mock_path.return_value = mock_file
                
                result = await process_scan_file('upload/test.xml', job_id, mock_db)
            
            # Assert
            assert result['status'] == 'success'
            assert 'file_path' in result
            assert 'processed_at' in result
            assert mock_db.commit.call_count >= 5  # One for each progress update
        finally:
            import os
            os.unlink(temp_file)


class TestParseScan:
    """Test cases for parse_scan worker function."""
    
    @pytest.mark.asyncio
    async def test_parse_scan_completes_successfully(self):
        """Test that parse_scan processes job and marks it as completed."""
        # Arrange
        job_id = uuid.uuid4()
        scan_id = uuid.uuid4()
        
        job_payload = {
            'job_id': str(job_id),
            'scan_id': str(scan_id),
            'user_id': str(uuid.uuid4()),
            'file_path': 'upload/test.xml',
            'job_type': 'parse_scan'
        }
        
        # Mock database session and models
        with patch('scripts.worker.get_db_session') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            # Mock job
            mock_job = Job(
                id=job_id,
                scan_id=scan_id,
                user_id=uuid.uuid4(),
                job_type='parse_scan',
                status='pending'
            )
            
            # Mock scan
            mock_scan = Scan(
                id=scan_id,
                user_id=uuid.uuid4(),
                filename='test.xml',
                file_path='upload/test.xml',
                status='uploaded'
            )
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.side_effect = [mock_job, mock_job, mock_job, mock_job, mock_job, mock_job, mock_scan]
            mock_db.execute.return_value = mock_result
            
            # Mock file existence
            with patch('scripts.worker.Path') as mock_path:
                mock_file = MagicMock()
                mock_file.exists.return_value = True
                mock_file.stat.return_value.st_size = 2048
                mock_path.return_value = mock_file
                
                # Act
                await parse_scan(job_payload)
                
                # Assert
                assert mock_job.status == 'completed'
                assert mock_scan.status == 'processed'
                assert mock_scan.processed_at is not None
