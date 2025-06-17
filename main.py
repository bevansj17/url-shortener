from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import shortuuid
import validators
from datetime import datetime

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'  # Your MySQL password
app.config['MYSQL_DB'] = 'url_shortener'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        
        if not validators.url(original_url):
            return render_template('index.html', error='Invalid URL')
        
        # Generate short code
        short_code = shortuuid.ShortUUID().random(length=6)
        
        # Save to database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO urls (original_url, short_code) VALUES (%s, %s)", 
                   (original_url, short_code))
        mysql.connection.commit()
        cur.close()
        
        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)
    
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
    result = cur.fetchone()
    cur.close()
    
    if result:
        # Update click count
        cur = mysql.connection.cursor()
        cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s", (short_code,))
        mysql.connection.commit()
        cur.close()
        
        return redirect(result['original_url'])
    else:
        return render_template('404.html'), 404

@app.route('/stats')
def stats():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM urls ORDER BY created_at DESC")
    urls = cur.fetchall()
    cur.close()
    return render_template('stats.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)