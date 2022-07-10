from fileinput import filename
from flask import Flask, request, render_template, jsonify, send_file, redirect
import youtube_dl
import os
import threading
import time
import random
import re

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/", code=302)

""" ROUTES """
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# get the video for conversion
@app.route('/convert', methods=['POST'])
def convert():
    args = request.args
    if(args.get("link") is not None):
        link = args.get("link")
        if(is_youtube_video_url(link) is not None):
            exec_thread(convert_mp3, {'video_link': link})
            ##filename = get_filename(link)
            filename = f"{get_video_info(link)['title']}.mp3".replace(" ", "_").replace("/", "-").replace("\\", "-")
            return jsonify({'filename': filename}), 201
            
    return jsonify({'erro': 'Requisição inválida.'}), 422

# provide the file for download, after delete
@app.route('/download/<filename>')
def download(filename):
    if(os.path.isfile('./download/' + filename)):
        exec_thread(delete_file, {'filename': './download/' + filename})
        return send_file('./download/' + filename, as_attachment=True), 200

    return 'Arquivo Não encontrado', 404

# check if the file as done for download
@app.route('/done')
def done():
    filename = request.args.get('filename')
    if(filename is not None):
        if(os.path.isfile('./download/' + filename)):
            return jsonify({'link': './download/' + filename}), 200
        return jsonify({'link': False}), 200
    return jsonify('bad request'), 422

# return a random word that stay in wordlist.txt
@app.route('/randomword', methods=['GET'])
def randomword():
    word_list = open('wordlist.txt', 'r').read().split("\n")
    word = random.choice(word_list)
    open('./temp/word', 'w').write(word)

    exec_thread(delete_file, {
        'filename': './temp/word',
        'time_wait': 30
    })

    return word

# delete all files in download path
@app.route('/maintenance', methods=['POST'])
def maintenance():
    auth = request.headers.get('auth-code')
    if auth is not None:
        if(os.path.isfile('./temp/word') and auth == open('./temp/word', 'r').read()):
            clean_download_folder()
            return open('./static/plastic_love.txt', 'r').read().replace("\n", "<br>"), 200
    return redirect("/", code=302)
""" ROUTES END """

""" FUNCTIONS """
# do the conversion
def convert_mp3(video_link):
    try:
        video_info = get_video_info(video_link)
        filename = f"{video_info['title']}.mp3".replace(" ", "_").replace("/", "-").replace("\\", "-")

        options={
            'format':'bestaudio/best',
            'outtmpl':'download/' + filename,
            'quiet': False
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            status = ydl.download([video_info['webpage_url']])
            print(status)
        
        return format(filename)
    except:
        return False

# delete file after 1 minute
def delete_file(filename, time_wait = 60):
    time.sleep(time_wait)
    os.remove(filename)

def clean_download_folder():
    paths = ['./download']
    for path in paths:
        i = 0 
        for p, _, files in os.walk(os.path.abspath(path)):
            if(i != 0): # dont delete the root download path
                os.rmdir(p)
            for file in files:
                if file == '.gitkeep':
                    continue
                os.remove(os.path.join(p, file))
            i = i + 1

# check if link is from youtube
def is_youtube_video_url(url):
    regex = re.compile('^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$')
    return regex.match(url)

# get video infos
def get_video_info(link):
    video_info = youtube_dl.YoutubeDL().extract_info(
        url = link,
        download=False
    )
    return video_info

def exec_thread(target_def, args):
    new_thread = threading.Thread(target=target_def, kwargs=args)
    new_thread.start()

""" FUNCTIONS END """