from random import randrange

__author__ = 'msd'
from sys import stdin
from msdworkflow import msd_workflow
import workflow.patterns as wp


import os.path
import os


#---------- TASK DEFINITIONS
def send_sms(message):
    def l(obj, eng):
        print message, " sent to ", eng.getVar('usermob')
    return l


def sleep_for_seconds(seconds):
    def l(obj, eng):
        print "[SYSMSG]run this process after ", seconds, "(s),again and fill input fields by these values:"
        print "User Mobile Number:", eng.getVar('usermob')
        print "Workflow Name:", eng._process_name
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
        print formatstr.format(**vars), " sent to ", eng.getVar('usermob')
    return l


def get_user_guess(obj, eng):
    obj['user_guess'] = stdin.readline().strip()
#---------------------------------------

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
    wp.IF_ELSE(lambda obj, eng:obj['user_guess'] == obj['mean'],
               send_sms('congratulation'),
               send_sms('it was wrong. finish')
               )

]}


def get_workflow_by_name(wf_name):
    return our_workflows[wf_name]


def main():
    print "Enter User Mobile Number:"
    usermobile = stdin.readline().strip()
    print "Enter Flow Name (if dont know any thing pls enter eng_lang):"
    wf_name = stdin.readline().strip()
    file_name = wf_name + '_' + usermobile
    if not os.path.exists(file_name):
        # user in progress continue its processing
        run_new_wf(wf_name, usermobile)
    else:
        #user is new
        continue_wf(wf_name, usermobile)


def continue_wf(wf_name, usermob):
    file_name = wf_name + '_' + usermob
    f = open(file_name, 'rb')
    file_content = f.read()
    f.close()
    wf = msd_workflow.deserialize_workflow(file_content, get_workflow_by_name)
    is_finished = wf.continue_process()
    after_run_wf(wf, is_finished)


def run_new_wf(wf_name, usermob):
    wf = msd_workflow(wf_name, get_workflow_by_name)
    wf.setVar('usermob', usermob)
    is_finished = wf.start({'word': None, 'mean': None})
    after_run_wf(wf, is_finished)


def after_run_wf(wf, is_finished):
    filename = wf._process_name + '_' + wf.getVar('usermob')
    if not is_finished:
        # save wf and to further run
        tmp = wf.serialize_workflow()
        f = open(filename, 'wb')
        f.write(tmp)
        f.close()
    else:
        # delete file
        os.remove(filename)


if __name__ == '__main__':
    main()
