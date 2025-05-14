from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserLearningProgress(models.Model):
    LEVEL_CHOICES = (
        (1, '초급 - AdvancedGuide'),
        (2, '중급 - AdvancedGuide'),
        (3, '고급 - AdvancedGuide'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    content_id = models.IntegerField(null=True)  # 가이드 ID (AdvancedGuide의 id)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'level', 'content_id')

    def __str__(self):
        return f"{self.user.username} | Level {self.level} | Content ID {self.content_id} | {'완료' if self.is_completed else '미완료'}"