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
    
    logger.info(f"Request parameters - Text: {text}, Voice: {voice}, Enhance: {enhance}")
    
    try:
        # First enhance the text if requested
        if enhance:
            logger.debug("Enhancing text with LLM")
            text = llm_service.enhance_text(text)
            logger.info(f"Text enhanced: {text}")
        
        # Then convert to speech
        logger.debug("Converting text to speech")
        audio_data = tts_service.generate_speech(text, voice)
        
        response_data = {
            'success': True,
            'audio': audio_data,
            'enhanced_text': text
        }
        logger.info("Request processed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing request: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400