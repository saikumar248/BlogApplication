from flask import Flask, render_template, request, redirect, url_for,session
import pandas as pd
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)

import sqlite3

connection = sqlite3.connect('Blog.db',check_same_thread=False)
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS
users(user_id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)"""

cursor.execute(command)

# cursor.execute("INSERT INTO users  VALUES (1, 'Sai', 'email@gmail','Sai733kumar@')")
connection.commit()
author = ''
# Helper function to read and write data from/to Excel
def read_data():
    return pd.read_excel('database.xlsx')

def write_data(df):
    df.to_excel('database.xlsx', index=False)

# Your code for login, signup, and user authentication goes here

# CRUD Operations for blog posts
@app.route('/home')
def home():
    if 'user_id' in session:
        df = read_data()
        posts = df.to_dict('records')
        return render_template('blog.html', posts=posts)
    else:
        return redirect('/')

@app.route('/login_validation',methods=['POST'])
def login_validation():
    global author
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT *From `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}' """
                   .format(email,password))
    users = cursor.fetchall()
    author = users[0][1]
    if len(users)>0:
        session['user_id'] = users[0][0]
        return redirect('/blog')
    else:
        return redirect('/')

@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('upassword')

    cursor.execute(""" Insert into `users` (`user_id`,`name`, `email`, `password`) values 
    (NULL,'{}','{}','{}')""".format(name, email, password))
    connection.commit()
    cursor.execute(""" SELECT *FROM `users` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    global author
    author=myuser[0][1]
    session['user_id']=myuser[0][0]
    return redirect('/blog')

@app.route('/blog')
def blog():
    if 'user_id' in session:
        df = read_data()
        posts = df.to_dict('records')
        return render_template('blog.html', posts=posts)
    else:
        return redirect('/')


@app.route('/blog/<title>')
def blog_detail(title):
    df = read_data()
    posts = df.to_dict('records')
    post = next((p for p in posts if p['title'] == title), None)
    if not post:
        return 'Blog not found', 404
    return render_template('blog_detail.html', post=post)








@app.route('/')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signout')
def signout():
    # session.pop('user_id')
    # return redirect('/')
    if 'user_id' not in session:
        return redirect('/')
    else:
        session.pop('user_id')
        return redirect('/')
# cursor.execute("""SELECT *From `users`""")
# users = cursor.fetchall()
# s=users[0][1]


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        df = read_data()
        # Create a new row for the new post
        new_post_data = {
            'title': title,
            'content': content,

            'author': author,  # You may want to change this based on user authentication
        }
        df = df._append(new_post_data, ignore_index=True)
        
        # Write the updated DataFrame back to the Excel file
        write_data(df)
        
        # Your code to add a new post to the Excel file goes here
        return redirect('/home')
    return render_template('new_post.html')

@app.route('/edit_post/<title1>', methods=['GET', 'POST'])
def edit_post(title1):
    title='title'
    df = read_data()
    post = df.loc[df.index == title1].iloc[0]
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        df.loc[df.title == title1, 'title'] = title
        df.loc[df.title == title1, 'content'] = content
        write_data(df)
        
        return redirect(url_for('blog'))
    
    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<title1>')
def delete_post(title1):
    df = read_data()
    df = pd.DataFrame(df)
    condition = df['title'] == title1
    df = df[~condition]
    df = df.reset_index(drop=True)
    write_data(df)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
