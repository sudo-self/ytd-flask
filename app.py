from flask import Flask, request, jsonify
import yt_dlp
import ffmpeg
import os

app = Flask(__name__)

# Ensure the downloads directory exists
os.makedirs('downloads', exist_ok=True)

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
        'cookiefile': 'yt_cookies.txt',  # Adjust or remove if unnecessary
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            base_name, ext = os.path.splitext(downloaded_file)

            m4a_file_path = f"{base_name}.m4a"
            mp3_file_path = f"{base_name}.mp3"
            m4r_file_path = f"{base_name}.m4r"

            # Convert m4a to mp3 and m4r
            ffmpeg.input(m4a_file_path, ss=0, t=20).output(mp3_file_path).run(overwrite_output=True)
            ffmpeg.input(m4a_file_path, ss=0, t=20).output(m4r_file_path).run(overwrite_output=True)

        return jsonify({
            'message': 'Files processed successfully.',
            'files': {
                'mp3': mp3_file_path,
                'm4r': m4r_file_path
            }
        })

    except yt_dlp.utils.DownloadError as e:
        if 'HTTP Error 429' in str(e):
            return jsonify({'error': 'Too many requests. Please try again later.'}), 429
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=10000)






