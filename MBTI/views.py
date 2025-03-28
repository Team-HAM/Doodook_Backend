from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .models import MBTIQuestion
from .serializers import MBTIQuestionSerializer

class MBTIQuestionListView(generics.ListAPIView):
    queryset = MBTIQuestion.objects.all()
    serializer_class = MBTIQuestionSerializer

class MBTIQuestionRandomListView(APIView):
    def get(self, request, *args, **kwargs):
        questions = MBTIQuestion.objects.all()
        serializer = MBTIQuestionSerializer(questions, many=True)
        return Response(serializer.data)