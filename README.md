# trunking-recorder-transcriptions-to-discord-webhook
Sends call info and transcription info from trunking recorder's sqlite database to a discord webhook when the text field (transcription info) is updated by either azure speech to text service or a OpenAI Whisper server

### Prerequisites
# auto install via python's module manager pip
pip install -r requirements.txt
# or manualy install requests via pip
python -m pip install requests

## Usage
python main.py
or
py main.py
