__author__ = 'msd'
from workflow.patterns.controlflow import *

from msdworkflow import msd_workflow
from tasks.wf_tasks import *
import msd_wf_storage as storage
import json

our_workflows = {'eng_lang': [
    send_sms('Hello Dear Friend'),
    send_sms('This is Only Test'),
    sleep_for_seconds(12),
    send_sms('hi, im waked up ...'),
    send_sms('lets go to learn english words'),
    select_random_english_word,
    send_format_message(
        'do u know meaning of {word}? it is {mean}', ['word', 'mean']),
    sleep_for_seconds(3600),
    send_format_message('Oh! What is {word} meaning?', ['word']),
    get_user_guess,
    IF_ELSE(lambda obj, eng: obj['user_guess'] == obj['mean'],
            send_sms('congratulation'),
            send_sms('it was wrong. finish')
            )

]}


def get_workflow_status(wfname, wfversion, custid):
    wf_name = wfname + "." + wfversion
    key_name = get_key_name(wf_name, custid)
    if not storage.exists(key_name):
        raise wf_workflow_instance_not_exists()
    wf_instance = storage.get(key_name)
    wf = msd_workflow.deserialize_workflow(wf_instance, get_workflow_by_name)
    return dict(index=wf._i, variables=wf._objects[0])


def _compile_taskcalls(arr):
    final_array = []
    for i in arr:
        if isinstance(i, dict):
            if 'type' in i and i['type'] == 'taskcall':
                params = _compile_taskcalls(i['params'])
                method = globals()[i['taskname']]
                res = method(*params)
                final_array.append(res)
            elif 'type' in i and i['type'] == 'eval':
                final_array.append(eval(i['params'][0]))
            else:
                final_array.append(i)

        elif isinstance(i, list):
            final_array.append(_compile_taskcalls(i))

        else:
            final_array.append(i)
    return final_array


def compile_dict_to_workflow(steps_array):
    steps = _compile_taskcalls(steps_array)
    return steps
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


def run_workflow_(wf_fullname, cust_id, custom_vars, rtn_var_names):
    '''

    :param wf_fullname: string -- workflow fullname which maked by workflow name and its version
    :param cust_id: string -- customer id which this workflow runs for. (in new workflow)
    :param custom_vars: dict -- dictionary specifies variables in workflow in the case of new workflow they are
                            initialize variables and in the case of existing workflow it overwrites exist variables
                            in the workflow
    :param rtn_var_names: array of string -- array of varaible name which at the end of workflow execution should return.
    :return: dict -- dictionary of variables and their values specified in rtn_var_names
    '''

    wf_instace_name = get_key_name(wf_fullname, cust_id)
    if not storage.exists(wf_instace_name):
        # user in progress continue its processing
        return run_new_wf(wf_fullname, cust_id, custom_vars, rtn_var_names)
    else:
        # user is new
        return continue_wf(wf_fullname, cust_id, custom_vars, rtn_var_names)


def run_workflow(wf_name, wf_version, cust_id, custom_vars, rtn_var_names):
    '''

    :param wf_name: string -- workflow name
    :param wf_version: string -- workflow version
    :param cust_id: string -- cutomer id which this workflow runs for
    :param custom_vars: dict -- dictionary specifies variables in workflow in the case of new workflow they are
                            initialize variables and in the case of existing workflow it overwrites exist variables
                            in the workflow
    :param rtn_var_names: array of string -- array of varaible name which at the end of workflow execution should return.
    :return: dict -- dictionary of variables and their values specified in rtn_var_names
    '''
    wf_fullname = wf_name + '.' + wf_version
    return run_workflow_(wf_fullname, cust_id, custom_vars, rtn_var_names)


def get_workflow_by_name(wf_name):
    if storage.exists(wf_name):
        js = json.loads(storage.get(wf_name))
        return compile_dict_to_workflow(js)
    else:
        return []


def get_key_name(wf_name, custid):
    name = "{wf}.{custid}".format(wf=wf_name, custid=custid)
    print name
    return name


class wf_workflow_instance_not_exists(Exception):
    pass


def continue_wf(wf_name, cust_id, custom_vars, rtn_var_names):
    '''

    :param wf_name: string -- specifies full name of workflow to continue
    :param cust_id: string -- customer id who this workflow runs for
    :param custom_vars: dict -- dictionary of variable names to overwrite current variables in workflow
    :param rtn_var_names: array of string -- array of variable names which should return at the end of workflow run
    :return: return dictionary of variables and their values which specified in rtn_var_names
    '''
    key_name = get_key_name(wf_name, cust_id)
    if not storage.exists(key_name):
        raise wf_workflow_instance_not_exists()
    wf_instance = storage.get(key_name)
    wf = msd_workflow.deserialize_workflow(wf_instance, get_workflow_by_name)
    if(custom_vars is not None and isinstance(wf._objects[0], dict) and isinstance(custom_vars, dict)):
        wf._objects[0].update(custom_vars)

    is_finished = wf.continue_process()
    after_run_wf(wf, is_finished)
    return wf.get_variables(rtn_var_names)


def run_new_wf(wf_name, usermob, init_obj, rtn_var_names):
    '''

    :param wf_name: string -- specifies workflow name to run
    :param usermob: string -- customer id which this workflow runs for
    :param init_obj: dict -- dictionary of variables to initialize variables of workflow with
    :param rtn_var_names: array of string -- the variables should return after execution of workflow
    :return: dict -- return variable names specified in rtn_var_names
    '''
    wf = msd_workflow(wf_name, get_workflow_by_name)
    wf.setVar('__cust_id', usermob)
    if(init_obj is None):
        init_obj = {}
    is_finished = wf.start(init_obj)
    after_run_wf(wf, is_finished)
    return wf.get_variables(rtn_var_names)


def after_run_wf(wf, is_finished):
    wf_instace_key = get_key_name(wf._process_name, wf.getVar(
        '__cust_id'))  # wf._process_name+'_'+wf.getVar('usermob')
    if not is_finished:
        # save wf and to further run
        tmp = wf.serialize_workflow()
        storage.store(wf_instace_key, tmp)
    else:
        # delete file
        storage.remove(wf_instace_key)


if __name__ == '__main__':
    k = compile_dict_to_workflow([])
    our_workflows['eng_lang'] = k
    run_workflow('eng_lang', 'test')
