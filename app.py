from flaskext.mysql import MySQL
from flask import Flask, url_for, request, redirect, render_template  
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth
import json,cryptography
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import closing
from six import text_type
from datetime import date, datetime
import sys
from operator import itemgetter

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
                    cursor.execute("SELECT * FROM fst_user where user_name = %s " % (_name))
                    data = cursor.fetchall()
                    if(len(data) != 1):
                        print("Error: name conflict")
                    cursor.callproc('sp_createAsset',(data[0][0],))
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
                    
    return 'Bad login'  
  
  
@app.route('/userHome')  
@login_required
def userHome():  
    """  
 在login_user(user)之後，我們就可以透過current_user.id來取得用戶的相關資訊了  
 """   
    #  current_user確實的取得了登錄狀態
    if current_user.is_active:  
        # d = make_summary()
        # data = make_summary()
        data={
            "user_id":current_user.id,
            "Login_is_active":True,
            "Available Action":["/userHome/view",
                                {"/userHome/buy":["cardType","num","$perCard"]},
                                {"/userHome/sell":["cardType","num","$perCard"]}]
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
        # return 'Logged in as: ' + current_user.id + 'Login is_active:True'

@app.route('/userHome/view')  
@login_required
def view():  
    """  
 在login_user(user)之後，我們就可以透過current_user.id來取得用戶的相關資訊了  
 """   
    #  current_user確實的取得了登錄狀態
    if current_user.is_active:  
        # d = make_summary()
        # orderInfo = request.json
        # print(orderInfo)
        data={
            "user":current_user.id,
            "Login_is_active":True
        }
        with closing(mysql.connect()) as conn:
            with closing( conn.cursor() ) as cursor:
                cursor.execute("SELECT * FROM asset where user_id = %s ",current_user.id)
                db_check = cursor.fetchall()
                # UserObject = User(db_check[0][0], db_check[0][1])
                if db_check != None:
                    # print(db_check)
                    data['asset_id'] = db_check[0][0]
                    data['balance'] = db_check[0][2]
                    data['pikachu'] = db_check[0][3]
                    data['bulbasaur'] = db_check[0][4]
                    data['charmander'] = db_check[0][5]
                    data['squirtle'] = db_check[0][6]

                else:
                    pass

        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
        # return 'Logged in as: ' + current_user.id + 'Login is_active:True'

@app.route('/userHome/buy')
@login_required
def buy():  
    if current_user.is_active:
        orderInfo = request.json
        timestamp = datetime.timestamp(datetime.now())
        user_id = current_user.id
        orderType = "buy"
        with closing(mysql.connect() ) as conn:
            with closing( conn.cursor()) as cursor:
                # check order that intended to sell
                cursor.execute("SELECT * FROM orders where status = %s and orderType = %s " % ("\'pending\'", "\'sell\'"))
                BuyPending = cursor.fetchall()
                # print(data)
                if len(BuyPending) == 0:
                    # The card does not have buyer yet
                    status = "pending"
                    try:
                        referId = None
                        cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                        timestamp, user_id, status, orderType,referId))

                        conn.commit()
                        cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                        data = cursor.fetchall()
                        order_id = data[0][0]

                        data={
                            "response":'Create Order successfully !',
                            "orderStatus":status,
                            "order_id":order_id
                        }
                        return response_self(data)
                    except Exception as e:
                        data={
                            "response":'Error: ' + str(e)
                        }
                        return response_self(data)                       
                else :
                    # The card has a seller                    
                    try:
                        num = orderInfo['num']
                        # Make sure our order is finished and BuyPending still has value
                        while( (num != 0) and (len(BuyPending) != 0)):
                            sellerTuple = min(BuyPending, key=itemgetter(3))
                            sellerTupleNum = sellerTuple[2]
                            sellerTupleId = sellerTuple[5]
                            sellerTupleMonPerCard = sellerTuple[3]
                            # if else max find or not
                            if sellerTupleNum >= num:
                                # Update the seller in sell function
                                ordernumber = num
                                leaveflag = True
                                num = 0
                            else:
                                leaveflag = False
                                ordernumber = sellerTupleNum
                                num -= sellerTupleNum

                            #### <whole proccess function Start> 
                            # Create a completed order    
                            status = "completed"

                            #### ------ Here has a problem how to decide the price ------ #
                            # Update the buyer in buy function
                            cursor.execute("UPDATE asset SET %s = %s + %s, balance = balance - %s WHERE user_id = %s ;" 
                                    % (orderInfo['cardType'],orderInfo['cardType'], ordernumber,
                                        orderInfo['num']*sellerTupleMonPerCard,
                                        user_id))

                            # Update the buyer in buy function
                            cursor.execute("UPDATE asset SET %s = %s + %s, balance = balance - %s WHERE user_id = %s ;" 
                                    % (orderInfo['cardType'],orderInfo['cardType'], num,
                                        orderInfo['num']*sellerTupleMonPerCard,
                                        sellerTupleId))
                            referID = sellerTuple[0]
                            # Create a sell order
                            cursor.callproc('sp_createOrders',(orderInfo['cardType'], num,sellerTupleMonPerCard,
                                                    timestamp, user_id, status, orderType, referID))
                            #Update the r
                            conn.commit()
                            cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                            data = cursor.fetchall()
                            order_id = data[0][0]
                            # Update the refer sell order
                            cursor.execute("UPDATE orders SET status = \'completed\', referId = %s where order_id = %s" %(order_id,referID))
                            conn.commit()
                            
                            #### <whole proccess function End> 
                            if (leaveflag == True):
                                data={
                                        "response":'Order Process successfully !',
                                        "orderStatus":status,
                                        "order_id":order_id
                                    }
                                return response_self(data)
                                break
                            else : 
                                pass

                            # Update the seller in sell function
                            # No more orders to buy break out while

                            cursor.execute("SELECT * FROM orders where status = %s and orderType = %s " % ("\'pending\'", "\'buy\'"))
                            BuyPending = cursor.fetchall()

                            ## create a pending order if len = 0
                            if len(BuyPending) == 0:
                            # The card does not have buyer anymore 
                                status = "pending"
                                try:
                                    referID = None
                                    cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                                    timestamp, user_id, status, orderType,referID))

                                    conn.commit()
                                    cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                                    data = cursor.fetchall()
                                    order_id = data[0][0]
                                    print("Debug: ", order_id)

                                    data={
                                        "response":'Order Process successfully !',
                                        "orderStatus":status,
                                        "order_id":order_id
                                    }
                                    return response_self(data)
                                except Exception as e:
                                    data={
                                        "response":'Error: ' + str(e)
                                    }
                                    return response_self(data)
                        
                        # Finish while loop
                        print("Error: should already finish loop")
                        # cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                        # timestamp, user_id, status, orderType))
                        # cursor.execute("UPDATE asset SET %s = %s - %s, balance = balance - %s WHERE user_id = %s ;" 
                        #             % (orderInfo['cardType'],orderInfo['cardType'], orderInfo['num'],
                        #                 orderInfo['num']*orderInfo['$perCard'],
                        #                 user_id))
                        # data = cursor.fetchall()

                        # conn.commit()
                        # cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                        # data = cursor.fetchall()
                        # order_id = data[0][0]
                        # print("Debug: ", order_id)

                        data={
                            "response":'Create Order successfully !',
                            "orderStatus":status,
                            "order_id":order_id
                        }
                        return response_self(data)
                    except Exception as e:
                        data={
                            "response":'Error: ' + str(e)
                        }
                        return response_self(data)   
    else:
        data={
            "response":"Please login before buy action"
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response

@app.route('/userHome/sell')
@login_required
def sell():  
    if current_user.is_active:
        orderInfo = request.json
        timestamp = datetime.timestamp(datetime.now())
        user_id = current_user.id
        orderType = "sell"
        with closing(mysql.connect() ) as conn:
            with closing( conn.cursor()) as cursor:
                # check order that intended to sell
                cursor.execute("SELECT * FROM orders where status = %s and orderType = %s " % ("\'pending\'", "\'buy\'"))
                BuyPending = cursor.fetchall()
                # print(data)
                if len(BuyPending) == 0:
                    # The card does not have sellter yet
                    status = "pending"
                    try:
                        referId = None
                        cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                        timestamp, user_id, status, orderType,referId))

                        conn.commit()
                        cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                        data = cursor.fetchall()
                        order_id = data[0][0]
                        print("Debug: ", order_id)

                        data={
                            "response":'Create Order successfully !',
                            "orderStatus":status,
                            "order_id":order_id
                        }
                        return response_self(data)
                    except Exception as e:
                        data={
                            "response":'Error: ' + str(e)
                        }
                        return response_self(data)                       
                else :
                    # The card has a buyer
                    
                    print("The card has seller")
                    print(BuyPending)
                    
                    try:
                        num = orderInfo['num']
                        # Make sure our order is finished and BuyPending still has value
                        while( (num != 0) and (len(BuyPending) != 0)):
                            buyerTuple = max(BuyPending, key=itemgetter(3))
                            buyerTupleNum = buyerTuple[2]
                            buyerTupleId = buyerTuple[5]
                            buyerTupleMonPerCard = buyerTuple[3]
                            # if else max find or not
                            if buyerTupleNum >= num:
                                # Update the seller in sell function
                                ordernumber = num
                                leaveflag = True
                                num = 0
                            else:
                                leaveflag = False
                                ordernumber = buyerTupleNum
                                num -= buyerTupleNum

                            #### <whole proccess function Start> 
                            # Create a completed order    
                            status = "completed"

                            #### ------ Here has a problem how to decide the price ------ #
                            cursor.execute("UPDATE asset SET %s = %s - %s, balance = balance + %s WHERE user_id = %s ;" 
                                    % (orderInfo['cardType'],orderInfo['cardType'], ordernumber,
                                        orderInfo['num']*buyerTupleMonPerCard,
                                        user_id))
                            # Update the buyer in sell function

                            cursor.execute("UPDATE asset SET %s = %s + %s, balance = balance - %s WHERE user_id = %s ;" 
                                    % (orderInfo['cardType'],orderInfo['cardType'], num,
                                        orderInfo['num']*buyerTupleMonPerCard,
                                        buyerTupleId))
                            referID = buyerTuple[0]
                            # Create a sell order
                            cursor.callproc('sp_createOrders',(orderInfo['cardType'], num,buyerTupleMonPerCard,
                                                    timestamp, user_id, status, orderType, referID))
                            #Update the refer buy order
                            conn.commit()
                            cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                            data = cursor.fetchall()
                            order_id = data[0][0]
                            cursor.execute("UPDATE orders SET status = \'completed\', referId = %s where order_id = %s" %(order_id,referID))
                            conn.commit()
                            
                            #### <whole proccess function End> 
                            if (leaveflag == True):
                                break
                            else : 
                                pass

                            # Update the seller in sell function
                            # No more orders to buy break out while

                            cursor.execute("SELECT * FROM orders where status = %s and orderType = %s " % ("\'pending\'", "\'buy\'"))
                            BuyPending = cursor.fetchall()

                            ## create a pending order if len = 0
                            if len(BuyPending) == 0:
                            # The card does not have buyer anymore 
                                status = "pending"
                                try:
                                    referID = None
                                    cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                                    timestamp, user_id, status, orderType,referID))

                                    conn.commit()
                                    cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                                    data = cursor.fetchall()
                                    order_id = data[0][0]
                                    print("Debug: ", order_id)

                                    data={
                                        "response":'Create Order successfully !',
                                        "orderStatus":status,
                                        "order_id":order_id
                                    }
                                    return response_self(data)
                                except Exception as e:
                                    data={
                                        "response":'Error: ' + str(e)
                                    }
                                    return response_self(data)  



                        
                        # cursor.callproc('sp_createOrders',(orderInfo['cardType'],orderInfo['num'],orderInfo['$perCard'],
                                                        # timestamp, user_id, status, orderType))
                        # cursor.execute("UPDATE asset SET %s = %s - %s, balance = balance - %s WHERE user_id = %s ;" 
                        #             % (orderInfo['cardType'],orderInfo['cardType'], orderInfo['num'],
                        #                 orderInfo['num']*orderInfo['$perCard'],
                        #                 user_id))
                        # data = cursor.fetchall()

                        # conn.commit()
                        # cursor.execute("SELECT order_id from orders ORDER BY order_id DESC LIMIT 1;")
                        # data = cursor.fetchall()
                        # order_id = data[0][0]
                        # print("Debug: ", order_id)

                        data={
                            "response":'Create Order successfully !',
                            "orderStatus":status,
                            "order_id":order_id
                        }
                        return response_self(data)
                    except Exception as e:
                        data={
                            "response":'Error: ' + str(e)
                        }
                        return response_self(data)   
    else:
        data={
            "response":"Please login before buy action"
        }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response

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
