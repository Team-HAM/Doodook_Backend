from django.urls import path
from .views import MBTIQuestionListView, MBTIResultView, MBTIResultDetailView

urlpatterns = [
    # 12개의 MBTI 질문 조회
    path("questions/", MBTIQuestionListView.as_view(), name="mbti-questions"),

    # 사용자의 응답을 받아 MBTI 결과 저장
    path("result/", MBTIResultView.as_view(), name="mbti-result"),

    # 사용자의 MBTI 결과 조회
    path("result/detail/", MBTIResultDetailView.as_view(), name="mbti-result-detail"),
]
