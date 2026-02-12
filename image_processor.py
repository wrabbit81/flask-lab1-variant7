import numpy as np
from PIL import Image
import matplotlib

matplotlib.use('Agg')  # для сохранения графиков без GUI
import matplotlib.pyplot as plt
import io
import base64
import os


def change_channel_order(image, order):
    """
    Изменяет порядок цветовых каналов RGB
    image: PIL Image
    order: строка из 3 букв, например 'BGR'
    """
    # Конвертируем в массив numpy
    img_array = np.array(image)

    # Если изображение в оттенках серого, конвертируем в RGB
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=2)
    elif img_array.shape[2] == 4:  # RGBA
        img_array = img_array[:, :, :3]

    # Словарь соответствия каналов
    channel_map = {
        'R': 0,
        'G': 1,
        'B': 2
    }

    # Создаём новый массив с переставленными каналами
    new_img = np.zeros_like(img_array)
    for i, ch in enumerate(order):
        new_img[:, :, i] = img_array[:, :, channel_map[ch]]

    return Image.fromarray(new_img.astype('uint8'))


def calculate_color_histogram(image):
    """Вычисляет гистограммы для R,G,B каналов"""
    img_array = np.array(image)

    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=2)

    hist_r = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))[0]
    hist_g = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))[0]
    hist_b = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))[0]

    return hist_r, hist_g, hist_b


def calculate_mean_by_row(image):
    """Среднее значение цвета по вертикали (по строкам)"""
    img_array = np.array(image)
    return np.mean(img_array, axis=(1, 2))


def calculate_mean_by_col(image):
    """Среднее значение цвета по горизонтали (по столбцам)"""
    img_array = np.array(image)
    return np.mean(img_array, axis=(0, 2))


def generate_histogram_plot(hist_r, hist_g, hist_b, title):
    """Генерирует график гистограммы RGB и возвращает base64 строку"""
    plt.figure(figsize=(10, 6))
    plt.plot(hist_r, color='red', alpha=0.7, label='Red')
    plt.plot(hist_g, color='green', alpha=0.7, label='Green')
    plt.plot(hist_b, color='blue', alpha=0.7, label='Blue')
    plt.title(title)
    plt.xlabel('Интенсивность')
    plt.ylabel('Количество пикселей')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Сохраняем в base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return plot_data


def generate_line_plot(data, title, xlabel, ylabel):
    """Генерирует линейный график (среднее по вертикали/горизонтали)"""
    plt.figure(figsize=(10, 6))
    plt.plot(data, color='purple', linewidth=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return plot_data


def allowed_file(filename):
    """Проверка расширения файла"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS