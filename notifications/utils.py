# notifications/utils.py
import os
from django.contrib.auth.models import User
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

# --- Initialisation Firebase ---
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.NOTIFICATION_CERTIFICATE)
    firebase_admin.initialize_app(cred)

# --- Envoi d'une notification à un token ---
def sendPush(token, title, body, data=None):
    """
    Envoie une notification push à un seul token FCM.
    """
    if not token:
        return {"success": False, "error": "Token vide"}

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token,
        data=data or {}
    )
    response = messaging.send(message)
    print("✅ Successfully sent message:", response)

    return {"success": True, "response": response}

# --- Envoi à un utilisateur précis ---
def send_to_user(username, title, description, data=None):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Utilisateur {username} introuvable.")
        return False

    token = None
    if hasattr(user, "userprofile"):
        token = getattr(user.userprofile, "notification_token", None)

    if not token:
        print(f"❌ Aucun token trouvé pour {username}")
        return False

    result = sendPush(token, title, description, data or {})
    print(f"✅ Notification envoyée à {username} → {result}")
    return True

# --- Test ---
def test_push():
    # Token FCM valide d'un appareil cible
    test_token = "f0iF1_CNkUPqtsmh2FusI4:APA91bGh1nWxEVsGOk53BPqsdUL-xyy4345mvTkVDR7DmBNbA2lXCqQB475kgRUryYXDEg79lIgU70OAHFn1e7P_RdP3YmzoqIa_DeXWOu93ixCXQR0QGII"

    result = sendPush(
        token=test_token,
        title="🔔 Test Notification",
        body="Ceci est un test depuis Django",
        data={"key1": "value1"}
    )
    print("Résultat test_push :", result)
    return result
