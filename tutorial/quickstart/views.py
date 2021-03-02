from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from tutorial.quickstart.serializers import UserSerializer, GroupSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
import uuid
import traceback


from django.db import connection

DEBUG = True
#DEBUG = False

def exception_handler(function):
    def wrapper(*args, **kwargs):
        if DEBUG:
            return function(*args, **kwargs)
        else:
            try:
                ret = function(*args, **kwargs)
            except:
                return JsonResponse({"status": "exception", "exception": traceback.format_exc()})
            return ret

    return wrapper



def mysql_read(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        desc = cursor.description 
        return [x for x in cursor.fetchall()]

def mysql_readdict(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        desc = cursor.description 
        ret = []
        for row in cursor.fetchall():
            ret.append( dict(zip(desc, row)))
        return ret

def mysql_write(query):
#    print("query:", query)
    with connection.cursor() as cursor:
        ret = cursor.execute(query)
    return ret

def parse_arguments(csv, _type):
    return [_type(x) for x in csv.split(",")]


@csrf_exempt
def sample_api(request):
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)

    xyz = parse_arguments(req['xyz'][0], str)
    ret = ""
    return JsonResponse({"status": "OK", "response": ret})


 # ============================== Old Code Below ============================
@csrf_exempt
def test(request):
    ret = {}
    ret['status'] = "0"
    ret['response'] = mysql_read("select name, id from users")
    return JsonResponse(ret)


@csrf_exempt
def add(request):
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)

    name = req['name'][0]
    q = "insert into users (name) values('%s')" % name  
    ret = {"hello": 123}
    return JsonResponse(ret)



@csrf_exempt
def create_user(request, name): 
    mysql_write("insert into users (name) column ('%s')" % name)

#mysql> create table transactions(uid varchar(20), owes float, paid float, tid varchar(40), expense float,  primary key (tid, uid));

@csrf_exempt
def create_transaction(request):
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)


    users = parse_arguments(req['users'][0], str)
    assert('percentage_share' in req) or ('share' in req), "share and percentage_share both missing" 
    
    paids = parse_arguments(req['paids'][0], float)
    share = None
    percentage_share = None

    if 'percentage_share' in req:
        percentage_share = parse_arguments(req['percentage_share'][0], float)
    else:
        share = parse_arguments(req['share'][0], float)
        assert sum(share) == sum(paids), "share != paid"
    if share:
        expense = sum(paids)
        percentage_share = [x/expense*100 for x in share]

    create_txn(users,percentage_share,paids)
    return JsonResponse({"status": "OK"})

def create_txn(users,percentage_share,paids, _type='transaction'):
#    print("users, percentage_share, paids", users, percentage_share, paids)
    expense = sum(paids)
    assert sum(percentage_share) == 100, "sum of percent = %s"% sum(percentage_share)
    tid = uuid.uuid1().hex
    for user, perc, paid in zip(users,percentage_share, paids):
        owes = -1 *( paid - perc/100 * expense)
        mysql_write(f"insert into transactions set uid = '{user}', tid = '{tid}', owes= {owes}, expense = {expense}, paid= {paid}, type='{_type}'")



@csrf_exempt
def settle(request):
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)

    users = parse_arguments(req['users'][0], str)
    u1, u2 = users

    assert u1
    assert u2

    query = f"""
    Select sum(owes), uid 
    from transactions
    where tid in (Select distinct tid from  transactions where uid = '{u1}' )
        and uid = '{u2}' 
        group by uid;
    """

#    print(query)
    ret = mysql_read(query)
#    print(ret)
    msg = ""
    for row in ret:
        amt, usr = row
        if amt > 0:
            # u2 owes u1
            create_txn([u1,u2], [100,0], [0,amt], _type="settlement")
        elif amt<0:
            amt = -1*amt
            create_txn([u2,u1], [100,0], [0,amt], _type="settlement")
            msg = "{u1} is paying {amt} to {u2}"
        else:
            msg = "No settlement required"



    return JsonResponse({"status": "OK", "response": ret, 'query': query, 'msg': msg  })


@csrf_exempt
@exception_handler
def view_balances(request):
    if request.method == 'GET':
        req = dict(request.GET)
    elif request.method == 'POST':
        req = dict(request.POST)

    users = parse_arguments(req['users'][0], str)
    u1 = users[0]

    assert u1
    #raise Exception("Dummy exception")

    query = f"""
    Select sum(owes), uid 
    from transactions
    where tid in (Select distinct tid from  transactions where uid = '{u1}' )
        and uid != '{u1}' 
        group by uid;
    """

    ret = mysql_read(query)

    return JsonResponse({"status": "OK", "response": ret, 'query': query  })


