import base64
import io
import os

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from flask import Flask, render_template, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-later'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

Bootstrap(app)

class ImageForm(FlaskForm):
    image = FileField('Выберите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    channel_order = SelectField('Порядок каналов', choices=[
        ('rgb', 'RGB (исходный)'),
        ('rbg', 'RBG'),
        ('grb', 'GRB'),
        ('gbr', 'GBR'),
        ('brg', 'BRG'),
        ('bgr', 'BGR')
    ], validators=[DataRequired()])
    submit = SubmitField('Обработать')

def change_channel_order(img_array, order='rgb'):
    """Меняет порядок цветовых каналов"""
    if order == 'rgb':
        return img_array
    orders = {
        'rbg': (0, 2, 1),
        'grb': (1, 0, 2),
        'gbr': (1, 2, 0),
        'brg': (2, 0, 1),
        'bgr': (2, 1, 0)
    }
    return img_array[:, :, orders[order]]

def create_color_histogram(img_array):
    """Создаёт гистограмму распределения цветов"""
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    colors = ('red', 'green', 'blue')
    for i, color in enumerate(colors):
        ax[i].hist(img_array[:, :, i].ravel(), bins=50, color=color, alpha=0.7)
        ax[i].set_title(f'{color.upper()} канал')
        ax[i].set_xlabel('Интенсивность')
        ax[i].set_ylabel('Частота')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_base64


def create_mean_plots(img_array):
    """Создаёт графики среднего значения по вертикали и горизонтали"""
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))

    mean_horizontal = np.mean(img_array, axis=1)
    for i, color in enumerate(['red', 'green', 'blue']):
        ax[0].plot(mean_horizontal[:, i], color=color, label=color.upper())
    ax[0].set_title('Среднее по вертикали (горизонтальный профиль)')
    ax[0].set_xlabel('Пиксели по вертикали')
    ax[0].set_ylabel('Интенсивность')
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)

    mean_vertical = np.mean(img_array, axis=0)
    for i, color in enumerate(['red', 'green', 'blue']):
        ax[1].plot(mean_vertical[:, i], color=color, label=color.upper())
    ax[1].set_title('Среднее по горизонтали (вертикальный профиль)')
    ax[1].set_xlabel('Пиксели по горизонтали')
    ax[1].set_ylabel('Интенсивность')
    ax[1].legend()
    ax[1].grid(True, alpha=0.3)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return img_base64


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)

        img = Image.open(filepath)
        img_array = np.array(img) / 255.0

        order = form.channel_order.data
        processed_array = change_channel_order(img_array, order)
        processed_img = Image.fromarray((processed_array * 255).astype(np.uint8))
        processed_filename = f'processed_{filename}'
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        processed_img.save(processed_path)

        histogram = create_color_histogram(img_array)
        mean_plots = create_mean_plots(img_array)

        return render_template('result.html',
                               original=filename,
                               processed=processed_filename,
                               histogram=histogram,
                               mean_plots=mean_plots,
                               order=order.upper())

    return render_template('index.html', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=8080)