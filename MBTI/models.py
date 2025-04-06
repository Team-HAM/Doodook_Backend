from django.db import models
from django.conf import settings

class InvestmentMBTI(models.Model):
    name = models.CharField(max_length=10, unique=True)  # MBTI 유형 (예: "ISTJ")
    alias = models.CharField(max_length=50, blank=True)  # 별칭
    books = models.TextField(blank=True)  # 추천 도서 (쉼표로 구분)
    websites = models.TextField(blank=True)  # 추천 웹사이트 (쉼표로 구분)
    newsletters = models.TextField(blank=True)  # 추천 뉴스레터 (쉼표로 구분)
    psychology_guide = models.TextField(blank=True)  # 심리 가이드 설명
    # created_at = models.DateTimeField(auto_now_add=True, null=True)  # 생성일

    def __str__(self):
        return self.name


class MBTIQuestion(models.Model):
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    type_a = models.CharField(max_length=1, default='S')  # 기본값 추가
    type_b = models.CharField(max_length=1, default='R')  # 기본값 추가
    related_trait = models.CharField(max_length=3)

    def __str__(self):
        return self.question_text
    
class MBTIResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    result = models.CharField(max_length=4)  # 예: 'INTJ', 'ESFP' 등
    created_at = models.DateTimeField(auto_now_add=True)

    