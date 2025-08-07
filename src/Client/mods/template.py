from datetime import datetime
def message_got(message: str, username: str, time_at: float):
    readable_time = datetime.fromtimestamp(time_at).strftime("%H:%M")
    print(f"A cool message by {username} was sent at {readable_time}. It reads: {message}")