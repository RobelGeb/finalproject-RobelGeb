import urllib.request, urllib.error, urllib.parse, json, webbrowser, jinja2, logging, requests
from flask import Flask, render_template, request
import cloudconvert
import cloudconvert_key as cloudconvert_key
import audd_key as audd_key

### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None


def audio_converter(video_file):
    cloudconvert.configure(api_key=cloudconvert_key.key, sandbox=False)

    job = cloudconvert.Job.create(payload={
        'tasks': {
            'upload-my-file': {
                'operation': 'import/upload'
            },
            'convert-my-file': {
                'operation': 'convert',
                'input': "upload-my-file",
                'output_format': "mp3",
            },
            'export-my-file': {
                'operation': 'export/url',
                'input': 'convert-my-file'
            }
        }
    })

    upload_task_id = job['tasks'][0]['id']

    upload_task = cloudconvert.Task.find(id=upload_task_id)
    res = cloudconvert.Task.upload(file_name=video_file, task=upload_task)

    res = cloudconvert.Task.find(id=upload_task_id)

    #print(pretty(res))

    job = cloudconvert.Job.wait(id=job['id'])

    #print(pretty(job))

    dl_link = job['tasks'][0]['result']['files'][0]['url']
    return dl_link

def audio_fingerprint(url):
    data = {
        'api_token': audd_key.key,
        'url': url,
        'return': 'apple_music,spotify',
    }
    result = requests.post('https://api.audd.io/', data)
    return json.loads(result.text)


app = Flask(__name__)
@app.route("/")
def greeting():
    app.logger.info("In Greeting")
    return render_template('greetingtemplate.html')


@app.route("/inputfile", methods=['POST'])
def input_handler():
    if request.method == 'POST':
        inputfile = request.files.get('inputfile')
        inputfile.save('uploads/input.mp4')

        url = audio_converter('uploads/input.mp4')

        result = audio_fingerprint(url)

    return render_template('outputtemplate.html', result=result['result'])


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)


#url = 'https://storage.cloudconvert.com/tasks/1ab8c579-ebd7-468f-88fe-e27db4ccb9a6/luther.mp3?AWSAccessKeyId=cloud' \
#      'convert-production&Expires=1608240655&Signature=7XTWdxwszJXrJuqzzJtwSBZfUfI%3D&response-content-disposition' \
#      '=attachment%3B%20filename%3D%22luther.mp3%22&response-content-type=audio%2Fmpeg'

'''
    "tasks": {
        "import-1": {
            "operation": "import/url"
        },
        "task-1": {
            "operation": "convert",
            "input_format": "mp4",
            "output_format": "mp3",
            "engine": "ffmpeg",
            "input": [
                "import-1"
            ],
            "audio_codec": "mp3",
            "audio_qscale": 0
        },
        "export-1": {
            "operation": "export/url",
            "input": [
                "task-1"
            ],
            "inline": False,
            "archive_multiple_files": False
        }
    }
    '''


"""
#getting the process URL
api = cloudconvert.Api(cloudconvert_key.key)
process = api.createProcess({
    "mode": "info",
    "inputformat": "mp4",
    "outputformat": "mp3"
})

#starting the process
process.start({
    "input": "upload",
    "file": open('luther.mp4', 'rb'),
    "save": "true"
})

process.refresh()
process.wait()
print(process['message'])

process.download('outputfile.ext')


"""
