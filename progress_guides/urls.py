from django.urls import path
from .views import (
    complete_content_by_level,
    level_progress_detail,
    can_access_content,
    level_progress_allcontent,
)

urlpatterns = [
    # 콘텐츠 완료 처리: 단계 + 콘텐츠 번호 방식
    path('complete/<int:level_id>/<int:content_number>/', complete_content_by_level, name='complete-by-level'),

    # 콘텐츠가 열렸는지 확인
    path('unlock/<int:level_id>/<int:content_number>/', can_access_content, name='can-access-content'),

    # 특정 단계의 전체 진도율 내용 확인
    path('level/<int:level_id>/', level_progress_detail, name='level-progress'),

    #특정 단계의 전체 content 진도율 확인
    path('level/<int:level_id>/content/', level_progress_allcontent, name='level_progress_allcontent'),

]