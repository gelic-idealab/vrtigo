"""
Author: Gaurav Dharra
Date: 01/18/2019
Description: Updates file names in the image folder updated and calls an app that renders a web vr of the images
Revision: 02/12/2019
"""
import fnmatch

from flask import Flask, render_template, request
from pathlib import Path
from werkzeug.utils import secure_filename
import zipfile
import glob, os

image_list = []
app = Flask(__name__)


def rename_images(grid_row, grid_column, grid_location, image_type):
    """

    :param grid_row:
    :param grid_column:
    :param grid_location:
    :param image_type:
    :return:
    """
    row_counter = 1
    column_counter = 1
    is_incrementing = True
    is_decrementing = False
    folderPath = 'static/'+grid_location
    image_extentsion= '*.'+image_type
    test_image_type=''

    print(image_extentsion)
    print(type(image_extentsion))
    print(type(image_type))
    print(len(fnmatch.filter(os.listdir(folderPath), image_extentsion)))
    print('root, dirs, files', os.walk(folderPath))

    for root, dirs, files in os.walk(folderPath):
        for filename in files:
            print(filename)
            if filename.endswith('.jpg'):
                test_image_type = 'jpg'
            elif filename.endswith('.png'):
                test_image_type = 'png'
            break

    print('test_image_type', test_image_type)

    if int(grid_row)*int(grid_column) <= len(fnmatch.filter(os.listdir(folderPath), image_extentsion)):
        if not(Path(folderPath+"/1_1."+image_type).is_file()):
            for pathAndFilename in glob.iglob(os.path.join(folderPath, image_extentsion)):
                title, ext = os.path.splitext(os.path.basename(pathAndFilename))
                print(pathAndFilename)
                print(title, ext)
                if row_counter <= int(grid_row):
                    if column_counter <= int(grid_column):
                        os.rename(pathAndFilename,
                                  os.path.join(folderPath, str(row_counter) + '_' + str(column_counter) + ext))
                    if is_incrementing:
                        if row_counter<int(grid_row):
                            row_counter += 1
                        else:
                            column_counter += 1
                            is_decrementing = True
                            is_incrementing = False
                            continue
                    if is_decrementing:
                        if row_counter>1:
                            row_counter -= 1
                        else:
                            column_counter += 1
                            is_incrementing = True
                            is_decrementing = False
                            continue
    else:
        print("please check the grid size")


def create_zip_file(path, ziph):
    # write code here to get zip file
    print('root, dirs, files',os.walk(path))
    for root, dirs, files in os.walk(path):
        print('root',root)
        print('dirs',dirs)
        for file in files:
            if (path == 'static/' and not file.endswith('zip')):
                ziph.write(os.path.join(root, file))


@app.route("/", methods=['GET', 'POST'])
def main():
    """

    :return:
    """
    if request.method == 'POST':
        print('I am here')
        # Then get the data from the form
        grid_row = request.form['grid_row']
        grid_column = request.form['grid_column']
        grid_location = request.files['grid_location']
        print(grid_row, grid_column, grid_location)
        title = request.form['title']
        email = request.form['email']
        print(grid_row, grid_column, grid_location, title, email)

        print(secure_filename(grid_location.filename))

        with zipfile.ZipFile(grid_location, "r") as zip_ref:
            zip_ref.printdir()
            print(zip_ref.infolist())
            if not(os.path.exists("static/"+grid_location.filename.split('.')[0])):
                zip_ref.extractall("static/"+grid_location.filename.split('.')[0])
                rename_images(grid_row, grid_column, grid_location.filename.split('.')[0], 'jpg')

        if request.form['submit_button'] == 'Preview':
            return render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                   path=''+str(grid_location.filename.split('.')[0]), image_type=str('jpg'))

        elif request.form['submit_button'] == 'Download':
            try:
                zipf = zipfile.ZipFile('static/'+grid_location.filename.split('.')[0]+'_result.zip', 'w', zipfile.ZIP_DEFLATED)
                create_zip_file('static/', zipf)
                html = render_template('index2.html', numberOfRows=grid_row, numberOfCol=grid_column,
                                       path=''+str(grid_location.filename.split('.')[0]), image_type=str('jpg'))
                html_file = open(os.path.join('static/','generated_html_'+str(grid_location.filename.split('.')[0])+'.html'),"w")
                html_file.write(html)
                html_file.close()
                zipf.write('static/generated_html_'+str(grid_location.filename.split('.')[0])+'.html', 'generated_html_'+str(grid_location.filename.split('.')[0])+'.html')
                zipf.close()

                return render_template('Success_Page.html',
                                       file_path=request.url_root+'static/'+grid_location.filename.split('.')[0] +
                                       '_result.zip',
                                       file_name=grid_location.filename.split('.')[0]+'_result')
            except:
                print('There was an error generating the zip file')
    else:
        return render_template('WebVR_BuildingTour_FE.html')


def before_request():
    app.jinja_env.cache = {}


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.before_request(before_request)
    app.run(debug=True, use_reloader =False)
