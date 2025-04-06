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
        extra_kwargs = {
            'email': {'validators': []}  # 기본 UniqueValidator 제거
        }

    def validate_email(self, email):
        email = email.strip()
        if not email_isvalid(email):
            raise serializers.ValidationError("메일 형식이 올바르지 않습니다.")

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.is_active:
                existing_user.delete()  # 인증 실패한 계정 제거
            else:
                raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return email

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            gender=validated_data.get("gender", ""),
            nickname=validated_data.get("nickname", ""),
            birthdate=validated_data.get("birthdate", None),
            address=validated_data.get("address", ""),
        )
        user.is_active = False
        user.save()

        jwt_token = generate_jwt_token(user)
        activation_url = f"{settings.SITE_URL}/users/{user.id}/activation?token={jwt_token}"

        message = render_to_string('users/user_activate_email.html', {
            'user': user,
            'activation_url': activation_url,
            'user_email': user.email,
            'user_nickname': user.nickname or user.email.split('@')[0],
        })

        email_obj = EmailMessage(
            subject='[SDP] 회원가입 인증 메일입니다',
            body=message,
            to=[user.email]
        )
        email_obj.content_subtype = 'html'

        try:
            email_obj.send()
            print("이메일 전송 성공")
        except Exception as e:
            user.delete()
            raise serializers.ValidationError({
                "status": "error",
                "message": "이메일 전송에 실패하여 회원가입이 완료되지 않았습니다.",
                "details": str(e)
            })

        return user

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