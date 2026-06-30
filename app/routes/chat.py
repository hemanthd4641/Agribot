"""Chat route blueprint.

Handles text, voice, and image chat interactions with session management,
Redis-backed memory, and LLM processing.
"""

import base64
import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, Tuple

from flask import (
    Blueprint, current_app, jsonify, request, session
)
from werkzeug.utils import secure_filename

from app.crew.crew import AgriCrew
from app.config import AppConfig

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)


# --------------------------------------------------------------------------- #
#  Helper Functions                                                           #
# --------------------------------------------------------------------------- #

def _get_session_id() -> str:
    """Get or create a unique session ID for the current user.

    Uses Flask's built-in session object with a session ID.
    Falls back to a simple session.sid if available.

    Returns:
        A string session identifier.
    """
    if not session.get('user_id'):
        import uuid
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['user_id']


def _allowed_audio_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed audio extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in AppConfig.ALLOWED_AUDIO_EXTENSIONS
    )


def _allowed_image_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed image extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in AppConfig.ALLOWED_IMAGE_EXTENSIONS
    )


def _get_mime_type(filename: str) -> str:
    """Get MIME type from file extension."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    mime_map = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp',
    }
    return mime_map.get(ext, 'image/jpeg')


def _get_services():
    """Retrieve initialized services from the Flask app."""
    return (
        current_app.llm_service,
        current_app.memory_service,
        current_app.stt_service,
        current_app.tts_service,
        current_app.domain_guard,
    )


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages (text and audio).

    Accepts:
        - Text via form field 'text'
        - Audio via file upload field 'audio'

    Returns:
        JSON response with 'text' (response) and optionally 'voice' (audio URL).
    """
    session_id = _get_session_id()
    llm_service, memory_service, stt_service, tts_service, domain_guard = _get_services()

    # --- Handle Audio Input ---
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename and _allowed_audio_file(audio_file.filename):
            try:
                # Save uploaded audio
                filename = secure_filename(audio_file.filename)
                upload_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], filename
                )
                audio_file.save(upload_path)

                # Transcribe audio to text
                transcription = stt_service.transcribe(upload_path)

                # Clean up uploaded file
                try:
                    os.remove(upload_path)
                except OSError:
                    pass

                if not transcription:
                    return jsonify({
                        'error': 'Could not transcribe audio. Please try again.'
                    }), 400

                # Process the transcribed text
                response_data = _process_text_query(
                    session_id, transcription,
                    llm_service, memory_service, tts_service, domain_guard
                )
                response_data['transcription'] = transcription
                return jsonify(response_data)

            except Exception as exc:
                logger.error("Audio processing error [%s]: %s", session_id, exc)
                return jsonify({'error': 'Audio processing failed.'}), 500

        return jsonify({'error': 'Invalid audio file format.'}), 400

    # --- Handle Image Input ---
    if 'image' in request.files:
        image_file = request.files['image']
        text = request.form.get('text', 'What do you see in this image? Please analyze it from an agricultural perspective.')

        if image_file.filename and _allowed_image_file(image_file.filename):
            try:
                # Read and encode image
                image_data = image_file.read()
                if len(image_data) > AppConfig.MAX_IMAGE_SIZE:
                    return jsonify({'error': 'Image too large. Max 4MB allowed.'}), 400

                image_b64 = base64.b64encode(image_data).decode('utf-8')
                mime_type = _get_mime_type(image_file.filename)

                # Domain Validation
                is_valid, error_msg = domain_guard.validate_image(image_b64, mime_type)
                
                if not is_valid:
                    memory_service.add_to_conversation(session_id, 'user', f"[Image] {text}")
                    memory_service.add_to_conversation(session_id, 'assistant', error_msg)
                    
                    voice_filename = tts_service.synthesize(error_msg)
                    result: Dict = {'text': error_msg}
                    if voice_filename:
                        result['voice'] = f'/static/audio/{voice_filename}'
                    return jsonify(result)

                # Generate vision response
                history = memory_service.get_conversation_history(session_id)
                llm_result = llm_service.generate_with_image(
                    user_query=text,
                    image_base64=image_b64,
                    image_mime=mime_type,
                    session_id=session_id,
                )

                # Save to memory (text only, not the image)
                memory_service.add_to_conversation(session_id, 'user', f"[Image] {text}")
                memory_service.add_to_conversation(session_id, 'assistant', llm_result.text)

                # Generate audio
                voice_filename = tts_service.synthesize(llm_result.text)
                result: Dict = {
                    'text': llm_result.text,
                    'cache': {
                        'prompt_tokens': llm_result.prompt_tokens,
                        'cached_tokens': llm_result.cached_tokens,
                        'hit_rate': round(llm_result.cache_hit_rate, 1),
                        'completion_tokens': llm_result.completion_tokens,
                    },
                }
                if voice_filename:
                    result['voice'] = f'/static/audio/{voice_filename}'

                return jsonify(result)

            except Exception as exc:
                logger.error("Image processing error [%s]: %s", session_id, exc)
                return jsonify({'error': 'Image processing failed.'}), 500

        return jsonify({'error': 'Invalid image format. Use JPG, PNG, GIF, or WebP.'}), 400

    # --- Handle Text Input ---
    text = request.form.get('text')
    if not text and request.is_json:
        text = request.json.get('text') if request.json else None
    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    response_data = _process_text_query(
        session_id, text, llm_service, memory_service, tts_service, domain_guard
    )
    if not response_data.get('success', True):
        return jsonify(response_data), 500
    return jsonify(response_data)


@chat_bp.route('/chat/clear', methods=['POST'])
def clear_conversation():
    """Clear the conversation history for the current session.

    Returns:
        JSON confirmation message.
    """
    session_id = _get_session_id()
    memory_service = current_app.memory_service
    memory_service.clear_conversation(session_id)
    logger.info("Conversation cleared for session %s", session_id)
    return jsonify({'status': 'ok', 'message': 'Conversation cleared.'})


@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring.

    Returns:
        JSON with service health status.
    """
    memory_service = current_app.memory_service
    memory_healthy = memory_service.health_check()

    return jsonify({
        'status': 'healthy' if memory_healthy else 'degraded',
        'redis': 'connected' if memory_healthy else 'disconnected',
        'timestamp': datetime.utcnow().isoformat(),
    })


@chat_bp.route('/chat/status', methods=['GET'])
def get_chat_status():
    """Poll endpoint for CrewAI execution status."""
    session_id = _get_session_id()
    memory_service = current_app.memory_service
    status_key = f"crew_status:{session_id}"
    
    if memory_service.client:
        status_data = memory_service.client.get(status_key)
        if status_data:
            return jsonify(json.loads(status_data))
    return jsonify([])

# --------------------------------------------------------------------------- #
#  Internal Processing                                                        #
# --------------------------------------------------------------------------- #

def _process_text_query(
    session_id: str,
    user_text: str,
    llm_service,
    memory_service,
    tts_service,
    domain_guard,
) -> Dict:
    """Process a text query through the LLM pipeline.

    Steps:
        1. Validate Domain
        2. Retrieve conversation history from Redis.
        3. Generate response using LLM.
        4. Save user and assistant messages to Redis.
        5. Generate audio response via TTS.

    Args:
        session_id: Current user session.
        user_text: The user's input text.
        llm_service: LLM service instance.
        memory_service: Memory service instance.
        tts_service: TTS service instance.
        domain_guard: DomainGuard service instance.

    Returns:
        Dict with 'text' (response) and optionally 'voice' (audio file URL).
    """
    # 0. Validate Domain
    is_valid, error_msg = domain_guard.validate_text(user_text)
    if not is_valid:
        memory_service.add_to_conversation(session_id, 'user', user_text)
        memory_service.add_to_conversation(session_id, 'assistant', error_msg)
        
        voice_filename = tts_service.synthesize(error_msg)
        result: Dict = {'text': error_msg}
        if voice_filename:
            result['voice'] = f'/static/audio/{voice_filename}'
        return result

    # 1. Get conversation history
    history = memory_service.get_conversation_history(session_id)

    # 2. Intent Routing
    from app.services.intent_router import IntentRouter
    router = IntentRouter()
    intent = router.classify_intent(user_text)

    if intent == "GENERAL_CHAT":
        logger.info("Routing to GENERAL_CHAT fast-path.")
        # Push UI status
        if memory_service.client:
            status_key = f"crew_status:{session_id}"
            memory_service.client.setex(status_key, 3600, json.dumps([{"agent": "General Agriculture Assistant", "status": "completed"}]))
            
        llm_result = llm_service.generate(
            user_query=user_text,
            conversation_history=history,
            session_id=session_id
        )
        final_response = llm_result.text
    else:
        logger.info("Routing to CrewAI (Intent: %s)", intent)
        try:
            crew = AgriCrew(session_id=session_id, groq_api_key=AppConfig.GROQ_API_KEY)
            final_response = crew.kickoff(user_query=user_text, intent=intent)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "crew_error": str(e),
                "traceback": traceback.format_exc()
            }

    # 3. Save to memory
    memory_service.add_to_conversation(session_id, 'user', user_text)
    memory_service.add_to_conversation(session_id, 'assistant', final_response)

    # 4. Generate audio (Warning: generating TTS for a huge report might be slow, but we keep it as requested)
    voice_filename = tts_service.synthesize(final_response)
    result: Dict = {'text': final_response}

    if voice_filename:
        result['voice'] = f'/static/audio/{voice_filename}'

    return result