import MySQLdb
from flask import request, make_response
from flask_mysqldb import MySQL
from flask import Flask, jsonify,render_template, session, redirect, url_for
from cls import UserSignUp, Products,portfo,portfoli
import hashlib
import datetime
import jwt
import time
import socket
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'SECRET KEY'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nagraj@37'
app.config['MYSQL_DB'] = 'investment_application'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/admin', methods=['POST','GET'])
def admin():
    if request.method == 'POST':
        userDetails = request.json
        USER_NAME = userDetails['USER_NAME']
        PASSWORD = userDetails['PASSWORD']
        cur = mysql.connection.cursor()
        cur.execute("select * from admin where USER_NAME=%s and PASSWORD=%s", (USER_NAME, PASSWORD))
        Data = cur.fetchone()
        # if USER_NAME=="admin" and PASSWORD =="admin":
        #     return "succesfully login"
        if Data is not None:
            # return "invalid credits"
            return ({"message":"succesfully_created"})
        else:
            return "invalid credits"
    return 'no user found', 401


@app.route('/login', methods=['POST'])
def index():
    if request.method == 'POST':
        userDetails = request.json
        EMAIL = userDetails['EMAIL']
        PASSWORD = userDetails['PASSWORD']
        h = hashlib.md5(PASSWORD.encode())
        print(h.hexdigest())
        cur = mysql.connection.cursor()
        cur.execute("select * from signup where EMAIL=%s and PASSWORD=%s",
                    (EMAIL, h.hexdigest()))
        Data = cur.fetchone()
        if Data is None:
            return "Invalid password/email"
        else:
            token = jwt.encode({'EMAIL': EMAIL, 'PASSWORD': h.hexdigest(),
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
                               app.config["SECRET_KEY"], algorithm='HS256')
            return jsonify(jwt.decode(token, app.config["SECRET_KEY"], algorithms='HS256'))
           # return token

    return jsonify({"message": 'token required'}), 401

@app.route('/login01', methods=['GET', 'POST'])
def login1():
    try:
        if request.method == 'POST':
            user_details = request.json
            user_mail_id = user_details['user_mail_id']
            user_password = user_details['user_password']
           # h = hashlib.md5(password.encode())
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT * FROM invested WHERE user_mail_id = % s AND user_password= % s',
                        (user_mail_id,user_password))
            user = cur.fetchone()
            print(user)
            if not user:
                return make_response('User Not There Could not verify', 401)
            if user:
                session['Login_user_mail'] = user['user_mail_id']
                session['Login_user_id'] = user['user_id']
                session['Login_opportunity_id'] = user['opportunity_id']

                login_time = datetime.datetime.now()
                logout_time = '0000-00-00'
                insert_query = " INSERT INTO LOGIN_DATA VALUES(%s,%s,%s,%s)"
                cur.execute(insert_query,(session['Login_user_mail'], login_time, logout_time,session['Login_user_id']),)
                mysql.connection.commit()
                cur.close()
                token = jwt.encode({'opportunity_id': user['opportunity_id'],'user_id': user['user_id']}, "secret", algorithm="HS256")
                data = jwt.decode(token, "secret", algorithms=["HS256"])
                return data
                #return redirect(url_for('ses'))
            else:
                return 'Incorrect username / password !'
    except Exception as e:
        print(e)
    return 'out of login'


@app.route('/session', methods=['GET', 'POST'])
def ses():
    try:
        if 'Login_user_mail' in session:
            mail_id = session['Login_user_mail']
            cur = mysql.connection.cursor()
            resultVal = cur.execute("select * from invested WHERE user_mail_id = %s ",(mail_id,))
            if resultVal > 0:
                userDetails = cur.fetchall()
                return json.dumps(userDetails, default=str)
        else:
            return 'no data found'
    except Exception as e:
        print(e)
    return 'try again'

@app.route('/in', methods=['POST', 'GET'])
def aad():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select * FROM invested where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/add', methods=['POST', 'GET'])
def naga():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select count(OPPORTUNITY_NAME) as OPPORTUNITY_NAME from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)


@app.route('/som', methods=['POST', 'GET'])
def som():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select sum(INVESTMENT_AMOUNT) as INVESTMENT_AMOUNT  from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)
@app.route('/rev', methods=['POST', 'GET'])
def rev():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select sum(REVENUE) as REVENUE  from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/prof', methods=['POST', 'GET'])
def prof():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select sum(PROFIT_LOSS) as PROFIT_LOSS  from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/inv', methods=['POST', 'GET'])
def aads():
    if request.method =='POST':
        ID = request.json['ID']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select * FROM invested where ID=%s", (ID,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/signup', methods=['POST','GET'])
def user_signup():
    try:
        if request.method == 'POST' and (request.json or request.form):
            ob1 = None
            print(request.json)

            if request.json:
                ob1 = UserSignUp(request.json)

            if ob1.useremail_req():
                return "invalid mail"

            # if ob1.user_number_req():
            #     return "invalid phone number"


            if ob1.userpass_req():
                return 'Password should contain atleat one small letter, one big letter, one numeric and one special character with 8 minimum letters'
            else:
                print("PASSWORD")
                h = hashlib.md5(ob1.PASSWORD.encode())
                print(h.hexdigest())
                user_ip = get_ip()
                print(user_ip)
                user_date = get_date()
                print(user_date)
                user_device = get_device()
                print(user_device)
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO signup(FULL_NAME,EMAIL,PHONE_NUMBER,PASSWORD,USER_IP,USER_DATE_CREATED,USER_DEVICE,TERMS,PRODUCT_NAME,LOCATION) VALUES '
                               '(%s,%s, %s, %s,%s, %s,%s,%s,%s,%s)',
                               (ob1.FULL_NAME,
                                ob1.EMAIL,
                                ob1.PHONE_NUMBER,
                                h.hexdigest(),
                                user_ip,
                                user_date,
                                user_device,
                                ob1.TERMS,
                                ob1.PRODUCT_NAME,
                                ob1.LOCATION))
                mysql.connection.commit()
                cursor.close()
                return ({"message": "successfully created"})
    except:
        return ({"message": "user exists"})
    #return render_template('signup.html')



@app.route('/userdetails', methods=['GET', 'POST'])
def userdetail():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup")
        data = cur.fetchall()
        users = json.dumps(data, default=str)
        data_s = json.loads(users)
        return jsonify({'users': data_s})
    return 'Unsuccess'


@app.route('/product', methods=['POST', 'GET'])
def product():
    if request.method == 'POST' and (request.json or request.form):
        ob1 = None
        print(request.json)

        if request.json:
            ob1 = Products(request.json)

            OPPORTUNITY_ID = "IN" + str(fillzero()).zfill(4)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO opportunity(OPPORTUNITY_NAME,OPPORTUNITY_IMAGE,INVESTMENT_AMOUNT,ROI,OPPORTUNITY_TYPE,"
                           "OPPORTUNITY_DESC,AREA_NAME,AREA_STANDARD,REVENUE,EXPENSES,TAX,TENANT_NAME,TENANT_COUNTRY,"
                           "TENANT_DESC,UPLOAD_FILE,CONTRACT_DURATION, STARTING_DATE,ENDING_DATE,OPPORTUNITY_ID,STATUS) VALUES"
                           "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (ob1.opportunity_name,
                            ob1.Opportunity_Image,
                            ob1.Investment_Amount,
                            ob1.ROI,
                            ob1.Opportunity_Type,
                            ob1.Opportunity_Desc,

                            ob1.Area_Name,
                            ob1.Area_Standard,
                            ob1.Revenue,
                            ob1.Expenses,
                            ob1.Tax,
                            ob1.Tenant_Name,
                            ob1.Tenant_Country,
                            ob1.Tenant_Desc,
                            ob1.upload_file,
                            ob1.Contract_Duration,
                            ob1.Starting_Date,
                            ob1.Ending_Date,
                            OPPORTUNITY_ID,
                            ob1.STATUS))
            mysql.connection.commit()
            cursor.close()
            return ({"message": "successfully created"})

        return ({"message": "user exists"})


def get_ip():
    hostName = socket.gethostname()
    ipaddr = socket.gethostbyname(hostName)
    return ipaddr


def get_device():
    hostName = socket.gethostname()
    return hostName


def get_date():
    date = datetime.datetime.now()
    return date


def fillzero():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("select OPPORTUNITY_ID from OPPORTUNITY")
    if resultVal >= 0:
        resultVal = resultVal + 1
        mysql.connection.commit()
        use = cur.fetchall()
        cur.close()
        return json.dumps(resultVal, default=str)


@app.route('/users')
def user():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT * FROM opportunity")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails,default=str)
    return "No Data Present"


@app.route('/type')
def type():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT TYPE FROM opportunity_type")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/standard')
def stnd():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT STANDARD FROM invetment_standard")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/country')
def cntry():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT COUNTRY_CODE FROM country")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


def cty():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT COUNTRY_CODE FROM country")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/city')
def city():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT CITY_NAME FROM city")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/contract')
def con():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT DURATION FROM contract")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/OPPORTUNITY_NAME')
def NAME():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT OPPORTUNITY_NAME FROM opportunity_name")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/preview')
def pre():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT ID,OPPORTUNITY_NAME,OPPORTUNITY_IMAGE ,STARTING_DATE,AREA_NAME,OPPORTUNITY_TYPE,STATUS FROM opportunity")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/status')
def stat():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT status FROM status")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)


@app.route('/update', methods=['GET', 'PUT'])
def up():
    if request.method == 'PUT':
        userDetails = request.json or request.form
        Id = userDetails['Id']
        opportunity_name = userDetails['opportunity_name']
        Investment_Amount = userDetails['Investment_Amount']
        ROI = userDetails['ROI']
        Opportunity_Type = userDetails['Opportunity_Type']
        Opportunity_Desc = userDetails['Opportunity_Desc']
        Area_Name = userDetails['Area_Name']
        Area_Standard = userDetails['Area_Standard']
        Revenue = userDetails['Revenue']
        Expenses = userDetails['Expenses']
        Tax = userDetails['Tax']
        Tenant_Name = userDetails['Tenant_Name']
        Tenant_Country = userDetails['Tenant_Country']
        Tenant_Desc = userDetails['Tenant_Desc']
        #upload_file = userDetails['upload_file']
        Contract_Duration = userDetails['Contract_Duration']
        Starting_Date = userDetails['Starting_Date']
        Ending_Date = userDetails['Ending_Date']
        STATUS = userDetails['STATUS']

        cur = mysql.connection.cursor()
        cur.execute("update opportunity set OPPORTUNITY_NAME=%s,INVESTMENT_AMOUNT=%s,ROI=%s,OPPORTUNITY_TYPE=%s,OPPORTUNITY_DESC=%s,"
                        "AREA_NAME=%s,AREA_STANDARD=%s,REVENUE=%s,EXPENSES=%s,TAX=%s,TENANT_NAME=%s,"
                        "TENANT_COUNTRY=%s,TENANT_DESC=%s,CONTRACT_DURATION=%s,STARTING_DATE=%s,"
                        "ENDING_DATE=%s,STATUS=%s where ID=%s",
                        (opportunity_name,Investment_Amount,ROI,Opportunity_Type,Opportunity_Desc,Area_Name,Area_Standard,
                         Revenue,Expenses,Tax,Tenant_Name,Tenant_Country,Tenant_Desc,Contract_Duration,
                         Starting_Date,Ending_Date,STATUS,Id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "REQUIREMENT UPDATED"})
    return "updated successfully!"


@app.route('/delete', methods=['POST','GET'])
def remove():
    if request.method == 'POST':
        Id = request.json['Id']
        cur = mysql.connection.cursor()
        cur.execute("delete FROM opportunity where ID=%s", (Id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Deleted Successfully"})
    return "unsuccessful!"


@app.route('/edit', methods=['POST','GET'])
def ide():
    if request.method == 'POST':
        ID = request.json['ID'] or request.form['ID']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select * FROM opportunity where ID=%s", (ID,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)
    return "something went wrong try again"




@app.route('/display')
def disp():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT ID,ROI,OPPORTUNITY_NAME,INVESTMENT_AMOUNT,AREA_NAME,OPPORTUNITY_TYPE,STATUS FROM opportunity")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)





@app.route('/portfo', methods=['POST', 'GET'])
def produce():
    if request.method == 'POST' and (request.json or request.form):
        ob1 = None
        print(request.json)

        if request.json:
            ob1 = portfo(request.json)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO portfolio(TOTAL_REVENUE,TOTAL_INVESTED_AMOUNT,PROFIT,TOTAL_NO_OF_INVESTMENTS,OUTLET_NAME) VALUES""(%s,%s,%s,%s,%s)",
                           (ob1.TOTAL_REVENUE,
                            ob1.TOTAL_INVESTED_AMOUNT,
                            ob1.PROFIT,
                            ob1.TOTAL_NO_OF_INVESTMENTS,
                            ob1.OUTLET_NAME,))
            mysql.connection.commit()
            cursor.close()
            return ({"message": "successfully created"})

        return ({"message": "user exists"})


@app.route('/users1')
def user1():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT * FROM portfolio")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails,default=str)
    return "No Data Present"


@app.route('/portfolio', methods=['POST', 'GET'])
def producee():
    if request.method == 'POST' and (request.json or request.form):
        ob1 = None
        print(request.json)

        if request.json:
            ob1 = portfoli(request.json)
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO pharmacy(CL_PRODUCT_ID,INVESTMENT_PRODUCT_NAME,LOCATION,INVESTMENT_AMOUNT,AMOUNT,GROWTH,PROFIT_LOSS,REVENUE,EXPENSES)"
                           " VALUES""(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (ob1.CL_PRODUCT_ID,
                            ob1.INVESTMENT_PRODUCT_NAME,
                            ob1.LOCATION,
                            ob1.INVESTMENT_AMOUNT,
                            ob1.AMOUNT,
                            ob1.GROWTH,
                            ob1.PROFIT_LOSS,
                            ob1.REVENUE,
                            ob1.EXPENSES,))
            mysql.connection.commit()
            cursor.close()
            return ({"message": "successfully created"})

        return ({"message": "user exists"})


@app.route('/play',methods=['GET'])
def play():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT ID,OPPORTUNITY_NAME FROM opportunity")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)



@app.route('/fakepa', methods=['GET', 'POST'])
def upp():
    if request.method == 'POST':
        userDetails = request.json or request.form
        OPPORTUNITY_IMAGE = userDetails['OPPORTUNITY_IMAGE']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO fakepath(OPPORTUNITY_IMAGE,)"  "VALUES""(%s)")
        mysql.connection.commit()
        cursor.close()
        return ({"message": "successfully created"})
    return render_template('upload.html')




@app.route('/invested', methods=['POST'])
def invested():
    if request.method == 'POST':
        userDetails = request.json
        EMAIL = userDetails['EMAIL']
        PASSWORD = userDetails['PASSWORD']

        cur = mysql.connection.cursor()
        cur.execute("select * from invested where EMAIL=%s and PASSWORD=%s",
                    (EMAIL, PASSWORD))
        Data = cur.fetchall()
        if Data is None:
            return "Invalid password/email"
        else:
            resultVal = cur.execute("select * FROM invested where EMAIL=%s", (EMAIL,))
            if resultVal > 0:
                userDetails = cur.fetchall()
                return json.dumps(userDetails, default=str)


@app.route('/inves', methods=['POST', 'GET'])
def inves():
    if request.method == 'POST':
        ID = request.json['ID']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select * FROM opportunity where ID=%s", (ID,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)


@app.route('/reven')
def investrev():
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT REVENUE FROM invested")
    if resultVal > 0:
        userDetails = cur.fetchall()
        return json.dumps(userDetails, default=str)

@app.route('/revenue', methods=['POST', 'GET'])
def revenue():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select REVENUE  from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/graph', methods=['POST', 'GET'])
def chart():
    if request.method =='GET':
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select * from chart")

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)



@app.route('/chart1', methods=['POST', 'GET'])
def revenue01():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select REVENUE,months  from INVESTED where user_id=%s", (user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/first_chart', methods=['POST', 'GET'])
def firstchart():
    if request.method =='POST':
        user_id = request.json['user_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute(" select first_chart.opportunity_id,first_chart.revenues,first_chart.months,first_chart.expenses from invested inner join first_chart on invested.opportunity_id=first_chart.opportunity_id where invested.user_id=%s",(user_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/userdetailsone', methods=['GET', 'POST'])
def userdetailone():
    if request.method == 'POST':
        opportunity_id=request.json['opportunity_id']
        cur = mysql.connection.cursor()
        # cur.execute(" select first_chart.months,first_chart.revenues from invested inner join first_chart on invested.opportunity_id=first_chart.opportunity_id where invested.user_id=%s && invested.opportunity_id=%s",(user_id,opportunity_id))
        # data = cur.fetchall()
        cur.execute("select first_chart.revenues, first_chart.months from invested inner join first_chart on invested.opportunity_id=first_chart.opportunity_id where invested.opportunity_id=%s",(opportunity_id,))
        data1 = cur.fetchall()
        users = json.dumps(data1, default=str)
        data_s = json.loads(users)
        # users1 = json.dumps(data1, default=str)
        # data_s1 = json.loads(users1)
        return jsonify({'users': data_s})

    return 'Unsuccess'


@app.route('/second_chart', methods=['POST', 'GET'])
def secondchart():
    if request.method =='GET':
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select second_chart.revenues,second_chart.months,second_chart.expenses from second_chart cross join invested where second_chart.opportunity_id=invested.opportunity_id")

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

@app.route('/third_chart', methods=['POST', 'GET'])
def thirdchart():
    if request.method =='GET':
        cur = mysql.connection.cursor()
        resultVal = cur.execute("select third_chart.revenues,third_chart.months,third_chart.expenses from third_chart cross join invested where third_chart.opportunity_id=invested.opportunity_id")

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method =='POST':
        opportunity_id = request.json['opportunity_id']
        cur = mysql.connection.cursor()
        resultVal = cur.execute(" select *,first_chart.months,first_chart.revenue from invested join on first_chart where invested.opportunity_id=first_chart.opportunity_id=%s",(opportunity_id,))

        if resultVal > 0:
            userDetails = cur.fetchall()
            return json.dumps(userDetails, default=str)

if __name__ == "__main__":
    app.run(debug=True)
