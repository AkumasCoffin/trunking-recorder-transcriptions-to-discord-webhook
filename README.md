# Trunking Recorder Transcriptions To Discord Webhook
Sends call info and transcription info from trunking recorder's sqlite database to a discord webhook when the text field (transcription info) is updated by either azure speech to text service or a OpenAI Whisper server

## Prerequisites
### auto install via python's module manager pip
```pip install -r requirements.txt```
### or manualy install requests via pip
```python -m pip install requests```

## Configuration
### Set your database path, discord webhook, keywords, discord role id, timeout threshold, and the webhhooks custom username and avatar in main.py

## Usage
### Run the main.py python file in the terminal/CMD using python
```python main.py``` or 
```py main.py```

### has been tested on windows, please let me know if theres any issues with linux

## Fetures 
* Keyword detection
* Discord Ping for Keywords
* custom avatar and username for the discord webhook
* Talk Group mappings for known talk group's
