from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from notification.models import Notification
from .utils import send_push_to_all, send_push_to_user, send_push_to_platform
import json

@csrf_exempt
@require_POST
def send_notification(request, notification_id):
    """공지사항을 모든 사용자에게 발송"""
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
        "success": success
    })

@csrf_exempt
@require_http_methods(["POST"])
def send_custom_notification(request):
    """커스텀 알림을 모든 사용자에게 발송"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return JsonResponse({"error": "제목과 내용이 필요합니다."}, status=400)
        
        success = send_push_to_all(title, content)
        
        return JsonResponse({
            "success": success,
            "message": "알림 발송 완료" if success else "알림 발송 실패"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"오류 발생: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_user_notification(request, user_id):
    """특정 사용자에게 알림 발송"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return JsonResponse({"error": "제목과 내용이 필요합니다."}, status=400)
        
        success = send_push_to_user(user_id, title, content)
        
        return JsonResponse({
            "success": success,
            "message": "사용자 알림 발송 완료" if success else "사용자 알림 발송 실패"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"오류 발생: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_platform_notification(request, platform):
    """특정 플랫폼 사용자에게 알림 발송"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return JsonResponse({"error": "제목과 내용이 필요합니다."}, status=400)
        
        success = send_push_to_platform(platform, title, content)
        
        return JsonResponse({
            "success": success,
            "message": f"플랫폼 {platform} 알림 발송 완료" if success else f"플랫폼 {platform} 알림 발송 실패"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"오류 발생: {str(e)}"}, status=500)