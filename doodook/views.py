from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Doodook
from .serializers import DoodookSeriallizer
import random
# Create your views here.
@api_view(['GET'])
def helloAPI(request):
    return Response("hello world!")

@api_view(['GET'])
def randomQuiz(request, id):
    totalQuizs=Doodook.objects.all()
    randomQuizs=random.sample(list(totalQuizs),id)
    serializer=DoodookSeriallizer(randomQuizs,many=True)
    return Response(serializer.data)

from django.http import JsonResponse
from .redis_queue import enqueue_stock_code

def enqueue_price_request(request):
    stock_code = request.GET.get("code")
    if not stock_code:
        return JsonResponse({"error": "stock_code 누락"}, status=400)

    enqueue_stock_code(stock_code)
    return JsonResponse({"message": f"{stock_code} 대기열에 추가됨"})
