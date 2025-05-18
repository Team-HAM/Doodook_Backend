import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def get_ai_response(user_input):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "초보 투자자에게 친절하게 존댓말로 설명해줘. 유쾌한 말투로, 예시나 비유도 들어주고고. 300자 이내로 간결하게."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content
