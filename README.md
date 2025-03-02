# trunking-recorder-transcriptions-to-discord-webhook
Sends call info and transcription info from trunking recorder's sqlite database to a discord webhook when the text field (transcription info) is updated by either azure speech to text service or a OpenAI Whisper server

###has been tested on windows, please let me know if theres any issues with linux

# Prerequisites
## auto install via python's module manager pip
```pip install -r requirements.txt```
## or manualy install requests via pip
```python -m pip install requests```

# Usage
## Run the main.py python file in the terminal/CMD using python
```python main.py``` or 
```py main.py```
