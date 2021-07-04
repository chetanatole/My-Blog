from flask import *
from flask_wtf.file import FileAllowed,FileField
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError

class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email', validators=[DataRequired(), Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('SignUp')

    def validate_username(self,username):
        from app import get_connection
        con=get_connection()
        cur=con.cursor()
        cur.execute('Select id from user where username=?',(username.data,))
        row=cur.fetchall()
        if row :
            raise ValidationError('Username already exists. Enter different Username')
    
    def validate_email(self,email):
        from app import get_connection
        con=get_connection()
        cur=con.cursor()
        cur.execute('Select id from user where email=?',(email.data,))
        row=cur.fetchall()
        if row :
            raise ValidationError('Email already exists. Enter different Email')

class LoginForm(FlaskForm):
    email=StringField('Email', validators=[DataRequired(), Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember me')
    submit=SubmitField('Login')

class UpdateForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit=SubmitField('Update')

    def validate_username(self,username):
        from app import get_connection
        if username.data!=session['username']:
            con=get_connection()
            cur=con.cursor()
            cur.execute('Select id from user where username=?',(username.data,))
            row=cur.fetchall()
            if row :
                raise ValidationError('Username already exists. Enter different Username')
        
    def validate_email(self,email):
        from app import get_connection
        if email.data!=session['email']:  
            con=get_connection()
            cur=con.cursor()
            cur.execute('Select id from user where email=?',(email.data,))
            row=cur.fetchall()
            if row :
                raise ValidationError('Email already exists. Enter different Email')

class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    image = FileField('Insert Image',validators=[DataRequired(),FileAllowed(['png','jpg','jpeg'])])
    content=TextAreaField('Content',validators=[DataRequired()])
    intro=TextAreaField('Write a catchy introduction!!',validators=[DataRequired()])
    submit=SubmitField('Post')


