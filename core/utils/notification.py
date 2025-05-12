from firebase_admin import messaging

def send_push_notification(registration_token, title, body):
    try:
        message = messaging.Message(notification=messaging.Notification(title=title,body=body),token=registration_token)
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return None