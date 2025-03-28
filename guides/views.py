
from rest_framework import viewsets
from .models import Guide, AdvancedGuide
from .serializers import GuideSerializer, AdvancedGuideSerializer
from rest_framework.permissions import AllowAny
# 튜토리얼 학습 가이드 ViewSet
class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
    permission_classes = [AllowAny]

# 고급 학습 가이드 ViewSet
class AdvancedGuideViewSet(viewsets.ModelViewSet):
    queryset = AdvancedGuide.objects.all()
    serializer_class = AdvancedGuideSerializer
    permission_classes = [AllowAny]