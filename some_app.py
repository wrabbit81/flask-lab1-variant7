import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from forms import ImageForm
from image_processor import (
    change_channel_order, calculate_color_histogram,
    calculate_mean_by_row, calculate_mean_by_col,
    generate_histogram_plot, generate_line_plot
)
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard-to-guess-secret-key-12345'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Настройки капчи (ключи Google)
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdmIGksAAAAAJ5sGt7XPZLwikma8L0JdclczXiT'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdmIGksAAAAAOy4gaiDhMXc8QogmOE5ywPx__zP'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

# Создаём папку для загрузок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()

    if form.validate_on_submit():
        # Сохраняем загруженный файл
        file = form.upload.data
        original_filename = secure_filename(file.filename)

        # Генерируем уникальное имя файла
        ext = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Получаем порядок каналов
        channel_order = form.channel_order.data

        # Перенаправляем на страницу результатов
        return redirect(url_for('result',
                                filename=filename,
                                order=channel_order))

    return render_template('index.html', form=form)


@app.route('/result')
def result():
    filename = request.args.get('filename')
    order = request.args.get('order')

    if not filename or not order:
        return redirect(url_for('index'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Открываем исходное изображение
        original_img = Image.open(filepath)

        # Изменяем порядок каналов
        processed_img = change_channel_order(original_img, order)

        # Сохраняем обработанное изображение
        processed_filename = f"processed_{filename}"
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        processed_img.save(processed_filepath)

        # Генерируем графики для исходного изображения
        hist_r, hist_g, hist_b = calculate_color_histogram(original_img)
        hist_plot_original = generate_histogram_plot(
            hist_r, hist_g, hist_b,
            'Гистограмма RGB - исходное изображение'
        )

        # Генерируем графики для обработанного изображения
        hist_r_p, hist_g_p, hist_b_p = calculate_color_histogram(processed_img)
        hist_plot_processed = generate_histogram_plot(
            hist_r_p, hist_g_p, hist_b_p,
            f'Гистограмма RGB - порядок {order}'
        )

        # График среднего по вертикали (исходное)
        mean_row = calculate_mean_by_row(original_img)
        row_plot = generate_line_plot(
            mean_row,
            'Среднее значение цвета по вертикали',
            'Строка', 'Средняя интенсивность'
        )

        # График среднего по горизонтали (исходное)
        mean_col = calculate_mean_by_col(original_img)
        col_plot = generate_line_plot(
            mean_col,
            'Среднее значение цвета по горизонтали',
            'Столбец', 'Средняя интенсивность'
        )

        return render_template('result.html',
                               original_image=filename,
                               processed_image=processed_filename,
                               channel_order=order,
                               hist_original=hist_plot_original,
                               hist_processed=hist_plot_processed,
                               row_plot=row_plot,
                               col_plot=col_plot)

    except Exception as e:
        return f"Ошибка обработки: {str(e)}"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)