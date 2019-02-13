from PIL import Image

import pika
import pika.exceptions

import os

def callback(ch, method, properties, body):
    filename = body.decode('utf8')
    im = Image.open(os.path.join(os.environ.get('UPLOADING_PATH'), filename))
    im.thumbnail((64, 64))
    im.save(os.path.join(os.environ.get('UPLOADING_PATH'), "{0}_thumb.{1}".format(*filename.rsplit('.', 1))))
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    while True:
        try:
            credentials = pika.PlainCredentials(os.environ.get('RABBITMQ_DEFAULT_USER'), os.environ.get('RABBITMQ_DEFAULT_PASS'))
            parameters = pika.ConnectionParameters('rabbitmq-server',
                                        credentials=credentials)
            connection = pika.BlockingConnection(parameters)

            print('connected')

            channel = connection.channel()
            channel.queue_declare(queue=os.environ.get('RABBITMQ_CHANNEL'))
            channel.basic_consume(callback,
                        queue=os.environ.get('RABBITMQ_CHANNEL'))

            print('waiting for messages')
            channel.start_consuming()
        except pika.exceptions.AMQPChannelError:
            continue
        except pika.exceptions.AMQPConnectionError:
            continue
