from flask import Blueprint, render_template, request, jsonify
from app.services.tts_service import TTSService
from app.services.llm_service import LLMService
from app.utils.logger import CustomLogger

bp = Blueprint('main', __name__)
tts_service = TTSService()
llm_service = LLMService()
logger = CustomLogger("routes").get_logger()

@bp.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    logger.info("Received synthesis request")
    
    data = request.get_json()
    text = data.get('text', '')
    voice = data.get('voice', 'amy')
    enhance = data.get('enhance', True)
    speed = data.get('speed', 1.0)  # New parameter for speed control
    
    logger.info(f"Request parameters - Text: {text}, Voice: {voice}, "
               f"Enhance: {enhance}, Speed: {speed}")
    
    try:
        # First, always humanize the text for better TTS
        humanized_text, enhanced_text = llm_service.process_text(text, enhance)
        
        response_data = {
            'success': True,
            'original_text': text,
            'humanized_text': humanized_text,
            'enhanced_text': enhanced_text if enhance else None,
        }
        
        logger.info("Text processing successful")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing request: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400

@bp.route('/speak', methods=['POST'])
def speak():
    logger.info("Received speech request")
    
    data = request.get_json()
    text = data.get('text', '')
    voice = data.get('voice', 'amy')
    speed = data.get('speed', 1.0)
    
    try:
        audio_data = tts_service.generate_speech(text, voice, speed)
        return jsonify({
            'success': True,
            'audio': audio_data
        })
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating speech: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400