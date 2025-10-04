"""
JarvisX STT Service
Speech-to-Text service using OpenAI Whisper for Sinhala and English transcription
"""

import os
import tempfile
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import whisper
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="JarvisX STT Service",
    description="Speech-to-Text service with Sinhala support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Whisper model
whisper_model = None

def load_whisper_model():
    """Load Whisper model on startup"""
    global whisper_model
    try:
        model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")
        logger.info(f"Loading Whisper model: {model_size}")
        whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    load_whisper_model()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "stt", "model_loaded": whisper_model is not None}

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("si"),  # Default to Sinhala
    timestamp: bool = Form(False)
):
    """
    Transcribe audio file to text
    
    Args:
        file: Audio file (wav, mp3, m4a, etc.)
        language: Language code (si for Sinhala, en for English)
        timestamp: Whether to include timestamps in response
    
    Returns:
        JSON with transcribed text and metadata
    """
    if not whisper_model:
        raise HTTPException(status_code=500, detail="Whisper model not loaded")
    
    # Validate file type
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        try:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            
            logger.info(f"Processing audio file: {file.filename} ({len(content)} bytes)")
            
            # Transcribe with Whisper
            result = whisper_model.transcribe(
                temp_file_path,
                language=language if language in ["si", "en"] else None,
                word_timestamps=timestamp
            )
            
            response = {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "duration": result.get("duration", 0),
                "filename": file.filename
            }
            
            if timestamp and "segments" in result:
                response["segments"] = [
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"]
                    }
                    for segment in result["segments"]
                ]
            
            logger.info(f"Transcription completed: {len(response['text'])} characters")
            return JSONResponse(content=response)
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

@app.post("/transcribe-batch")
async def transcribe_batch(
    files: list[UploadFile] = File(...),
    language: Optional[str] = Form("si")
):
    """
    Transcribe multiple audio files
    
    Args:
        files: List of audio files
        language: Language code for transcription
    
    Returns:
        List of transcription results
    """
    results = []
    
    for file in files:
        try:
            # Create a single-file upload for the transcribe endpoint
            single_file = UploadFile(
                filename=file.filename,
                file=file.file,
                content_type=file.content_type
            )
            
            result = await transcribe_audio(
                file=single_file,
                language=language,
                timestamp=False
            )
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "result": result.body.decode() if hasattr(result, 'body') else result
            })
            
        except Exception as e:
            logger.error(f"Failed to transcribe {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return JSONResponse(content={"results": results})

@app.get("/languages")
async def supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": [
            {"code": "si", "name": "Sinhala"},
            {"code": "en", "name": "English"},
            {"code": "auto", "name": "Auto-detect"}
        ],
        "default": "si"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
