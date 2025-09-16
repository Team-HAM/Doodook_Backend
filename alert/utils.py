import requests
import json
from django.conf import settings
from push_tokens.models import PushToken
from push_tokens.push_services import push_service


def send_push_to_all(title, content, data=None):
    """
    모든 활성 사용자에게 푸시 알림 발송
    iOS: Expo, Android: FCM
    """
    try:
        print(f"[INFO] 모든 사용자에게 알림 발송 시작")
        
        success = push_service.send_push_notification(
            title=title,
            content=content,
            data=data
        )
        
        if success:
            print(f"[SUCCESS] 푸시 알림 발송 완료")
        else:
            print(f"[ERROR] 푸시 알림 발송 실패")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] 푸시 알림 발송 중 오류 발생: {str(e)}")
        return False

def send_push_to_user(user_id, title, content, data=None):
    """
    특정 사용자에게만 푸시 알림 발송
    iOS: Expo, Android: FCM
    """
    try:
        print(f"[INFO] 사용자 {user_id}에게 알림 발송 시작")
        
        success = push_service.send_push_notification(
            title=title,
            content=content,
            data=data,
            user_id=user_id
        )
        
        if success:
            print(f"[SUCCESS] 사용자 {user_id}에게 푸시 알림 발송 완료")
        else:
            print(f"[ERROR] 사용자 {user_id}에게 푸시 알림 발송 실패")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] 사용자별 푸시 알림 발송 중 오류 발생: {str(e)}")
        return False

def send_push_to_platform(platform, title, content, data=None):
    """
    특정 플랫폼 사용자에게만 푸시 알림 발송
    iOS: Expo, Android: FCM
    """
    try:
        print(f"[INFO] 플랫폼 {platform} 사용자에게 알림 발송 시작")
        
        success = push_service.send_push_notification(
            title=title,
            content=content,
            data=data,
            platform=platform
        )
        
        if success:
            print(f"[SUCCESS] 플랫폼 {platform} 사용자에게 푸시 알림 발송 완료")
        else:
            print(f"[ERROR] 플랫폼 {platform} 사용자에게 푸시 알림 발송 실패")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] 플랫폼별 푸시 알림 발송 중 오류 발생: {str(e)}")
        return False