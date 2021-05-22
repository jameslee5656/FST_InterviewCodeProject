from flaskext.mysql import MySQL
from flask import Flask, url_for, request, redirect, render_template  
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth
import json,cryptography
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

## MySQL initial function
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'fstadmin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'P@ssw0rdJames'
app.config['MYSQL_DATABASE_DB'] = 'FST'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

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
  
  
class User(UserMixin):  
    """  
 設置一： 只是假裝一下，所以單純的繼承一下而以 如果我們希望可以做更多判斷，
 如is_administrator也可以從這邊來加入 
 """
    pass  
  
  
@login_manager.user_loader  
def user_loader(email):  
    """  
 設置二： 透過這邊的設置讓flask_login可以隨時取到目前的使用者id   
 :param email:官網此例將email當id使用，賦值給予user.id    
 """   
    if email not in users:  
        return  
  
    user = User()  
    user.id = email  
    return user  
  
@app.route('/signup', methods=['POST'])  
def signup():  
    """  
 官網git很給力的寫了一個login的頁面，在GET的時候回傳渲染     
 """   
    if request.method == 'POST':  
        print(request.json)
        data = request.json
        # Ignore json format error
        _name = data['user']
        _password = data['password']
        # validate the received values
        print(_name and _password)
        data = {}
        if _name and _password:
            data={
                "response":"All fields good !!"
            }
            print("Debug", response_self(data))
            _hashed_password = generate_password_hash(_password)
            print("Debug: ",_hashed_password )
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
            print(response_self(data))
            return response_self(data)

    else:
        return 'Wrong HTTP Method, please use POST'
    return 'Bad login'  

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    """  
 官網git很給力的寫了一個login的頁面，在GET的時候回傳渲染     
 """   
    if request.method == 'GET':  
        print(request.data)
        print(request.args['user'])
        username = request.args['user']  
        print(request.args['password'] == users[username]['password'])
        if request.args['password'] == users[username]['password']:  
            #  實作User類別  
            user = User()  
            #  設置id就是email  
            user.id = username  
            #  這邊，透過login_user來記錄user_id，如下了解程式碼的login_user說明。  
            login_user(user)  
            #  登入成功，轉址  
            return redirect(url_for('view'))  
    return 'Bad login'  
  
  
@app.route('/view')  
@login_required
def view():  
    """  
 在login_user(user)之後，我們就可以透過current_user.id來取得用戶的相關資訊了  
 """   
    #  current_user確實的取得了登錄狀態
    # print("Debug Here-------")
    # print(current_user)
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
