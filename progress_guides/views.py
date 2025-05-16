from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from guides.models import AdvancedGuide
from .models import UserLearningProgress

# 🔧 공통: 단계에 맞는 콘텐츠 가져오기
def get_contents(level):
    if level == 1:
        return AdvancedGuide.objects.filter(id__gte=1, id__lte=8).order_by('id')
    elif level == 2:
        return AdvancedGuide.objects.filter(id__gte=9, id__lte=13).order_by('id')
    elif level == 3:
        return AdvancedGuide.objects.filter(id__gte=14, id__lte=19).order_by('id')
    return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_content_by_level(request, level_id, content_number):
    user = request.user

    contents = get_contents(level_id)
    if contents is None:
        return Response({"error": "Invalid level_id"}, status=400)

    try:
        content = list(contents)[content_number - 1]  # 0-indexed
    except IndexError:
        return Response({"error": "Content number out of range"}, status=404)

    progress, _ = UserLearningProgress.objects.get_or_create(
        user=user,
        level=level_id,
        content_id=content.id
    )
    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.save()

    return Response({
        "message": f"Level {level_id} - Content {content_number} marked as completed."
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def level_progress_detail(request, level_id):
    user = request.user

    contents = get_contents(level_id)
    if contents is None:
        return Response({"error": "Invalid level_id"}, status=400)

    total = contents.count()
    content_ids = contents.values_list('id', flat=True)

    completed = UserLearningProgress.objects.filter(
        user=user, level=level_id, content_id__in=content_ids, is_completed=True
    ).count()

    return Response({
        "level_id": level_id,
        "total": total,
        "completed": completed,
        "progress_percent": int((completed / total) * 100) if total else 0,
        "progress_ratio": f"{completed}/{total}",
        "is_level_completed": completed == total and total != 0,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def can_access_content(request, level_id, content_number):
    user = request.user

    contents = get_contents(level_id)
    if contents is None:
        return Response({"error": "Invalid level_id"}, status=400)

    contents_list = list(contents)

    # ✅ 1번 콘텐츠: 이전 단계 전체 완료 여부 확인
    if content_number == 1:
        if level_id == 1:
            return Response({"can_access": True, "message": "첫 콘텐츠는 열 수 있습니다."})
        else:
            prev_level = level_id - 1
            prev_contents = get_contents(prev_level)
            if not prev_contents:
                return Response({"error": "이전 단계 정보 없음"}, status=400)

            total = prev_contents.count()
            content_ids = prev_contents.values_list('id', flat=True)
            completed = UserLearningProgress.objects.filter(
                user=user, level=prev_level, content_id__in=content_ids, is_completed=True
            ).count()

            if completed == total and total != 0:
                return Response({"can_access": True, "message": f"{prev_level}단계 완료로 접근 가능"})
            else:
                return Response({
                    "can_access": False,
                    "message": f"{prev_level}단계를 모두 완료해야 {level_id}-1 콘텐츠에 접근할 수 있습니다.",
                    "required_level": prev_level,
                    "progress": f"{completed}/{total}"
                })

    # ✅ 2번 이후 콘텐츠: 같은 레벨 내 이전 콘텐츠 완료 여부 확인
    if content_number > len(contents_list) or content_number < 2:
        return Response({"error": "콘텐츠를 찾을 수 없습니다."}, status=404)

    prev_content = contents_list[content_number - 2]

    is_completed = UserLearningProgress.objects.filter(
        user=user, level=level_id, content_id=prev_content.id, is_completed=True
    ).exists()

    if is_completed:
        return Response({"can_access": True, "message": "열람 가능합니다."})
    else:
        return Response({
            "can_access": False,
            "required_previous": f"{level_id}-{content_number - 1}",
            "message": f"{level_id}-{content_number - 1} 콘텐츠를 먼저 완료해야 합니다."
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def level_progress_allcontent(request, level_id):
    user = request.user
    contents = get_contents(level_id)

    if contents is None:
        return Response({"error": "Invalid level_id"}, status=400)

    contents_list = list(contents)
    total = len(contents_list)
    completed_count = 0

    content_progress = {}

    for idx, content in enumerate(contents_list, start=1):
        is_completed = UserLearningProgress.objects.filter(
            user=user, level=level_id, content_id=content.id, is_completed=True
        ).exists()
        content_progress[str(idx)] = is_completed
        if is_completed:
            completed_count += 1

    return Response({
        "level": level_id,
        "content_progress": content_progress,
        "total": total,
        "completed": completed_count
    })

