from flask import Flask, render_template, request, redirect, url_for
from mysql.connector import Error
import mysql.connector
import os
import re

UPLOAD_FOLDER = 'static/img/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection  = mysql.connector.connect(host="localhost",user="root",password="12345", database="ott")
mycursor = connection.cursor(buffered=True)

def create_user_table():
    try:
        user_table_query = f"""
        CREATE TABLE IF NOT EXISTS `users` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            mobile VARCHAR(15) NOT NULL,
            password VARCHAR(15) NOT NULL
        )
        """
        mycursor.execute(user_table_query)
        connection.commit()
        return True
    except Exception as e:
        print(f"Create User Table Function Error: {e}")
        return False
    
def create_movie_table():
    try:
        movie_table_query = f"""
        CREATE TABLE IF NOT EXISTS `movies` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        director VARCHAR(50) NOT NULL,
        cast VARCHAR(200) NOT NULL,
        imgfile VARCHAR(150) NOT NULL,
        country VARCHAR(50) NOT NULL,
        year VARCHAR(50) NOT NULL,
        rating VARCHAR(50) NOT NULL,
        duration VARCHAR(50) NOT NULL,
        type VARCHAR(50) NOT NULL,
        description TEXT NOT NULL
        );
        """
        mycursor.execute(movie_table_query)
        connection.commit()
        return True
    except Exception as e:
        print(f"Create Movie Table Function Error: {e}")
        return False

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/user_reg', methods = ['POST','GET'])
def use_reg():
    try:
        if request.method == 'POST':
            name = request.form.get('username')
            phone = request.form.get('phone')
            password = request.form.get('password')
            user_table = create_user_table()
            if user_table:
                sql = 'INSERT INTO `users` (`name`, `mobile`, `password`) VALUES (%s, %s, %s)'
                val = (name, phone, password)
                mycursor.execute(sql, val)
                connection.commit()
                return render_template('login.html')
            print("User Table Not Exists")
    except Exception as e:
        print(f"User Registration Function Error: {e}")

@app.route('/index')
def index():
    try:
        movie_table = create_movie_table()
        if movie_table:
            sql = 'SELECT * FROM `movies` ORDER BY `id` DESC;'
            mycursor.execute(sql)
            result = mycursor.fetchall()
            if result:
                return render_template('index.html', data = result)
            else:
                return render_template('index.html', msg = 'No Movies')
    except Exception as e:
        print(f"Index Function Error: {e}")

@app.route('/view')
def view():
    sql = 'SELECT * FROM `movies`'
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if result:
        return render_template('view.html', data = result)
    else:
        return render_template('view.html', msg = 'No Movies Available')

@app.route('/validate',methods = ['POST','GET'])
def validate():
    if request.method == 'POST':
        uname = request.form.get('username')
        upass = request.form.get('password')
        sql = 'SELECT * FROM `users` WHERE `name` = %s AND `password` = %s'
        val = (uname, upass)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        if request.form.get('username') == 'admin' and request.form.get('password') == '1234':
            return render_template('admin.html')
        elif result:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', msg = 'Invalid Data')
        
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/upload', methods = ['POST','GET'])
def upload():
    if request.method == 'POST':
        imgfile = request.files['imgfile']
        print(imgfile)
        title = request.form.get('title')
        director = request.form.get('director')
        cast = request.form.get('cast')
        country = request.form.get('country')
        year = request.form.get('year')
        rating = request.form.get('rating')
        duration = request.form.get('duration')
        type = request.form.get('type')
        desc = request.form.get('desc')
        img_ = os.path.join(app.config['UPLOAD_FOLDER'], imgfile.filename)
        imgfile.save(img_)

        sql = 'INSERT INTO `movies` (`imgfile`, `title`, `director`, `cast`, `country`, `year`, `rating`, `duration`, `type`, `description`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        val = (img_, title, director, cast, country, year, rating, duration, type, desc)
        mycursor.execute(sql, val)
        connection.commit()
        return render_template('admin.html',msg = 'Movie uploaded Successfully')

@app.route('/details', methods = ['POST','GET'])
def details():
    if request.method == 'POST':
        title = request.form.get('title')

        sql = 'SELECT * FROM `movies` WHERE `title` = %s'
        val = (title, )
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        return render_template('details.html', data = result)

@app.route('/search_select', methods = ['POST','GET'])
def search_select():
    if request.method == 'POST':
        movie = request.form.get('movie_name')
        if movie == 'top_20':
            sql = 'SELECT * FROM `movies` WHERE `top_20` = %s'
            val = ('yes', )
        elif movie == 'top_40':
            sql = 'SELECT * FROM `movies` WHERE `top_40` = %s'
            val = ('yes', )
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
        if result:
            return render_template('index.html', data = result)
        else:
            return render_template('index.html', msg = 'No Similar Movies')

@app.route('/search',methods = ['POST','GET'])
def search():
    if request.method == 'POST':
        movie = request.form.get('movie_name')
        movie = movie.lower()
        sql = 'SELECT * FROM `movies`'
        mycursor.execute(sql)
        result = mycursor.fetchall()
        result1 = []
        for i in result:
            s = re.split(',|&',i[9])
            s = [x.lower() for x in s]
            s = [x.strip() for x in s]
            if movie in s:
                result1.append(i)
        if result1:
            return render_template('index.html', data = result1)
        else:
            sql = 'SELECT `type` FROM `movies` WHERE `title` = %s'
            val = (movie, )
            mycursor.execute(sql, val)
            result1 = mycursor.fetchone()
            if result1:
                s = re.split(',|&',result1[0])
                s = [x.lower() for x in s]
                s1 = [x.strip() for x in s]
                sql = 'SELECT * FROM `movies`'
                mycursor.execute(sql)
                result = mycursor.fetchall()
                result1 = []
                for i in result:
                    # print(i)
                    s = re.split(',|&',i[9])
                    s = [x.lower() for x in s]
                    s = [x.strip() for x in s]
                    if s1[0] in s:
                        print(i)
                        result1.append(i)
                if result1:
                    return render_template('index.html', data = result1)
                else:
                    return render_template('index.html', msg = 'No Similar Movies')
            else:
                return render_template('index.html', msg = 'No Similar Movies')

@app.route('/delete', methods = ['POST','GET'])
def delete():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        sql = 'DELETE FROM `movies` WHERE  `title` = %s AND `year` = %s'
        val = (title, year)
        mycursor.execute(sql,val)
        connection.commit()
        return redirect(url_for('view'))

if __name__ == '__main__':
    app.run(debug=True)