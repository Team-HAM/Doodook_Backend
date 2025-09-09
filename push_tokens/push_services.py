import requests
import json
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from django.utils import timezone
from .models import PushToken
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        self.expo_url = "https://exp.host/--/api/v2/push/send"
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            if not firebase_admin._apps:
                cred_path = getattr(settings, 'FCM_CREDENTIALS_PATH', None)
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                else:
                    cred_dict = getattr(settings, 'FCM_CREDENTIALS_DICT', None)
                    if cred_dict:
                        cred = credentials.Certificate(cred_dict)
                    else:
                        logger.warning("Firebase credentials not configured")
                        return

                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized")
        except Exception as e:
            logger.error(f"Firebase 초기화 실패: {e}")

    def send_to_expo(self, tokens, title, content, data=None):
        try:
            messages = [{
                "to": token,
                "sound": "default",
                "title": title,
                "body": content,
                "data": data or {
                    "title": title,
                    "content": content,
                    "type": "notification"
                }
            } for token in tokens]

            headers = {
                "Accept": "application/json",
                "Accept-encoding": "gzip, deflate",
                "Content-Type": "application/json"
            }

            batch_size = 100
            total_success = 0
            total_failed = 0

            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                try:
                    response = requests.post(
                        self.expo_url,
                        data=json.dumps(batch),
                        headers=headers,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        for idx, res in enumerate(result.get('data', [])):
                            if res.get('status') == 'error':
                                error_code = res.get('details', {}).get('error')
                                self._deactivate_token(batch[idx]['to'])
                                total_failed += 1
                            else:
                                total_success += 1

                    elif response.status_code == 400:
                        logger.error("[EXPO] 400 Bad Request (푸시 형식 또는 토큰 문제)")
                        total_failed += len(batch)
                    else:
                        logger.error(f"[EXPO] 응답 실패: status={response.status_code}")
                        total_failed += len(batch)

                except requests.exceptions.RequestException as e:
                    logger.error(f"[EXPO] 요청 예외 발생: {e}")
                    total_failed += len(batch)

            logger.info(f"[EXPO] 발송 결과: 성공={total_success}, 실패={total_failed}")
            return total_failed == 0

        except Exception as e:
            logger.error(f"[EXPO] 예외 발생: {e}")
            return False

    def send_to_fcm(self, tokens, title, content, data=None):
        try:
            if not firebase_admin._apps:
                logger.error("Firebase not initialized")
                return False

            message_data = data or {
                "title": title,
                "content": content,
                "type": "notification"
            }

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=content
                ),
                data=message_data,
                tokens=tokens
            )

            response = messaging.send_each_for_multicast(message)

            logger.info(f"[FCM] 발송 결과: 성공={response.success_count}, 실패={response.failure_count}")

            for idx, resp in enumerate(response.responses):
                if not resp.success and hasattr(resp.exception, 'code'):
                    if resp.exception.code in ['INVALID_ARGUMENT', 'UNREGISTERED', 'SENDER_ID_MISMATCH']:
                        self._deactivate_token(tokens[idx])

            return response.failure_count == 0

        except Exception as e:
            logger.error(f"[FCM] 예외 발생: {e}")
            return False

    def _deactivate_token(self, token):
        try:
            PushToken.objects.filter(token=token).update(
                is_active=False,
                revoked_at=timezone.now()
            )
        except Exception as e:
            logger.error(f"[TOKEN] 비활성화 실패: {e}")

    def send_push_notification(self, title, content, data=None, user_id=None, platform=None):
        try:
            filters = {"is_active": True}
            if user_id:
                filters["user_id"] = user_id
            if platform:
                filters["platform"] = platform

            push_tokens = PushToken.objects.filter(**filters)

            expo_ios_tokens = []
            expo_android_tokens = []
            fcm_tokens = []

            for token_obj in push_tokens:
                token = token_obj.token
                plat = token_obj.platform

                if token.startswith("ExponentPushToken"):
                    if plat == "ios":
                        expo_ios_tokens.append(token)
                    elif plat == "android":
                        expo_android_tokens.append(token)
                else:
                    fcm_tokens.append(token)

            total_success = True

            if expo_ios_tokens:
                logger.info(f"[EXPO] iOS 대상 {len(expo_ios_tokens)}건 발송")
                success = self.send_to_expo(expo_ios_tokens, title, content, data)
                total_success = total_success and success

            if expo_android_tokens:
                logger.info(f"[EXPO] Android 대상 {len(expo_android_tokens)}건 발송")
                success = self.send_to_expo(expo_android_tokens, title, content, data)
                total_success = total_success and success

            if fcm_tokens:
                logger.info(f"[FCM] 대상 {len(fcm_tokens)}건 발송")
                success = self.send_to_fcm(fcm_tokens, title, content, data)
                total_success = total_success and success

            return total_success

        except Exception as e:
            logger.error(f"[PUSH] 전체 발송 실패: {e}")
            return False


push_service = PushNotificationService()
