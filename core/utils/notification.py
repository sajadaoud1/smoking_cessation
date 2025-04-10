from firebase_admin import messaging

def send_push_notification(registration_token, title, body):
    message = messaging.Message(notification=messaging.Notification(title=title,body=body),token=registration_token)
    response = messaging.send(message)
    return response