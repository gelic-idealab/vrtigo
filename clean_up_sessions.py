from apscheduler.schedulers.blocking import BlockingScheduler
import os, time, json, shutil
from datetime import datetime, timedelta
from dateutil import parser

from app import SESSION_TRACKER

def delete_session_files():
    if os.path.exists(os.path.join(os.getcwd(), SESSION_TRACKER)):
        files_to_be_deleted = []
        with open(os.path.join(os.getcwd(), SESSION_TRACKER), 'r+') as json_file:
            session = json.load(json_file)
            for each_session in session:
                if os.path.exists(os.path.join(os.getcwd(), 'static', each_session)) and parser.parse(session[each_session]['created_time']) < datetime.now() - timedelta(hours=1):
                    files_to_be_deleted.append(each_session)


    print(os.listdir(os.path.join(os.getcwd(),'static')))

    for each_file in os.listdir(os.path.join(os.getcwd(),'static')):
        if each_file in files_to_be_deleted:
            shutil.rmtree(os.path.join(os.getcwd(),'static',each_file))
            if os.path.exists(os.path.join(os.getcwd(), 'static', each_file+'.zip')):
                os.remove(os.path.join(os.getcwd(),'static', each_file+'.zip'))


scheduler = BlockingScheduler()
scheduler.add_job(delete_session_files, 'interval', minutes=1)
scheduler.start()

