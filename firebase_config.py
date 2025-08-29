import firebase_admin
from firebase_admin import credentials, messaging
import os

# 테스트 모드 설정
TEST_MODE = os.getenv('FIREBASE_TEST_MODE', 'false').lower() == 'true'

# Firebase 자격 증명 파일 경로들
ANDROID_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'firebase-credentials-android.json')
IOS_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'firebase-credentials-ios.json')

# Firebase 앱 인스턴스들
android_app = None
ios_app = None

def initialize_firebase():
    """Android와 iOS용 Firebase 앱 초기화"""
    global android_app, ios_app
    
    if TEST_MODE:
        print("[TEST MODE] Firebase 초기화 건너뜀")
        return
    
    try:
        # Android 앱 초기화
        android_cred = credentials.Certificate(ANDROID_CREDENTIALS_PATH)
        android_app = firebase_admin.initialize_app(android_cred, name='android')
        
        # iOS 앱 초기화
        ios_cred = credentials.Certificate(IOS_CREDENTIALS_PATH)
        ios_app = firebase_admin.initialize_app(ios_cred, name='ios')
        
        print("Android와 iOS Firebase 앱 초기화 완료")
        
    except Exception as e:
        print(f"Firebase 초기화 오류: {e}")

def send_fcm_message(token, title, body, data=None, platform='android'):
    """플랫폼별 Firebase 프로젝트로 메시지 전송"""
    if TEST_MODE:
        print(f"[TEST MODE] {platform.upper()} 메시지 전송 시뮬레이션:")
        print(f"  프로젝트: doodook-{platform}")
        print(f"  토큰: {token}")
        return True
    
    try:
        # 플랫폼별 앱 선택
        if platform == 'android' and android_app:
            app = android_app
        elif platform == 'ios' and ios_app:
            app = ios_app
        else:
            raise ValueError(f"지원하지 않는 플랫폼: {platform}")
        
        # 메시지 구성 및 전송
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token
        )
        
        response = messaging.send(message, app=app)
        print(f"Successfully sent {platform} message via doodook-{platform} project: {response}")
        return True
        
    except Exception as e:
        print(f"Error sending {platform} message: {e}")
        return False

def send_fcm_to_multiple_tokens(tokens, title, body, data=None, platform_tokens=None):
    """
    플랫폼별로 그룹화하여 FCM 메시지 전송
    """
    if TEST_MODE:
        print(f"[TEST MODE] 플랫폼별 다중 메시지 전송 시뮬레이션:")
        if platform_tokens:
            for platform, token_list in platform_tokens.items():
                print(f"  {platform.upper()}: {len(token_list)}개 토큰")
        print(f"  제목: {title}")
        print(f"  내용: {body}")
        
        total_tokens = sum(len(tokens) for tokens in platform_tokens.values()) if platform_tokens else len(tokens)
        return {
            "success": total_tokens,
            "failure": 0,
            "total": total_tokens
        }
    
    if not tokens and not platform_tokens:
        return {"success": 0, "failure": 0, "total": 0}
    
    success_count = 0
    failure_count = 0
    
    # 플랫폼별로 메시지 전송
    if platform_tokens:
        for platform, platform_token_list in platform_tokens.items():
            if not platform_token_list:
                continue
                
            try:
                # 플랫폼별 앱 선택
                if platform == 'android' and android_app:
                    app = android_app
                elif platform == 'ios' and ios_app:
                    app = ios_app
                else:
                    print(f"지원하지 않는 플랫폼: {platform}")
                    failure_count += len(platform_token_list)
                    continue
                
                # MulticastMessage 전송
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    tokens=platform_token_list
                )
                
                response = messaging.send_multicast(message, app=app)
                success_count += response.success_count
                failure_count += response.failure_count
                
            except Exception as e:
                print(f"Error sending {platform} multicast message: {e}")
                failure_count += len(platform_token_list)
    else:
        # 기존 로직 (단일 앱 사용)
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            success_count = response.success_count
            failure_count = response.failure_count
            
        except Exception as e:
            print(f"Error sending multicast message: {e}")
            failure_count = len(tokens)
    
    return {
        "success": success_count,
        "failure": failure_count,
        "total": success_count + failure_count
    }
