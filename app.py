import time
import os
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, redirect, render_template
from tensorflow.keras.models import load_model


# Menentukan ekstensi file yang diperbolehkan untuk diunggah
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Menentukan folder unggah dan atur batas konten maksimum untuk unggah file
UPLOAD_FOLDER = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Batas 10MB untuk unggah file

# Menentukan path model yang telah dilatih
model_used = 'D:\SEMESTER 7\Pembelajaran Mesin\Modul_6\Modul 6\model\model_rps.h5'

# Fungsi untuk memprediksi hasil menggunakan model yang dimuat
def predict_result(model, run_time, probs, img):
    class_list = {'Paper': 0, 'Rock': 1, 'Scissors': 2, 'Other': 3}
    idx_pred = probs.index(max(probs))
    labels = list(class_list.keys())
    return render_template('/result.html', labels=labels,
                           probs=probs, model=model, pred=idx_pred,
                           run_time=run_time, img=img)

# Fungsi untuk menambahkan header ke respons untuk menonaktifkan caching
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# Route untuk halaman utama
@app.route("/")
def index():
    return render_template('/index.html', )

# Route untuk menangani prediksi dari gambar yang diunggah
@app.route('/predict', methods=['POST'])
def predict():
    # Load model yang telah dilatih
    model = load_model(model_used)

    # Mendapatkan file dari form HTML
    file = request.files["file"]
    
    # Menyimpan file ke lokasi sementara
    file.save(os.path.join('static', 'temp.jpg'))

    # Konversi gambar ke format RGB
    img = cv2.cvtColor(np.array(Image.open(file)), cv2.COLOR_BGR2RGB)

    # Praproses gambar untuk prediksi model
    img = np.expand_dims(cv2.resize(img, (224, 224)).astype('float32') / 255, axis=0)

    # Waktu mulai untuk perhitungan waktu proses
    start = time.time()

    # Lakukan prediksi menggunakan model
    pred = model.predict(img)[0]

    # Konversi probabilitas prediksi menjadi label biner
    labels = (pred > 0.5).astype(int)

    # Hitung waktu proses
    runtimes = round(time.time() - start, 4)

    # Format respons model untuk ditampilkan
    respon_model = [round(elem * 100, 2) for elem in pred]

    # Memanggil fungsi untuk merender halaman hasil
    return predict_result('CLASS', runtimes, respon_model, 'temp.jpg')

# Run aplikasi Flask
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=2000)
