# from celery import Celery
# import requests
# app = Celery(broker='redis://localhost/')
#
#
# @app.task
# def add(x, y):
#     return x + y
#
#
# @app.task
# def celery_execute_workflow_(wf_fullname, cust_id):
#     requests.post('http://localhost:8181/wf/run/{wf_name}/{cust_id}'.format(
#         wf_name=wf_fullname, cust_id=cust_id), data={})
