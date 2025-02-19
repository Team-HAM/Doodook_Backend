from rest_framework import serializers

class TradeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    stock_code = serializers.CharField(max_length=10)
    action = serializers.ChoiceField(choices=["buy", "sell"])  # buy 또는 sell만 가능
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        if data["quantity"] <= 0:
            raise serializers.ValidationError({"quantity": "수량은 1 이상이어야 합니다."})
        if data["price"] <= 0:
            raise serializers.ValidationError({"price": "가격은 1 이상이어야 합니다."})
        return data
    

from .models import StockPortfolio  # StockPortfolio 모델 가져오기

class StockPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPortfolio
        fields = ['stock_code', 'quantity', 'price']  # 포트폴리오에 필요한 필드들
