from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import string

app = Flask(__name__)

# Caesar Cipher
def caesar_encrypt(text, key):
    result = ""
    for char in text:
        if char.isalpha():
            shift = key % 26
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

# Caesar Cipher - Dekripsi dengan Brute Force
def caesar_brute_force(cipher_text):
    results = []
    for key in range(1, 26):
        decrypted = caesar_encrypt(cipher_text, -key)
        results.append((key, decrypted))
    return results


# Steganografi - Embed
def embed_message(img, message):
    binary_msg = ''.join([format(ord(c), '08b') for c in message]) + '1111111111111110'  # delimiter
    img = img.convert('RGB')
    data = list(img.getdata())

    new_data = []
    msg_index = 0

    for pixel in data:
        r, g, b = pixel
        if msg_index < len(binary_msg):
            r = (r & ~1) | int(binary_msg[msg_index])
            msg_index += 1
        if msg_index < len(binary_msg):
            g = (g & ~1) | int(binary_msg[msg_index])
            msg_index += 1
        if msg_index < len(binary_msg):
            b = (b & ~1) | int(binary_msg[msg_index])
            msg_index += 1
        new_data.append((r, g, b))

    img.putdata(new_data)
    return img

# Steganografi - Extract
def extract_message(img):
    img = img.convert('RGB')
    data = list(img.getdata())

    binary_msg = ""
    for pixel in data:
        for color in pixel[:3]:  # R, G, B
            binary_msg += str(color & 1)

    # delimiter
    end_index = binary_msg.find('1111111111111110')
    if end_index != -1:
        binary_msg = binary_msg[:end_index]
        chars = [chr(int(binary_msg[i:i+8], 2)) for i in range(0, len(binary_msg), 8)]
        return ''.join(chars)
    return ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    text = request.form['plain_text']
    key = int(request.form['key'])
    encrypted = caesar_encrypt(text, key)
    return f"""
    <html>
    <head>
        <title>Hasil Enkripsi</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f1f3f6;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding-top: 80px;
            }}
            .box {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .btn {{
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                text-decoration: none;
            }}
            .btn:hover {{
                background-color: #2980b9;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>🔐 Hasil Enkripsi</h2>
            <p style="font-size: 20px; margin: 20px 0;">{encrypted}</p>
            <a href="/" class="btn">🔙 Kembali</a>
        </div>
    </body>
    </html>
    """

@app.route('/decrypt', methods=['POST'])
def decrypt():
    text = request.form['cipher_text']
    results = caesar_brute_force(text)
    html_rows = "".join([f"<tr><td>{key}</td><td>{decrypted}</td></tr>" for key, decrypted in results])

    return f"""
    <html>
    <head>
        <title>Hasil Brute Force</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f1f3f6;
                padding: 40px;
            }}
            table {{
                width: 100%;
                max-width: 600px;
                margin: auto;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-radius: 12px;
                overflow: hidden;
            }}
            th, td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            h2 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 20px;
            }}
            .btn {{
                display: block;
                margin: 30px auto 0;
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                text-decoration: none;
            }}
            .btn:hover {{
                background-color: #1e8449;
            }}
        </style>
    </head>
    <body>
        <h2>🤖 Hasil Dekripsi Otomatis</h2>
        <table>
            <tr><th>Kunci</th><th>Hasil</th></tr>
            {html_rows}
        </table>
        <a href="/" class="btn">🔙 Kembali</a>
    </body>
    </html>
    """

@app.route('/embed', methods=['POST'])
def embed():
    image_file = request.files['image']
    message = request.form['message']
    image = Image.open(image_file.stream)
    encoded_image = embed_message(image, message)

    buf = io.BytesIO()
    encoded_image.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='output.png')

@app.route('/extract', methods=['POST'])
def extract():
    image_file = request.files['image']
    image = Image.open(image_file.stream)
    message = extract_message(image)
    return f"""
    <html>
    <head><title>Pesan Tersembunyi</title></head>
    <body style="font-family: sans-serif; padding: 40px; background: #f1f3f6; text-align: center;">
        <h2>📥 Pesan yang Ditemukan:</h2>
        <p style="font-size: 20px;">{message}</p>
        <a href="/" style="margin-top:20px; display:inline-block; padding:10px 20px; background:#3498db; color:white; border-radius:8px; text-decoration:none;">🔙 Kembali</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
