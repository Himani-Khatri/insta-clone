from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil import parser
from flask import g
import time
import speech_recognition as sr
from flask_login import current_user
from werkzeug.security import check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import current_user
# from bee_intelligence import BeeAI, VoiceRecognizer, TTSEngine
from flask_wtf.csrf import CSRFProtect
# import os
# from flask import Flask

# app = Flask(__name__)

# # your existing routes are here

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)


# bee_ai = BeeAI()
# voice_recognizer = VoiceRecognizer()
# tts_engine = TTSEngine()



import os
from flask import Flask, send_from_directory, session, redirect, url_for, request, make_response
from flask_login import LoginManager, UserMixin

# -----------------------------
# Define paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))           # backend folder
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")        # frontend folder
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")       # frontend/templates
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")             # frontend/static

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,  # not using render_template, but keeps folder reference
    static_folder=STATIC_DIR
)

# -----------------------------
# Configurations
# -----------------------------
app.secret_key = 'mysecretkey1234'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SESSION_TYPE'] = 'filesystem'
login_manager.login_view = "login_page" 

UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'wav', 'mp3', 'ogg'}

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

class User(UserMixin):
    def __init__(self, id):
        self.id = id




@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_following_users(current_user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT followee FROM followers WHERE follower = ?;
    """, (current_user,))
    following_users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return following_users

def delete_user_account(user_id):
    conn = sqlite3.connect('your_database.db')  
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM hive WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()

def find_user_in_database(username):
    try:
        connection = sqlite3.connect('bee.db')  
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        connection.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "name": user[2],
                "profile_pic": user[3]
            }
        else:
            return None
    except Exception as e:
        print(f"Error finding user in database: {e}")
        return None
def find_user_suggestions(prefix):
    try:
        connection = sqlite3.connect('bee.db')  
        cursor = connection.cursor()

        cursor.execute("SELECT username FROM users WHERE username LIKE ? LIMIT 5", (prefix + '%',))
        users = cursor.fetchall()
        connection.close()

        return [user[0] for user in users]
    except Exception as e:
        print(f"Error finding user suggestions: {e}")
        return []

def verify_password(input_password):
    return check_password_hash(current_user.password, input_password)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('bee.db', check_same_thread=False)
    return g.db
def execute_with_retry(cursor, query, params, retries=5, delay=0.1):
    for attempt in range(retries):
        try:
            cursor.execute(query, params)
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(delay)
            else:
                raise
    raise sqlite3.OperationalError("Max retries reached for database query.")

def get_chat_messages(user1, user2):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message_content, timestamp 
        FROM messages 
        WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
        ORDER BY timestamp ASC
    """, (user1, user2, user2, user1))
    messages = [{'sender': row[0], 'content': row[1], 'timestamp': row[2]} for row in cursor.fetchall()]
    conn.close()
    return messages




def send_message(sender, recipient, content, media_path=None, media_type=None):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (sender, recipient, message_content, timestamp, media_path, media_type)
        VALUES (?, ?, ?, datetime('now'), ?, ?)
    """, (sender, recipient, content, media_path, media_type))
    conn.commit()
    conn.close()



def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'webm', 'wav', 'mp3', 'ogg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def time_ago(timestamp):
    now = datetime.now()
    timestamp = parser.parse(timestamp)
    diff = now - timestamp

    day = timestamp.day

    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    formatted_date = timestamp.strftime(f"{day}{suffix} %b")

    return formatted_date



def setup_database():
    connection = sqlite3.connect("bee.db")
    cursor = connection.cursor()
    
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS hive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER NOT NULL,
        phone TEXT NOT NULL,
        profile_picture TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        content TEXT,
        photo_url TEXT,
        video_url TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS followers (
        follower_username TEXT NOT NULL,
        followed_username TEXT NOT NULL,
        PRIMARY KEY (follower_username, followed_username)
    );
    ''')

    migrate_datetimes()

    connection.commit()
    connection.close()
def migrate_datetimes():
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, blocked_until FROM voice_assistant_blocks")
    blocks = cursor.fetchall()
    
    for username, old_date in blocks:
        try:
            # Convert to UTC datetime
            new_date = datetime.fromisoformat(old_date).astimezone(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE voice_assistant_blocks 
                SET blocked_until = ?
                WHERE username = ?
            """, (new_date, username))
        except Exception as e:
            print(f"Migration error: {e}")
            cursor.execute("DELETE FROM voice_assistant_blocks WHERE username = ?", (username,))
    
    conn.commit()
    conn.close()

def get_posts_by_user(username):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT content, photo_url, video_url, timestamp FROM posts WHERE username = ?", (username,))
    posts = cursor.fetchall()
    
    conn.close()
    
    post_list = []
    for post in posts:
        post_dict = {
            'content': post[0],
            'photo_url': post[1],
            'video_url': post[2],
            'timestamp': post[3]
        }
        post_list.append(post_dict)
    
    return post_list

def get_db_connection():
    conn = sqlite3.connect('bee.db')  
    conn.row_factory = sqlite3.Row 
    return conn
def get_user_posts_from_db(username):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, content, photo_url, video_url, timestamp FROM posts WHERE username = ? ORDER BY timestamp DESC', (username,))
    posts = cursor.fetchall()

    conn.close()
    return posts
def get_user_by_username(username):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()  
    
    conn.close()
    
    if user:
        return {
            'username': user[0],
            'email': user[1],
            'profile_picture': user[2],
        }
    return None

def get_user_by_username(username):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone() 
    
    conn.close()
    
    if user:
        return {
            'username': user[1], 
            'email': user[2],     
            'profile_picture': user[4],  
        }
    return None


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form  

        connection = sqlite3.connect("bee.db")
        connection.row_factory = sqlite3.Row 
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM hive WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        connection.close()

        if user:
            session['user_id'] = user['id']  
            session['username'] = username  

            if remember_me:
                resp = make_response(redirect(url_for('home_page')))
                resp.set_cookie('username', username, max_age=30*24*60*60)  
                return resp
            else:
                return redirect(url_for('home_page'))
        else:
            error = "Login Failed. Invalid username or password. Please try again."
    
    username_from_cookie = request.cookies.get('username')

    return render_template('index.html', error=error, username=username_from_cookie)

from flask import send_file

# Example usage in your route
def verify_user_identity():
    """
    Verify the identity of the current user based on the session.
    """
    if 'username' not in session:
        return None  # User is not logged in
    
    # You can add more sophisticated checks here, such as verifying against a database
    return session['username']


    # try:
    #     if mode == 'audio':
    #         audio_file = request.files['audio']
    #         text = voice_recognizer.transcribe(audio_file)
    #     else:
    #         text = request.json.get('text', '')
        
    #     response = bee_ai.process_input(user_id, text)
        
    #     if mode == 'audio':
    #         audio_path = tts_engine.generate_speech(response)
    #         return send_file(audio_path, mimetype='audio/wav')
        
    #     return jsonify({
    #         'text_response': response,
    #         'voice_url': url_for('static', filename=f'tts/{os.path.basename(audio_path)}')
    #     })
    
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        age = int(request.form['age'])
        phone = request.form['phone']

        if age < 15:
            error = "You must be at least 15 years old to sign up."
            return render_template('signup.html', error=error)

        if password != repassword:
            error = "Passwords do not match. Please try again."
            return render_template('signup.html', error=error)

        if password.isalpha():
            error = "Password is too weak. Use a combination of letters and numbers or special characters."
            return render_template('signup.html', error=error)
        if len(phone) != 10 or not phone.isdigit():
            error = "Phone number must be exactly 10 digits."
            return render_template('signup.html', error=error)

        connection = sqlite3.connect("bee.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM hive WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            error = "Username already taken. Please choose another."
            connection.close()
            return render_template('signup.html', error=error)
        cursor.execute("SELECT * FROM hive WHERE phone = ?", (phone,))
        user = cursor.fetchone()

        if user:
            error = "Phone number already used. Please choose another."
            connection.close()
            return render_template('signup.html', error=error)
        cursor.execute("INSERT INTO hive (username, password, age, phone) VALUES (?, ?, ?, ?)",
                       (username, password, age, phone))
        connection.commit()
        connection.close()

        return redirect(url_for('login_page'))

    return render_template('signup.html', error=error)

def get_like_count(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) 
        FROM post_likes 
        WHERE post_id = ?
    """, (post_id,))
    like_count = cursor.fetchone()[0]
    return like_count



import random
import sqlite3
from flask import render_template, session, redirect, url_for

@app.route('/home')
def home_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    username = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    # Get the list of users the current user is following
    cursor.execute(""" 
        SELECT following 
        FROM followers 
        WHERE follower = ? 
    """, (username,))
    following_users = cursor.fetchall()
    following_usernames = [user[0] for user in following_users] if following_users else []

    # If the user is following others, fetch posts from followed users
    if following_usernames:
        cursor.execute(""" 
            SELECT p.post_id, p.username, p.content, p.photo_url, p.video_url, p.timestamp, p.like_count
            FROM posts p 
            LEFT JOIN hive u ON p.username = u.username 
            WHERE p.username IN ({}) AND u.deleted = 0 
            ORDER BY p.timestamp DESC
            LIMIT 20
        """.format(','.join('?' for _ in following_usernames + [username])), following_usernames + [username])
    else:
        # If the user isn't following anyone, show their own posts
        cursor.execute(""" 
            SELECT p.post_id, p.username, p.content, p.photo_url, p.video_url, p.timestamp, p.like_count
            FROM posts p 
            LEFT JOIN hive u ON p.username = u.username 
            WHERE p.username = ? AND u.deleted = 0 
            ORDER BY p.timestamp DESC
            LIMIT 20
        """, (username,))

    posts = cursor.fetchall()

    # Shuffle the posts to display them randomly
    random.shuffle(posts)

    posts_with_reactions = []
    for post in posts:
        cursor.execute("SELECT profile_picture FROM hive WHERE username = ?", (post[1],))
        result = cursor.fetchone()
        profile_picture = result[0] if result else 'd1.jpg'

        cursor.execute(""" 
            SELECT 1 
            FROM post_likes 
            WHERE post_id = ? AND username = ? 
        """, (post[0], username))
        is_liked = cursor.fetchone() is not None

        cursor.execute(""" 
            SELECT c.comment_id, c.username, c.content, c.timestamp, h.profile_picture
            FROM comments c
            LEFT JOIN hive h ON c.username = h.username
            WHERE c.post_id = ?
            ORDER BY c.timestamp DESC
        """, (post[0],))
        comments = cursor.fetchall()

        comments_with_replies = []
        for comment in comments:
            cursor.execute(""" 
                SELECT r.reply_id, r.username, r.content, r.timestamp, h.profile_picture 
                FROM comment_replies r 
                LEFT JOIN hive h ON r.username = h.username 
                WHERE r.comment_id = ? 
                ORDER BY r.timestamp ASC
            """, (comment[0],))
            replies = cursor.fetchall()
            comments_with_replies.append({
                'comment_id': comment[0],
                'username': comment[1],
                'content': comment[2],
                'timestamp': time_ago(comment[3]),
                'profile_picture': comment[4] if comment[4] else 'd1.jpg',
                'replies': [{
                    'reply_id': reply[0],
                    'username': reply[1],
                    'content': reply[2],
                    'timestamp': time_ago(reply[3]),
                    'profile_picture': reply[4] if reply[4] else 'd1.jpg'
                } for reply in replies]
            })

        posts_with_reactions.append({
            'post_id': post[0],
            'username': post[1],
            'content': post[2],
            'photo_url': post[3],
            'video_url': post[4],
            'timestamp': time_ago(post[5]),
            'profile_picture': profile_picture,
            'like_count': post[6],
            'is_liked': is_liked,
            'comments': comments_with_replies
        })

    # Fetch suggested users who the current user doesn't follow
    cursor.execute(""" 
        SELECT username, profile_picture 
        FROM hive 
        WHERE username NOT IN ({}) AND username != ? AND deleted = 0 
        LIMIT 5
    """.format(','.join('?' for _ in following_usernames)), following_usernames + [username])
    suggested_users = cursor.fetchall()

    suggested_user_details = [
        {
            'username': user[0],
            'profile_picture': user[1] if user[1] else 'd1.jpg'
        } for user in suggested_users
    ]

    # Count unread notifications for the current user
    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (username,))
    unread_count = cursor.fetchone()[0]

    conn.close()
    theme = session.get('theme', 'default')

    # Render the home page with the fetched and shuffled posts
    return render_template('home.html', 
                         posts=posts_with_reactions, 
                         suggested_users=suggested_user_details, 
                         unread_count=unread_count,
                         theme=theme)



@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    
    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM posts WHERE post_id = ?", (post_id,))
        post_data = cursor.fetchone()
        
        if not post_data:
            return jsonify({'error': 'Post not found'}), 404
            
        post_author = post_data[0]
        
        should_notify = username != post_author
        
        cursor.execute("""
            SELECT 1 FROM post_likes 
            WHERE post_id = ? AND username = ?
        """, (post_id, username))
        
        already_liked = cursor.fetchone() is not None
        
        if not already_liked:
            cursor.execute("""
                INSERT INTO post_likes (post_id, username) 
                VALUES (?, ?)
            """, (post_id, username))
            
            cursor.execute("""
                UPDATE posts 
                SET like_count = like_count + 1 
                WHERE post_id = ?
            """, (post_id,))
            
            if should_notify:
                cursor.execute("""
                    INSERT INTO notifications (
                        user_id,
                        type,
                        sender,
                        message,
                        timestamp,
                        is_read
                    ) VALUES (
                        (SELECT id FROM hive WHERE username = ?),
                        'like',
                        ?,
                        ?,
                        datetime('now'),
                        0
                    )
                """, (post_author, username, f"{username} liked your post"))
        else:
            cursor.execute("""
                DELETE FROM post_likes 
                WHERE post_id = ? AND username = ?
            """, (post_id, username))
            
            cursor.execute("""
                UPDATE posts 
                SET like_count = CASE 
                    WHEN like_count > 0 THEN like_count - 1 
                    ELSE 0 
                END 
                WHERE post_id = ?
            """, (post_id,))
        
        cursor.execute("SELECT like_count FROM posts WHERE post_id = ?", (post_id,))
        new_like_count = cursor.fetchone()[0]
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'like_count': new_like_count,
            'is_liked': not already_liked
        })
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if conn:
            conn.close()
            
@app.route('/edit_post/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    username = session['username']
    content = request.json.get('content', '').strip()  

    if not content:
        return jsonify({'error': 'Content cannot be empty'}), 400

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username FROM posts WHERE post_id = ?
    """, (post_id,))
    post_owner = cursor.fetchone()

    if not post_owner or post_owner[0] != username:
        conn.close()
        return jsonify({'error': 'Unauthorized action'}), 403

    cursor.execute("""
        UPDATE posts
        SET content = ?
        WHERE post_id = ?
    """, (content, post_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Post edited successfully', 'content': content})

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    username = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT username, photo_url, video_url FROM posts WHERE post_id = ?
        """, (post_id,))
        post_data = cursor.fetchone()

        if not post_data or post_data[0] != username:
            conn.close()
            return jsonify({'error': 'Unauthorized action'}), 403

        cursor.execute("DELETE FROM post_likes WHERE post_id = ?", (post_id,))

        cursor.execute("""
            DELETE FROM notifications 
            WHERE type = 'like' AND message LIKE ? AND user_id = (
                SELECT id FROM hive WHERE username = ?
            )
        """, (f"%post {post_id}%", username))

        cursor.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))

        if post_data[1] and post_data[1] != 'None':
            try:
                os.remove(os.path.join('static/uploads', post_data[1]))
            except OSError:
                pass 

        if post_data[2] and post_data[2] != 'None':
            try:
                os.remove(os.path.join('static/uploads', post_data[2]))
            except OSError:
                pass  

        conn.commit()
        return jsonify({'success': True, 'message': 'Post and all associated data deleted successfully'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/profile')
def profile_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    username = session['username']
    
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, age, phone, profile_picture, bio FROM hive WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        flash("User not found.", "danger")
        return redirect(url_for('home_page'))  

    user_details = {
        'id': user[0],
        'username': user[1],
        'age': user[2],
        'phone': user[3],
        'profile_picture': user[4] if user[4] else 'd1.jpg',  
        'bio': user[5] 
    }

    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM followers f
        LEFT JOIN hive h ON f.follower = h.username
        WHERE f.following = ? AND h.deleted = 0
    """, (username,))
    followers_count = cursor.fetchone()[0]

    cursor.execute(""" 
        SELECT COUNT(*) 
        FROM followers f
        LEFT JOIN hive h ON f.following = h.username
        WHERE f.follower = ? AND h.deleted = 0
    """, (username,))
    following_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT p.post_id, p.username, p.content, p.photo_url, p.video_url, p.timestamp, p.like_count,
               (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.post_id AND pl.username = ?) as is_liked
        FROM posts p
        WHERE p.username = ? 
        ORDER BY p.timestamp DESC
    """, (username, username))
    posts = cursor.fetchall()

    formatted_posts = []
    for post in posts:
        post_timestamp = datetime.strptime(post[5], "%Y-%m-%d %H:%M:%S") 
        formatted_timestamp = post_timestamp.strftime("%d %b %Y")  
        formatted_posts.append(post + (formatted_timestamp,))

    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (username,))
    unread_count = cursor.fetchone()[0]

    conn.close()
    
    return render_template(
        'profile.html', 
        user=user_details, 
        posts=formatted_posts,
        followers_count=followers_count, 
        following_count=following_count,
        unread_count=unread_count
    )



@app.route('/update_profile_picture', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    username = session['username']
    profile_picture = request.files.get('profile_picture')

    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture.save(file_path)

        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE hive SET profile_picture = ? WHERE username = ?", (filename, username))
        conn.commit()
        conn.close()

        flash("Profile picture updated successfully!", "success")

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (username,))
    unread_count = cursor.fetchone()[0]  
    conn.close()

    return redirect(url_for('profile_page', username=username, unread_count=unread_count))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    username = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, age, phone, profile_picture, bio FROM hive WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user[3]:
        profile_picture = user[3]
    else:
        profile_picture = 'd1.jpg'

    if request.method == 'POST':
        file = request.files.get('profile_picture')

        if file:
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)
            
            filename = f"{username}_{file.filename}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            conn = sqlite3.connect('bee.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE hive SET profile_picture = ? WHERE username = ?", (file_path, username))
            conn.commit()
            conn.close()

            return redirect(url_for('profile_page', username=username))

        if 'update_bio' in request.form:
            bio = request.form.get('bio', '').strip()
            conn = sqlite3.connect('bee.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE hive SET bio = ? WHERE username = ?", (bio, username))
            conn.commit()
            conn.close()

            return redirect(url_for('profile_page', username=username))

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (username,))
    unread_count = cursor.fetchone()[0]
    conn.close()

    return render_template('edit_profile.html', user=user, profile_picture=profile_picture, unread_count=unread_count)
@app.route('/post', methods=['GET', 'POST'])
def post_content():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    username = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hive WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        content = request.form.get('content') 
        photo_url = None
        video_url = None

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                photo_filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                photo_url = photo_filename

        if 'video' in request.files:
            video = request.files['video']
            if video and allowed_file(video.filename):
                video_filename = secure_filename(video.filename)
                video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))
                video_url = video_filename

        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (username, content, photo_url, video_url) VALUES (?, ?, ?, ?)",
                       (username, content, photo_url, video_url))
        conn.commit()
        conn.close()

        return redirect(url_for('home_page'))

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (username,))
    unread_count = cursor.fetchone()[0]
    conn.close()

    return render_template('post.html', user=user, unread_count=unread_count)


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    if request.method == 'POST':
        session.pop('username', None)  
        return redirect(url_for('login_page'))  
    return render_template('logout.html') 

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    search_query = None
    users = []
    current_user = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    # Get unread notifications count
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (current_user,))
    unread_count = cursor.fetchone()[0]

    # Handle search
    if request.method == 'POST':
        search_query = request.form['search_query']
        
        cursor.execute("SELECT id, username, age, phone, profile_picture, followers FROM hive WHERE username LIKE ?", ('%' + search_query + '%',))
        rows = cursor.fetchall()
        
        for row in rows:
            cursor.execute("SELECT * FROM followers WHERE follower = ? AND following = ?", (current_user, row[1]))
            is_following = cursor.fetchone() is not None

            user = {
                'id': row[0],
                'username': row[1],
                'age': row[2],
                'phone': row[3],
                'profile_picture': row[4],
                'followers': row[5],
                'is_following': is_following
            }
            users.append(user)

    # Get explore posts (random posts from users not followed by current user)
    cursor.execute("""
        SELECT p.post_id, p.username, p.content, p.photo_url, p.video_url, p.timestamp, 
               h.profile_picture, p.like_count,
               EXISTS(SELECT 1 FROM post_likes WHERE post_id = p.post_id AND username = ?) as is_liked
        FROM posts p
        JOIN hive h ON p.username = h.username
        LEFT JOIN followers f ON p.username = f.following AND f.follower = ?
        WHERE f.follower IS NULL 
        AND p.username != ?
        AND (p.photo_url IS NOT NULL OR p.video_url IS NOT NULL)
        ORDER BY RANDOM()
        LIMIT 9
    """, (current_user, current_user, current_user))
    
    explore_posts = []
    for post in cursor.fetchall():
        explore_posts.append({
            'post_id': post[0],
            'username': post[1],
            'content': post[2],
            'photo_url': post[3],
            'video_url': post[4],
            'timestamp': post[5],
            'profile_picture': post[6] if post[6] else 'd1.jpg',
            'like_count': post[7],
            'is_liked': bool(post[8])
        })

    conn.close()

    return render_template('search.html', 
                         users=users, 
                         unread_count=unread_count, 
                         explore_posts=explore_posts)

@app.route('/profile/<username>')
def user_profile(username):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    logged_in_user = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    # Fetch unread notifications count
    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (logged_in_user,))
    unread_count = cursor.fetchone()[0]

    # Fetch user data
    cursor.execute("SELECT id, username, age, bio, profile_picture, followers FROM hive WHERE username = ?", (username,))
    user_data = cursor.fetchone()

    if user_data is None:
        flash('User not found', 'error')
        return redirect(url_for('search_page'))

    user = {
        'id': user_data[0],
        'username': user_data[1],
        'age': user_data[2],
        'bio': user_data[3],
        'profile_picture': user_data[4] or 'd1.jpg',
        'followers': user_data[5],
        'is_following': False
    }

    # Check if the logged-in user is following this user
    cursor.execute("SELECT * FROM followers WHERE follower = ? AND following = ?", (logged_in_user, username))
    user['is_following'] = cursor.fetchone() is not None

    # Fetch user posts
    cursor.execute("""
        SELECT p.post_id, p.username, p.content, p.photo_url, p.video_url, p.timestamp, p.like_count,
               CASE WHEN pl.username IS NOT NULL THEN 1 ELSE 0 END as is_liked
        FROM posts p
        LEFT JOIN post_likes pl ON p.post_id = pl.post_id AND pl.username = ?
        WHERE p.username = ?
        ORDER BY p.timestamp DESC
    """, (logged_in_user, username))
    
    user_posts = cursor.fetchall()
    
    formatted_posts = []
    for post in user_posts:
        post_timestamp = datetime.strptime(post[5], "%Y-%m-%d %H:%M:%S") 
        formatted_timestamp = post_timestamp.strftime("%d %b %Y")
        
        formatted_post = {
            'post_id': post[0],
            'username': post[1],
            'content': post[2],
            'photo_url': post[3],
            'video_url': post[4],
            'timestamp': formatted_timestamp,
            'like_count': post[6],
            'is_liked': bool(post[7])
        }
        formatted_posts.append(formatted_post)

    # Fetch following count
    cursor.execute("SELECT COUNT(*) FROM followers WHERE follower = ?", (username,))
    user['following'] = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'users.html',
        user=user,
        posts=formatted_posts,
        back_to_users_url=url_for('search_page'),
        unread_count=unread_count
    )

@app.route('/get_followers/<username>')
def get_followers(username):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    # Fetch followers with their profile pictures
    cursor.execute("""
        SELECT h.username, h.profile_picture 
        FROM followers f 
        JOIN hive h ON f.follower = h.username 
        WHERE f.following = ?
    """, (username,))
    followers = cursor.fetchall()

    conn.close()

    # Format the response
    followers_list = [{'username': follower[0], 'profile_picture': follower[1] or 'd1.jpg'} for follower in followers]
    return jsonify({'followers': followers_list})
@app.route('/get_following/<username>')
def get_following(username):
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    # Fetch following users with their profile pictures
    cursor.execute("""
        SELECT h.username, h.profile_picture 
        FROM followers f 
        JOIN hive h ON f.following = h.username 
        WHERE f.follower = ?
    """, (username,))
    following = cursor.fetchall()

    conn.close()

    # Format the response
    following_list = [{'username': user[0], 'profile_picture': user[1] or 'd1.jpg'} for user in following]
    return jsonify({'following': following_list})

@app.route('/follow/<username>', methods=['POST'])
def follow_user(username):
    if 'username' not in session:
        flash("You must be logged in to follow users.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM followers WHERE follower = ? AND following = ?", (current_user, username))
    existing_follow = cursor.fetchone()

    if existing_follow:
        cursor.execute("DELETE FROM followers WHERE follower = ? AND following = ?", (current_user, username))
        cursor.execute("UPDATE hive SET followers = followers - 1 WHERE username = ?", (username,))
        cursor.execute("UPDATE hive SET following = following - 1 WHERE username = ?", (current_user,))

        action = 'unfollow'
        cursor.execute("""
            INSERT INTO notifications (user_id, sender, type, message, is_read) 
            VALUES ((SELECT id FROM hive WHERE username = ?), ?, 'unfollow', ?, 0)
        """, (username, current_user, f"{current_user} has unfollowed you"))
        
    else:
        cursor.execute("INSERT INTO followers (follower, following) VALUES (?, ?)", (current_user, username))
        cursor.execute("UPDATE hive SET followers = followers + 1 WHERE username = ?", (username,))
        cursor.execute("UPDATE hive SET following = following + 1 WHERE username = ?", (current_user,))

        action = 'follow'
        cursor.execute("""
            INSERT INTO notifications (user_id, sender, type, message, is_read) 
            VALUES ((SELECT id FROM hive WHERE username = ?), ?, 'follow', ?, 0)
        """, (username, current_user, f"{current_user} is now following you"))

    conn.commit()

    cursor.execute("SELECT followers, following FROM hive WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    cursor.execute("SELECT following FROM hive WHERE username = ?", (current_user,))
    current_user_data = cursor.fetchone()

    conn.close()

    flash(f"You have {action}ed {username}.", "success")

    return redirect(url_for('user_profile', username=username, updated_followers=user_data[0], updated_following=current_user_data[0]))


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow_user(username):
    if 'username' not in session:
        flash("You must be logged in to unfollow users.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM followers WHERE follower = ? AND following = ?", (current_user, username))
    cursor.execute("UPDATE hive SET followers = followers - 1 WHERE username = ?", (username,))

    cursor.execute("""
        INSERT INTO notifications (user_id, sender, type, message, is_read) 
        VALUES ((SELECT id FROM hive WHERE username = ?), ?, 'unfollow', ?, 0)
    """, (username, current_user, f"{current_user} has unfollowed you"))

    conn.commit()
    conn.close()

    return redirect(url_for('user_profile', username=username))





def send_message_notification(sender, receiver, content=None, media_path=None, media_type=None):
    """Send message notification to the recipient"""
    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()

        if content:
            message = f'{sender} sent you a message: "{content}"'
        else:
            message = f'{sender} sent you a media message.'

        cursor.execute("""
            INSERT INTO notifications (user_id, type, sender, message)
            VALUES ((SELECT id FROM hive WHERE username = ?), ?, ?, ?)
        """, (receiver, 'message', sender, message))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting message notification: {e}")
    finally:
        conn.close()


@app.route('/create_voice_post', methods=['POST'])
def create_voice_post():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    content = request.form.get('content', '').strip()
    media_file = request.files.get('media')
    media_type = request.form.get('media_type', 'photo')  # Get media type from form data

    photo_url = None
    video_url = None

    if media_file and allowed_file(media_file.filename):
        filename = secure_filename(media_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        media_file.save(file_path)
        
        # Use media_type from form instead of file extension detection
        if media_type == 'photo':
            photo_url = filename
        elif media_type == 'video':
            video_url = filename

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO posts (username, content, photo_url, video_url) 
            VALUES (?, ?, ?, ?)
        """, (username, content, photo_url, video_url))
        conn.commit()
        return jsonify({'success': True, 'message': 'Post created successfully.'})

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/update_voice_assistant_state', methods=['POST'])
def update_voice_assistant_state():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    data = request.json
    state = data.get('state')

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE hive SET voice_assistant_state = ? WHERE username = ?", (state, username))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()



@app.route('/check_voice_assistant_state', methods=['GET'])
def check_voice_assistant_state():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT voice_assistant_state FROM hive WHERE username = ?", (username,))
        state = cursor.fetchone()
        if state and state[0] == 'active':
            return jsonify({'state': 'active'})
        else:
            return jsonify({'state': 'inactive'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()



@app.route('/follow_unfollow_voice', methods=['POST'])
def follow_unfollow_voice():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    action = data.get('action')  # 'follow' or 'unfollow'
    username = data.get('username')  # Username to follow/unfollow

    if not action or not username:
        return jsonify({'error': 'Missing action or username'}), 400

    current_user = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Check if the user exists
        cursor.execute("SELECT username FROM hive WHERE username = ?", (username,))
        user_exists = cursor.fetchone()

        if not user_exists:
            return jsonify({'error': f"User '{username}' does not exist."}), 404

        if action == 'follow':
            # Check if already following
            cursor.execute("""
                SELECT 1 FROM followers 
                WHERE follower = ? AND following = ?
            """, (current_user, username))
            already_following = cursor.fetchone()

            if already_following:
                return jsonify({'error': f"You are already following {username}."}), 400

            # Follow the user
            cursor.execute("""
                INSERT INTO followers (follower, following) 
                VALUES (?, ?)
            """, (current_user, username))
            message = f"You are now following {username}."

        elif action == 'unfollow':
            # Check if not following
            cursor.execute("""
                SELECT 1 FROM followers 
                WHERE follower = ? AND following = ?
            """, (current_user, username))
            not_following = cursor.fetchone() is None

            if not_following:
                return jsonify({'error': f"You are not following {username}."}), 400

            # Unfollow the user
            cursor.execute("""
                DELETE FROM followers 
                WHERE follower = ? AND following = ?
            """, (current_user, username))
            message = f"You have unfollowed {username}."

        else:
            return jsonify({'error': 'Invalid action'}), 400

        conn.commit()
        return jsonify({'success': True, 'message': message})

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/process_voice_command', methods=['POST'])
def process_voice_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "No command provided"}), 400

    command = data['command'].lower()

    if 'search' in command and 'user' in command:
        search_query = command.replace('search for user', '').replace('find user', '').strip()
        if search_query:
            return jsonify({"redirect": url_for('search_user', username=search_query)})
        else:
            return jsonify({"error": "Please specify a username to search for."}), 400
    # Other command handling...
    if 'home' in command:
        return jsonify({"redirect": url_for('home_page')})
    elif 'settings' in command:
        return jsonify({"redirect": url_for('settings_page')})
    elif 'messages' in command:
        return jsonify({"redirect": url_for('messages_page')})
    elif 'search' in command:
        if 'user' in command:
            search_query = None
            users = []
            current_user = session['username']

            if request.method == 'POST':
                search_query = request.form['search_query']
        
                conn = sqlite3.connect('bee.db')
                cursor = conn.cursor()
        
                cursor.execute("SELECT id, username, age, phone, profile_picture, followers FROM hive WHERE username LIKE ?", ('%' + search_query + '%',))
                rows = cursor.fetchall()
        
                for row in rows:
                    cursor.execute("SELECT * FROM followers WHERE follower = ? AND following = ?", (current_user, row[1]))
                    is_following = cursor.fetchone() is not None

                    user = {
                'id': row[0],
                'username': row[1],
                'age': row[2],
                'phone': row[3],
                'profile_picture': row[4],
                'followers': row[5],
                'is_following': is_following
                    }
                    users.append(user)
        
                conn.close()

            return jsonify({"action": "search_user"})
    elif 'post' in command:
        if 'photo' in command or 'video' in command:
            return jsonify({"action": "post_media"})
        else:
            return jsonify({"redirect": url_for('post_content')})
    elif 'notifications' in command:
        return jsonify({"redirect": url_for('notification_page')})
    elif 'profile' in command:
        if 'edit' in command:
            return jsonify({"action": "edit_profile"})
        else:
            return jsonify({"redirect": url_for('profile_page')})
    elif 'follow' in command:
        if 'unfollow' in command:
            return jsonify({"action": "unfollow_user"})
        else:
            return jsonify({"action": "follow_user"})
    elif 'logout' in command:
        return jsonify({"redirect": url_for('logout_page')})
    else:
        return jsonify({"error": "Command not recognized"}), 400

# In Python shell
from datetime import datetime, timedelta, timezone
blocked_until = datetime.now(timezone.utc) + timedelta(seconds=30)  # Test with 30s block
# Update database with test value
@app.route('/log_inappropriate_language', methods=['POST'])
def log_inappropriate_language():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    data = request.json
    command = data.get('command', '')

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Log the inappropriate language
        cursor.execute("""
            INSERT INTO inappropriate_language_logs (username, command, timestamp)
            VALUES (?, ?, ?)
        """, (username, command, datetime.now()))
        conn.commit()

        # Check if the user has used inappropriate language 3 or more times in the last 24 hours
        cursor.execute("""
            SELECT COUNT(*) 
            FROM inappropriate_language_logs 
            WHERE username = ? AND timestamp > ?
        """, (username, datetime.now() - timedelta(hours=24)))
        count = cursor.fetchone()[0]

        if count >= 3:
            # Block the voice assistant for 24 hours
            blocked_until = datetime.now(timezone.utc) + timedelta(seconds=120)
            cursor.execute("""
            INSERT OR REPLACE INTO voice_assistant_blocks (username, blocked_until)
            VALUES (?, ?)
            """, (username, blocked_until.isoformat()))
            conn.commit()

            return jsonify({
                'success': True,
                'message': 'Voice assistant disabled for 2 minutes due to inappropriate language.'
            })

        return jsonify({'success': True, 'message': 'Inappropriate language logged.'})

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/check_voice_assistant_block', methods=['GET'])
def check_voice_assistant_block():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT blocked_until FROM voice_assistant_blocks WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result and result[0]:
            try:
                blocked_until = datetime.fromisoformat(result[0]).replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                print(f"Current UTC: {current_time}, Blocked until: {blocked_until}")

                if current_time > blocked_until:
                    cursor.execute("DELETE FROM voice_assistant_blocks WHERE username = ?", (username,))
                    conn.commit()
                    return jsonify({'blocked': False})
                else:
                    return jsonify({
                        'blocked': True,
                        'blocked_until': blocked_until.isoformat()
                    })
            except ValueError as e:
                print(f"Error parsing datetime: {e}")
                # Cleanup invalid format
                cursor.execute("""
                    DELETE FROM voice_assistant_blocks 
                    WHERE username = ?
                """, (username,))
                conn.commit()

        return jsonify({'blocked': False})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/start_voice_assistant', methods=['POST'])
def start_voice_assistant():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT voice_assistant_disabled_until 
            FROM hive 
            WHERE username = ?
        """, (username,))
        disabled_until = cursor.fetchone()[0]

        if disabled_until and datetime.now() < datetime.strptime(disabled_until, '%Y-%m-%d %H:%M:%S'):
            return jsonify({'error': 'Voice assistant is disabled for 24 hours due to inappropriate language.'}), 403

        return jsonify({'success': True, 'message': 'Voice assistant started.'})

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
@app.route('/search_user', methods=['GET'])
def search_user():
    search_query = request.args.get('username', '').strip()

    if not search_query:
        return jsonify({'error': 'No username provided'}), 400

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Fetch all users matching the search query
        cursor.execute("""
            SELECT username, profile_picture 
            FROM hive 
            WHERE username LIKE ? AND deleted = 0
        """, (f"%{search_query}%",))
        users = cursor.fetchall()

        if not users:
            return jsonify({'error': 'No users found'}), 404

        # Format the response
        user_list = [{'username': user[0], 'profile_picture': user[1] or 'd1.jpg'} for user in users]
        return jsonify({'success': True, 'users': user_list})

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/settings')
def settings_page():
    current_user = session.get("username", "user1")  
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
    """, (current_user,))
    unread_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT f.follower 
        FROM followers f
        JOIN hive h ON f.follower = h.username
        WHERE f.following = ? AND h.deleted = 0
    """, (current_user,))
    followers = cursor.fetchall()
    followers_list = [f[0] for f in followers]

    cursor.execute("""
        SELECT f.following 
        FROM followers f
        JOIN hive h ON f.following = h.username
        WHERE f.follower = ? AND h.deleted = 0
    """, (current_user,))
    following = cursor.fetchall()
    following_list = [f[0] for f in following]

    conn.close()

    return render_template(
        'settings.html',
        followers=followers_list, 
        following=following_list,
        unread_count=unread_count  
    )

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' not in session:
        flash("You must be logged in to change your password.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM hive WHERE username = ?", (current_user,))
    result = cursor.fetchone()

    if result:
        db_password = result[0]

        if db_password != current_password:
            flash("😞Current password is incorrect!", "password_error")
            conn.close()
            return redirect(url_for('settings_page'))

        if new_password != confirm_password:
            flash("😢New passwords do not match!", "password_error")
            conn.close()
            return redirect(url_for('settings_page'))

        if not any(char in "!@#$%^&*()_+1234567890" for char in new_password) or len([char for char in new_password if char in "1234567890!@#$%^&*()_+"]) < 2:
            flash("😭Password must contain at least 2 special characters!", "password_error")
            conn.close()
            return redirect(url_for('settings_page'))

        cursor.execute("UPDATE hive SET password = ? WHERE username = ?", (new_password, current_user))
        conn.commit()
    else:
        flash("User not found in the database.", "password_error")

    conn.close()
    return redirect(url_for('login_page')) 


@app.route('/change_phone_number', methods=['POST'])
def change_phone_number():
    current_user = session.get("username", "user1") 
    new_phone_number = request.form.get('phone_number')

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM hive WHERE phone = ?", (new_phone_number,))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("😞Phone number is already in use!", "phone_error")
    else:
        cursor.execute("UPDATE hive SET phone = ? WHERE username = ?", (new_phone_number, current_user))
        conn.commit()
        flash("😊Phone number successfully updated!", "phone_success")

    conn.close()
    return redirect(url_for('settings_page'))



@app.route('/change_background', methods=['POST'])
def change_background():
    theme = request.form.get('theme')
    
    if theme:
        session['theme'] = theme
    
    flash("Theme successfully updated!", "success")
    return redirect(url_for('settings_page'))



@app.route('/followers')
def followers_page():
    if 'username' not in session:
        flash("You must be logged in to view followers.", "error")
        return redirect(url_for('login_page'))

    logged_in_user = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hive.username, hive.profile_picture
        FROM followers
        JOIN hive ON followers.following = hive.username
        WHERE followers.follower = ?
    """, (logged_in_user,))
    
    followers_data = cursor.fetchall()  
    followers = [{'username': data[0], 'profile_pic': data[1]} for data in followers_data]

    conn.close()

    return render_template('followers.html', followers=followers)


@app.route('/following')
def following_page():
    if 'username' not in session:
        flash("You must be logged in to view following.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']
    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hive.username, hive.profile_picture
        FROM followers
        JOIN hive ON followers.following = hive.username
        WHERE followers.follower = ?
    """, (current_user,))
    
    following_data = cursor.fetchall()  
    following = [{'username': data[0], 'profile_pic': data[1]} for data in following_data]

    conn.close()

    return render_template('settings.html', following=following, followers=None)  

@app.route('/delete_account', methods=['POST'])
def delete_account():
    data = request.json  
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required to delete the account'}), 400

    conn = get_db_connection()
    try:
        # First check if user exists
        user = conn.execute('SELECT * FROM hive WHERE username = ?', (username,)).fetchone()
        print(user)  
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Delete all posts by the user
        conn.execute('DELETE FROM posts WHERE username = ?', (username,))
        
        # Delete all follows relationships
        conn.execute('DELETE FROM follows WHERE follower = ? OR followee = ?', (username, username))
        
        # Delete all followers relationships
        conn.execute('DELETE FROM followers WHERE follower = ? OR following = ? OR followee = ?', 
                    (username, username, username))
        
        # Finally delete the user account
        conn.execute('DELETE FROM hive WHERE username = ?', (username,))
        
        # Commit all changes
        conn.commit()

        return jsonify({'message': 'Account and all related data deleted successfully'}), 200
    except Exception as e:
        print(f"Error during deletion: {e}")
        return jsonify({'error': str(e)}), 500  
    finally:
        conn.close()

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    content = request.json.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Get the commenter's profile picture
        cursor.execute("SELECT profile_picture FROM hive WHERE username = ?", (username,))
        profile_picture = cursor.fetchone()[0]

        # Insert the comment
        cursor.execute("""
            INSERT INTO comments (post_id, username, content, timestamp) 
            VALUES (?, ?, ?, datetime('now'))
        """, (post_id, username, content))
        conn.commit()
        comment_id = cursor.lastrowid

        # Get the comment count for the post
        cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,))
        comment_count = cursor.fetchone()[0]

        # Get post owner for notification
        cursor.execute("SELECT username FROM posts WHERE post_id = ?", (post_id,))
        post_owner = cursor.fetchone()[0]

        # Insert notification for post owner
        if post_owner != username:  # Avoid notifying the commenter
            message = f"{username} commented: \"{content}\""
            cursor.execute("""
                INSERT INTO notifications (user_id, type, sender, message) 
                VALUES (
                    (SELECT id FROM hive WHERE username = ?), 
                    'comment', 
                    ?, 
                    ?
                )
            """, (post_owner, username, message))
            conn.commit()

        return jsonify({
            'success': True,
            'comment_id': comment_id,
            'username': username,
            'content': content,
            'profile_picture': profile_picture,  # Use commenter's profile picture
            'timestamp': 'Just now',
            'comment_count': comment_count
        })

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        conn.close()

@app.route('/reply/<int:comment_id>', methods=['POST'])
def add_reply(comment_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    content = request.json.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Get replier's profile picture
        cursor.execute("SELECT profile_picture FROM hive WHERE username = ?", (username,))
        profile_picture = cursor.fetchone()[0]

        # Get comment owner for notification
        cursor.execute("SELECT username FROM comments WHERE comment_id = ?", (comment_id,))
        comment_owner = cursor.fetchone()[0]

        # Insert the reply
        cursor.execute("""
            INSERT INTO comment_replies (comment_id, username, content, timestamp) 
            VALUES (?, ?, ?, datetime('now'))
        """, (comment_id, username, content))
        conn.commit()
        reply_id = cursor.lastrowid

        # Insert notification for comment owner
        if comment_owner != username:  # Avoid notifying yourself
            message = f"{username} replied to your comment: \"{content}\""
            cursor.execute("""
                INSERT INTO notifications (user_id, type, sender, message) 
                VALUES (
                    (SELECT id FROM hive WHERE username = ?), 
                    'reply', 
                    ?, 
                    ?
                )
            """, (comment_owner, username, message))
            conn.commit()

        return jsonify({
            'success': True,
            'reply_id': reply_id,
            'username': username,
            'content': content,
            'profile_picture': profile_picture,  # Use replier's profile picture
            'timestamp': 'Just now'
        })

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        conn.close()

        
@app.route('/delete_comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Fetch the comment and post owner
        cursor.execute("""
            SELECT c.username, p.username AS post_owner
            FROM comments c
            JOIN posts p ON c.post_id = p.post_id
            WHERE c.comment_id = ?
        """, (comment_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'Comment not found'}), 404

        comment_author, post_owner = result

        # Check if the current user is the comment author or the post owner
        if session['username'] != comment_author and session['username'] != post_owner:
            return jsonify({'error': 'Unauthorized to delete this comment'}), 403

        # Delete the comment
        cursor.execute("DELETE FROM comments WHERE comment_id = ?", (comment_id,))
        conn.commit()

        return jsonify({'success': True})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        conn.close()

@app.route('/delete_reply/<int:reply_id>', methods=['DELETE'])
def delete_reply(reply_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Fetch the reply and the post owner
        cursor.execute("""
            SELECT r.username, p.username AS post_owner
            FROM comment_replies r
            JOIN comments c ON r.comment_id = c.comment_id
            JOIN posts p ON c.post_id = p.post_id
            WHERE r.reply_id = ?
        """, (reply_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'Reply not found'}), 404

        reply_owner, post_owner = result

        # Check if the current user is the reply author or the post owner
        if username != reply_owner and username != post_owner:
            return jsonify({'error': 'Unauthorized to delete this reply'}), 403

        # Delete the reply
        cursor.execute("""
            DELETE FROM comment_replies WHERE reply_id = ?
        """, (reply_id,))
        conn.commit()

        return jsonify({'success': True})

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        conn.close()

@app.route('/get_profile_comments/<int:post_id>')
def get_profile_comments(post_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    try:
        # Get post owner
        cursor.execute("SELECT username FROM posts WHERE post_id = ?", (post_id,))
        post_owner = cursor.fetchone()[0]

        # Fetch comments with user profile pictures
        cursor.execute("""
            SELECT c.comment_id, c.username, c.content, c.timestamp, h.profile_picture
            FROM comments c
            LEFT JOIN hive h ON c.username = h.username
            WHERE c.post_id = ?
            ORDER BY c.timestamp DESC
        """, (post_id,))
        comments = cursor.fetchall()

        formatted_comments = []
        for comment in comments:
            # Debugging: Print the comment and profile picture
            print(f"Comment: {comment}, Profile Picture: {comment[4]}")

            # Get replies for each comment
            cursor.execute("""
                SELECT r.reply_id, r.username, r.content, r.timestamp, h.profile_picture
                FROM comment_replies r
                LEFT JOIN hive h ON r.username = h.username
                WHERE r.comment_id = ?
                ORDER BY r.timestamp ASC
            """, (comment[0],))
            replies = cursor.fetchall()

            formatted_replies = [{
                'reply_id': reply[0],
                'username': reply[1],
                'content': reply[2],
                'timestamp': reply[3],
                'profile_picture': reply[4] if reply[4] else 'd1.jpg',  # Default image if no profile picture
                'can_delete': reply[1] == session['username'] or session['username'] == post_owner
            } for reply in replies]

            formatted_comments.append({
                'comment_id': comment[0],
                'username': comment[1],
                'content': comment[2],
                'timestamp': comment[3],
                'profile_picture': comment[4] if comment[4] else 'd1.jpg',  # Default image if no profile picture
                'can_delete': comment[1] == session['username'] or session['username'] == post_owner,
                'replies': formatted_replies
            })

        return jsonify({
            'success': True,
            'comments': formatted_comments
        })

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        conn.close()
        
@app.route('/unread_notifications_count', methods=['GET'])
def unread_notifications_count():
    if 'username' not in session:
        return jsonify({'unread_count': 0})  

    current_user = session['username']
    unread_count = 0

    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
        """, (current_user,))
        unread_count = cursor.fetchone()[0]

    except sqlite3.Error as e:
        print(f"Error fetching unread notifications count: {e}")
    finally:
        conn.close()

    return jsonify({'unread_count': unread_count})


@app.route('/notifications', methods=['GET'])
def notifications_page():
    if 'username' not in session:
        flash("You must be logged in to view notifications.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']
    notifications = []
    unread_count = 0  

    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT n.id, n.type, n.sender, n.message, n.timestamp, n.is_read, 
                   COALESCE(sender_h.profile_picture, 'd1.jpg') AS sender_profile_picture
            FROM notifications n
            JOIN hive sender_h ON n.sender = sender_h.username
            WHERE n.user_id = (SELECT id FROM hive WHERE username = ?) 
            ORDER BY n.timestamp DESC
        """, (current_user,))

        notifications = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
        """, (current_user,))
        unread_count = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = (SELECT id FROM hive WHERE username = ?) AND is_read = 0
        """, (current_user,))
        conn.commit()

    except sqlite3.Error as e:
        print(f"Error fetching notifications: {e}")
    finally:
        conn.close()

    return render_template('notifications.html', notifications=notifications, unread_count=unread_count)

@app.route('/messages', methods=['GET', 'POST'])
def messages_page():
    if 'username' not in session:
        flash("You must be logged in to view messages.", "error")
        return redirect(url_for('login_page'))

    logged_in_user = session['username']
    search_query = request.args.get('search', '')  

    conn = sqlite3.connect('bee.db')
    cursor = conn.cursor()

    search_sql = """
        SELECT DISTINCT hive.username, hive.profile_picture, 
               (SELECT content FROM messages 
                WHERE (sender = hive.username OR receiver = hive.username) 
                ORDER BY timestamp DESC LIMIT 1) AS last_message
        FROM followers
        JOIN hive ON followers.following = hive.username
        LEFT JOIN messages ON (messages.sender = hive.username OR messages.receiver = hive.username)
        WHERE followers.follower = ? AND hive.username LIKE ?
    """
    cursor.execute(search_sql, (logged_in_user, f"%{search_query}%"))
    following_users = [{'username': row[0], 'profile_picture': row[1], 'last_message': row[2]} for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT messages.sender, hive.profile_picture
        FROM messages
        LEFT JOIN followers ON messages.sender = followers.following AND followers.follower = ?
        JOIN hive ON messages.sender = hive.username
        WHERE messages.receiver = ? AND followers.follower IS NULL
    """, (logged_in_user, logged_in_user))
    unfollowed_users = [{'username': row[0], 'profile_picture': row[1]} for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'message.html',
        following_users=following_users,
        unfollowed_users=unfollowed_users, 
        search_query=search_query
    )
@app.route('/message/<username>', methods=['GET', 'POST'])
def message_user(username):
    if 'username' not in session:
        flash("You must be logged in to send messages.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']
    search_query = request.args.get('search', '') 

    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()

        cursor.execute(""" 
            SELECT hive.username, hive.profile_picture, 
                   COALESCE(SUM(CASE WHEN messages.is_read = 0 THEN 1 ELSE 0 END), 0) AS unread_count,
                   (SELECT content FROM messages 
                    WHERE (sender = hive.username OR receiver = hive.username) 
                    ORDER BY timestamp DESC LIMIT 1) AS last_message
            FROM followers
            JOIN hive ON followers.following = hive.username
            LEFT JOIN messages ON messages.sender = hive.username AND messages.receiver = ?
            WHERE followers.follower = ? AND hive.username LIKE ?
            GROUP BY hive.username
        """, (current_user, current_user, f"%{search_query}%"))
        following_users = [{
            'username': row[0],
            'profile_picture': row[1],
            'unread_count': row[2],
            'last_message': row[3]
        } for row in cursor.fetchall()]

        messages = get_chat_messages(current_user, username)
        messages = [{
            'sender': msg['sender'],
            'content': msg['content'],
            'timestamp': msg['timestamp'],
            'media_path': msg.get('media_path'),
            'media_type': msg.get('media_type'),
            'is_sent_by_user': msg['sender'] == current_user
        } for msg in messages]

        cursor.execute("""SELECT username, profile_picture FROM hive WHERE username IN (?, ?)""", 
                       (current_user, username))
        profiles = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""SELECT id, username, bio, profile_picture FROM hive WHERE username = ?""", 
                       (current_user,))
        user = cursor.fetchone()

        if user:
            user_details = {
                'id': user[0],
                'username': user[1],
                'bio': user[2],
                'profile_picture': user[3]
            }
        else:
            user_details = {}

    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "error")
        following_users = []
        messages = []
        profiles = {}
    finally:
        conn.close()

    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        audio_file = request.files.get('audio')

        if not content and audio_file:
            if allowed_file(audio_file.filename):
                filename = secure_filename(audio_file.filename)
                audio_path = os.path.join('static/uploads/audio', filename)
                audio_file.save(audio_path)

                send_message(current_user, username, content=None, media_path=audio_path, media_type='audio')

                send_message_notification(current_user, username, content=None, media_path=audio_path, media_type='audio')

                return redirect(url_for('message_user', username=username))

        elif content:
            send_message(current_user, username, content)

            send_message_notification(current_user, username, content)

            return redirect(url_for('message_user', username=username))

        else:
            flash("Message content cannot be empty.", "error")

    return render_template(
        'message.html',
        following_users=following_users, 
        recipient=username,
        messages=messages,
        profiles=profiles,
        user=user_details,
        search_query=search_query 
    )


@app.route('/accept_request/<username>', methods=['POST'])
def accept_request(username):
    if 'username' not in session:
        flash("You must be logged in to accept a request.", "error")
        return redirect(url_for('login_page'))

    current_user = session['username']
    try:
        conn = sqlite3.connect('bee.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO followers (follower, following) VALUES (?, ?)
        """, (current_user, username))

        cursor.execute("""
            UPDATE messages
            SET is_read = 1
            WHERE sender = ? AND receiver = ?
        """, (username, current_user))

        conn.commit()

        flash(f"You are now following {username} and have accepted the message request.", "success")
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('messages_page'))


if __name__ == '__main__':
    app.run(debug=True)