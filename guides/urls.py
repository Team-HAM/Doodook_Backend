from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuideViewSet, AdvancedGuideViewSet

router = DefaultRouter()
router.register('guides', GuideViewSet)  # 기존 튜토리얼 가이드 엔드포인트
router.register('advanced-guides', AdvancedGuideViewSet)  # 고급 학습 가이드 엔드포인트 추가

urlpatterns = [
    path('', include(router.urls)),
]
