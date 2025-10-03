import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings


def sendPushp(title, body, tokens, data_payload=None):
    if not tokens:
        return {"error": "No valid device tokens provided"}

    if not isinstance(tokens, list):
        tokens = [tokens]

    tokens = [t for t in tokens if t]  # Nettoyage des tokens vides

    if not tokens:
        return {"error": "No valid device tokens provided"}

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data_payload or {},
        tokens=tokens
    )

    try:
        response = messaging.send_multicast(message)
        return {"success": response.success_count, "failure": response.failure_count}
    except firebase_admin.exceptions.FirebaseError as e:
        return {"error": str(e)}
