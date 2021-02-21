from rest_framework import serializers
from .models import Film

class DvdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        # fields = ('film_id','title')
        fields = '__all__'
    
    def create(self, validated_data):
        film = Film.objects.create(**validated_data)
        return film

    def update(self, instance, validated_data):
        if instance.rental_flag is None:
            instance.rental_flag = 1
        else:
            instance.rental_flag = None
        instance.save()
        return instance