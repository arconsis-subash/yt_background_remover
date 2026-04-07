import os
from io import BytesIO

from PIL import Image
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from rembg import remove

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index() -> str:
    return render_template('index.html')


@app.route('/remove', methods=['POST'])
def remove_bg() -> object:
    uploaded = request.files.get('image')
    if not uploaded or uploaded.filename == '':
        flash('Please select an image file to upload.')
        return redirect(url_for('index'))

    if not allowed_file(uploaded.filename):
        flash('Unsupported file type. Use PNG, JPG, WEBP, BMP, TIFF, or GIF.')
        return redirect(url_for('index'))

    try:
        input_bytes = uploaded.read()
        output_bytes = remove(input_bytes)
        output_image = Image.open(BytesIO(output_bytes)).convert('RGBA')
    except Exception:
        flash('Failed to remove the background. Try a different image.')
        return redirect(url_for('index'))

    output_buffer = BytesIO()
    output_image.save(output_buffer, format='PNG')
    output_buffer.seek(0)

    return send_file(
        output_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name='background_removed.png',
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
