from django.db import transaction
from django.utils import timezone
from .models import PushToken

@transaction.atomic
def register_token(*, user, token:str, platform:str, device_id:str,
                   app_version:str|None=None, os_version:str|None=None) -> PushToken:
    # 1) 먼저 device_id 기준으로 찾는다(유저-디바이스는 유니크)
    try:
        pt = PushToken.objects.select_for_update().get(device_id=device_id)
        # 소유자/디바이스는 동일하되 토큰만 바뀐 경우 or 유저 변경
        pt.user = user
        pt.platform = platform
        pt.token = token              # ✅ 새 토큰으로 교체
        pt.app_version = app_version or pt.app_version
        pt.os_version  = os_version or pt.os_version
        pt.is_active = True
        pt.revoked_at = None
        pt.save(update_fields=['user','platform','token','app_version','os_version','is_active','revoked_at','updated_at'])
        return pt
    except PushToken.DoesNotExist:
        # 2) device_id가 처음 등록되는 경우 → 토큰 중복 체크
        # (이 토큰이 다른 누군가에게 귀속됐으면 회수)
        try:
            tok = PushToken.objects.select_for_update().get(token=token)
            tok.user = user
            tok.device_id = device_id
            tok.platform = platform
            tok.is_active = True
            tok.revoked_at = None
            tok.app_version = app_version or tok.app_version
            tok.os_version  = os_version or tok.os_version
            tok.save(update_fields=['user','device_id','platform','is_active','revoked_at','app_version','os_version','updated_at'])
            return tok
        except PushToken.DoesNotExist:
            # 3) 완전 신규
            return PushToken.objects.create(
                user=user, token=token, platform=platform, device_id=device_id,
                app_version=app_version, os_version=os_version, is_active=True
            )

@transaction.atomic
def revoke_token(*, user, token:str) -> bool:
    # 같은 유저의 해당 토큰만 비활성화
    qs = PushToken.objects.select_for_update().filter(user=user, token=token, is_active=True)
    updated = qs.update(is_active=False, revoked_at=timezone.now())
    return updated > 0
