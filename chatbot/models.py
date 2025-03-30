from django.db import models

class ChatbotResponse(models.Model):
    keyword = models.CharField(max_length=100, unique=True)  # 키워드 (예: "주식", "배당금")
    response = models.TextField()  # 챗봇의 응답

    def __str__(self):
        return self.keyword
    
    