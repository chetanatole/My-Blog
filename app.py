import os
import datetime
import secrets
from flask import * 
from PIL import Image 
from forms import RegistrationForm,LoginForm,UpdateForm,PostForm
import sqlite3
import os
app = Flask(__name__)  
app.config['SECRET_KEY']='597eb31cd315caf94dd08a1dfc33973b'
  
def get_connection():
    f=os.path.isfile("blog.db")
    con=sqlite3.connect("blog.db")
    if not f:
        cur=con.cursor()
        with open("schema.sql","r") as file:
            cur.executescript(file.read())
        con.commit()
    return con
    
@app.route('/')
@app.route('/home')
def home():
    # con=get_connection()
    # cur=con.cursor()
    # cur.execute('select * from user')
    # rows=cur.fetchall()
    # for row in rows:
    #     print(row[0],row[1],row[2],row[3])
    # cur.execute('select * from post')
    # rows=cur.fetchall()
    # for row in rows:
    #     print(row[0],row[1],row[2],row[3],row[4])
    con=get_connection()
    cur=con.cursor()
    cur.execute('select user.username,user.image_file,post.title,post.image_file,post.date_posted,post.content,post.intro,post.id from user inner join post on user.id=post.user_id')
    rows=cur.fetchall()
    posts=[]
    for row in rows:
        post={}
        post['author']=row[0]
        post['profile_pic']=row[1]
        post['title']=row[2]
        post['post_image']=row[3]
        post['date_posted']=row[4].split()[0]
        post['content']=row[5]
        post['intro']=row[6]
        post['postid']=row[7]
        posts.append(post)
    return render_template('home.html',title='home',posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',title="About" )

@app.route('/register',methods=['GET','POST'])
def register():
    if 'email' in session:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        con=get_connection()
        con.execute('insert into user(username,email,passwordval) values(?,?,?)',(form.username.data,form.email.data,form.password.data,))
        con.commit()
        flash(f'Account Created for { form.username.data}! Please log in','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        con=get_connection()
        cur=con.cursor()
        cur.execute('select username,image_file,id from user where email=? and passwordval=?',(form.email.data,form.password.data,))
        row=cur.fetchall()
        if row :
            flash(f'You have been logged in!','success')
            session['email']=form.email.data
            session['username']=row[0][0]
            session['image_file']=row[0][1]
            session['id']=row[0][2]
            session.permanent=form.remember.data
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Check email and password!','danger')
    return render_template('login.html',title='Login',form=form)   

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email',None)
        session.pop('username',None)
        session.pop('image_file',None)
        session.pop('id',None)
    return redirect(url_for('home'))  

@app.route('/account',methods=['GET','POST'])
def account():
    if 'email' in session:
        form=UpdateForm()
        if form.validate_on_submit():
            con=get_connection()
            if form.profile_pic.data:
                random=secrets.token_hex(8)
                filename,extension=os.path.splitext(form.profile_pic.data.filename)
                saved_name = random+extension
                destination = os.path.join(app.root_path,'static/profile_pics',saved_name)
                size=(125,125)
                i=Image.open(form.profile_pic.data)
                i.thumbnail(size)
                i.save(destination)
                con.execute('update user set image_file=? where id=?',(saved_name,session['id'],))
                con.commit()
                session['image_file']=saved_name
            con.execute('update user set username=?,email=? where id=?',(form.username.data,form.email.data,session['id'],))
            con.commit()
            session['username']=form.username.data
            session['email']=form.email.data
            flash('Your account has been updated!','success')
            redirect(url_for('account'))
        elif request.method=='GET':
            form.username.data=session['username']
            form.email.data=session['email']
        image_file=url_for('static',filename='profile_pics/' + session['image_file'])
        return render_template('account.html',title='Account',image_file=image_file,form=form,username=session['username'],email=session['email'])  
    return redirect(url_for('login'))    

@app.route('/newpost',methods=['GET','POST'])
def newpost():
    if 'email' in session:
        form=PostForm()
        if form.validate_on_submit():
            random=secrets.token_hex(8)
            filename,extension=os.path.splitext(form.image.data.filename)
            saved_name = random+extension
            destination = os.path.join(app.root_path,'static/content_images',saved_name)
            form.image.data.save(destination)
            con=get_connection()
            con.execute('insert into post(title,content,user_id,image_file,intro) values(?,?,?,?,?)',(form.title.data,form.content.data,session['id'],saved_name,form.intro.data))
            con.commit()
            flash('Post published successfully','success') 
            return redirect(url_for('home'))      
        return render_template('new_post.html',title='New Post',form=form)
    return redirect(url_for('login'))

@app.route('/viewpost/<int:postid>')
def viewpost(postid):
    con=get_connection()
    cur=con.cursor()
    cur.execute('select user.id,user.username,user.image_file,post.title,post.intro,post.content,post.date_posted,post.image_file,post.id from user inner join post on user.id=post.user_id where post.id=?',(postid,))
    rows=cur.fetchall()
    post={}
    for row in rows:
        post['user_id']=row[0]
        post['author']=row[1]
        post['profile_pic']=row[2]
        post['title']=row[3]
        post['intro']=row[4]
        post['content']=row[5]
        post['date_posted']=row[6].split()[0]
        post['post_image']=row[7]
        post['id']=row[8]
    flag=False
    if 'id' in session and session['id']==post['user_id']:
        flag=True
    return render_template('viewpost.html',post=post,flag=flag)

@app.route('/update/<int:postid>',methods=['GET','POST'])
def update(postid):
    form=PostForm()
    if form.validate_on_submit():
        random=secrets.token_hex(8)
        filename,extension=os.path.splitext(form.image.data.filename)
        saved_name = random+extension
        destination = os.path.join(app.root_path,'static/content_images',saved_name)
        form.image.data.save(destination)
        con=get_connection()
        con.execute('update post set title=?,content=?,image_file=?,intro=? where id=?',(form.title.data,form.content.data,saved_name,form.intro.data,postid))
        con.commit()
        flash('Post updated successfully','success') 
        return redirect(url_for('home'))
    elif request.method=='GET':
        con=get_connection()
        cur=con.cursor()
        cur.execute('select title,intro,content,image_file from post where id=?',(postid,))
        rows=cur.fetchall()
        for row in rows:
            form.title.data=row[0]
            form.intro.data=row[1]
            form.content.data=row[2]
    return render_template('update.html',title='Update',form=form)

@app.route('/delete/<postid>')
def delete(postid):
    con=get_connection()
    con.execute('delete from post where id=?',(postid,))
    con.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':  
   app.run(debug = True)  