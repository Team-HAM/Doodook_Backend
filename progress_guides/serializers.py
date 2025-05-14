from rest_framework import serializers

class LevelProgressSerializer(serializers.Serializer):
    level_id = serializers.IntegerField()
    level_title = serializers.CharField()
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    progress_percent = serializers.IntegerField()
    is_level_completed = serializers.BooleanField()