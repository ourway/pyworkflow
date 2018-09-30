

## Basic Deploy
run web server:
```
	./app.py
```

## Test
To learn better run
```
python tests/test_simple.py
```

------------


## Tutorial

- in the first step you should define a workflow to server 
   to define new workflow call below address using standard HTTP call:
 
```
http POST http://server_address/wf/{workflow name:string}/{workflow version:number}
```

- content must be a json which defines our workflow. for example:

```
http POST http://server_address/wf/my_test_workflow/1
```

- json which sends to server must have below schema:
```
{ 
   	"name" : "workflow name",
	"steps":[
				{type= "taskcall", taskname="taskname to call in this step", params = [parameters to pass to task]}
				...
```

or
				
```
{
	type="eval",
	params = [ ''' string to evaluate ''']
}
				...	
```

### Full example:

```
http POST http://server_address/wf/my_test_workflow/1
```

```

{
        "name":"my_test_workflow",
            "steps":[
                        {
                            "type":"taskcall",
                            "taskname":"test_task_add_two_number",
                            "params":[12,13,"c"]
                        }
                    ]
}

```


this sample defines a simple workflow that add two number. ``test_task_add_two_number`` is a task which defined in our workflow server as below:

```
def test_task_add_two_number(a,b,
					result_var_name):
    	def l(obj,eng):
        	obj[result_var_name]=a+b
    	return l
```

as you see, our function has 3 parameter that pass to it using params section of task call in our json. all tasks must defined to our workflow server

To run this workflow :

```
POST http://server_address/run/{workflow name}/{workflow version}/{customer id}
```
And Body: 

json that initialize workflow variables
	``customer id`` is an identifcation number which specifies this ``wf(workflow)`` instance

in the case of VAS service it is user mobile number that this wf runs for.
to run pervious workflow:
```
http POST http://server_address/run/my_test_workflow/1/242233
```
``Content-Type``: ``application/json``
	
To get variables from workflow after its run we should defines which
variables we need, see below:

```
http POST http://server_address/run/my_test_workflow/1/123232
```
```
	{
		"__rtn_vars__":["c"]
	}
```
	
above says to workflow engine (WE) runs ``my_test_workflow`` for customer id ``123232`` and returns variable ``c``.	as you know c must be ``25`` (12+13)

to improve our understanding see this example:
```
{
	"name":"simple_login"
   "steps":[
      {
	  	 "taskname":"IF_ELSE",
         "type":"taskcall",
         "params":[
				{
				   "type":"eval",
				   "params":[
					  " lambda obj,eng: obj['username']=='gholi' and obj['password']=='gholi' "
				   ]
				},
					{
					   "taskname":"task_exec",
					   "type":"taskcall"
						"params":[
						  "
						  def l(obj,eng):
						  	obj['rtn']= 'hello dear '+obj['username']
							obj['user_login']=True
							",
						  "l"
					   	],
					},
					{
					   "taskname":"task_exec",
					   "type":"taskcall"
					   "params":[
						  "
						  def l(obj,eng):
						  	obj['rtn']='failed to Login'\n    obj['user_login']=False
							",
						  "l"
					   ],
					}
         ],
         
      }
   ],
   
}
```

Explanation:
- this example created by 1 task, it is ``IF_ELSE`` task, ``IF_ELSE`` task has 3 arguments
- first is condition which is a lambda expression to determine ``True`` of ``False``.
- second parameter is list of tasks if condition was ``True``.
 - Thrid parameter is list of tasks if condition was ``False``.

- As you see first parameter of ``IF_ELSE`` task is:

```
 {	
	"type":"eval",
	"params":[
			" lambda obj,eng: obj['username']=='gholi' and obj['password']=='gholi' "
		      ]
}
```
which defines an eval task that compiles to :
```
lambda obj,eng: obj['username']=='gholi' and obj['password']=='gholi'
```
that compare username and password to gholi
and if both of them are gholi returns True else returns ``False``.
	
- the second parameter is (True Branch of IF_ELSE [can be list of tasks]):

```	
{
	"taskname":"task_exec",
	"type":"taskcall",
	"params":[
		'''
		def l(obj,eng):
			obj['rtn']= 'hello dear '
				+obj['username']
			obj['user_login']=True
		''',
		"l"
	],
}
```

it is a task_exec which exec string in server, task_exec has two parameters:
```
task_exec(code_string,function_name_string)
```

code_string can be full Python Module but at final should define a function that has two parameter ``(obj,eng)`` that returns from it.

as you see this Task sets rtn variable of WF to "hello dear {username}" and 
	sets user_login variable to ```True```

to run this WF we call run method using:
```	
POST http://server_address/wf/run/simple_login/1/12344
```

```
	{
		'__rtn_vars__':['rtn','user_login'],
		'username':'gholi',
		'password':'jafar'
	}
```

above call sets username and password variable of workflow to 'gholi' and 'jafar' and 	says to workflow returns rtn,user_login variables from workflow.

----

Sometimes we need call external web-api and interact with them to do this we do below steps:
	1. define web url and its type to server using below call:
```
POST http://server_address/wf/define/task
```

```
{
	"task_name":"task name which use in WF to specifies this web task",
	"task_type":"can be sync or async"
	"url":"url of server method"
}
```

sync tasks wait to get response from server and workflow waits for the result
async tasks halts workflow and wait to call from web server to callbacked

for example:
```
POST http://server_address/wf/define/task
```
```
{
		"task_name":"reg_user",
		"task_type":"sync",
		"url":"http://127.0.0.1:8282/mockservice/user"
}
```

	2. To use in our wf we should define a task as below:
```
{
	"type":"taskcall",
	"taskname":"task_dynamic_task",
    params=[
			"web task name",
			"prefix of return result",
				{
                   web_call_param1:{type='var or value',var_name='variable name' or value = "direct value"},
					 ....
                 }]
}
```

For example:
``` 
{
	type='taskcall',
	taskname='task_dynamic_task',
    params=[
			'reg_user',
			'ru',
			{
               username:{type:'var',var_name:'username'},
               password:{type:'var',var_name:'password'},
               req_date:{type:'value',value:13931413},
               from_service_name:{type:'value',value:'simple test to farsheed!'}
            }
		]
}
```

in this sample WF calls ``reg_user`` web task which defined before and add ``ru`` prefix in the head of its returns json

for example if this web call returns json as below:
```
{userid:12,status:'ok'}
```

the wf add re as prefix to them and add them to wf variables,	``re_userid=12`` and ``re_status='ok'`` added to wf variables

last parameter is a dictionary which pass as parameter to web call
``username`` variable from workflow pass to web call as ``username`` in json body
``password`` variable from wf pass to web-call as ``password`` in json body
``req_date`` as direct value ``13931413`` pass to web-call as ``req_date`` 	and so on.
	
	
	
	
   
   
