import logging

__author__ = 'msd'
from workflow.engine import GenericWorkflowEngine, HaltProcessing
from pickle import loads, dumps


class msd_workflow(GenericWorkflowEngine):

    def __init__(self, process_name, retrive_process_callback, processing_factory=None, callback_chooser=None,
                 before_processing=None, after_processing=None):

        super(msd_workflow, self).__init__(processing_factory, callback_chooser,
                                           before_processing, after_processing)

        if(retrive_process_callback):
            self.setWorkflow(retrive_process_callback(process_name))
            self._process_name = process_name

    def serialize_workflow(self):
        a = self.__getstate__()
        a.pop('log')
        a['_msd_process_name'] = self._process_name
        return dumps(a)

    def start(self, init_object):

        try:
            super(msd_workflow, self).process([init_object])
        except HaltProcessing:
            return False  # process not finished

        return True  # process finished

    def get_variables(self, arr_var_names):
        '''

        :param arr_var_names: array of string -- variable names to return from workflow
        :return: dict -- dictionary of variable and its value
        '''
        rtn = dict()
        varnames = arr_var_names or []

        for i in varnames:
            if i in self._objects[0]:
                rtn[i] = self._objects[0][i]
            else:
                rtn[i] = None
        return rtn

    def continue_process(self):
        try:
            self.restart('current', 'next')
        except HaltProcessing:
            return False  # process not finished
        return True  # process finished

    @classmethod
    def deserialize_workflow(cls, str_workflow, retrive_process_callback):
        des = loads(str_workflow)
        wname = des.pop('_msd_process_name')
        w = msd_workflow(wname, retrive_process_callback)
        des['log'] = logging.getLogger('msdtest')
        des['_callbacks'] = w._callbacks
        w.__setstate__(des)
        return w

    @staticmethod
    def after_processing(objects, self):
        # overrides standard post-processing callback
        pass
        # """Standard post-processing callback, basic cleaning."""

        # self._objects = []
        # self._i = [-1, [0]]
