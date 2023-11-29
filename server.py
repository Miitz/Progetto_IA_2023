import os
import io
import zipfile
import tempfile
import shutil
from analizzatore_hrx import * 
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/generate_zip', methods=['POST'])
def generate_zip():
    try:
        hrc_file = request.files.get('hrc')

        if hrc_file and hrc_file.filename.endswith('.hrc'):
           
            temp_dir = tempfile.mkdtemp()
            file_name = os.path.splitext(hrc_file.filename)[0]
            
            temp_hrc_path = os.path.join(temp_dir, hrc_file.filename)
            hrc_file.save(temp_hrc_path)
            stanze = componitore_elementi(temp_hrc_path)
            json_path = os.path.join('.',stanze[0])
            immagine_path = os.path.join('/home/miitz/Immagini/Server/', stanze[1])
            zip_data = io.BytesIO()

            with zipfile.ZipFile(zip_data, 'w') as zipf:
                zipf.write(json_path, os.path.basename(json_path))
                zipf.write(immagine_path, os.path.basename(immagine_path))
           
            zip_data.seek(0)

            
            response = send_file(
                zip_data,
                mimetype='application/zip',
                as_attachment=True,
                download_name='files.zip'
            )

            
            shutil.rmtree(temp_dir)

            return response
        else:
            return 'File .hrc non valido', 400

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=6000)
