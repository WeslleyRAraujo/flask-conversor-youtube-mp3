from flask import Flask, request, render_template, jsonify, send_file, redirect
import youtube_dl
import os
import threading
import time
import random

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/", code=302)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    args = request.args
    if(args.get("link") is not None):
        link = args.get("link")
        result = convert_mp3(link)
        if(result is False):
            return jsonify({'erro': 'Não foi possível completar a requisição.'})
    
        return jsonify({'link': '/download/' + result}), 201

    return jsonify({'erro': 'Requisição inválida.'}), 422

@app.route('/download/<filename>')
def download(filename):
    if(os.path.isfile('./download/' + filename)):
        thread = threading.Thread(target=delete_file, kwargs={
            'filename': './download/' + filename
        })
        thread.start()

        return send_file('./download/' + filename, as_attachment=True), 200

    return 'Arquivo Não encontrado', 404

@app.route('/randomword', methods=['GET'])
def randomword():
    word_list = open('wordlist.txt', 'r').read().split("\n")
    word = random.choice(word_list)
    open('./temp/word', 'w').write(word)

    delete_word = threading.Thread(target=delete_file, kwargs={
        'filename': './temp/word',
        'time_wait': 30
    })
    delete_word.start()

    return word

@app.route('/maintenance', methods=['POST'])
def maintenance():
    auth = request.headers.get('auth-code')
    if auth is not None:
        if(os.path.isfile('./temp/word') and auth == open('./temp/word', 'r').read()):
            clean_download_folder()
            return open('./static/plastic_love.txt', 'r').read().replace("\n", "<br>"), 200
    return redirect("/", code=302)

def convert_mp3(video_link):
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(
            url = video_link,
            download=False
        )
        filename = f"{video_info['title']}.mp3".replace(" ", "_").replace("/", "-").replace("\\", "-")

        options={
            'format':'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl':'download/' + filename,
            'quiet': False
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            status = ydl.download([video_info['webpage_url']])
            print(status)
        
        return format(filename)
    except:
        return False

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