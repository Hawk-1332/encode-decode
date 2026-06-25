from PIL import Image
import math
import tkinter
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet
import struct
import requests

def encode():
    message = requests.form["message"]
    if len(message) > 0:
        entr.delete(0, tkinter.END)

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

        root = tkinter.Tk()
        root.withdraw()

        file = filedialog.asksaveasfilename(
            title="\n",
            filetypes=[
                ("PNG", "*.png"),
            ]
        )
        if file[-4:] == ".png":
            file_name = file
        else:
            file_name = f"{file}.png"
        img.save(file_name)

    else:
        messagebox.showerror(title="Typing Error", message="You must complete the field !")

def decode():

    path = path2.get()
    try:
        Image.open(path)
    except FileNotFoundError:
        messagebox.showerror(title="Typing Error", message="Incorrect path")
    else:

        img = Image.open(path)
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
        rep.config(text=f"Transcription : \n\n{message}")

def select():
    file = filedialog.askopenfile(
        title="\n",
        filetypes=[
            ("PNG", "*.png"),
        ]
    )
    if not file == None:
        path2.delete(0, tkinter.END)
        path2.insert(0, file.name)

window = tkinter.Tk()
window.title("Encode/Decode")

notebook = ttk.Notebook(window)

notebook.pack(fill="both", expand=True)

frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Encode")

ttk.Label(frame1, text='''
Type anything to encode.''').grid(row=0, column=0, columnspan=2)

entr = ttk.Entry(frame1)
entr.grid(row=1, column=0, columnspan=2)

ttk.Button(frame1, text="Encode", command=encode).grid(row=4, column=0, columnspan=2)

frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="Decode")

ttk.Button(frame2, text="Decode", command=decode).grid(row=2, column=0, columnspan=2)

path2 = ttk.Entry(frame2)
path2.grid(row=1, column=0)

ttk.Label(frame2, text='''
Specify path to file.''').grid(row=0, column=0, columnspan=2)

ttk.Button(frame2, text="Select", command=select).grid(row=1, column=1)

rep = ttk.Label(frame2, text="")
rep.grid(row=3, column=0, columnspan=2)

window.mainloop()