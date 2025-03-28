from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .logic import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message")

            if not user_input:
                return JsonResponse({"error": "Message field is required"}, status=400)

            # 챗봇 응답 가져오기
            response = get_chatbot_response(user_input)

            return JsonResponse({"response": response})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)