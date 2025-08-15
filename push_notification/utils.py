from firebase_admin import messaging

def send_to_firebase_cloud_messaging(registration_token, title, body):
    """
    주어진 registration_token으로 FCM 푸시 전송
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=registration_token,
    )

    response = messaging.send(message)
    return response
