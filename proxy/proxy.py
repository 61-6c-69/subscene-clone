import  requests
import  time
from flask import Flask, request, jsonify
import cloudscraper
import base64
import psutil
import json

app = Flask(__name__)

def isBase64(s):
    try:
        return base64.b64decode(s)
    except Exception as e:
        return False

def proxyUrl(url, cookies = None, post_data = None, isfile = None):
    #decode base64 url
    try:
        url = base64.b64decode(url).decode('utf-8')
        print('new url: {}'.format(url))
        #get html
        scraper = cloudscraper.create_scraper()

        if isfile != None:
            return scraper.get(url).content

        if post_data != None:
            b64data = base64.b64decode(post_data).decode('utf-8')
            print("post data: {}".format(b64data))
            html = scraper.post(url, data=json.loads(b64data)).text
        else:
            html = scraper.get(url, cookies=cookies).text

        return html
    except Exception as e:
        print(e)
        return 'Error'
#end def

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        #current timestamp
        timestamp = int(time.time())

        #get url query
        url = request.args.get('url')
        cookies = None
        if 'cookies' in request.args:
            cookies = request.args.get('cookies')

        post_data = None
        if 'post_data' in request.args:
            post_data = request.args.get('post_data')

        #check url
        if url is None:
            return jsonify({'error': 'url is None', 'code': '400'})
        if not isBase64(url):
            return jsonify({'error': 'url is not base64', 'code': '400'})
        #end if

        isfile = None
        if 'file' in request.args:
            isfile = True

        #proxy url
        html = proxyUrl(url, cookies, post_data, isfile)

        if 'file' in request.args:
            return html

        #return json html
        return jsonify({
            'res_data': base64.b64encode(html.encode('utf-8')).decode('utf-8'),
            'code': '200',
            'timestamp': {
                'start': timestamp,
                'end': int(time.time())
            }
        })
    except Exception as e:
        print(e)
        return ''

@app.route('/info', methods=['GET'])
def proxy():
    #current system ram
    ram = int(psutil.virtual_memory().available / (1024 * 1024))
    #current system cpu
    cpu = psutil.cpu_percent()
    #current system disk
    disk = int(psutil.disk_usage('/').free / (1024 * 1024))
    #current system uptime
    uptime = int(time.time() - psutil.boot_time())

    return jsonify({
        'title': 'Proxy',
        'description': 'Proxy url',
        'version': '1.0.0',
        'ram': ram,
        'cpu': cpu,
        'disk': disk,
        'uptime': uptime,
        'code': '200'
    })

if __name__ == '__main__':
    app.run(debug=True, port=1000)
