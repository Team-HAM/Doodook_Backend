from rest_framework import serializers
from .models import MBTIQuestion

class MBTIQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIQuestion
        fields = '__all__'
