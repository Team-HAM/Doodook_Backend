import pandas as pd
from stock_search.models import Stock

def update_stock_data_from_excel(file_path):
    """
    KIND에서 받은 엑셀 파일을 읽어 Django DB에 한 번에 저장 (batch_size=200 적용)
    """
    # 엑셀 파일 로드
    df = pd.read_excel(file_path, engine='openpyxl')

    # 필요한 컬럼만 선택
    df = df[['회사명', '종목코드']]
    df.rename(columns={'회사명': 'name', '종목코드': 'symbol'}, inplace=True)

    # 공백 제거 및 종목코드 6자리 변환
    df['name'] = df['name'].str.strip()
    df['symbol'] = df['symbol'].astype(str).str.zfill(6)

    # DB에 한 번에 저장할 데이터 리스트 생성
    stock_list = [
        Stock(symbol=row['symbol'], name=row['name'])
        for _, row in df.iterrows()
    ]

    # 기존 데이터 삭제 (필요한 경우만 사용)
    Stock.objects.all().delete()

    # batch_size=200으로 설정하여 데이터 저장
    batch_size = 200
    for i in range(0, len(stock_list), batch_size):
        Stock.objects.bulk_create(stock_list[i:i+batch_size], batch_size=batch_size)

    print(f"✅ 총 {len(stock_list)}개의 종목이 DB에 저장되었습니다!")
