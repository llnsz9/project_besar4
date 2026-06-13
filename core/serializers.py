from rest_framework import serializers
from .models import DataEntry  # Kita pakai model DataEntry sebagai contoh

class DataEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataEntry
        fields = '__all__' # Ini artinya semua kolom (title, content, dll) akan dikirim ke Flutter