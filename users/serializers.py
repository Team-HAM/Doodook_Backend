import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_jwt.settings import api_settings

# JWT 핸들러 설정
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


# 유효성 검사 함수 정의
def email_isvalid(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def username_isvalid(username):
    return len(username) > 0
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            #"username",
            "password",
            "gender",
            "nickname",
            "birthdate",
            "email",
            "address",
        )
        read_only_fields = ("id",)

    def validate_email(self, obj):
        if email_isvalid(obj):
            return obj
        raise serializers.ValidationError('메일 형식이 올바르지 않습니다.')


    def validate_username(self, obj):
        if username_isvalid(obj):
            return obj
        raise serializers.ValidationError('닉네임은 한 글자 이상이어야 합니다.')

    def create(self, validated_data):
        # 사용자 생성
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.is_active = False  # 이메일 인증이 완료될 때까지 계정 비활성화
        user.save()

        # JWT 토큰 생성
        payload = JWT_PAYLOAD_HANDLER(user)
        jwt_token = JWT_ENCODE_HANDLER(payload)

        # 이메일 내용 렌더링
        message = render_to_string('users/user_activate_email.html', {
            'user': user,
            'domain': 'localhost:8000',
            'uid': force_str(urlsafe_base64_encode(force_bytes(user.pk))),
            'token': jwt_token,
        })

        mail_subject = '[SDP] 회원가입 인증 메일입니다'
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])

        # 이메일 전송
        try:
            email.send()
            print("이메일 전송 성공")
        except Exception as e:
            print(f"이메일 전송 실패: {e}")

        return user

    
#login
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        
        if user is None:
            return {
                'email': 'None'
            }

        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exist'
            )
        return {
            'email': user.email,
            'token': jwt_token
        }
    