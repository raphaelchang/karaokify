from flask import *
import os
from lyrics_aligner import align_lyrics

app = Flask(__name__)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/upload", methods=['POST'])
def upload_image():
    file = request.files['audio']
    if not os.path.exists('upload'):
        os.makedirs('upload')
    name = 'upload/audio.' + file.filename.split('.')[-1]
    lyrics = "upload/lyrics.txt"
    file.save(name)
    with open(lyrics, "w") as lyrics_file:
        lyrics_file.write(request.form['lyrics'])
    result = align_lyrics(name, lyrics)
    os.remove(name)
    os.remove(lyrics)
    return jsonify(lyrics=result)

@app.route('/<path:path>')
def send_static(path):
    return app.send_static_file(path)
