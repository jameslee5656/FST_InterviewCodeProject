from flaskext.mysql import MySQL
from flask import Flask, url_for, request, redirect, render_template  
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth
import json,cryptography
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import closing
from six import text_type

app = Flask(__name__)

## MySQL initial function
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'fstadmin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'P@ssw0rdJames'
app.config['MYSQL_DATABASE_DB'] = 'FST'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# flask-login secret key
app.config['SECRET_KEY'] = 'JamesSecretKey'
#  實作
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#  看__init__的部份，在實作的時候將app當參數應該是可行的，如下說明
login_manager = LoginManager(app)
#  login\_manager.init\_app(app)也可以  
#  假裝是我們的使用者  
users = {'fstadmin@localhost': {'password': 'P@ssw0rdJames'}}  
  
class UserMixin(object):
    
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return text_type(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

class User(UserMixin): 
    def __init__(self, id, name):
        self.name = name
        self.id = id
  
@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@login_manager.user_loader  
def user_loader(id):  
    return check_db(id)

def check_db(userid):
    with closing(mysql.connect()) as conn:
        with closing( conn.cursor() ) as cursor:
            cursor.execute("SELECT * FROM fst_user where user_id = %s ",userid)
            db_check = cursor.fetchall()
            UserObject = User(db_check[0][0], db_check[0][1])
            if db_check != None:
                return UserObject
            else:
                return None


@app.route('/signup', methods=['POST'])  
def signup():  
    """  
 官網git很給力的寫了一個login的頁面，在GET的時候回傳渲染     
 """   
    if request.method == 'POST':  
        # print(request.json)
        data = request.json
        _name = data['user']
        _password = data['password']
        # validate the received values
        # print(_name and _password)
        data = {}

        # MySQL connect
        # conn = mysql.connect()
        # cursor = conn.cursor()
        #  Make sure the connection and cursor close
        with closing(mysql.connect() ) as conn:
            with closing( conn.cursor() ) as cursor:
                if _name and _password:
                    data={
                        "response":"All fields good !!"
                    }
                    _hashed_password = generate_password_hash(_password)
                    cursor.callproc('sp_createUser',(_name,_hashed_password))
                    data = cursor.fetchall()
        
                    if len(data) == 0:
                        conn.commit()
                        data={
                            "response":'User created successfully !'
                        }
                        return response_self(data)
                    else:
                        data={
                            "response":'Error' + str(data[0])
                        }
                        return response_self(data)
                    return response_self(data)
                else:
                    data={
                        "response":"Json data error"
                    }
                    response_self(data)
                    return response_self(data)

    else:
        data={
            "response":"Wrong HTTP Method, please use POST"
        }    
        return response_self(data)

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'GET':
        try: 
            data = request.json
            _name = data['user']
            _password = data['password']
 
        except Exception as e:
            data={
                "response":"Error: " + str(e)
            }
            return response_self(data)

        # MySQL connect
        with closing(mysql.connect() ) as conn:
            with closing( conn.cursor() ) as cursor:
                cursor.callproc('sp_validateLogin',(_name,))
                data = cursor.fetchall()
                if len(data) > 0:
                    if check_password_hash(str(data[0][2]),_password):
                         #  實作User類別 
                        user = User(data[0][0],_name)  
                        #  這邊，透過login_user來記錄user_id，如下了解程式碼的login_user說明。 
                        print(user) 
                        login_user(user)
                        #  登入成功，轉址 
                        print("Success login")
                        print(current_user.id)
                        return redirect('/userHome')
                    else:
                        data={
                        "response":"Wrong Email address or Password."
                        }
                        return response_self(data)
                else:
                    data={
                    "response":"Wrong Email address or Password."
                    }
                    return response_self(data)
                    
        print(request.args['user'])
        username = request.args['user']  
        print(request.args['password'] == users[username]['password'])
        if request.args['password'] == users[username]['password']:  
           
            return redirect(url_for('view'))  
    return 'Bad login'  
  
  
@app.route('/userHome')  
@login_required
def userHome():  
    """  
 在login_user(user)之後，我們就可以透過current_user.id來取得用戶的相關資訊了  
 """   
    #  current_user確實的取得了登錄狀態
    print("Debug Here-------")
    print(current_user.is_active)
    if current_user.is_active:  
        # d = make_summary()
        # data = make_summary()
        data={
            "user":current_user.id,
            "Login_is_active":True
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
        # return 'Logged in as: ' + current_user.id + 'Login is_active:True'
        
@app.route('/buy')  
@login_required
def buy():  
    if current_user.is_active:  
        data={
            "user":current_user.id,
            "Login_is_active":True
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
        # return 'Logged in as: ' + current_user.id + 'Login is_active:True'
  
@app.route('/logout')  
def logout():  
    """  
 logout\_user會將所有的相關session資訊給pop掉 
 """ 
    logout_user()  
    return 'Logged out'  

@app.route('/summary')
def summary():
    data = make_summary()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/")
@app.route("/help")
def help():
    data={
        "All actions":["/login","/logout","/signup","/buy","/sell"]
    }
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# some function for multiple usage
def response_self(data):
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__=='__main__':
    app.run(debug=True)
