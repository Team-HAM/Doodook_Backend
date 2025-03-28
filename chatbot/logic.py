from .models import ChatbotResponse
import difflib

def get_chatbot_response(user_input):
    #입력값을 소문자로 변환
    user_input = user_input.lower()

    #완전 일치하는 키워드 검색
    response = ChatbotResponse.objects.filter(keyword=user_input).first()
    if response:
        return response.response

    #키워드가 포함된 응답 검색 (긴 키워드부터 우선 검색)
    possible_responses = ChatbotResponse.objects.all()
    for entry in sorted(possible_responses, key=lambda x: -len(x.keyword)):
        if user_input in entry.keyword:  # 부분 일치하는 경우
            return entry.response

    #유사한 키워드 검색 (difflib 활용)
    keywords = [entry.keyword for entry in possible_responses]
    similar_keywords = difflib.get_close_matches(user_input, keywords, n=1, cutoff=0.6)
    if similar_keywords:
        best_match = similar_keywords[0]
        response = ChatbotResponse.objects.filter(keyword=best_match).first()
        return response.response if response else "죄송해요, 해당 내용을 찾을 수 없어요."

    #기본 응답 반환
    return "죄송해요, 해당 내용을 찾을 수 없어요."