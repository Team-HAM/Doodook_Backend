import json
from guides.models import Guide

def import_guides(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            guides = json.load(file)
            for guide in guides:
                Guide.objects.create(
                    title=guide['title'],
                    category=guide['category'],
                    content=guide['content']
                )
        print("학습 가이드가 성공적으로 삽입되었습니다!")
    except Exception as e:
        print(f"에러 발생: {e}")

# 명령어로 실행
if __name__ == "__main__":
    import_guides("guides.json")
