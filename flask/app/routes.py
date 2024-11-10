from flask import request, jsonify, send_file
from cryptography.fernet import Fernet
from stegano import lsb
from app.app import app

# from flask.app.app import app
import os


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

        print(file)

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

            response = {"path": "/static/uploads/hasil.png", "key": kunci.decode()}

            return jsonify(response), 200
            # return render_template("input.html", key=kunci.decode())

    return jsonify({"error": "Invalid input"}), 400
    # return render_template("input.html")


@app.route("/uploads/<filename>")
def download_file(filename):
    path = os.path.abspath(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return send_file(path, as_attachment=True, download_name=filename)


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
        file = request.files["images"]
        key_message = request.form["key"]

        try:
            pesan_terenkripsi = ambil_gambar(file)
            pesan_terdekripsi = ambil_pesan(pesan_terenkripsi, key_message.encode())

            response = {"pesan": pesan_terdekripsi}
            return jsonify(response), 200

        except Exception as e:
            print("terjadi kesalahan", e)
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid input"}), 400


if __name__ == "__main__":
    app.run(debug=True)


# Serverless handler untuk Vercel
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
