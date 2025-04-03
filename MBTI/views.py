from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from .models import MBTIQuestion, MBTIResult, InvestmentMBTI
from .serializers import MBTIQuestionSerializer

class MBTIQuestionListView(generics.ListAPIView):
    """ 12개의 MBTI 질문을 반환하는 API """
    queryset = MBTIQuestion.objects.all()[:12]
    serializer_class = MBTIQuestionSerializer

class MBTIResultView(APIView):
    """ 사용자가 12개의 응답을 제출하면 결과를 저장하는 API """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        answers = request.data.get("answers")  # 12개 응답 리스트
        
        if not answers or len(answers) != 12:
            return Response({"error": "12개의 응답이 필요합니다."}, status=400)

        # MBTI 유형별 카운트
        mbti_score = {
            "S": 0, "R": 0,
            "F": 0, "D": 0,
            "V": 0, "G": 0,
            "H": 0, "Q": 0
        }
        questions = MBTIQuestion.objects.all()[:12]

        for i, question in enumerate(questions):
            if answers[i] == "A":
                mbti_score[question.type_a] += 1
            elif answers[i] == "B":
                mbti_score[question.type_b] += 1

        # 각 그룹에서 점수가 높은 유형 선택
        result = (
            "S" if mbti_score["S"] >= mbti_score["R"] else "R"
        ) + (
            "F" if mbti_score["F"] >= mbti_score["D"] else "D"
        ) + (
            "V" if mbti_score["V"] >= mbti_score["G"] else "G"
        ) + (
            "H" if mbti_score["H"] >= mbti_score["Q"] else "Q"
        )

        # 결과 저장
        MBTIResult.objects.update_or_create(user=user, defaults={"result": result})

        return Response({"message": "MBTI 결과가 저장되었습니다."}, status=201)

class MBTIResultDetailView(APIView):
    """ 사용자의 MBTI 결과를 조회하는 API """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        mbti_result = MBTIResult.objects.filter(user=user).first()
        if not mbti_result:
            return Response({"message": "MBTI 결과가 없습니다."}, status=404)

        return Response({"result": mbti_result.result})

class MBTIRecommendationView(APIView):
    """ 사용자의 MBTI 유형에 따른 추천 정보를 제공하는 API """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        mbti_result = MBTIResult.objects.filter(user=user).first()
        
        if not mbti_result:
            return Response({"message": "MBTI 결과가 없습니다."}, status=404)
        
        investment_mbti = InvestmentMBTI.objects.filter(name=mbti_result.result).first()
        
        if not investment_mbti:
            return Response({"message": "해당 MBTI에 대한 추천 정보가 없습니다."}, status=404)
        
        recommendation_data = {
            "mbti": investment_mbti.name,
            "alias": investment_mbti.alias,
            "books": investment_mbti.books.split(",") if investment_mbti.books else [],
            "websites": investment_mbti.websites.split(",") if investment_mbti.websites else [],
            "newsletters": investment_mbti.newsletters.split(",") if investment_mbti.newsletters else [],
            "psychology_guide": investment_mbti.psychology_guide,
        }
        
        return Response(recommendation_data, status=200)