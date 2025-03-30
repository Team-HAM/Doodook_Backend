from rest_framework import serializers
from .models import Guide

class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = ['id', 'title', 'category', 'content', 'created_at', 'updated_at']
from rest_framework import serializers
from .models import AdvancedGuide

# 고급 학습 가이드 시리얼라이저
class AdvancedGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedGuide
        fields = '__all__'  # 모델의 모든 필드를 반환
