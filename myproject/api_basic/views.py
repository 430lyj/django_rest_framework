from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators import csrf
from rest_framework import authentication
from rest_framework.parsers import JSONParser
from .models import Article
from .serializers import ArticleSerializer, serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view #좀 더 간편하고 예쁘게 하기 위해서?
from rest_framework.response import Response
from rest_framework import status
#아래는 클래스 기반 view를 위한 추가
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
# Create your views here.
'''
class ArticleViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin): 
    #mixins.ListModelMixin만 추가하면 되고 def 필요 없음
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
'''

#이걸 이용하면 list, retrieve, create, update, partial update, destory function을 다 직접 만들어야 함.
'''
class ArticleViewSet (viewsets.ViewSet): 
    def list(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data) 
    def create(self, request):
        serializer = ArticleSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED ) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, pk=None):
        queryset = Article.objects.all()
        article = get_object_or_404(queryset, pk = pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    def update(self, request, pk= None):
        article = Article.objects.get(pk = pk)
        serializer = ArticleSerializer(article, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
'''


class GenericAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    lookup_field = 'id'
    #authentication_classes = [SessionAuthentication, BasicAuthentication] #만약 가능한 session authentication이 없다면 basic authentication을 사용
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, id = None):
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)
    def post(self, request):
        return self.create(request)
    def put (self, request, id=None):
        return self.update(request, id)
    def delete(self, request, id): 
        return self.destroy(request, id)


class ArticleAPIView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data) 
    
    def post(self, request):
        serializer = ArticleSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED ) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

class ArticleDetails(APIView):
    def get_object(self, id):
        try:
            return Article.objects.get(id = id)
        except Article.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND )
    def get(self, request, id):
        article = self.get_object(id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    def put(self, request, id):
        article = self.get_object(id)
        serializer = ArticleSerializer(article, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id):
        article = self.get_object(id)
        article.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)



# @csrf_exempt 이 부분은 get, post 방식을 위해 필요한 것. decorators에서 api_view를 사용하면 필요 없는 부분임. 
@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == "GET":
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        #return JsonResponse(serializer.data, safe=False) 이부분도 api_view 사용 전에 직접 Json으로 받아라 해 준 것. 
        return Response(serializer.data) #safe = False는 필요 없음
    elif request.method == "POST":
        #data = JSONParser().parse(request) #이 부분은 이제 필요 없음 (자동으로 해줌)
        serializer = ArticleSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED ) #created 되었다는 status임 (404 not found와 동일한 개념인 듯), status를 import 해온 후 이걸로 바뀜
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

#여기는 주석으로 바뀐 부분 처리 X
@api_view(['GET', 'PUT', 'DELETE'])
def article_detail(request, pk):
    try:
        article = Article.objects.get(pk= pk)
    except Article.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND )
    
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ArticleSerializer(article, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        article.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
