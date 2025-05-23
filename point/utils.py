# point/utils.py

from django.http import JsonResponse

def error_response(message, code):
    return JsonResponse({
        "status": "error",
        "message": message,
        "code": code
    }, status=code)
