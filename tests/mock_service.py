__author__ = 'msd'

import random

from bottle import run, post, request, get, HTTPResponse
from json import dumps


@post('/mockservice/user')
def user():
    print request.json
    # this method add user to db
    # if user exists before returns 409
    # if user not exists and add successfully returns 200 and user id in json
    # if problem in add user returns 500
    if random.randint(0, 10) < 5:
        # 50% probiblity user exists before!!!!!
        return HTTPResponse(status=409, body=dumps(dict(message='try after 100s')), headers={'Content-type': 'application/json'})
    else:
        if random.randint(0, 10) < 2:
            # probeblity 20% error happend
            return HTTPResponse(status=500, body=dumps(dict(error='salam man error hastam')), headers={'Content-type': 'application/json'})
        else:
            # user added successfully
            return dict(user_id=random.randint(0, 100000))


@post('/mockservice/async_sms')
def asyn_sms():
    print 'received request:', request.json
    print "please manualy call this url after awhile:", request.json['__callback']


if __name__ == '__main__':
    run(host='127.0.0.1', port=8282)
