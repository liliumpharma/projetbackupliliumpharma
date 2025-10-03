from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .serializers import NotificationSerializer 
from .models import Notification , UserNotification
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


class NotificationAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        serializer=NotificationSerializer(Notification.objects.filter(users=request.user).order_by('-id')[:50], many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


# views.py

# @login_required
# def get_unread_notifications(request):
#     user_notifications_not_read_count = UserNotification.objects.filter(user=request.user, read=False).select_related('notification')
#     user_notifications = UserNotification.objects.filter(user=request.user).select_related('notification').order_by('-notification__added')
#     notifications = [{
#         'id': un.notification.id,
#         'title': un.notification.title,
#         'description': un.notification.description,
#         'data': un.notification.data,
#         'added': un.notification.added.strftime('%Y-%m-%d à %H:%M:%S'),
#         'read':un.read,
#     } for un in user_notifications]
#     unread_count = user_notifications_not_read_count.count()
#     return JsonResponse({'unread_count': unread_count, 'notifications': notifications})

@login_required
def get_unread_notifications(request):
    # Fetch unread notifications and order by '-notification__added' to get most recent first
    unread_notifications = UserNotification.objects.filter(user=request.user, read=False).select_related('notification').order_by('-notification__added')

    # Fetch all notifications (both read and unread) and order by '-notification__added'
    all_notifications = UserNotification.objects.filter(user=request.user).select_related('notification').order_by('-notification__added')

    # Combine unread notifications with read notifications
    notifications = [{
        'id': un.notification.id,
        'title': un.notification.title,
        'description': un.notification.description,
        'data': un.notification.data,
        'added': un.notification.added.strftime('%Y-%m-%d à %H:%M:%S'),
        'read': un.read,
    } for un in unread_notifications]  # First add unread notifications

    # Append read notifications after unread notifications
    notifications += [{
        'id': un.notification.id,
        'title': un.notification.title,
        'description': un.notification.description,
        'data': un.notification.data,
        'added': un.notification.added.strftime('%Y-%m-%d à %H:%M:%S'),
        'read': un.read,
    } for un in all_notifications if un not in unread_notifications]  # Then add read notifications

    unread_count = unread_notifications.count()  # Count of unread notifications

    return JsonResponse({'unread_count': unread_count, 'notifications': notifications})


# views.py

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime

@csrf_exempt
@require_POST
@login_required
def mark_notifications_read(request):
    data = request.POST  # Récupère les données POST envoyées par la requête Ajax
    notification_id = data.get('id')  # Récupère l'ID de la notification à marquer comme lue

    if notification_id:
        try:
            # Marquer la notification comme lue
            user_notification = UserNotification.objects.get(user=request.user, notification__id=notification_id)
            user_notification.read = True
            user_notification.read_at = datetime.datetime.now()
            user_notification.save()

            return JsonResponse({'status': 'success'})
        except UserNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Missing notification ID'}, status=400)



from django.contrib.auth.models import User
from notifications.models import Notification  # adapte selon ton app
from notifications.utils import sendPush  # adapte selon où est ta fonction

def test_push_to_user(username, title, description, data=None):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"Utilisateur {username} introuvable")
        return

    tokens = []
    if hasattr(user, 'userprofile'):
        if user.userprofile.notification_token:
            tokens.append(user.userprofile.notification_token)
        if user.userprofile.ios_notification_token:
            tokens.append(user.userprofile.ios_notification_token)

    if not tokens:
        print(f"Aucun token trouvé pour {username}")
        return

    sendPush(
        title,
        description,
        tokens,
        data or {}
    )
    print(f"Notification envoyée à {username} avec tokens {tokens}")

