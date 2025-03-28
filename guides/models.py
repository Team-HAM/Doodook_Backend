from django.db import models

class Guide(models.Model):
    title = models.CharField(max_length=100)        # 가이드 제목
    category = models.CharField(max_length=50)      # 카테고리 (초급, 중급, 고급 등)
    content = models.TextField()                    # 마크다운 형식의 전체 내용
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
# 고급 학습 가이드 모델
class AdvancedGuide(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title