from rest_framework import serializers
from .models import Article

#ModelSerializer을 이용하면 다음 전체 과정을 할 필요는 없다. 
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        #fields =['id', 'title', 'author', 'email']
        fields = '__all__'
