from repositories.db import get_pool
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash, check_password_hash

def get_all_courses():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                SELECT
                    *
                FROM courses;
            ''')
            return cur.fetchall()

def get_course_by_id(course_id: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                SELECT
                    course_id,
                    course_name,
                    course_description,
                    professor_name
                FROM courses
                WHERE course_id = %s;
            ''', [course_id])
            return cur.fetchone()

def get_all_comments_with_course_id(course_id: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                SELECT
                    r.review_id,
                    r.comment,
                    r.rating,
                    r.final_grade,
                    r.user_id,
                    u.name
                FROM reviews r
                JOIN courses c ON r.course_id = c.course_id
                JOIN users u ON r.user_id = u.user_id
                WHERE r.course_id = %s;
            ''', [course_id])
            return cur.fetchall()

def add_comment_to_course(course_id: str, user_id: str, rating: int, final_grade: str, comment: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                INSERT INTO reviews (course_id, user_id, comment, rating, final_grade)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            ''', [course_id, user_id, comment, rating, final_grade])
            return cur.fetchone()

def edit_comment_from_course(course_id: str, review_id: str, rating: int, final_grade: str, comment: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                UPDATE reviews
                SET comment = %s, rating = %s, final_grade = %s
                WHERE course_id = %s AND review_id = %s
                RETURNING *;
            ''', [comment, rating, final_grade, course_id, review_id])
            return cur.fetchone()

def delete_comment_from_course(course_id: str, user_id: str, review_id: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                DELETE FROM reviews
                WHERE course_id = %s AND user_id = %s AND review_id = %s
                RETURNING *;
            ''', [course_id, user_id, review_id])
            return cur.fetchone()
        


def signup_user(username: str, email: str, password: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Check if the user already exists
            cur.execute('SELECT user_id FROM Users WHERE username = %s OR email = %s', (username, email))
            if cur.fetchone():
                return False, 'Username or email already exists.'

            # Insert the new user into the database
            password_hash = generate_password_hash(password)
            cur.execute('INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)',
                        (username, email, password_hash))
            conn.commit()
            return True, 'Registration successful, please login.'
        

def login_user(username: str, password: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Check if the user exists and fetch credentials
            cur.execute('SELECT user_id, password FROM Users WHERE username = %s OR email = %s', (username, username))
            user_record = cur.fetchone()
            if user_record:
                user_id, password_hash = user_record
                # Verify the password
                if check_password_hash(password_hash, password):
                    return True, user_id, 'Login successful'
            return False, None, 'Invalid username or password'