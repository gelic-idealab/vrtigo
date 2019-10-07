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


@app.route("/", methods=['GET', 'POST'])
def main():
    print(request.method)
    if request.method == 'POST':
        try:
            # get tour params from form
            grid_row = int(request.form['grid_row'])
            grid_column = int(request.form['grid_column'])
            title = request.form['title']
            email = request.form['email']
            session_id = ''
            message = ''

            if request.form['submit_button'] == 'Generate Tour':
                grid_location = request.files['grid_location']
                # use aframtour library to generate package: returns success/fail message, image extension value, and a session id
                message, img_ext, session_id = aft.generate_package_web_tour(grid_location, title, grid_row, grid_column, 'static')
                print('generate_package_web_tour returned:', message, img_ext, session_id) 
                
                # if no error message, set tour_generated flag, redirect back to form page with pre-loaded params
                if message == '':

                    # log session to session_tracker.json, create file if necessary
                    if os.path.exists(os.path.join(os.getcwd(), SESSION_TRACKER)):
                        with open(os.path.join(os.getcwd(), SESSION_TRACKER), 'r+') as json_file:
                            session = json.load(json_file)
                            session[str(session_id)] = {}
                            session[str(session_id)]['created_time'] = str(
                                datetime.fromtimestamp(os.path.getctime(os.path.join('static', str(session_id)))))
                            json.dump(session, json_file)
                            json_file.seek(0)
                            json.dump(session, json_file)
                            json_file.truncate()
                    else:
                        with open(SESSION_TRACKER, 'w+') as json_file:
                            session = {}
                            session[str(session_id)] = {}
                            session[str(session_id)]['created_time'] = str(datetime.fromtimestamp(os.path.getctime(os.path.join('static', str(session_id)))))
                            json.dump(session, json_file)

                    tour_generated = True
                    return render_template(
                        'WebVR_BuildingTour_FE.html', 
                        tour_generated=tour_generated, 
                        session_id=session_id,
                        title=title,
                        email=email,
                        grid_row=grid_row, 
                        grid_column=grid_column)
                
                # if error message, return error message to render on form page
                else:
                    raise Exception(message)

        except Exception as err:
            logging.error(str(err))
            error = str(err)
            return render_template(
                'WebVR_BuildingTour_FE.html', 
                error=error,
                tour_generated=False, 
                session_id=session_id,
                title=title,
                email=email,
                grid_row=grid_row, 
                grid_column=grid_column)

    # if request method is not POST
    else:
        return render_template('WebVR_BuildingTour_FE.html', tour_generated=False)


def before_request():
    app.jinja_env.cache = {}


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.before_request(before_request)
    temp_map={}
    app.run(debug=True, use_reloader = True)
