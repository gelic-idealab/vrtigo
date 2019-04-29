"""
Author: Gaurav Dharra
Date: 01/18/2019
Description: Updates file names in the image folder updated and calls an app that renders a web vr of the images
Revision: 03/27/2019
"""
import fnmatch
import shutil

from flask import Flask, render_template, request, flash
from pathlib import Path
from werkzeug.utils import secure_filename
import zipfile
import glob, os

image_list = []
app = Flask(__name__)


app.config['SECRET_KEY'] = 'dev'

temp_map = {}

def rename_images(grid_row, grid_column, grid_location):
    """

    :param grid_row:
    :param grid_column:
    :param grid_location:
    :return:
    """
    row_counter = 1
    column_counter = 1
    is_incrementing = True
    folderPath = os.path.join('static', grid_location)

    image_type = ''
    # print('root, dirs, files', os.walk(folderPath))

    for root, dirs, files in os.walk(folderPath):
        for filename in files:
            print(filename)
            if filename.endswith('.jpg'):
                image_type = 'jpg'
            elif filename.endswith('.png'):
                image_type = 'png'
            break

    # print('test_image_type', image_type)
    image_extension = '*.' + image_type
    number_of_images_in_extracted_zip = len(fnmatch.filter(os.listdir(folderPath), image_extension))
    # print('image_extension=',image_extension)
    # print(os.listdir(folderPath))
    # print('number of images',number_of_images_in_extracted_zip)

    if int(grid_row)*int(grid_column) == number_of_images_in_extracted_zip:
        if not(Path(folderPath+"/1_1."+image_type).is_file()):
            for pathAndFilename in glob.iglob(os.path.join(folderPath, image_extension)):
                title, ext = os.path.splitext(os.path.basename(pathAndFilename))
                # print('path and file name',pathAndFilename)
                # print('Test title and ext',title, ext)
                if row_counter <= int(grid_row):
                    if column_counter <= int(grid_column):
                        os.rename(pathAndFilename,
                                  os.path.join(folderPath, str(row_counter) + '_' + str(column_counter) + ext))
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
    for root, dirs, files in os.walk(path):
        # print('root',root)
        # print('dirs',dirs)
        for file in files:
            if path == 'static/' and not file.endswith('zip'):
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

    if request.method == 'POST':
        # print('I am here')

        # Then get the data from the form

        # print('request',request)
        # print('request form', request.form)

        if request.form['submit_button'] == 'delete':
            for file in os.listdir(os.fsencode('static')):
                filename = os.fsdecode(file)
                # print('filename=', filename)
                if filename.find('arrow.png') < 0 and filename.find('assignImageObject.js') < 0 and filename.find(
                        'setImage.js') < 0:
                    path = filename
                    if os.path.exists(os.path.join('static', path)):
                        if path.find('.zip') >= 0 or path.find('.html') >= 0:
                            os.unlink(os.path.join('static', path))
                        else:
                            shutil.rmtree(os.path.join('static', path))
            return render_template('WebVR_BuildingTour_FE.html')
            """
            path = request.form['path']
            print('path=', path)
            shutil.rmtree(os.path.join('static', path))
            os.unlink(os.path.join('static', path + '_result.zip'))
            os.unlink(os.path.join('static', 'generated_html_'+path + '.html'))
            return render_template('WebVR_BuildingTour_FE.html')
            """
        else:
            grid_row = request.form['grid_row']
            grid_column = request.form['grid_column']

            title = request.form['title']
            email = request.form['email']

            message = ''

            if request.form['submit_button'] == 'Preview':
                grid_location = request.files['grid_location']
                print(grid_row, grid_column, grid_location)
                try:
                    with zipfile.ZipFile(grid_location, "r") as zip_ref:
                        zip_ref.printdir()
                        print(zip_ref.infolist())
                        if not(os.path.exists(os.path.join('static', grid_location.filename.split('.')[0]))):
                            zip_ref.extractall(path='static/')
                        message += rename_images(grid_row, grid_column, grid_location.filename.split('.')[0])

                    if message == 'ERROR':
                        flash('The grid size does not match the number of images in the zip folder. '
                              'Please check the grid size and resubmit.', category='danger')
                        return render_template('WebVR_BuildingTour_FE.html',
                                               title=title,
                                               email=email,
                                               grid_row=grid_row,
                                               grid_column=grid_column,
                                               grid_location=grid_location)

                except Exception as e:
                    # print('Exception: ' + str(e))
                    return render_template('Success_Page.html', category = 'danger',
                                           html_to_display='<h1>There was an error extracting the zip file!</h1>',
                                           )

                return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                       path=''+str(grid_location.filename.split('.')[0]), image_type=str('jpg'),
                                       title=title, email=email)

            elif request.form['submit_button'] == 'Download':
                # print("I am in download")
                grid_location = request.form['grid_location']
                filename = grid_location
                try:
                    zipf = zipfile.ZipFile('static/'+filename+'_result.zip', 'w', zipfile.ZIP_DEFLATED)
                    create_zip_file('static/', zipf)
                    html = render_template('index3.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                           path=''+str(filename), image_type=str('jpg'), title=''+str(title))
                    html_file = open(os.path.join('static', 'index.html'), "w")
                    html_file.write(html)
                    html_file.close()
                    zipf.write(os.path.join('static','index.html'), 'index.html')
                    zipf.close()

                    file_path = request.url_root + 'static/' + grid_location + '_result.zip'
                    file_name = filename + '_result'

                    return render_template('index2.html', category = 'success', numberOfRows=grid_row, numberOfCol=grid_column,
                                           path=filename, image_type=str('jpg'),
                                           title=title, email=email,
                                           html_to_display='<h1>Web VR Tour zip file successfully generated! '
                                                           'Click <a id="message" href="'+file_path+'" '
                                                           'download="'+file_name+'">here</a> to download!</h1>'
                                           )

                except Exception as e:
                    return render_template('Success_Page.html', category = 'danger',
                                           html_to_display='<h1>There was an error generating the zip file!</h1>',
                                           )
    else:
        return render_template('WebVR_BuildingTour_FE.html')


def before_request():
    app.jinja_env.cache = {}


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.before_request(before_request)
    temp_map={}
    app.run(debug=True, use_reloader = True)
