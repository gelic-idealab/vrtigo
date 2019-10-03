"""
Author: Gaurav Dharra
Date: 01/18/2019
Description: Updates file names in the image folder updated and calls an app that renders a web vr of the images
Revision: 03/27/2019
Revision 2:
Data: 09/14/2019
Integrating with vrticl
"""
import fnmatch
import shutil, urllib

from flask import Flask, render_template, request, redirect
import aframetour.aframetour as aft
import os, urllib, logging, json
from datetime import datetime

image_list = []
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

app.config['SECRET_KEY'] = 'dev'

SESSION_TRACKER = 'session_tracker.json'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


@app.route('/<string:session_id>', methods=['GET'])
def session_preview(session_id):
    
    return app.send_static_file(session_id+'/index.html', session_id=session_id)

@app.route("/", methods=['GET', 'POST'])
def main():
    print(request.method)
    if request.method == 'POST':
        try:
            print("I am in post request")
            grid_row = int(request.form['grid_row'])
            grid_column = int(request.form['grid_column'])

            title = request.form['title']
            email = request.form['email']
            session_id = ''
            message = ''

            if request.form['submit_button'] == 'Preview':
                grid_location = request.files['grid_location']
                message, session_id = aft.generate_package_web_tour(grid_location, title, grid_row, grid_column, 'static')
                print('returned value = {} {}'.format(message, session_id))
                if os.path.exists(os.path.join(os.getcwd(), SESSION_TRACKER)):
                    with open(os.path.join(os.getcwd(), SESSION_TRACKER), 'r+') as json_file:
                        session = json.load(json_file)
                        print(session)
                        session[str(session_id)] = {}
                        session[str(session_id)]['created_time'] = str(
                            datetime.fromtimestamp(os.path.getctime(os.path.join('static', str(session_id)))))
                        json.dump(session, json_file)
                        json_file.seek(0)
                        json.dump(session, json_file)
                        json_file.truncate()
                    # json_file.close()

                else:
                    with open(SESSION_TRACKER, 'w+') as json_file:
                        session = {}
                        session[str(session_id)] = {}
                        session[str(session_id)]['created_time'] = str(datetime.fromtimestamp(os.path.getctime(os.path.join('static', str(session_id)))))
                        json.dump(session, json_file)
                    # json_file.close()

                # if message == '':
                    # print(os.path.join(os.getcwd(), 'static', str(session_id), 'index.html'))
                return redirect("/"+str(session_id))
                    # # return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                    #                        path=os.path.join('static', str(session_id), 'static', 'images'),
                    #                        image_type=str('jpg'),
                    #                        title=title, email=email, is_file_ready='No', file_location='')
                # else:
                #     return render_template('Success_Page.html', category='danger',
                #                            html_to_display='<h1>'+message+'</h1>',
                #                            )
            elif request.form['submit_button'] == 'Download':
                grid_location = request.form['grid_location']
                filename = grid_location
                session_id = filename.split('\\')[1]
                return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                        path=grid_location, image_type=str('jpg'),
                                        title=title, email=email,
                                        is_file_ready='Yes', file_location=os.path.join('static', str(session_id)+'.zip')
                                        )
        except Exception as err:
            logging.error(str(err))
            print('Error = ', str(err))
            return None

    else:
        return render_template('WebVR_BuildingTour_FE.html')



@app.route("/web_vr", methods=['GET', 'POST'])
def web_vr_page():
    return render_template('WebVR_BuildingTour_FE.html')


def before_request():
    app.jinja_env.cache = {}


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.before_request(before_request)
    temp_map={}
    app.run(debug=True, use_reloader = True)
