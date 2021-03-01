from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from tutorial.quickstart.serializers import UserSerializer, GroupSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json

from django.db import connection

def mysql_read(query):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from users")
        return [x for x in cursor.fetchall()]

def mysql_write(query):
    print("query:", query)
    with connection.cursor() as cursor:
        ret = cursor.execute(query)
    return ret

@csrf_exempt
def test(request):
    ret = {}
    ret['status'] = "0"
    ret['response'] = mysql_read("select name, id from users")
    print(ret)
    return JsonResponse(ret)


@csrf_exempt
def add(request):
    print("== add == ")
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)

    print(req)
    name = req['name'][0]
    q = "insert into users (name) values('%s')" % name  
    print(q)
    print("Writeresponse:", mysql_write(q))
    ret = {"hello": 123}
    return JsonResponse(ret)
