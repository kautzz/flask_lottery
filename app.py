import os
import sys
from random import randrange

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_db_connection():
	if os.path.isfile('/home/elg0rd0/flask_lottery/database.db'):
		conn = sqlite3.connect('/home/elg0rd0/flask_lottery/database.db')
		print ("running on pyanywhere", file=sys.stderr)
	else:
		conn = sqlite3.connect('database.db')
		print ("running locally", file=sys.stderr)
	conn.row_factory = sqlite3.Row
	return conn

def get_post(post_code):
	conn = get_db_connection()
	post = conn.execute('SELECT * FROM posts WHERE code = ?',
						(post_code,)).fetchone()
	conn.close()
	if post is None:
		abort(404)
	return post

def get_images(image_code):
	conn = get_db_connection()
	post = conn.execute('SELECT * FROM images WHERE code = ?',
						(image_code,)).fetchall()
	conn.close()
	return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DAsSupErGehEImeSchlUESseLDinG'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#It will allow below 16MB contents only, you can change it
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024



@app.route('/')
def index():
	return render_template('index.html')

@app.route('/tickets')
def tickets():
	conn = get_db_connection()
	tickets = conn.execute('SELECT * FROM tickets').fetchall()
	conn.close()
	return render_template('tickets.html', tickets=tickets)

@app.route('/posts')
def posts():
	conn = get_db_connection()
	posts = conn.execute('SELECT * FROM posts').fetchall()
	conn.close()
	return render_template('posts.html', posts=posts)

@app.route('/<post_code>')
def post(post_code):
	post = get_post(post_code)
	images = get_images(post_code)
	print(images, file=sys.stderr)

	return render_template('post.html', post=post, images=images)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/uploads')
# def upload_form():
#     return render_template('uploads.html')


@app.route('/uploads', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File(s) successfully uploaded')
        return redirect('/')

# @app.route('/uploads/<filename>')
# def display_image(filename):
# 	#print('display_image filename: ' + filename)
# 	return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/create', methods=('GET', 'POST'))
def create():
	if request.method == 'POST':
		code    = request.form['code']
		name    = request.form['name']
		country = request.form['country']
		city    = request.form['city']
		content = request.form['content']
		files	= request.files.getlist('files[]')

		if not code or not name or not country or not city or not content:
			flash('Please fill out all fields!')
		else:

			conn = get_db_connection()
			tickets = conn.execute('SELECT * FROM tickets').fetchall()

			print('---------------------------------')
			print('Checking Ticket Code!', file=sys.stderr)
			print('---------------------------------')
			mat = 0
			for s in range(len(tickets)):

				if tickets[s]["ticket_id"] == code and tickets[s]["valid"] == 0:
					print(tickets[s]['ticket_id'], file=sys.stderr)
					print('already used...', file=sys.stderr)
					flash('Ticket already registered!')
					return render_template('create.html')
					#mat = 1
					#break

				if tickets[s]["ticket_id"] == code and tickets[s]["valid"] == 1:
					print(tickets[s]['ticket_id'], file=sys.stderr)
					#conn = get_db_connection()
					conn = get_db_connection()
					conn.execute('INSERT INTO posts (code, name, country, city, content) VALUES (?, ?, ?, ?, ?)',(code, name, country, city, content))
					conn.execute('UPDATE tickets SET valid = 0 WHERE ticket_id = ?',(code,))

					for file in files:
						if file and allowed_file(file.filename):
							filename = secure_filename(file.filename)
							file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
							conn.execute('INSERT INTO images (code, filename) VALUES (?, ?)',(code, filename))

					conn.commit()
					conn.close()


					return redirect(url_for('posts'))
			flash('Invalid ticket code!')
	return render_template('create.html')


@app.route('/reset')
def reset():

	conn = get_db_connection()
	tickets = conn.execute('SELECT * FROM tickets').fetchall()

	print('---------------------------------')
	print('Tickets: ', file=sys.stderr)
	print('---------------------------------')

	for s in range(len(tickets)):
		print(tickets[s]['ticket_id'], file=sys.stderr)

	conn.execute('UPDATE tickets SET valid = 1')
	conn.commit()
	conn.close()
	flash('Tickets Reset!')

	return redirect(url_for('tickets'))


@app.route('/<code>/edit', methods=('GET', 'POST'))
def edit(code):
	post = get_post(code)

	if request.method == 'POST':
		name    = request.form['name']
		country = request.form['country']
		city    = request.form['city']
		content = request.form['content']

		if not name or not country or not city or not content:
			flash('Please fill out all fields!')
		else:
			conn = get_db_connection()
			conn.execute('UPDATE posts SET name = ?, country = ?, city = ?, content = ?'
						 ' WHERE code = ?',
						 (name, country, city, content, code))
			conn.commit()
			conn.close()
			return redirect(url_for('index'))

	return render_template('edit.html', post=post)

@app.route('/<code>/delete', methods=('POST',))
def delete(code):
	post = get_post(code)
	conn = get_db_connection()
	conn.execute('DELETE FROM posts WHERE code = ?', (code,))
	conn.execute('UPDATE tickets SET valid = 1 WHERE ticket_id = ?', (code,))
	conn.commit()
	conn.close()
	flash('"{}" was successfully deleted!'.format(post['name']))
	return redirect(url_for('index'))

@app.route('/lottery')
def lottery():
	conn = get_db_connection()
	posts = conn.execute('SELECT * FROM posts').fetchall()

	winner = randrange(len(posts))
	win = posts[winner]
	code = win[2]

	images = conn.execute('SELECT * FROM images WHERE code = ?', (code,))


	print(win[3], file=sys.stderr)
	print(code, file=sys.stderr)
	conn.commit()


	return render_template('lottery.html', win=win, images=images)
