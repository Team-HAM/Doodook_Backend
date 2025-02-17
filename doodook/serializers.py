from rest_framework import serializers
from .models import Doodook

class DoodookSeriallizer(serializers.ModelSerializer):
    class Mets:
        model=Doodook
        fields=('title','body','answer')
    