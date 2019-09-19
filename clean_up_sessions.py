from apscheduler.schedulers.blocking import BlockingScheduler
import os, time, json, shutil
from datetime import datetime, timedelta
from dateutil import parser


def delete_session_files():
    if os.path.exists(os.path.join(os.getcwd(), 'session_tracker')):
        files_to_be_deleted = []
        with open(os.path.join(os.getcwd(), 'session_tracker'), 'r+') as json_file:
            session = json.load(json_file)
            for each_session in session:
                if datetime.now() - timedelta(hours=2) < parser.parse(session[each_session]['created_time']) < datetime.now() - timedelta(hours=1):
                    files_to_be_deleted.append(each_session)

        json_file.close()

    print(os.listdir(os.path.join(os.getcwd(),'static')))

    for each_file in os.listdir(os.path.join(os.getcwd(),'static')):
        if each_file in files_to_be_deleted:
            shutil.rmtree(os.path.join(os.getcwd(),'static',each_file))
        if each_file.replace('.zip', '') in files_to_be_deleted:
            os.remove(os.path.join(os.getcwd(),'static', each_file))


scheduler = BlockingScheduler()
scheduler.add_job(delete_session_files, 'interval', hours=1)
scheduler.start()
