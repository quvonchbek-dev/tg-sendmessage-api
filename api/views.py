from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import MessageSerializer
from utils import tg_api

@csrf_exempt
def snippet_list(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)