from django.shortcuts import render
from django.http import JsonResponse
from .models import Notification

# 전체 조회
def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    data = [
        {
            "id":n.id,
            "title":n.title,
            "content":n.content,
            "created_at":n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for n in notifications
    ]
    return JsonResponse(data,safe=False)

# 개별 조회
def notification_detail(request,pk):
    try:
        n= Notification.objects.get(pk=pk)
        data = {
            "id":n.id,
            "title":n.title,
            "content":n.content,
            "created_at":n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return JsonResponse(data)
    except Notification.DoesNotExist:
        return JsonResponse({"error":"공지사항을 찾을 수 없습니다."},status=404)
