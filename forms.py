from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired


class ImageForm(FlaskForm):
    """Форма загрузки изображения и выбора порядка каналов"""

    # Загрузка файла - только изображения
    upload = FileField('Выберите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])

    # Выбор порядка каналов RGB
    channel_order = SelectField('Порядок цветовых каналов',
                                choices=[
                                    ('RGB', 'RGB - исходный'),
                                    ('RBG', 'RBG'),
                                    ('GRB', 'GRB'),
                                    ('GBR', 'GBR'),
                                    ('BRG', 'BRG'),
                                    ('BGR', 'BGR')
                                ],
                                validators=[DataRequired()])

    # Капча
    recaptcha = RecaptchaField()

    # Кнопка отправки
    submit = SubmitField('Обработать')