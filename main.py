import time
from datetime import datetime
import requests
import sqlite3
from collections import deque

DATABASE_PATH = r"path/to/trunking_recorder.sqlite3" # add a lower case "r" before the first " if you use \
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_url"
KEYWORDS_TO_MENTION = ["urgent", "fire", "police", "rescue"]  # Add important keywords here
MENTION_ROLE_ID = "123456789012345678"  # Replace with your Discord role ID
TIMEOUT_THRESHOLD = 160  # Timeout for waiting calls (10 mins)

# Don't change below this line, unless you know what your doing

TEXT_FETCH_DELAY = 1  # Wait time before pulling text data

# Track sent call IDs to prevent duplicates
sent_calls = set()

def convert_unix_timestamp(calltime):
    """Convert a Unix timestamp to a human-readable format (DD-MM-YYYY HH:MM:SS)"""
    return datetime.utcfromtimestamp(calltime).strftime('%d-%m-%Y %S:%M:%H')

def send_to_discord(callid, calltime, targetid, text):
    """Send call details to Discord webhook"""
    formatted_calltime = convert_unix_timestamp(calltime)
    mentions = [f"<@&{MENTION_ROLE_ID}>" for kw in KEYWORDS_TO_MENTION if kw.lower() in text.lower()]
    
    embed = {
        "embeds": [{
            "title": f"Call {callid} Details",
            "color": FCBA03,
            "fields": [
                {"name": "Call ID", "value": str(callid), "inline": True},
                {"name": "Call Time", "value": formatted_calltime, "inline": True},
                {"name": "Target ID", "value": str(targetid), "inline": True},
                {"name": "Text", "value": text, "inline": False}
            ],
            "footer": {"text": "Trunking Recorder"}
        }]
    }
    
    if mentions:
        embed["content"] = " ".join(mentions)

    response = requests.post(DISCORD_WEBHOOK_URL, json=embed)

    if response.status_code == 204:
        print(f"[SUCCESS] Sent message for callid {callid}.")
        sent_calls.add(callid)  # Mark as sent before sending
        return True
    else:
        print(f"[ERROR] Failed to send message for callid {callid}. Status: {response.status_code}")
        return False

def get_last_processed_callid():
    """Retrieve the last processed callid"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(callid) FROM calls")
        last_callid = cursor.fetchone()[0]
        conn.close()
        return last_callid if last_callid else 0
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return 0

def get_new_transcriptions(last_callid):
    """Fetch new transcriptions from the database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT callid, calltime, targetid, text FROM calls WHERE callid > ? ORDER BY callid ASC", (last_callid,))
        new_records = cursor.fetchall()
        conn.close()
        return new_records
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return []

def get_call_text(callid):
    """Retrieve the text for a callid"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM calls WHERE callid = ?", (callid,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return None

def main():
    last_callid = get_last_processed_callid()
    print(f"[START] Monitoring calls from last_callid: {last_callid}")
    
    waiting_for_text = deque()

    while True:
        new_transcriptions = get_new_transcriptions(last_callid)

        if new_transcriptions:
            print(f"[INFO] Found {len(new_transcriptions)} new transcription(s).")
            for callid, calltime, targetid, text in new_transcriptions:
                if callid in sent_calls:
                    print(f"[SKIP] Callid {callid} already processed.")
                    continue

                if not text:
                    if callid not in [c[0] for c in waiting_for_text]:
                        print(f"[WAIT] No text for callid {callid}, adding to queue.")
                        waiting_for_text.append((callid, calltime, targetid, time.time()))
                    continue

                # Send to Discord and mark as processed
                if send_to_discord(callid, calltime, targetid, text):
                    sent_calls.add(callid)
                    last_callid = callid

        # Process waiting calls
        current_time = time.time()
        i = 0
        while i < len(waiting_for_text):
            callid, calltime, targetid, added_time = waiting_for_text[i]

            if callid in sent_calls:
                waiting_for_text.remove((callid, calltime, targetid, added_time))
                continue

            if current_time - added_time > TIMEOUT_THRESHOLD:
                print(f"[TIMEOUT] Callid {callid} exceeded timeout, removing from queue.")
                waiting_for_text.remove((callid, calltime, targetid, added_time))
                continue

            text = get_call_text(callid)
            if text:
                print(f"[FOUND] Text available for callid {callid}, sending to Discord.")
                if send_to_discord(callid, calltime, targetid, text):
                    sent_calls.add(callid)
                    waiting_for_text.remove((callid, calltime, targetid, added_time))
            else:
                print(f"[WAIT] Text still unavailable for callid {callid}, retrying later.")
                i += 1  # Only increment if we don't remove an item

        time.sleep(10)  # Wait before checking again

if __name__ == "__main__":
    main()
