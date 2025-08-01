from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'aadi123'


# Get secrets from .env
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_BLOB_CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
        blob_client.upload_blob(file, overwrite=True)
    
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    files = [blob.name for blob in blob_list]
    
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    with open(filename, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    return send_file(filename, as_attachment=True)


@app.route('/delete/<filename>')
def delete_file(filename):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.delete_blob()
    flash(f"File '{filename}' deleted successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
