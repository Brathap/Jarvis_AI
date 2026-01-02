# J.A.R.V.I.S. Rectified 🤖

A Python-based desktop AI assistant for **Linux**. It features a futuristic Tkinter GUI, voice control, AI chat, and system automation tools.

## 🌟 Features
* **Reactive HUD:** A sci-fi visual interface that pulses with voice input and processing status.
* **Voice Control:** Hands-free commands using `SpeechRecognition`.
* **AI Chat:** Connected to Pollinations.ai for intelligent conversation.
* **Automation:**
    * **WhatsApp:** Send messages automatically via WhatsApp Web.
    * **Browser:** Voice-controlled searching for Google, YouTube, and GitHub.
    * **Auto-Typing:** Dictate text to be typed into any active window.

## ⚠️ Requirements (Linux Only)
This project is built for Linux and relies on specific system tools.

### 1. System Dependencies
Install these via your terminal (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3-tk xdotool mpv portaudio19-dev
pip install SpeechRecognition pyaudio

⚙️ Configuration
Before running, open jarvis.py and edit the configuration section at the top:
USER_NAME = "Brathap"
CONTACTS = {
    "friend_name": "919876543210" # Format: CountryCode + Number (No + symbol)
}

Run the assistant from your terminal:
python3 jarvis.py
