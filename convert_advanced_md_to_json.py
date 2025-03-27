import json
import re

def convert_md_to_json(file_path):
    guides = []
    current_guide = {}
    current_content = []
    current_title = ""
    current_category = "고급"  # 기본 카테고리
    in_guide = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # 카테고리 감지 (예: "## **1. 투자 분석 기초** (고급)")
            category_match = re.match(r"## \*\*[\d.]+ (.*?)\*\* \((.*?)\)", line)
            if category_match:
                current_category = category_match.group(2).strip()
                continue

            # 소제목 감지 (예: "@@@ - 종목 선택 및 기본 분석 방법")
            if line.startswith("@@@ - "):
                # 이전 가이드가 있다면 저장
                if current_content:
                    current_guide['content'] = "\n".join(current_content).strip()
                    guides.append(current_guide)
                    current_content = []

                # 새로운 가이드 시작
                current_title = line.replace("@@@ - ", "").strip()
                current_guide = {
                    "title": current_title,
                    "category": current_category  # 현재 감지된 카테고리 사용
                }
                in_guide = True
                continue

            # 가이드 본문인 경우
            if in_guide:
                current_content.append(line)

        # 마지막 가이드 처리
        if current_content:
            current_guide['content'] = "\n".join(current_content).strip()
            guides.append(current_guide)

    # JSON 파일로 저장
    with open("advanced_guides.json", "w", encoding="utf-8") as output_file:
        json.dump(guides, output_file, ensure_ascii=False, indent=4)

    print("고급 Markdown 파일이 JSON으로 변환되었습니다!")

# 실행
convert_md_to_json("advanced_guides.md")
