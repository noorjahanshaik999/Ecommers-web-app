from flask import Flask,redirect,request,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from adminotp import adotp
from itemid import itemidotp
from cmail import sendmail
from adminmail import adminsendmail
import stripe
import os
import random
import stripe
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from admintokenreset import admintoken
from io import BytesIO
app=Flask(__name__)
app.secret_key='hfbfe78hjefk'
app.config['SESSION_TYPE']='filesystem'
stripe.api_key='sk_test_51MzuqjSBGy9yhE2kI5aTydv4Rc8uUF1zIJVwH4BCXzwtFtyuWbQR0NcCieF8zzAKffBqWy7yBakNXoLDW7hg8h1p00VpKFHJDw'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='ecommerceproject'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('home1.html')
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        cursor.execute('select mobile from signup')
        edata=cursor.fetchall()
        #print(data)
        if (mobile, ) in edata:
            flash('User already exisit')
            return render_template('signup.html')
        if (email, ) in data:
            flash('Email id already exisit')
            return render_template('signup.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,address=address,password=password)
    else:
        return render_template('signup.html')    
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from signup where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/Shome')
def home():
    return render_template('home1.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<name>/<mobile>/<email>/<address>/<password>',methods=['GET','POST'])
def otp(otp,name,mobile,email,address,password):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[name,mobile,email,address,password]
            query='insert into signup values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,address=address,password=password)
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            name=request.form['name']
            mobile=request.form['mobile']
            email=request.form['email']
            address=request.form['address']
            password=request.form['password']
            cursor=mysql.connection.cursor()
            email=session.get('user')
            cursor.execute('insert into signup(name,mobile,email,address,password) values(%s,%s,%s,%s,%s)',[name,mobile,email,address,password])
            mysql.connection.commit()
            cursor.close()
            flash(f'{email} added successfully')
            return redirect(url_for('noteshome'))
        return render_template('home1.html')
    else:
        return redirect(url_for('login'))
@app.route('/forgetpassword',methods=['GET','POST'])
def forgetpassword():
    if request.method=='POST':
        email=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from signup where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset password for {data}'
            body=f'reset the password using -{request.host+url_for("createpassword",token=token(email,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user email'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        email=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update signup set password=%s where email=%s',[npass,email])
                mysql.connection.commit()
                return 'Password reset successfull'
            else:
                return 'password mismatch'
        return render_template('newpassword.html')
    except:
        return 'link expired try again'   

'''admin login code'''
@app.route('/adminsignup',methods=['GET','POST'])
def adminsignup():
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from adminsignup')
        data=cursor.fetchall()
        cursor.execute('select mobile from adminsignup')
        edata=cursor.fetchall()
        #print(data)
        if (mobile, ) in edata:
            flash('User already exisit')
            return render_template('adminsignup.html')
        if (email, ) in data:
            flash('Email id already exisit')
            return render_template('adminsignup.html')
        cursor.close()
        adminotp=adotp()
        subject='thanks for registering to the application'
        body=f'use this adminotp to register {adminotp}'
        sendmail(email,subject,body)
        return render_template('adminotp.html',adminotp=adminotp,name=name,mobile=mobile,email=email,password=password)
    else:
        return render_template('adminsignup.html')    
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if session.get('admin'):
        return redirect(url_for('adminhome'))
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from adminsignup where email=%s and password=%s',[email,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid email or password')
            return render_template('adminlogin.html')
        else:
            session['admin']=email
            return redirect(url_for('adminhome'))
    return render_template('adminlogin.html')
@app.route('/adminhome')
def adminhome():
    if session.get('admin'):
        return render_template('admindashboard.html')
    else:
        #flash('login first')
        return redirect(url_for('adminlogin'))
@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('already logged out!')
        return redirect(url_for('adminlogin'))
@app.route('/adminotp/<adminotp>/<name>/<mobile>/<email>/<password>',methods=['GET','POST'])
def adminotp(adminotp,name,mobile,email,password):
    if request.method=='POST':
        uotp=request.form['adminotp']
        if adminotp==uotp:
            cursor=mysql.connection.cursor()
            lst=[name,mobile,email,password]
            query='insert into adminsignup values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('adminlogin'))
        else:
            flash('Wrong otp')
            return render_template('adminotp.html',adminotp=adminotp,name=name,mobile=mobile,email=email,password=password)
@app.route('/adminnotes',methods=['GET','POST'])
def adminnotes():
    if session.get('admin'):
        if request.method=='POST':
            name=request.form['name']
            mobile=request.form['mobile']
            email=request.form['email']
            password=request.form['password']
            cursor=mysql.connection.cursor()
            email=session.get('admin')
            cursor.execute('insert into adminsignup(name,mobile,email,password) values(%s,%s,%s,%s)',[name,mobile,email,password])
            mysql.connection.commit()
            cursor.close()
            flash(f'{email} added successfully')
            return redirect(url_for('noteshome'))
        return render_template('adminhome.html')
    else:
        return redirect(url_for('adminlogin'))
@app.route('/adminforgetpassword',methods=['GET','POST'])
def adminforgetpassword():
    if request.method=='POST':
        email=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select email from adminsignup')
        data=cursor.fetchall()
        if (email,) in data:
            cursor.execute('select email from adminsignup where email=%s',[email])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset password for {data}'
            body=f'reset the password using -{request.host+url_for("admincreatepassword",admintoken=admintoken(email,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('adminlogin'))
        else:
            return 'Invalid user email'
    return render_template('forgot.html')
@app.route('/admincreatepassword/<admintoken>',methods=['GET','POST'])
def admincreatepassword(admintoken):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        email=s.loads(admintoken)['admin']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update adminsignup set password=%s where email=%s',[npass,email])
                mysql.connection.commit()
                return 'Password reset successfull'
            else:
                return 'password mismatch'
        return render_template('adminnewpassword.html')
    except:
        return 'link expired try again'

    '''''additems '''
@app.route('/additems',methods=['GET','POST'])
def additems():
    if session.get('admin'):
        if request.method=="POST":
            name=request.form['name']
            discription=request.form['desc']
            quantity=request.form['qty']
            category=request.form['category']
            price=request.form['price']
            image=request.files['image']
            cursor=mysql.connection.cursor()
            email=session.get('admin')
            idotp=itemidotp()
            filename=idotp+'.jpg'
            cursor.execute('insert into additems(itemid,name,discription,qty,category,price) values(%s,%s,%s,%s,%s,%s)',[idotp,name,discription,quantity,category,price])
            mysql.connection.commit()
            
            print(filename)
            path=r"C:\Users\sk noorjahan\OneDrive\Desktop\ecommerce\static"
            image.save(os.path.join(path,filename))
            print('success')
        return render_template('items.html')
@app.route('/dashboardpage/')
def dashboardpage():
    cursor=mysql.connection.cursor()
    cursor.execute("select * from additems")
    items=cursor.fetchall()
    print(items)
    return render_template('dashboard.html',items=items)
@app.route('/homepage/<category>')
def homepage(category):
    cursor=mysql.connection.cursor()
    cursor.execute("select * from additems where category=%s",[category])
    items=cursor.fetchall()
    return render_template('dashboard.html',items=items)

@app.route('/status')
def status():
    cursor=mysql.connection.cursor()
    cursor.execute('select itemid,name,discription,qty,category,price from additems')
    items=cursor.fetchall()

    return render_template('status.html',items=items)

@app.route('/updateproducts/<itemid>',methods=['GET','POST'])
def updateproducts(itemid):
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select name,discription,qty,category,price from additems where itemid=%s',[itemid])
        items=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
           
            name=request.form['name']
            discription=request.form['discription']
            quantity=request.form['qty']
            category=request.form['category']
            price=request.form['price']

            cursor=mysql.connection.cursor()
            cursor.execute('update additems set name=%s,discription=%s,qty=%s,category=%s,price=%s  where itemid=%s',[name,discription,quantity,category,price,itemid])
            mysql.connection.commit()
            cursor.close()
           
            return redirect(url_for('adminhome'))
        return render_template('updateproducts.html',items=items)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/deleteproducts/<itemid>')
def deleteproducts(itemid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from additems where itemid=%s',[itemid])
    mysql.connection.commit()
    cursor.close()
    path=r"C:\Users\sk noorjahan\OneDrive\Desktop\ecommerce\static"
    filename=itemid+'.jpg'
    os.remove(os.path.join(path,filename))
    return redirect(url_for('status'))





@app.route('/cart/<itemid>/<name>/<discription>/<category>/<price>')
def cart(itemid,name,discription,category,price):
    if not session.get('user'):
        return redirect(url_for('login'))
    if itemid not in session[session.get('user')]:
        session[session.get('user')][itemid]=[name,discription,1,price]
        session.modified=True
        flash(f'{name} added to cart')
        return redirect(url_for('homepage',category=category))
  
    session[session.get('user')][itemid][2]+=1
    flash('Item already in cart')
    return redirect(url_for('homepage',category=category))
@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    items=session.get(session.get('user')) if session.get(session.get('user')) else 'empty'
    if items=='empty':
        return 'no products in cart'
    return render_template('cart.html',items=items)
@app.route('/remcart/<item>')
def rem(item):
    if session.get('user'):
        session[session.get('user')].pop(item)
        return redirect(url_for('viewcart'))
    return redirect(url_for('login'))

@app.route('/dis/<itemid>')
def dis(itemid):
    cursor=mysql.connection.cursor()
    cursor.execute("select * from additems where itemid=%s",[itemid])
    items=cursor.fetchone()
    return render_template('discription.html',items=items)


@app.route('/orders')
def orders():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from orders where username=%s', (session['user'],))
        orders=cursor.fetchall()
        return render_template('orders.html',orders=orders)

@app.route('/pay/<itemid>/<name>/<int:price>',methods=['POST'])
def pay(itemid,price,name):
    if session.get('user'):
        q=int(request.form['qty'])
        username=session.get('user')
        total=price*q
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',itemid=itemid,name=name,q=q,total=total,_external=True),
            line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': q,
                },
                ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<itemid>/<name>/<q>/<total>')
def success(itemid,name,q,total):
    if session.get('user'):
        print(session.get('user'))
        cursor=mysql.connection.cursor()
        cursor.execute('insert into orders(itemid,name,qty,total_price,username) values(%s,%s,%s,%s,%s)',[itemid,name,q,total,session.get('user')])
        mysql.connection.commit()
        return 'Order Placed'
    return redirect(url_for('login'))



@app.route('/review/<itemid>',methods=['GET','POST'])
def review(itemid):
    if session.get('user'):
        if request.method=='POST':
            print(request.form)
            userid=session.get('user')
            title=request.form['title']
            decs=request.form['decs']
            rate=request.form['rate']
            cursor=mysql.connection.cursor()
            cursor.execute('insert into reviews(username,itemid,title,review,rating) values(%s,%s,%s,%s,%s)',[userid,itemid,title,decs,rate])
            mysql.connection.commit()
        return render_template('review.html')
    else:
        return redirect(url_for('login'))
@app.route('/readreview/<itemid>')
def readreview(itemid):
    cursor=mysql.connection.cursor()
    cursor.execute("select * from reviews where itemid=%s",[itemid])
    reviews=cursor.fetchall()
    return render_template('readreview.html',reviews=reviews)
@app.route('/search',methods=['GET','POST'])
def search():
   if request.method=="POST":
       name=request.form['search']
       cursor=mysql.connection.cursor()
       cursor.execute('SELECT * from additems where name=%s',[name])
       data=cursor.fetchall()
       return render_template('dashboard.html',items=data)
@app.route('/contactus',methods=['GET','POST'])
def contactus():
    if request.method=="POST":
        print(request.form)
        name=request.form['name']
        emailid=request.form['emailid']
        message=request.form['message']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into contactus(name,emailid,message) values(%s,%s,%s)',[name,emailid,message])
        mysql.connection.commit()
    return render_template('contactus.html')
    

@app.route('/readcontactus')
def readcontactus():
    cursor=mysql.connection.cursor()
    cursor.execute("select * from contactus ")
    contact=cursor.fetchall()
    return render_template('readcontactus.html',contact=contact)
       
    
app.run(debug=True,use_reloader=True)





