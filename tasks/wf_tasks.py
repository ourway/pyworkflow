from random import randrange
from sys import stdin
import requests
from json import loads, dumps
from tasks import agent
import engine.msd_wf_storage as storage
from workflow.patterns.controlflow import IF_ELSE, CHOICE


__AUTHOR__ = 'MSD'


def task_exec(exec_str, funcname):
    d = {}
    exec(exec_str) in d
    return d[funcname]


def task_dynamic_task(task_name, return_var_prefix, dict_params):
    """
    call user defined task
    dict_params is something like below:
        {
            param1: { type:'value',value:'string' or number},
            param2: { type:'var', var_name:'workflow variable name'}
            ...
        }
    """
    ddt = loads(storage.get(
        "dynamic_task:{task_name}".format(task_name=task_name)))
    RVP = return_var_prefix if return_var_prefix else ''

    def l(obj, eng):
        dict_to_pass_to_service = dict()
        for _key in dict_params.keys():
            if dict_params[_key]['type'] == 'value':
                dict_to_pass_to_service[_key] = dict_params[_key]['value']
            elif dict_params[_key]['type'] == 'var':
                dict_to_pass_to_service[_key] = obj[
                    dict_params[_key]['var_name']]

        if ddt['task_type'] == 'async':
            dict_to_pass_to_service['__callback'] = '/wf/async_task_result/{wf_name}/{cust_id}/{prefix}'.format(
                wf_name=eng._process_name, cust_id=eng.getVar('__cust_id'), prefix=RVP)

        respo = requests.post(ddt['url'], data=dumps(dict_to_pass_to_service), headers={
                              'Content-type': 'application/json'})
        respo_dict = _dynamic_task_parse_server_response(respo)
        respo_dict = {"{RVP}_{KEY}".format(RVP=RVP, KEY=key): value for (
            key, value) in respo_dict.iteritems()}
        obj.update(respo_dict)

        if ddt['task_type'] == 'async':
            eng.haltProcessing()

    return l


def _dynamic_task_parse_server_response(server_resp):
    rtn_dict = dict()
    assert isinstance(server_resp, requests.Response)
    rtn_dict["status_code"] = server_resp.status_code
    if server_resp.status_code > 299 or server_resp.status_code < 200:
        rtn_dict["body"] = server_resp.content
    else:
        if 'application/json' not in server_resp.headers['content-type'].lower().strip().split(';'):
            rtn_dict['body'] = server_resp.content
        else:
            # server response is json
            rtn_dict.update(server_resp.json())

    return rtn_dict


def assign_value_to_var(varname, value):
    def l(obj, eng):
        obj[varname] = value
    return l


def assign_var_to_var(varname1, varname2):
    def l(obj, eng):
        obj[varname1] = obj[varname2]
    return l


def test_task_add_two_number(a, b, result_var_name):
    def l(obj, eng):
        obj[result_var_name] = a + b
    return l


# ---------- TASK DEFINITIONS

def send_sms(message):
    def l(obj, eng):
        print message, " sent to ", eng.getVar('__cust_id')

    return l


def sleep_for_seconds(seconds):
    def l(obj, eng):
        print "[SYSMSG]run this process after ", seconds, "(s),again and fill input fields by these values:"
        print "User Mobile Number:", eng.getVar('__cust_id')
        print "Workflow Name:", eng._process_name
        agent.celery_execute_workflow_.apply_async(
            (eng._process_name, eng.getVar('__cust_id')), countdown=seconds)
        eng.haltProcessing()

    return l


def select_random_english_word(obj, eng):
    words = dict(cat='pishih', water='Su', nothing='Hava , Hech',
                 father='dada', mother='ana')
    m = randrange(0, len(words.keys()))
    word = words.keys()[m]
    mean = words[word]
    obj['word'] = word
    obj['mean'] = mean


def send_format_message(formatstr, variablenamesarray):
    def l(obj, eng):
        vars = dict()
        for i in variablenamesarray:
            vars[i] = obj[i]
        print formatstr.format(**vars), " sent to ", eng.getVar('__cust_id')

    return l


def get_user_guess(obj, eng):
    obj['user_guess'] = stdin.readline().strip()


def task_select_random_english_word():
    return select_random_english_word


def task_get_user_guess():
    return get_user_guess

#---------------------------------------
