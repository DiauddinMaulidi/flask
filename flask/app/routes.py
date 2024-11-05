from flask import render_template, request
from cryptography.fernet import Fernet
from stegano import lsb
from app import app
import os

UPLOAD_FOLDER = "./app/static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# fungsi untuk menghasilkan key
def buat_key():
    return Fernet.generate_key()


def enkripsi_pesan(pesan, key):
    cipher_suite = Fernet(key)
    pesan_terenkripsi = cipher_suite.encrypt(pesan.encode())
    return pesan_terenkripsi


# menyembunyikan pesan yang sudah di enkripsi ke dalam gambar yang sudah di siapkan
def sisipkan_pesan_ke_gambar(gambar_asli, pesan_terenkripsi, gambar_output):
    lsb.hide(gambar_asli, pesan_terenkripsi.decode()).save(gambar_output)


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["image"]
        secret_message = request.form["pesan"]

        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

            if len(os.listdir(app.config["UPLOAD_FOLDER"])) == 0:
                file.save(file_path)
            else:
                for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    os.remove(file_path)

                file.save(file_path)

            kunci = buat_key()
            pesan_terenkripsi = enkripsi_pesan(secret_message, kunci)

            file_hasil = os.path.join(app.config["UPLOAD_FOLDER"], "hasil.png")
            sisipkan_pesan_ke_gambar(file_path, pesan_terenkripsi, file_hasil)

            return render_template("input.html", key=kunci.decode())

    return render_template("input.html")


# dekrip pesan
# ambil gambar
def ambil_gambar(gambar_path):
    pesan_terenkripsi = lsb.reveal(gambar_path)
    return pesan_terenkripsi


# ambil pesan
def ambil_pesan(pesan_terenkripsi, key):
    kunci = Fernet(key)
    pesan_terdekripsi = kunci.decrypt(pesan_terenkripsi.encode())
    return pesan_terdekripsi.decode()


@app.route("/dekrip", methods=["GET", "POST"])
def dekrip_file():
    if request.method == "POST":
        file = request.files["image"]
        key_message = request.form["key"]

        try:
            pesan_terenkripsi = ambil_gambar(file)
            pesan_terdekripsi = ambil_pesan(pesan_terenkripsi, key_message.encode())
        except Exception as e:
            print("terjadi kesalahan", e)

        return render_template("dekrip.html", pesan=pesan_terdekripsi)

    return render_template("dekrip.html")
