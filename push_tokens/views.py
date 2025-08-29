# push/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PushToken
from .serializers import PushTokenSerializer
from firebase_config import initialize_firebase, send_fcm_message, send_fcm_to_multiple_tokens
from django.db.models import Q
from django.utils import timezone
import os

class PushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = PushTokenSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data

        obj, created = PushToken.objects.update_or_create(
            token=data["token"],                                  # token 기준 upsert
            defaults={
                "user": request.user,
                "device_id": data.get("deviceId"),
                "platform": data.get("platform", "web"),
            },
        )
        return Response(
            {"ok": True, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        # 필요 시 제거용: token로 삭제
        token = request.data.get("token")
        if not token:
            return Response({"detail": "token is required"}, status=400)
        deleted, _ = PushToken.objects.filter(user=request.user, token=token).delete()
        return Response(status=status.HTTP_204_NO_CONTENT if deleted else status.HTTP_404_NOT_FOUND)

class PushNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        푸시 알림 전송 API
        """
        # Firebase 초기화
        initialize_firebase()
        
        # 요청 데이터 검증
        title = request.data.get('title')
        body = request.data.get('body')
        target_type = request.data.get('target_type', 'all')
        
        if not title or not body:
            return Response(
                {"error": "title과 body는 필수입니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 플랫폼별 토큰 수집
        platform_tokens = self._get_platform_tokens(request, target_type)
        
        if not platform_tokens:
            return Response(
                {"error": "전송할 대상이 없습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # FCM 메시지 전송 (플랫폼별 분기)
        result = send_fcm_to_multiple_tokens(
            tokens=[],  # 전체 토큰 리스트 (사용하지 않음)
            title=title,
            body=body,
            data=request.data.get('data', {}),
            platform_tokens=platform_tokens  # 플랫폼별 토큰 그룹
        )
        
        # 플랫폼별 통계 추가
        platform_stats = {
            platform: len(tokens) for platform, tokens in platform_tokens.items()
        }
        
        return Response({
            "message": "플랫폼별 푸시 알림 전송 완료",
            "result": result,
            "platform_stats": platform_stats,
            "total_target_count": sum(len(tokens) for tokens in platform_tokens.values())
        })
    
    def _get_platform_tokens(self, request, target_type):
        """플랫폼별로 토큰을 그룹화하여 수집"""
        from collections import defaultdict
        platform_tokens = defaultdict(list)
        
        if target_type == 'all':
            # 모든 활성 토큰을 플랫폼별로 그룹화
            tokens = PushToken.objects.filter(is_active=True).select_related('user')
            for token_obj in tokens:
                platform_tokens[token_obj.platform].append(token_obj.token)
                
        elif target_type == 'user':
            # 특정 사용자들의 토큰을 플랫폼별로 그룹화
            user_ids = request.data.get('target_users', [])
            tokens = PushToken.objects.filter(
                user_id__in=user_ids,
                is_active=True
            ).select_related('user')
            for token_obj in tokens:
                platform_tokens[token_obj.platform].append(token_obj.token)
                
        elif target_type == 'platform':
            # 특정 플랫폼의 토큰만
            platform = request.data.get('target_platform')
            tokens = PushToken.objects.filter(
                platform=platform,
                is_active=True
            ).select_related('user')
            for token_obj in tokens:
                platform_tokens[token_obj.platform].append(token_obj.token)
                
        elif target_type == 'tokens':
            # 직접 지정된 토큰들 (플랫폼 정보가 없으므로 기본값으로 처리)
            target_tokens = request.data.get('target_tokens', [])
            # 플랫폼 정보가 없는 경우 기본값으로 처리
            platform_tokens['android'] = target_tokens
        
        return dict(platform_tokens)

class PushNotificationTestView(APIView):
    """테스트용 푸시 알림 전송 API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """테스트 메시지 전송"""
        initialize_firebase()
        
        # 테스트용 토큰과 플랫폼
        test_token = request.data.get('test_token')
        platform = request.data.get('platform', 'android')  # 기본값은 android
        
        if not test_token:
            return Response(
                {"error": "test_token이 필요합니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = send_fcm_message(
            token=test_token,
            title="테스트 알림",
            body="백엔드에서 전송한 테스트 메시지입니다.",
            data={"type": "test", "timestamp": str(timezone.now())},
            platform=platform  # 플랫폼 정보 전달
        )
        
        return Response({
            "success": success,
            "message": "테스트 메시지 전송 완료" if success else "테스트 메시지 전송 실패",
            "platform": platform,
            "test_mode": os.getenv('FIREBASE_TEST_MODE', 'false'),
            "token_used": test_token
        })
