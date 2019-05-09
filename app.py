"""
Author: Gaurav Dharra
Date: 01/18/2019
Description: Updates file names in the image folder updated and calls an app that renders a web vr of the images
Revision: 03/27/2019
"""
import fnmatch
import shutil, urllib

from flask import Flask, render_template, request, flash, session
from pathlib import Path
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import glob, os

image_list = []
app = Flask(__name__)


app.config['SECRET_KEY'] = 'dev'

temp_map = {}

session_dir = tempfile.TemporaryDirectory(dir='static').name
print(session_dir)



def rename_images(grid_row, grid_column, file_dir):
    """

    :param grid_row:
    :param grid_column:
    :param grid_location:
    :return:
    """
    row_counter = 1
    column_counter = 1
    is_incrementing = True

    image_type = ''
    # print('root, dirs, files', os.walk(folderPath))

    full_session_path = os.path.join(session_dir, file_dir)
    print(full_session_path)

    for root, dirs, files in os.walk(full_session_path):
        
        for filename in files:
            print(filename)
            if filename.endswith('.jpg'):
                image_type = 'jpg'
            elif filename.endswith('.png'):
                image_type = 'png'
            break

    # print('test_image_type', image_type)
    image_extension = '*.' + image_type
    number_of_images_in_extracted_zip = len(fnmatch.filter(os.listdir(full_session_path), image_extension))
    # print('image_extension=',image_extension)
    # print(os.listdir(session_dir))
    # print('number of images',number_of_images_in_extracted_zip)

    if int(grid_row)*int(grid_column) == number_of_images_in_extracted_zip:
        if not(Path(session_dir+"/1_1."+image_type).is_file()):
            for pathAndFilename in glob.iglob(os.path.join(full_session_path, image_extension)):
                title, ext = os.path.splitext(os.path.basename(pathAndFilename))
                # print('path and file name',pathAndFilename)
                # print('Test title and ext',title, ext)
                if row_counter <= int(grid_row):
                    if column_counter <= int(grid_column):
                        os.rename(pathAndFilename,
                                  os.path.join(full_session_path, str(row_counter) + '_' + str(column_counter) + ext))
                    if is_incrementing:
                        if row_counter<int(grid_row):
                            row_counter += 1
                        else:
                            column_counter += 1
                            is_incrementing = False
                            continue
                    else:
                        if row_counter>1:
                            row_counter -= 1
                        else:
                            column_counter += 1
                            is_incrementing = True
                            continue
        return "SUCCESS"
    else:
        return "ERROR"


def create_zip_file(path, ziph):
    # write code here to get zip file
    # print('root, dirs, files',os.walk(path))
    """
    root, dirs, files = os.walk(path)
    print('root=',root[0])
    for file in os.listdir(os.fsencode('static')):
        filename = os.fsdecode(file)
        print('filename=', filename)
        session_id = os.path.split(session_dir)[1]
        print("session_id=", session_id)
        if not filename.endswith('zip') and \
                (filename.find(session_id) >= 0 or
                 filename.find('arrow.png') >= 0 or filename.find('assignImageObject.js') >= 0 or filename.find(
                            'setImage.js') >= 0):
            ziph.write(os.path.join(root[0], file))

    """
    for root, dirs, files in os.walk(path):
        print('root',root)
        print('dirs',dirs)
        session_id = os.path.split(session_dir)[1]
        print("session_id=", session_id)
        for file in files:
            print('file_name= ',file)
            if path == 'static/' and not file.endswith('zip') and \
                    (file.find('arrow.png') >= 0 or file.find('assignImageObject.js') >= 0 or file.find('setImage.js') >= 0
                    or root.find(session_id)>=0):
                ziph.write(os.path.join(root, file))


@app.route("/web_vr", methods=['GET', 'POST'])
def web_vr_page():
    # print('I am somehow here')
    return render_template('WebVR_BuildingTour_FE.html')


@app.route("/", methods=['GET', 'POST'])
def main():
    """

    :return:
    """
    session_id = os.path.split(session_dir)[1]
    print("I am in server")
    print(session_id)

    if request.method == 'POST':
        grid_row = request.form['grid_row']
        grid_column = request.form['grid_column']

        title = request.form['title']
        email = request.form['email']

        message = ''

        if request.form['submit_button'] == 'Preview':
            grid_location = request.files['grid_location']
            # print(grid_row, grid_column, grid_location)
            file_dir = grid_location.filename.split('.')[0]
            try:
                with zipfile.ZipFile(grid_location, "r") as zip_ref:
                    # zip_ref.printdir()
                    # print(zip_ref.infolist())
                    if not(os.path.exists(session_dir)):
                        zip_ref.extractall(path=session_dir)
                    message += rename_images(grid_row, grid_column, file_dir)

                if message == 'ERROR':
                    flash('The grid size does not match the number of images in the zip folder. '
                          'Please check the grid size and resubmit.', category='danger')
                    return render_template('WebVR_BuildingTour_FE.html',
                                           title=title,
                                           email=email,
                                           grid_row=grid_row,
                                           grid_column=grid_column,
                                           grid_location=os.path.join(session_dir, file_dir))

            except Exception as e:
                print('Exception: ' + str(e))
                return render_template('Success_Page.html', category = 'danger',
                                       html_to_display='<h1>There was an error extracting the zip file!</h1>',
                                       )

            return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                   path=os.path.join(session_dir, file_dir), image_type=str('jpg'),
                                   title=title, email=email, is_file_ready='No', file_location='')

        elif request.form['submit_button'] == 'Download':
            # print("I am in download")
            grid_location = request.form['grid_location']
            filename = grid_location
            try:
                zipf = zipfile.ZipFile('static/'+session_id+'_result.zip', 'w', zipfile.ZIP_DEFLATED)
                create_zip_file('static/', zipf)
                html = render_template('index3.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                       path=''+str(filename), image_type=str('jpg'), title=''+str(title))
                html_file = open(os.path.join('static', 'index_'+session_id+'.html'), "w")
                html_file.write(html)
                html_file.close()
                zipf.write(os.path.join('static','index_'+session_id+'.html'), 'index.html')
                zipf.close()

                file_path = request.url_root + 'static/' + session_id + '_result.zip'
                file_name = filename + '_result'

                """with urllib.request.urlopen(file_path) as response, open(file_name, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)"""

                for file in os.listdir(os.fsencode('static')):
                    filename = os.fsdecode(file)
                    if filename.find(session_id) > 0:
                        print('filename=', filename)
                        path = filename
                        if os.path.exists(os.path.join('static', path)):
                            if path.find('.zip') >= 0 or path.find('.html') >= 0:
                                os.unlink(os.path.join('static', path))
                            else:
                                shutil.rmtree(os.path.join('static', path))

                """return render_template('WebVR_BuildingTour_FE.html')"""

                """return file_path"""

                return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                       path=grid_location, image_type=str('jpg'),
                                       title=title, email=email,
                                       is_file_ready='Yes', file_location=file_path
                                       )

            except Exception as e:
                zipf.close()
                for file in os.listdir(os.fsencode('static')):
                    filename = os.fsdecode(file)
                    print('filename=', filename)
                    if filename.find(session_id) >= 0:
                        print('filename=', filename)
                        path = filename
                        if os.path.exists(os.path.join('static', path)):
                            if path.find('.zip') >= 0 or path.find('.html') >= 0:
                                os.unlink(os.path.join('static', path))
                            else:
                                shutil.rmtree(os.path.join('static', path))
                return render_template('Success_Page.html', category = 'danger',
                                       html_to_display='<h1>There was an error generating the zip file!</h1>' + str(e),
                                       )
    else:
        print('I am in get request')
        for file in os.listdir(os.fsencode('static')):
            filename = os.fsdecode(file)
            print('filename=', filename)
            if filename.find(session_id) >= 0:
                print('filename=', filename)
                path = filename
                if os.path.exists(os.path.join('static', path)):
                    if path.find('.zip') >= 0 or path.find('.html') >= 0:
                        os.unlink(os.path.join('static', path))
                    else:
                        shutil.rmtree(os.path.join('static', path))
        return render_template('WebVR_BuildingTour_FE.html')


def before_request():
    app.jinja_env.cache = {}


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.before_request(before_request)
    temp_map={}
    app.run(debug=True, use_reloader = True)
