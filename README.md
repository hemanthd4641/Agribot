# Raitha mitra

![Raitha mitra Banner](app/static/images/og-image.png)

Raitha mitra is an AI-powered agricultural advisory application designed to help farmers with crop advice, pest control, soil health, weather information, and government schemes. It supports voice, text, and image-based crop disease diagnosis using state-of-the-art Large Language Models and Vision models.

## Features

- **Crop Disease Diagnosis**: Upload a photo of your crop, and Raitha mitra will analyze it for diseases, pests, or nutrient deficiencies.
- **Voice Support (Multilingual)**: Speak your queries and hear responses using advanced STT (Speech-to-Text) and TTS (Text-to-Speech).
- **Comprehensive Agricultural Advisory**: Ask questions about best planting times, fertilizers, pest control, and weather.
- **Weather Intelligence**: Built-in Open-Meteo free API integration for current weather, 7-day forecasting, and smart agricultural insights.
- **Government Schemes**: Get information on PM-KISAN and other relevant agricultural schemes.
- **Modern Web Interface**: Fully responsive, SaaS-style glassmorphism UI with dark/light modes.
- **Chat History**: Redis-backed conversation memory for context-aware interactions.
- **Data Export**: Download chat history as PDF or Markdown.

## Architecture

Built with modern Python and JavaScript technologies:

- **Backend**: Flask (Python)
- **AI Integration**: LangChain, Groq API (LLaMA-3, Whisper, Orpheus)
- **Memory**: Redis
- **Frontend**: Vanilla HTML/CSS/JS with modern APIs (Web Speech API, marked.js, highlight.js)

For detailed information, refer to [ARCHITECTURE.md](ARCHITECTURE.md).

## Installation

### Prerequisites

- Python 3.9+
- Redis Server (Running locally or hosted)
- Groq API Key

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HemanthD/raithamitra-assistant.git
   cd raithamitra-assistant
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```

   The app will be available at `http://localhost:5000`.

## Environment Variables

See `.env.example` for a complete list of required environment variables. Key variables include:

- `GROQ_API_KEY`: Your Groq API Key.
- `REDIS_HOST`, `REDIS_PORT`: Your Redis configuration.
- `FLASK_SECRET_KEY`: A secure random string for Flask sessions.

## Deployment Guide

### Render

1. Create a new Web Service on Render.
2. Connect your GitHub repository.
3. Set the Environment to `Python`.
4. Set the Build Command to `pip install -r requirements.txt`.
5. Set the Start Command to `gunicorn -c gunicorn.conf.py run:app`.
6. Add your environment variables in the Render Dashboard.

## Screenshots

*(Add screenshots of the web interface here)*

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Author:** Hemanth D  