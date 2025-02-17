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