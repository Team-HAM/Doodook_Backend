import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

User = get_user_model()

# JWT 핸들러 설정
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


# JWT 토큰 생성 함수
def generate_jwt_token(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    return JWT_ENCODE_HANDLER(payload)


# 유효성 검사 함수 정의
def email_isvalid(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "password", "gender", "nickname", "birthdate", "email", "address")
        read_only_fields = ("id",)

    def validate_email(self, obj):
        if email_isvalid(obj):
            return obj
        raise serializers.ValidationError('메일 형식이 올바르지 않습니다.')

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.is_active = False
        user.save()

        jwt_token = generate_jwt_token(user)
        activation_url = f"{settings.SITE_URL}/users/{user.id}/activation?token={jwt_token}"

        # 이메일 내용 렌더링
        message = render_to_string('users/user_activate_email.html', {
            'user': user,
            'activation_url': activation_url,
            'user_email': user.email,
            'user_nickname': user.nickname or user.email.split('@')[0],
        })

        email = EmailMessage(
            subject='[SDP] 회원가입 인증 메일입니다',
            body=message,
            to=[user.email]
        )
        email.content_subtype = 'html'

        try:
            email.send()
            print("이메일 전송 성공")
        except Exception as e:
            user.delete()
            raise serializers.ValidationError({
                "status": "error",
                "message": "이메일 전송에 실패하여 회원가입이 완료되지 않았습니다.",
                "details": str(e)
            })

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError({
                "status": "error",
                "message": "로그인 실패. 이메일 또는 비밀번호가 잘못되었습니다.",
                "code": 401
            })

        try:
            jwt_token = generate_jwt_token(user)
            update_last_login(None, user)
        except Exception as e:
            raise serializers.ValidationError({
                "status": "error",
                "message": "로그인 중 오류가 발생했습니다. 다시 시도해주세요.",
                "code": 500,
                "details": str(e)
            })
        return {'email': user.email, 'token': jwt_token}

from rest_framework import serializers
from .models import User  

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nickname', 'gender', 'birthdate', 'address', 'balance']  # balance 포함

#비밀번호 변경
from rest_framework import serializers
from django.contrib.auth.hashers import check_password

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """ 현재 비밀번호가 맞는지 확인 """
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value