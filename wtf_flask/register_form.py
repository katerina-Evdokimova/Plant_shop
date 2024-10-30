from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from data.users import User
from data import db_session

class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=50)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(max=100)])
    middle_name = StringField('Отчество', validators=[Length(max=100)])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Пол', choices=[('Male', 'Мужской'), ('Female', 'Женский'), ('Other', 'Другой')], validators=[DataRequired()])
    
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Зарегистрироваться')
    
    def validate_login(self, login_data):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login_data.data).first()
        if user:
            raise ValidationError('Этот логин уже занят.')
    
    def validate_email(self, email):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email.data).first()
        if user:
            raise ValidationError('Этот email уже используется.')