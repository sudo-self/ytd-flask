from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import ffmpeg

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "YT Ringtones"

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'cookiefile': 'yt_cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            m4a_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.m4a')
            mp3_file_path = m4a_file_path.replace('.m4a', '.mp3')
            ffmpeg.input(m4a_file_path, ss=0, t=20).output(mp3_file_path).run(overwrite_output=True)
            m4r_file_path = m4a_file_path.replace('.m4a', '.m4r')
            ffmpeg.input(m4a_file_path, ss=0, t=20).output(m4r_file_path).run(overwrite_output=True)

        return jsonify({
            'message': 'Files processed successfully.',
            'files': {
                'mp3': mp3_file_path,
                'm4r': m4r_file_path
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('./downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)



