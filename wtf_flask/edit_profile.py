from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

class ProfileForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=7, max=15)])
    gender = SelectField('Пол', choices=[('Male', 'Мужской'), ('Female', 'Женский'), ('Other', 'Другой')])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=2, max=50)])
    middle_name = StringField('Отчество', validators=[Optional(), Length(max=50)])
    new_password = PasswordField('Новый пароль', validators=[
        Optional(),
        Length(min=8, message="Пароль должен содержать минимум 8 символов")
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        Optional(),
        EqualTo('new_password', message="Пароли не совпадают")
    ])
    submit = SubmitField('Сохранить')

    def validate_login(self, login):
        # Пример кастомной проверки логина
        if ' ' in login.data:
            raise ValidationError("Логин не может содержать пробелы")