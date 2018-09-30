#!/usr/bin/env python


import json

from bottle import run, post, request, get

from engine.msd_workflow_interface import run_workflow, compile_dict_to_workflow, run_workflow_, get_workflow_status
import engine.msd_wf_storage as storage


@post('/wf/<wfname>/<wf_version>/<custid>/status')
def get_status(wfname, wf_version, custid):
    return get_workflow_status(wfname, wf_version, custid)


@post('/wf/run/<wf_fullname>/<custid>')
def do_workflow_(wf_fullname, custid):
    rtn_var_names = []
    if '__rtn_vars__' in request.json:
        rtn_var_names = request.json.pop('__rtn_vars__')
    return run_workflow_(wf_fullname, custid, request.json, rtn_var_names)


@post('/wf/run/<wfname>/<wf_version>/<custid>')
def do_workflow(wfname, wf_version, custid):
    rtn_var_names = []
    if '__rtn_vars__' in request.json:
        rtn_var_names = request.json.pop('__rtn_vars__')
    return run_workflow(wfname, wf_version, custid, request.json, rtn_var_names)


@post('/wf/<wf_name>/<wf_version>')
def create_workflow(wf_name, wf_version):
    try:
        js = request.json['steps']
        compile_dict_to_workflow(js)
        storage.store(wf_name + "." + wf_version, json.dumps(js))
        return json.dumps(js)
    except TypeError as e:
        print e
        raise e


@post('/wf/task/define')
def define_dynamic_task():
    """
    define new task as below:
    {
        "task_name":"Task Name",
        "task_type":"sync or async",
        "url":"http://url.hostname.ext/path",

    }
    """
    storage.store('dynamic_task:{task_name}'.format(
        task_name=request.json['task_name']
    ), json.dumps(request.json))


@get('/wf/task/define/<taskname>')
def get_define_task_name(taskname):
    return storage.get('dynamic_task:{task_name}'.format(task_name=taskname))


@post('/wf/async_task_result/<wf_fullname>/<cust_id>/<prefix>')
def continue_async_dynamic_task(wf_fullname, cust_id, prefix):

    if hasattr(request, 'json') and request.json is not None:
        cor_dic = {"{RVP}_{KEY}".format(RVP=prefix, KEY=key): value for (
            key, value) in request.json.iteritems()}
    else:
        cor_dic = {}
    run_workflow_(wf_fullname, cust_id, cor_dic, [])

run(host='localhost', port=8181)
