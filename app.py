from flask import Flask, render_template, request, send_file
from PIL import Image
from cryptography.fernet import Fernet
import math
import struct
from io import BytesIO

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():

    message = request.form.get("message", "")

    if not message:
        return render_template("index.html", error="Message vide")

    key = Fernet.generate_key()
    fernet = Fernet(key)

    encrypted = fernet.encrypt(message.encode())

    payload = key + b"\x14" + encrypted
    payload = struct.pack(">I", len(payload)) + payload

    nb_pixels = math.ceil(len(payload) / 3)
    side = math.ceil(math.sqrt(nb_pixels))

    img = Image.new("RGB", (side, side))

    data = bytearray(payload)

    while len(data) < side * side * 3:
        data.append(0)

    i = 0

    for y in range(side):
        for x in range(side):

            r = data[i]
            g = data[i + 1]
            b = data[i + 2]

            img.putpixel((x, y), (r, g, b))
            i += 3

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name="message_secret.png"
    )


@app.route("/decode", methods=["POST"])
def decode():

    file = request.files.get("image")

    if not file:
        return render_template("index.html", decoded_message="Aucun fichier sélectionné")

    img = Image.open(file)

    data = bytearray()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = img.getpixel((x, y))
            data.append(r)
            data.append(g)
            data.append(b)

    payload_length = struct.unpack(">I", data[:4])[0]

    payload = bytes(data[4:4 + payload_length])

    key, encrypted = payload.split(b"\x14", 1)

    fernet = Fernet(key)
    message = fernet.decrypt(encrypted).decode()

    return render_template(
        "index.html",
        decoded_message=message
    )


if __name__ == "__main__":
    app.run(debug=True)