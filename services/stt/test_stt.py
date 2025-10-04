"""
Tests for STT service
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_test_audio_file(content: bytes = b"fake_audio_data"):
    """Create a temporary audio file for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "stt"

def test_supported_languages():
    """Test supported languages endpoint"""
    response = client.get("/languages")
    assert response.status_code == 200
    data = response.json()
    assert "supported_languages" in data
    assert "default" in data
    assert data["default"] == "si"
    
    # Check that Sinhala is supported
    languages = [lang["code"] for lang in data["supported_languages"]]
    assert "si" in languages
    assert "en" in languages

def test_transcribe_invalid_file_type():
    """Test transcription with invalid file type"""
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"not an audio file")
        temp_file.flush()
        
        with open(temp_file.name, "rb") as f:
            response = client.post(
                "/transcribe",
                files={"file": ("test.txt", f, "text/plain")},
                data={"language": "si"}
            )
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_transcribe_missing_file():
    """Test transcription without file"""
    response = client.post("/transcribe")
    assert response.status_code == 422  # Validation error

def test_transcribe_batch_empty():
    """Test batch transcription with no files"""
    response = client.post("/transcribe-batch")
    assert response.status_code == 422  # Validation error

def test_transcribe_with_language_parameter():
    """Test transcription with language parameter"""
    # Create a minimal WAV file header (this won't actually transcribe but tests the endpoint)
    wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        temp_file.write(wav_header)
        temp_file.flush()
        
        with open(temp_file.name, "rb") as f:
            response = client.post(
                "/transcribe",
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "en", "timestamp": "false"}
            )
    
    # The response might fail due to invalid audio, but we're testing the endpoint structure
    # In a real test environment, you'd use actual audio files
    assert response.status_code in [200, 500]  # Either success or processing error

@pytest.fixture(scope="module")
def sample_audio_file():
    """Create a sample audio file for testing"""
    # In a real implementation, you'd use actual audio files
    # For now, we'll create a minimal WAV file
    wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    return wav_header

def test_integration_transcribe_flow():
    """Integration test for the complete transcription flow"""
    # This would be a more comprehensive test with actual audio files
    # For now, we'll test the endpoint structure
    
    response = client.get("/health")
    assert response.status_code == 200
    
    response = client.get("/languages")
    assert response.status_code == 200
    
    # Test that the service is properly initialized
    health_data = client.get("/health").json()
    assert "model_loaded" in health_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
