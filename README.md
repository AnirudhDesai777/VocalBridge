# VocalBridge - AI-Powered Speech Assistant

VocalBridge is a web-based speech assistance tool designed to help people with speech impairments communicate more effectively. It combines text-to-speech technology with AI-powered text enhancement to create natural, clear speech output.

## Features

- **Text-to-Speech Conversion**: Convert written text to natural-sounding speech
- **Multiple Voice Options**: Choose from various voice options (Amy, Arctic, Bryce, and more)
- **Dual LLM Enhancement**:
  - Text Humanization: Adds natural breaks and punctuation for better TTS output
  - Content Enhancement: Optional AI-powered text enhancement for clearer communication
- **Voice Customization**: Adjust speech rate and voice selection
- **Predictive Text**: Smart text predictions for faster input
- **Review System**: Preview and approve AI-enhanced text before speaking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vocalbridge.git
cd vocalbridge
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
FLASK_APP=run.py
FLASK_ENV=development
GROQ_API_KEY=your-groq-api-key-here
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://127.0.0.1:5000/`

## Usage

1. **Basic Text-to-Speech**:
   - Enter text in the input field
   - Select a voice from the dropdown
   - Click "Generate Speech"

2. **Enhanced Speech**:
   - Enable "Enhance with LLaMA" option
   - Enter text
   - Review the enhanced version
   - Accept or reject the enhancement
   - Listen to the generated speech

3. **Voice Settings**:
   - Choose from multiple voice options
   - Adjust speech rate (slow/normal/fast)
   - Customize voice characteristics

## Architecture

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **LLM Integration**: Groq API with LLaMA model
- **TTS Engine**: Yapper-TTS
- **Logging**: Custom logging system with rotation

## Components

1. **LLM Service**:
   - Text humanization for better TTS
   - Optional content enhancement
   - Groq API integration

2. **TTS Service**:
   - Multiple voice support
   - Speed control
   - Audio file handling

3. **Web Interface**:
   - Responsive design
   - Accessibility features
   - Real-time feedback

## API Endpoints

- `GET /`: Main application interface
- `POST /synthesize`: Generate speech from text
  - Parameters:
    - `text`: Input text
    - `voice`: Selected voice
    - `enhance`: Boolean for enhancement
    - `speed`: Speech rate

## Logging

The application maintains detailed logs in the `logs` directory:
- Daily rotating logs for each component
- Latest logs in separate files
- Console output for development



## License

MIT License - see LICENSE file for details

## Acknowledgments

- Yapper-TTS for speech synthesis
- Groq API for LLaMA model access
- Flask framework