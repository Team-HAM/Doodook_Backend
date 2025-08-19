from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from notification.models import Notification
from .utils import send_push_to_all

@csrf_exempt
@require_POST
def send_notification(request, notification_id):
    try:
        n = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return JsonResponse({"error": "공지사항을 찾을 수 없습니다."}, status=404)

    success = send_push_to_all(n.title, n.content)

    if success:
        n.is_sent = True
        n.save()

    return JsonResponse({
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "is_sent": n.is_sent,
    })