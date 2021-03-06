from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

import os
import pika

connection = None
channel = None
queue_name = os.environ.get('RABBITMQ_CHANNEL')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)

# from http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/resize', methods=['POST'])
def resize():
    global connection, channel
    if connection is None:
        credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_DEFAULT_USER'), os.environ.get('RABBITMQ_DEFAULT_PASS'))
        parameters = pika.ConnectionParameters('rabbitmq-server',
                                       credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)

    if 'image' not in request.files:
        return jsonify({
            'message': 'wrong request'
        }), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({
            'message': 'no selected file'
        }), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({
            'message': 'cannot upload this file'
        }), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(os.environ.get('UPLOADING_PATH'), filename))

    channel.basic_publish(exchange='',
                      routing_key=queue_name,
                      body=filename)
    return jsonify({
        'message': 'success'
    })

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
