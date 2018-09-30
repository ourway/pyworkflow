__author__ = 'msd'
wf_base_address = 'http://127.0.0.1:8181/wf'
from json import dumps, loads

import requests
# wf = dict(name='eng_lang',
#           steps = [
#               dict(type='taskcall',taskname='send_sms',params=['Hello Dear Friend']),
#               dict(type='taskcall',taskname='send_sms',params=['This is Only Test']),
#               dict(type='taskcall',taskname='sleep_for_seconds',params=[12]),
#               dict(type="taskcall",taskname="send_sms",params=['hi, im waked up ...']),
#               dict(type='taskcall',taskname="send_sms",params=['lets go to learn english words']),
#               dict(type='taskcall',taskname='task_select_random_english_word',params=[]),
#               dict(type='taskcall',taskname='send_format_message',params=['do u know meaning of {word}? it is {mean}', ['word', 'mean']]),
#               dict(type='taskcall',taskname='sleep_for_seconds',params=[26]),
#               dict(type='taskcall',taskname='send_format_message',params=['Oh! What is {word} meaning?', ['word']]),
#               dict(type='taskcall',taskname='task_get_user_guess',params=[]),
#               dict(type='taskcall',taskname='IF_ELSE',params=[dict(type='eval',params=["""lambda obj, eng: obj['user_guess'] == obj['mean']"""]),
#                                                               dict(type='taskcall',taskname='send_sms',params=['congratulation']),
#                                                               dict(type='taskcall',taskname='send_sms',params=['it was wrong. finish'])])
#           ])


def run_wf1():
    res = requests.post(
        "{baseurl}/run/{wfname}/{wfver}/{custid}".format(
            baseurl=wf_base_address, wfname='simple_add_two_number', wfver=1, custid=123),
        data=dumps({'__rtn_vars__': ['c']}),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(res, requests.Response)
    if res.status_code > 299:
        raise 'Problem in run workflow wf1 status code', res.status_code
    print res.content


def def_wf1():
    simp_d = dict(name='simple_add_two_number',
                  steps=[
                      dict(type='taskcall', taskname='test_task_add_two_number', params=[
                           12, 13, 'c'])
                  ])
    # define wf to server
    a = requests.post(
        "{baseurl}/{wfname}/{wfver}".format(
            baseurl=wf_base_address, wfname='simple_add_two_number', wfver=1),
        data=dumps(simp_d),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(a, requests.Response)
    if a.status_code > 299:
        raise 'wf server response is,', a.status_code
    print "workflow defined to wf server"


def def_wf2():
    w = dict(name='simple_login',
             steps=[
                 dict(type='taskcall', taskname='IF_ELSE', params=[
                     dict(type='eval', params=[
                          ''' lambda obj,eng: obj['username']=='gholi' and obj['password']=='gholi' ''']),
                     # if username and password is correct:
                     dict(type='taskcall', taskname='task_exec', params=['''
def l(obj,eng):
    obj['rtn']= 'hello dear '+obj['username']
    obj['user_login']=True
                     ''', 'l']),
                     # if username and password is not correct
                     dict(type='taskcall', taskname='task_exec', params=['''
def l(obj,eng):
    obj['rtn']='failed to Login'
    obj['user_login']=False
                     ''', 'l'])
                 ])
             ])
    # define wf to server
    a = requests.post(
        "{baseurl}/{wfname}/{wfver}".format(
            baseurl=wf_base_address, wfname='simple_login', wfver=1),
        data=dumps(w),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(a, requests.Response)
    if a.status_code > 299:
        raise 'wf server response is,', a.status_code
    print "workflow defined to wf server"


def run_wf2(username, password):
    res = requests.post(
        "{baseurl}/run/{wfname}/{wfver}/{custid}".format(
            baseurl=wf_base_address, wfname='simple_login', wfver=1, custid=123),
        data=dumps({'__rtn_vars__': ['rtn', 'user_login'],
                    'username': username, 'password': password}),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(res, requests.Response)
    if res.status_code > 299:
        raise 'Problem in run workflow wf1 status code', res.status_code
    print res.content


def run_w3(username, password):
    res = requests.post(
        "{baseurl}/run/{wfname}/{wfver}/{custid}".format(
            baseurl=wf_base_address, wfname='register_user', wfver=1, custid=123),
        data=dumps({'__rtn_vars__': ['username', 'ru_status_code',
                                     'ru_body'], 'username': username, 'password': password}),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(res, requests.Response)
    if res.status_code > 299:
        raise 'Problem in run workflow wf1 status code', res.status_code
    print res.content


def def_w3():

    # define sync web call reg_user which add user to db
    taskdef = dict(task_name="reg_user", task_type="sync",
                   url="http://127.0.0.1:8282/mockservice/user")
    res = requests.post(
        "{baseurl}/task/define".format(baseurl=wf_base_address),
        data=dumps(taskdef),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(res, requests.Response)
    if res.status_code > 299:
        raise 'task definition problem ', res.status_code

    # define async webcall send_sms which sends sms asyncronsly
    taskdef = dict(task_name="send_sms_async", task_type="async",
                   url="http://127.0.0.1:8282/mockservice/async_sms")
    res = requests.post(
        "{baseurl}/task/define".format(baseurl=wf_base_address),
        data=dumps(taskdef),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(res, requests.Response)

    if res.status_code > 299:
        raise 'task definition problem ', res.status_code

    w = dict(
        name='register_user',
        steps=[
            dict(type='taskcall', taskname='task_dynamic_task',
                 params=['reg_user', 'ru', dict(
                     username=dict(type='var', var_name='username'),
                     password=dict(type='var', var_name='password'),
                     req_date=dict(type='value', value=13931413),
                     from_service_name=dict(
                         type='value', value='simple test to farsheed!')
                 )]),
            dict(type='taskcall', taskname='CHOICE', params=[
                dict(type='eval', params=[
                     '''lambda obj,eng: 'r'+str(obj['ru_status_code']) ''']),

                ['r200',
                 dict(type='taskcall', taskname='assign_value_to_var',
                      params=['STATUS', True]),
                 dict(type='taskcall', taskname='assign_var_to_var',
                      params=['user_id', 'ru_user_id']),
                 dict(type='taskcall', taskname='send_sms',
                      params=['You Are Joined Successfully']),
                 dict(type='taskcall', taskname='task_dynamic_task',
                      params=['send_sms_async', 'ssa',
                              dict(
                                  username=dict(
                                      type='var', var_name='username'),
                                  STATUS=dict(type='var', var_name='STATUS')
                              )]),
                 dict(type='taskcall', taskname='send_sms',
                      params=['FINISHED!'])
                 ], [
                    'r409',
                    dict(type='taskcall', taskname='assign_value_to_var',
                         params=['STATUS', False]),
                    dict(type='taskcall', taskname='send_sms',
                         params=['409 error happen'])

                ],
                ['r500', dict(type='taskcall', taskname='send_sms',
                              params=['500 error'])]

            ])

        ]
    )
    a = requests.post(
        "{baseurl}/{wfname}/{wfver}".format(
            baseurl=wf_base_address, wfname='register_user', wfver=1),
        data=dumps(w),
        headers={'Content-type': 'application/json'}
    )
    assert isinstance(a, requests.Response)
    if a.status_code > 299:
        print a.status_code
        print a.reason
        #raise 'wf server response is,',a.status_code
    print "workflow register_user defined to wf server"

if __name__ == '__main__':

    print "to run this test, sure that your workflow baseurl is :", wf_base_address
    raw_input("press any key to continue...")

    print 'define wf1 '
    def_wf1()
    print 'run wf1'
    run_wf1()
    print 'define simple login'
    def_wf2()
    print 'run simple logiin with username:gholi,password:gholi'
    run_wf2('gholi', 'gholi')
    print "run simple login with username:gholi1,password:1"
    run_wf2('gholi1', '1')
    raw_input(
        "to continue run mock_service.py to test web calls,press any key to continue ...")
    def_w3()
    run_w3('a', 'a')
