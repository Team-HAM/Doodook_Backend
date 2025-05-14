from rest_framework import serializers
from .models import MBTIQuestion, MBTIResult

class MBTIQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIQuestion
        fields = '__all__'


class MBTIResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIResult
        fields = ['user', 'result', 'created_at']