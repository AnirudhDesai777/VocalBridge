from flask import Blueprint, render_template, request, jsonify
from app.services.tts_service import TTSService
from app.services.llm_service import LLMService

bp = Blueprint('main', __name__)
tts_service = TTSService()
llm_service = LLMService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    data = request.get_json()
    text = data.get('text', '')
    voice = data.get('voice', 'amy')
    enhance = data.get('enhance', True)  # New parameter to control enhancement
    
    try:
        # First enhance the text if requested
        if enhance:
            text = llm_service.enhance_text(text)
        
        # Then convert to speech
        audio_data = tts_service.generate_speech(text, voice)
        
        return jsonify({
            'success': True, 
            'audio': audio_data,
            'enhanced_text': text  # Return the enhanced text to display
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 400