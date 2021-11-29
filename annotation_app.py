import time
from datetime import datetime
from flask import Flask, escape, request, render_template
from influxdb import InfluxDBClient
#from OpenSSL import SSL
#context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
#context.use_privatekey_file('server.key')
#context.use_certificate_file('server.crt') 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

SECRET_KEY = os.environ.get("SECRET_KEY")
print(SECRET_KEY)
app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return render_template("home.html")


@app.route('/annotate')
def annotate():
    #name = request.args.get("name", "World")
    return render_template("annotate.html", hostname=SECRET_KEY)


@app.route('/post')
def post():
    value = request.args.get('button')
    print(value)

    timestamp = int(time.time()*1000000000)
    #dt_object = datetime.fromtimestamp(timestamp)
    json_body = [
    {
        "measurement": "annotation",
        "tags": {
            "host": "server01",
            "region": "assen"
        },
        "time": timestamp,
        "fields": {
            "value": value
        }
    }
    ]
    print(timestamp)
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'db1')
    client.write_points(json_body)
    return f'Hello!'

@app.route('/recording',methods = ['POST'])
def record():
    #print(request.data)
    name = '{}-assesment.wav'.format(int(time.time()))
    f = open(name, 'wb')
    f.write(request.data)
    f.close()
    return f'Hello!'

if __name__ == '__main__':
    #app.run('0.0.0.0', debug=True, port=8100, ssl_context=('server.crt', 'server.key'))
    app.run('0.0.0.0', debug=True, port=8100, ssl_context=('host.cert', 'host.key'))
