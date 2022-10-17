from flask import Flask, render_template, request, redirect, url_for, session,flash
import ibm_db
import json
import requests
from datetime import date
import pandas as pd
import numpy as np
import smtplib
import ssl
from datetime import datetime as dt
from email.message import EmailMessage
import math,random
county=1
countn=1
pid=0
cart=pd.DataFrame(columns=['Prod','Quantity','Price'])
months = [
    "Jan",
    "Feb",
    "March",
    "April",
    "May",
    "June",
    "July",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec"
]

app = Flask(__name__)
app.secret_key="jugcrtcyf"
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=trs01834;PWD=LYPOnVemOwDBv059",'','')
global user
user=" "

@app.route('/registration')
def home():
    if "user" in session:
        if user=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    return render_template('signup.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if "user" in session:
        if user=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    else:
        x = [x for x in request.form.values()]
        print(x)
        email=x[0]
        username=x[1]
        firstname=x[2]
        lastname=x[3]
        gender=x[4]
        phno=x[5]
        password=x[6]
        cpassword=x[7]
        sql = "SELECT * FROM TRS01834.USER WHERE USERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            flash("You are already a member, please login using your details", category="success")
            return redirect(url_for('login'))
        else:
            if password==cpassword:
                insert_sql = "INSERT INTO TRS01834.USER VALUES (?, ?, ?, ?, ?,?,?)"
                prep_stmt = ibm_db.prepare(conn, insert_sql)
                ibm_db.bind_param(prep_stmt, 1, email)
                ibm_db.bind_param(prep_stmt, 2, username)
                ibm_db.bind_param(prep_stmt, 3, firstname)
                ibm_db.bind_param(prep_stmt, 4, lastname)
                ibm_db.bind_param(prep_stmt, 5, password)
                ibm_db.bind_param(prep_stmt, 6, gender)
                ibm_db.bind_param(prep_stmt, 7, phno)
                ibm_db.execute(prep_stmt)
                
                email_sender='paymentsbook.digital@gmail.com'
                email_password='dvwbxivfnbyvrubz'
                receiver=email
                email_receiver=receiver
                subject="Thank you for creating an account in Digital Payments Book"
                body=f"""Digital Payments Book welcomes to the best community.\nYour account has been successfully created with the username {username}\n\nBest Regards\nTeam Digital Payments Book"""
                em=EmailMessage()
                em['From']=email_sender
                em['To']=email_receiver
                em['subject']=subject
                em.set_content(body)
                context=ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
                flash("Registration Successful, please login using your details", category="success")
                return redirect(url_for('login'))
            else:
                flash("Incorrect Password Confirmation", category="error")
                return redirect(url_for('home'))

       
@app.route('/')    
@app.route('/login')
def login():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main')) 
    else:
        return render_template('login.html')
    
@app.route('/loginpage',methods=['GET','POST'])
def loginpage():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    else:
        user = request.form['username']
        passw = request.form['password']
        sql = "SELECT * FROM TRS01834.USER WHERE USERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,user)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            if passw==account["PASSWORD"]:
                session["user"]=user
                session["fname"]=account["FIRSTNAME"]
                session["lname"]=account["LASTNAME"]
                session["mail"]=account["EMAILID"]
                if user=='Sakshit':
                    flash("Logged in successfully", category="success")
                    return redirect(url_for('amain'))
                else:
                    flash("Logged in successfully", category="success")
                    return redirect(url_for('main'))
            else:
                flash("Login unsuccessful. Incorrect username / password !", category="error")
                return redirect(url_for('login'))
        else:
            flash("Create an account to login", category="error")
            return redirect(url_for('home'))
      
        
@app.route('/main',methods=['POST','GET'])
def main():
    username=" "
    if "user" in session:
        today=date.today()
        month = today.month
        sql="SELECT PRICE,QUANTITY FROM TRS01834.PURCHASES WHERE MONTH(DATE)=? and USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,month)
        ibm_db.bind_param(stmt,2,session["user"])
        ibm_db.execute(stmt)
        expense=ibm_db.fetch_assoc(stmt)
        expenses=0
        count=0
        num=0
        while expense!=False:
            count+=expense["QUANTITY"]
            expenses+=expense["PRICE"]
            
            num+=1
            expense=ibm_db.fetch_assoc(stmt)
        if num==0:
            count=0
            expenses=0
        fname=session["fname"]
        lname=session["lname"]
        select_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,select_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df=pd.json_normalize(prod)
        print(df)
        df.index = df.index + 1
        records = df.to_records(index=False)
        print(records)
        data=list(records)
        print(data)
        return render_template("home.html",user=fname+" "+lname,prod=num,login=session["user"],home="yes",expenses=expenses,month=months[month-1],count=count)
    else:
        return redirect(url_for('login'))

@app.route('/amain',methods=['POST','GET'])
def amain():
    username=" "
    if "user" in session and session["user"]=='Sakshit':
        delete_sql="DELETE FROM TRS01834.PURCHASES WHERE PAID is NULL and QUANTITY is NULL and PRICE is NULL"
        stmt=ibm_db.prepare(conn,delete_sql)
        ibm_db.execute(stmt)
        cart.drop(cart.index,inplace=True) 
        [session.pop(i, None) for i in ["pid","countn","county","price","quantity","uname","next"]]
        fname=session["fname"]
        lname=session["lname"]
        sel_sql="SELECT COUNT(*) AS COUNT FROM (SELECT USERNAME FROM TRS01834.USER WHERE USERNAME!='Sakshit')"
        stmt=ibm_db.prepare(conn,sel_sql)
        ibm_db.execute(stmt)
        cust=ibm_db.fetch_assoc(stmt)
        custs=0
        while cust!=False:
            custs+=cust["COUNT"]
            cust=ibm_db.fetch_assoc(stmt)
        sel_sql="SELECT COUNT(*) AS COUNT FROM (SELECT PID FROM TRS01834.PURCHASES)"
        stmt=ibm_db.prepare(conn,sel_sql)
        ibm_db.execute(stmt)
        pur=ibm_db.fetch_assoc(stmt)
        purs=0
        while pur!=False:
            purs+=pur["COUNT"]
            pur=ibm_db.fetch_assoc(stmt)
        select_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,select_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df=pd.json_normalize(prod)
        print(df)
        df.index = df.index + 1
        records = df.to_records(index=False)
        print(records)
        data=list(records)
        return render_template("ahome.html",user=fname+" "+lname,prod=len(data),login=session["user"],home="yes",cust=custs,purs=purs)
    else:
        return redirect(url_for('login'))

@app.route('/Entry',methods=['POST','GET'])
def Entry():
    if "user" in session:
        if session["user"]=='Sakshit':
            return render_template('aEntry.html',user=session["fname"]+" "+session["lname"])
        else:
            return render_template('Entry.html',user=session["fname"]+" "+session["lname"]) 
    return redirect(url_for('login'))

@app.route('/submitted',methods=['POST','GET'])
def submitted():
    if "user" in session:
        x = [x for x in request.form.values()]
        print(x)
        pname=x[0]
        quantity=x[1]
        paid=x[2]
        user=session["user"]
        if pname=='Choose...':
            flash("Please select product name", category="error")
            return redirect(url_for('main'))
        today = date.today()
        selected_sql="SELECT AMOUNT FROM TRS01834.PRODUCTS WHERE PNAME=?"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.bind_param(prep_stmt1,1,pname)
        ibm_db.execute(prep_stmt1)
        amount = ibm_db.fetch_assoc(prep_stmt1)
        print(amount["AMOUNT"])
        print(quantity)
        price=amount["AMOUNT"]*int(quantity)
        print(price)
        print(today)
        insert_sql = "INSERT INTO TRS01834.PURCHASES(PNAME,QUANTITY,DATE,PAID,USERNAME,PRICE) VALUES (?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, pname)
        ibm_db.bind_param(prep_stmt, 2, quantity)
        ibm_db.bind_param(prep_stmt, 3, today)
        ibm_db.bind_param(prep_stmt, 4, paid)
        ibm_db.bind_param(prep_stmt, 5,user )
        ibm_db.bind_param(prep_stmt, 6,price )
        ibm_db.execute(prep_stmt)
        flash("Purchase added successfully", category="success")
        return redirect(url_for('history')) 
    else:
        return redirect(url_for('login'))
     

@app.route('/aEntry',methods=['POST','GET'])
def aEntry():
    if "user" in session:
        if session["user"]=='Sakshit':
            return render_template('aEntry.html',session["fname"]+" "+session["lname"])
        else:
            return render_template('Entry.html',session["fname"]+" "+session["lname"]) 
    return redirect(url_for('login'))


@app.route('/asubmitted',methods=['POST','GET'])
def asubmitted():
    if "user" in session and session["user"]=='Sakshit':
        x = [x for x in request.form.values()]
        print(x)
        pname=x[0]
        price=x[1]
        cat=x[2]
        insert_sql = "INSERT INTO TRS01834.PRODUCTS(PNAME,AMOUNT,CATEGORY) VALUES (?, ?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, pname)
        ibm_db.bind_param(prep_stmt, 2, price)
        ibm_db.bind_param(prep_stmt, 3, cat)
        try:
            ibm_db.execute(prep_stmt)
            flash("Product added successfully", category="success")
            return redirect(url_for('product'))
        except:
            flash("Product already exists", category="error")
            return redirect(url_for('product')) 
    else:
        return redirect(url_for('login'))

@app.route('/aEntry2',methods=['POST','GET'])
def aEntry2():
    if "user" in session:
        global cart
        today = date.today()
        carts = list(zip(*map(cart.get, cart)))
        sql="SELECT USERNAME FROM TRS01834.USER where USERNAME!='Sakshit'"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.execute(stmt)
        users=ibm_db.fetch_assoc(stmt)
        user1=[]
        while users!=False:
            user1.append(users)
            users=ibm_db.fetch_assoc(stmt)
        df1=pd.json_normalize(user1)
        users=df1.to_records(index=False)
        userlist=list(users)
        select_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,select_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df=pd.json_normalize(prod)
        print(df)
        df.index = df.index + 1
        records = df.to_records(index=False)
        print(records)
        data=list(records)
        if "uname" in session:
            if len(cart)==0:
                if "next" in session:
                    return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,uname=session["uname"],cart=" ",date=today,userdata=userlist,special='no')
                else:
                    return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,uname=session["uname"],cart=" ",date=today,userdata=userlist,special=" ")
            if "next" in session:
                return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,uname=session["uname"],cart=carts,date=today,userdata=userlist,special='no')
            else:
                return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,uname=session["uname"],cart=carts,date=today,userdata=userlist,special=" ")
        if len(cart)==0:
            if "next" in session:
                return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,cart=" ",date=today,userdata=userlist,special="no")
            else:
                return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,cart=" ",date=today,userdata=userlist,special=" ")
        if "next" in session:
            return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,cart=carts,date=today,userdata=userlist,special='no')
        else:
            return render_template('aEntry2.html',user=session["fname"]+" "+session["lname"],login=session["user"],prod=data,cart=carts,date=today,userdata=userlist,special=" ")
    else:
        return redirect(url_for('login'))

@app.route('/asubmitted2',methods=['POST','GET'])
def asubmitted2():
    if "user" in session and session["user"]=='Sakshit':
        global cart
        x = [x for x in request.form.values()]
        print(x)
        uname=x[0]
        pname=x[1]
        print(pname)
        quantity=x[2]
        paid=x[3]
        today=x[4]
        if "countn" not in session and "county" not in session:
            cart.drop(cart.index,inplace=True)
            # today = date.today()
            insert_sql = "SELECT PID FROM FINAL TABLE(INSERT INTO TRS01834.PURCHASES(DATE,USERNAME) VALUES (?,?))"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, today)
            ibm_db.bind_param(prep_stmt, 2,uname )
            ibm_db.execute(prep_stmt)
            pids = ibm_db.fetch_assoc(prep_stmt)
            session["pid"]=pids["PID"]
            session["countn"]=1
            if pname=='Choose...':
                flash("Please select product name", category="error")
                return redirect(url_for('aEntry2'))
            in_sql="INSERT INTO PAYMENT VALUES(?,?,?)"
            pre_stmt=ibm_db.prepare(conn,in_sql)
            ibm_db.bind_param(pre_stmt,1,pname)
            ibm_db.bind_param(pre_stmt,3,session["pid"])
            ibm_db.bind_param(pre_stmt,2,int(quantity))
            ibm_db.execute(pre_stmt)
            selected_sql="SELECT AMOUNT FROM TRS01834.PRODUCTS WHERE PNAME=?"
            prep_stmt1=ibm_db.prepare(conn,selected_sql)
            ibm_db.bind_param(prep_stmt1,1,pname)
            ibm_db.execute(prep_stmt1)
            amount = ibm_db.fetch_assoc(prep_stmt1)
            print(amount["AMOUNT"])
            print(quantity)
            price=amount["AMOUNT"]*int(quantity)
            if "price" in session:
                session["price"]+=price
            else:
                session["price"]=price
            if "quantity" in session:
                session["quantity"]+=int(quantity)
            else:
                session["quantity"]=int(quantity)
            insert_sql1 = "UPDATE TRS01834.PURCHASES SET QUANTITY=?,PRICE=?,PAID=?,DATE=? WHERE PID=?"
            prep1_stmt = ibm_db.prepare(conn, insert_sql1)
            ibm_db.bind_param(prep1_stmt, 1, session["quantity"])
            ibm_db.bind_param(prep1_stmt, 2,session["price"])
            ibm_db.bind_param(prep1_stmt, 3,paid)
            ibm_db.bind_param(prep1_stmt, 4,today)
            ibm_db.bind_param(prep1_stmt, 5,session["pid"])
            ibm_db.execute(prep1_stmt)
            pri=session["price"]
            [session.pop(i, None) for i in ["pid","county","conutn","price","quantity","uname","next"]]
            flash(f"Purchase added successfully,Total price = {pri}", category="success")
            del pri
            return redirect(url_for('ahistory',usr=uname))
        else:
            cart.drop(cart.index,inplace=True)
            if pname=='Choose...':
                flash("Please select product name", category="error")
                return redirect(url_for('aEntry2'))
            in_sql="INSERT INTO PAYMENT VALUES(?,?,?)"
            pre_stmt=ibm_db.prepare(conn,in_sql)
            ibm_db.bind_param(pre_stmt,1,pname)
            ibm_db.bind_param(pre_stmt,3,session["pid"])
            ibm_db.bind_param(pre_stmt,2,int(quantity))
            ibm_db.execute(pre_stmt)    
            selected_sql="SELECT AMOUNT FROM TRS01834.PRODUCTS WHERE PNAME=?"
            prep_stmt1=ibm_db.prepare(conn,selected_sql)
            ibm_db.bind_param(prep_stmt1,1,pname)
            ibm_db.execute(prep_stmt1)
            amount = ibm_db.fetch_assoc(prep_stmt1)
            print(amount["AMOUNT"])
            print(quantity)
            price=amount["AMOUNT"]*int(quantity)
            if "price" in session:
                session["price"]+=price
            else:
                session["price"]=price
            if "quantity" in session:
                session["quantity"]+=int(quantity)
            else:
                session["quantity"]=int(quantity)
            insert_sql1 = "UPDATE TRS01834.PURCHASES SET QUANTITY=?,PRICE=?,PAID=?,DATE=? WHERE PID=?"
            prep1_stmt = ibm_db.prepare(conn, insert_sql1)
            ibm_db.bind_param(prep1_stmt, 1, session["quantity"])
            ibm_db.bind_param(prep1_stmt, 2,session["price"])
            ibm_db.bind_param(prep1_stmt, 3,paid)
            ibm_db.bind_param(prep1_stmt, 4,today)
            ibm_db.bind_param(prep1_stmt,5,session["pid"])
            ibm_db.execute(prep1_stmt)
            pri=session["price"]
            [session.pop(i, None) for i in ["pid","county","conutn","price","quantity","uname","next"]]
            flash(f"Purchase added successfully,Total price={pri}", category="success")
            del pri
            return redirect(url_for('ahistory',usr=uname))

    else:
        return redirect(url_for('login'))

@app.route('/next',methods=['GET','POST'])
def next():
    x = [x for x in request.form.values()]
    global cart
    print(x)
    uname=x[0]
    pname=x[1]
    print(pname)
    quantity=x[2]
    today=x[4]
    if "county" not in session:
        [session.pop(i, None) for i in ["pid","conutn","price","quantity","next"]]
        # today = date.today()
        session["next"]="yes"
        insert_sql = "SELECT PID FROM FINAL TABLE(INSERT INTO TRS01834.PURCHASES(DATE,USERNAME) VALUES (?,?))"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, today)
        ibm_db.bind_param(prep_stmt, 2,uname )
        ibm_db.execute(prep_stmt)
        pids = ibm_db.fetch_assoc(prep_stmt)
        session["pid"]=pids["PID"]
        session["uname"]=uname
        session["county"]=1
        if pname=='Choose...':
            flash("Please select product name", category="error")
            return redirect(url_for('aEntry2'))
        in_sql="INSERT INTO PAYMENT VALUES(?,?,?)"
        pre_stmt=ibm_db.prepare(conn,in_sql)
        ibm_db.bind_param(pre_stmt,1,pname)
        ibm_db.bind_param(pre_stmt,3,session["pid"])
        ibm_db.bind_param(pre_stmt,2,int(quantity))
        ibm_db.execute(pre_stmt)
        selected_sql="SELECT AMOUNT FROM TRS01834.PRODUCTS WHERE PNAME=?"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.bind_param(prep_stmt1,1,pname)
        ibm_db.execute(prep_stmt1)
        amount = ibm_db.fetch_assoc(prep_stmt1)
        print(amount["AMOUNT"])
        print(quantity)
        price=amount["AMOUNT"]*int(quantity)
        cart=cart.append({'Prod':pname,'Quantity':quantity,'Price':price},ignore_index=True)
        if "price" in session:
                session["price"]+=price
        else:
            session["price"]=price
        if "quantity" in session:
            session["quantity"]+=int(quantity)
        else:
            session["quantity"]=int(quantity)
        return redirect(url_for('aEntry2'))
    else:
              
        if pname=='Choose...':
                flash("Please select product name", category="error")
                return redirect(url_for('amain'))
        in_sql="INSERT INTO PAYMENT VALUES(?,?,?)"
        pre_stmt=ibm_db.prepare(conn,in_sql)
        ibm_db.bind_param(pre_stmt,1,pname)
        ibm_db.bind_param(pre_stmt,3,session["pid"])
        ibm_db.bind_param(pre_stmt,2,int(quantity))
        ibm_db.execute(pre_stmt)
        selected_sql="SELECT AMOUNT FROM TRS01834.PRODUCTS WHERE PNAME=?"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.bind_param(prep_stmt1,1,pname)
        ibm_db.execute(prep_stmt1)
        amount = ibm_db.fetch_assoc(prep_stmt1)
        print(amount["AMOUNT"])
        print(quantity)
        price=amount["AMOUNT"]*int(quantity)
        cart=cart.append({'Prod':pname,'Quantity':quantity,'Price':price},ignore_index=True)
        if "price" in session:
                session["price"]+=price
        else:
            session["price"]=price
        if "quantity" in session:
            session["quantity"]+=int(quantity)
        else:
            session["quantity"]=int(quantity)
        return redirect(url_for('aEntry2'))
   
@app.route('/special')
def special():
    if "user" in session and session["user"]=='Sakshit':
        today=date.today()
        sql="SELECT USERNAME FROM TRS01834.USER where USERNAME!='Sakshit'"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.execute(stmt)
        users=ibm_db.fetch_assoc(stmt)
        user1=[]
        while users!=False:
            user1.append(users)
            users=ibm_db.fetch_assoc(stmt)
        df1=pd.json_normalize(user1)
        users=df1.to_records(index=False)
        userlist=list(users)
        return render_template("special.html",date=today,userdata=userlist,user=session["fname"]+" "+session["lname"],login=session["user"])
    else:
        return redirect(url_for('login'))

@app.route('/purchase',methods=['GET','POST'])
def purchase():
    if "user" in session:
        x = [x for x in request.form.values()]
        uname=x[0]
        pname=x[1]
        num=x[2]
        price=x[3]
        paid=x[4]
        today=x[5]
        select_sql="SELECT PID FROM FINAL TABLE(INSERT INTO TRS01834.PURCHASES(QUANTITY,DATE,PAID,USERNAME,PRICE) VALUES (?,?,?,?,?))"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,num)
        ibm_db.bind_param(prep1_stmt, 2,today)
        ibm_db.bind_param(prep1_stmt, 3,paid)
        ibm_db.bind_param(prep1_stmt, 4,uname)
        ibm_db.bind_param(prep1_stmt, 5,price)
        ibm_db.execute(prep1_stmt)
        pids=ibm_db.fetch_assoc(prep1_stmt)
        pid=pids["PID"]
        insert_sql="INSERT INTO PAYMENT VALUES (?,?,?)"
        prep1_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep1_stmt, 1,pname)
        ibm_db.bind_param(prep1_stmt, 2,num)
        ibm_db.bind_param(prep1_stmt, 3,pid)
        ibm_db.execute(prep1_stmt)
        flash(f"Purchase added successfully,Total price={price}", category="success")
        return redirect(url_for('ahistory',usr=uname))
    else:
        return redirect(url_for('login'))

@app.route('/history',methods=['GET','POST'])
def history():
    if "user" in session:
        select_sql="SELECT TRS01834.PURCHASES.PID,TRS01834.PURCHASES.DATE,TRS01834.PURCHASES.QUANTITY,TRS01834.PURCHASES.PRICE,PAID FROM TRS01834.USER u,TRS01834.PURCHASES WHERE u.USERNAME=? and TRS01834.PURCHASES.USERNAME=u.USERNAME"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,session["user"])
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        pids=[]
        while count!=False:
            hist.append(count)
            pids.append(count["PID"])
            count = ibm_db.fetch_assoc(prep1_stmt)
        product=[]
        for i in pids:
            sel_sql="SELECT PNAME,COUNT FROM TRS01834.PAYMENT WHERE PID=?"
            pre_stmt=ibm_db.prepare(conn,sel_sql)
            ibm_db.bind_param(pre_stmt,1,i)
            ibm_db.execute(pre_stmt)
            count=ibm_db.fetch_assoc(pre_stmt)
            var=""
            j=0
            while count!=False:
                if j==0:
                    var+=(count["PNAME"]+"*"+str(count["COUNT"]))
                else:
                    var+=(', '+count["PNAME"]+"*"+str(count["COUNT"]))
                j+=1
                count=ibm_db.fetch_assoc(pre_stmt)
            product.append(var)

        print(hist)
        selected_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df1=pd.json_normalize(prod)
        df1.index = df1.index + 1
        records1 = df1.to_records(index=False)
        print(records1)
        prods=list(records1)
        df=pd.json_normalize(hist)
        if len(df)==0:
            return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=" ",usern=session["user"],prod=prods,login=session["user"],pending=" ")
        df.insert(loc=2,column='product',value=product)
        print(df)
        df.index = df.index + 1
        records = df.to_records(index=False)
        data=list(records)
        return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=data,usern=session["user"],prod=prods,login=session["user"],pending=" ")
    else:
        return redirect(url_for('login'))

@app.route('/pending',methods=['GET','POST'])
def pending():
    if "user" in session:
        username=" "
        usern=session["user"]
        select_sql="SELECT TRS01834.PURCHASES.PID,TRS01834.PURCHASES.DATE,TRS01834.PURCHASES.QUANTITY,TRS01834.PURCHASES.PRICE,PAID FROM TRS01834.USER u,TRS01834.PURCHASES WHERE u.USERNAME=? and TRS01834.PURCHASES.USERNAME=u.USERNAME and paid='no'"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,session["user"])
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        pids=[]
        while count!=False:
            hist.append(count)
            pids.append(count["PID"])
            count = ibm_db.fetch_assoc(prep1_stmt)
        print(hist)
        product=[]
        for i in pids:
            sel_sql="SELECT PNAME,COUNT FROM TRS01834.PAYMENT WHERE PID=?"
            pre_stmt=ibm_db.prepare(conn,sel_sql)
            ibm_db.bind_param(pre_stmt,1,i)
            ibm_db.execute(pre_stmt)
            count=ibm_db.fetch_assoc(pre_stmt)
            var=""
            j=0
            while count!=False:
                if j==0:
                    var+=(count["PNAME"]+"*"+str(count["COUNT"]))
                else:
                    var+=(', '+count["PNAME"]+"*"+str(count["COUNT"]))
                j+=1
                count=ibm_db.fetch_assoc(pre_stmt)
            product.append(var)
        selected_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df1=pd.json_normalize(prod)
        df1.index = df1.index + 1
        records1 = df1.to_records(index=False)
        print(records1)
        prods=list(records1)
        df=pd.json_normalize(hist)
        if len(df)==0:
            return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=" ",usern=usern,prod=prods,login=session["user"],pending='yes')
        
        df.insert(loc=2,column='product',value=product)
        print(df)
        df.index = df.index + 1
        
        records = df.to_records(index=False)
        data=list(records)

        print(count)
        return render_template('history.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=data,usern=usern,prod=prods,login=session["user"],pending='yes')
    else:
        return redirect(url_for('login'))


@app.route('/ahistory/<usr>',methods=['GET','POST'])
def ahistory(usr):
    if "user" in session and session["user"]=='Sakshit':
        delete_sql="DELETE FROM TRS01834.PURCHASES WHERE PAID is NULL and QUANTITY is NULL and PRICE is NULL"
        stmt=ibm_db.prepare(conn,delete_sql)
        ibm_db.execute(stmt)
        select_sql="SELECT TRS01834.PURCHASES.PID,TRS01834.PURCHASES.DATE,TRS01834.PURCHASES.QUANTITY,TRS01834.PURCHASES.PRICE,PAID FROM TRS01834.USER u,TRS01834.PURCHASES WHERE u.USERNAME=? and TRS01834.PURCHASES.USERNAME=u.USERNAME"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,usr)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        pids=[]
        while count!=False:
            hist.append(count)
            pids.append(count["PID"])
            count = ibm_db.fetch_assoc(prep1_stmt)
        product=[]
        for i in pids:
            sel_sql="SELECT PNAME,COUNT FROM TRS01834.PAYMENT WHERE PID=?"
            pre_stmt=ibm_db.prepare(conn,sel_sql)
            ibm_db.bind_param(pre_stmt,1,i)
            ibm_db.execute(pre_stmt)
            count=ibm_db.fetch_assoc(pre_stmt)
            var=""
            j=0
            while count!=False:
                if j==0:
                    var+=(count["PNAME"]+"*"+str(count["COUNT"]))
                else:
                    var+=(', '+count["PNAME"]+"*"+str(count["COUNT"]))
                j+=1
                count=ibm_db.fetch_assoc(pre_stmt)
            product.append(var)

        print(hist)
        selected_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df1=pd.json_normalize(prod)
        df1.index = df1.index + 1
        records1 = df1.to_records(index=False)
        print(records1)
        prods=list(records1)
        df=pd.json_normalize(hist)
        if len(df)==0:
            return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=" ",usern=session["user"],usr=usr,prod=prods,login=session["user"],pending=" ")
        df.insert(loc=2,column='product',value=product)
        print(df)
        df.index = df.index + 1
        records = df.to_records(index=False)
        data=list(records)
        return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=data,usr=usr,usern=session["user"],prod=prods,login=session["user"],pending=" ")
    else:
        return redirect(url_for('login'))

@app.route('/apending/<usr>',methods=['GET','POST'])
def apending(usr):
    if "user" in session and session["user"]=='Sakshit':
        username=" "
        usern=session["user"]
        session["pend"]=usr
        select_sql="SELECT TRS01834.PURCHASES.PID,TRS01834.PURCHASES.DATE,TRS01834.PURCHASES.QUANTITY,TRS01834.PURCHASES.PRICE,PAID FROM TRS01834.USER u,TRS01834.PURCHASES WHERE u.USERNAME=? and TRS01834.PURCHASES.USERNAME=u.USERNAME and paid='no'"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,usr)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        pids=[]
        while count!=False:
            hist.append(count)
            pids.append(count["PID"])
            count = ibm_db.fetch_assoc(prep1_stmt)
        print(hist)
        product=[]
        for i in pids:
            sel_sql="SELECT PNAME,COUNT FROM TRS01834.PAYMENT WHERE PID=?"
            pre_stmt=ibm_db.prepare(conn,sel_sql)
            ibm_db.bind_param(pre_stmt,1,i)
            ibm_db.execute(pre_stmt)
            count=ibm_db.fetch_assoc(pre_stmt)
            var=""
            j=0
            while count!=False:
                if j==0:
                    var+=(count["PNAME"]+"*"+str(count["COUNT"]))
                else:
                    var+=(', '+count["PNAME"]+"*"+str(count["COUNT"]))
                j+=1
                count=ibm_db.fetch_assoc(pre_stmt)
            product.append(var)
        selected_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df1=pd.json_normalize(prod)
        df1.index = df1.index + 1
        records1 = df1.to_records(index=False)
        print(records1)
        prods=list(records1)
        df=pd.json_normalize(hist)
        if len(df)==0:
            return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=" ",usern=usern,prod=prods,login=session["user"],pending='yes',usr=usr)
        
        df.insert(loc=2,column='product',value=product)
        print(df)
        df.index = df.index + 1
        
        records = df.to_records(index=False)
        data=list(records)

        print(count)
        return render_template('history.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=data,usern=usern,prod=prods,login=session["user"],pending='yes',usr=usr)
    else:
        return redirect(url_for('login'))

@app.route('/updatepaid/<pid>')
def updatepaid(pid):
    if "user" in session and "pend" in session and session["user"]=='Sakshit':
        update_sql="UPDATE TRS01834.PURCHASES SET PAID='yes' WHERE PID=?"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1,pid)
        ibm_db.execute(prep_stmt)
        flash("Purchase removed from pending payments")
        return redirect(url_for('apending',usr=session["pend"]))
    elif "user" in session:
        return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))

@app.route('/users',methods=['GET','POST'])
def users():
    if "user" in session and session["user"]=='Sakshit':
        select_sql="SELECT USERNAME,FIRSTNAME,LASTNAME FROM TRS01834.USER where USERNAME!='Sakshit'"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        user=[]
        while count!=False:
            user.append(count)
            count = ibm_db.fetch_assoc(prep1_stmt)
        print(user)
        df=pd.json_normalize(user)
        print(df)
        df.index = df.index + 1
        if len(df)==0:
            return render_template('users.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=" ",login=session["user"])
        df["Name"] = df['FIRSTNAME'] +" "+ df["LASTNAME"]
        df=df.drop(['FIRSTNAME','LASTNAME'],axis=1)
        df["history"]=" "
        records = df.to_records(index=False)
        data=list(records)
        print(data)

        print(count)
        return render_template('users.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=data,login=session["user"])
    else:
        return redirect(url_for('login'))


@app.route('/profile') 
def profile():
    if "user" in session:
        username=" "
        username=session["user"]
        select_sql="SELECT EMAILID,FIRSTNAME,LASTNAME,GENDER,PHNNO FROM TRS01834.USER where USERNAME=?"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,username)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        session["email"]=count["EMAILID"]
        email=session["email"]
        session["fname"]=count["FIRSTNAME"]
        firstname=session["fname"]
        session["lname"]=count["LASTNAME"]
        lastname=session["lname"]
        session["gender"]=count["GENDER"]
        gender=session["gender"]
        session["phno"]=count["PHNNO"]
        phno=session["phno"]
        select_sql="SELECT DATE FROM TRS01834.PURCHASES where USERNAME=?"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,username)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        if count!=False:
            num=0
            while count!=False:
                num=num+1
                count = ibm_db.fetch_assoc(prep1_stmt)
            select_sql="SELECT DATE FROM TRS01834.PURCHASES where USERNAME=? and DATE>=(SELECT MAX(DATE) FROM TRS01834.PURCHASES where USERNAME=?)"
            prep1_stmt = ibm_db.prepare(conn, select_sql)
            ibm_db.bind_param(prep1_stmt, 1,username)
            ibm_db.bind_param(prep1_stmt, 2,username)
            ibm_db.execute(prep1_stmt)
            count = ibm_db.fetch_assoc(prep1_stmt)
            session["lpurchase"]=count["DATE"]
            lpur=session["lpurchase"]
            return render_template('profile.html',usr=username,email=email, lname=lastname, fname=firstname,user=session["fname"]+" "+session["lname"],lpur=lpur,num=num,gender=gender,phn=phno,login=session["user"])
        else:
            return render_template('profile.html',usr=username,email=email, lname=lastname, fname=firstname,user=session["fname"]+" "+session["lname"],lpur="NA",num="NA",gender=gender,phn=phno,login=session["user"])  
    else:
         return redirect(url_for('login'))

@app.route('/expenses')
def expenses():
    if "user" in session:
        select_sql="SELECT DISTINCT MONTH(DATE) AS MONTH,YEAR(DATE) AS YEAR FROM TRS01834.PURCHASES WHERE USERNAME=?"
        prep_stmt=ibm_db.prepare(conn,select_sql)
        ibm_db.bind_param(prep_stmt,1,session["user"])
        ibm_db.execute(prep_stmt)
        month=ibm_db.fetch_assoc(prep_stmt)
        years=[]
        months1=[]
        prices=[]
        quant=[]
        months2=[]
        while month!=False:
            years.append(month["YEAR"])
            months1.append(month["MONTH"])
            months2.append(months[month["MONTH"]-1])
            month=ibm_db.fetch_assoc(prep_stmt)
        for i in zip(months1,years):
            select_sql="SELECT PRICE,QUANTITY FROM TRS01834.PURCHASES WHERE MONTH(DATE)=? AND YEAR(DATE)=? AND USERNAME=?"
            prep_stmt=ibm_db.prepare(conn,select_sql)
            ibm_db.bind_param(prep_stmt,1,i[0])
            ibm_db.bind_param(prep_stmt,2,i[1])
            ibm_db.bind_param(prep_stmt,3,session["user"])
            ibm_db.execute(prep_stmt)
            price=ibm_db.fetch_assoc(prep_stmt)
            num=0
            count=0
            while price!=False:
                num+=price["PRICE"]
                count+=price["QUANTITY"]
                price=ibm_db.fetch_assoc(prep_stmt)
            prices.append(num)
            quant.append(count)
        df = pd.DataFrame(list(zip(years, months2,quant,prices)),
               columns =['Year', 'Month','Count','Price'])
        records = df.to_records(index=False)
        data=list(records)
        if len(df)==0:
            return render_template('expenses.html',data=" ",user=session["fname"]+" "+session["lname"],login=session["user"],usr=session["user"])
        return render_template('expenses.html',data=data,user=session["fname"]+" "+session["lname"],login=session["user"],usr=session["user"])

@app.route('/contactus')
def contactus():
    if "user" in session:
        usern=session["user"]
        select_sq="SELECT * FROM TRS01834.USER where USERNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,usern)
        ibm_db.execute(prep_stmt)
        mail = ibm_db.fetch_assoc(prep_stmt)
        receiver=mail["EMAILID"]
        fname=mail["FIRSTNAME"]
        lname=mail["LASTNAME"]
        gender=mail["GENDER"]
        phno=mail["PHNNO"]
        return render_template('contact.html',user=session["fname"]+" "+session["lname"],login=session["user"],usr=usern,mail=receiver,fname=fname,lname=lname)
    else:
        return redirect(url_for('login'))

@app.route('/sendmail')
def sendmail():
    if "user" in session and session["user"]=="Sakshit":
        x=0
        email_sender='paymentsbook.digital@gmail.com'
        email_password='dvwbxivfnbyvrubz'
        today = date.today()
        select_sql="SELECT PID,USERNAME,DATE,PRICE FROM TRS01834.PURCHASES where PAID='no'"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        receiver=[]
        while count!=False:
            today=str(today)
            date1=str(count["DATE"])
            res = (dt.strptime(today, "%Y-%m-%d") - dt.strptime(date1, "%Y-%m-%d")).days
            if res>=60:
                x+=1
                select_sq="SELECT EMAILID FROM TRS01834.USER where USERNAME=?"
                prep_stmt = ibm_db.prepare(conn, select_sq)
                ibm_db.bind_param(prep_stmt, 1,count["USERNAME"])
                ibm_db.execute(prep_stmt)
                mail = ibm_db.fetch_assoc(prep_stmt)
                receiver=mail["EMAILID"]
                email_receiver=receiver
                subject="Payment Reminder"
                body=f"""Hi {count["USERNAME"]}\n\nI hope you are well.\n\nIt's been 30 days since you haven't paid us for your purchase.The amount of Rs.{count["PRICE"]} in respect of our invoice {count["PID"]} is due for payment on {count["DATE"]}.\n\nThis is the last call from us.You must pay the amount as soon as possible.It would be really grateful if you could confirm that everything is on track for payment.\n\nBest regards\nTeam Digital Payments Book"""
                
                em=EmailMessage()
                em['From']=email_sender
                em['To']=email_receiver
                em['subject']=subject
                em.set_content(body)
                context=ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
            elif res>=30:
                x+=1
                select_sq="SELECT EMAILID FROM TRS01834.USER where USERNAME=?"
                prep_stmt = ibm_db.prepare(conn, select_sq)
                ibm_db.bind_param(prep_stmt, 1,count["USERNAME"])
                ibm_db.execute(prep_stmt)
                mail = ibm_db.fetch_assoc(prep_stmt)
                receiver=mail["EMAILID"]
                email_receiver=receiver
                subject="Payment Reminder"
                body=f"""Hi {count["USERNAME"]}\n\nI hope you are well.\n\nIt's been 30 days since you haven't paid us for your purchase.The amount of Rs.{count["PRICE"]} in respect of our invoice {count["PID"]} is due for payment on {count["DATE"]}.\n\nYou need to pay the amount immediately.It would be really grateful if you could confirm that everything is on track for payment.\n\nBest regards\nTeam Digital Payments Book"""
                em=EmailMessage()
                em['From']=email_sender
                em['To']=email_receiver
                em['subject']=subject
                em.set_content(body)
                context=ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
            elif res>=0:
                x+=1
                select_sq="SELECT EMAILID FROM TRS01834.USER where USERNAME=?"
                prep_stmt = ibm_db.prepare(conn, select_sq)
                ibm_db.bind_param(prep_stmt, 1,count["USERNAME"])
                ibm_db.execute(prep_stmt)
                mail = ibm_db.fetch_assoc(prep_stmt)
                receiver=mail["EMAILID"]
                email_receiver=receiver
                subject="Payment Reminder"
                body=f"""Hi {count["USERNAME"]}\n\nI hope you are well.\n\nI just wanted to drop you a quick note to remind you that Rs.{count["PRICE"]} in respect of our invoice {count["PID"]} is due for payment on {count["DATE"]}.\n\nIt would be really grateful if you could confirm that everything is on track for payment.\n\nBest regards\nTeam Digital Payments Book"""
                em=EmailMessage()
                em['From']=email_sender
                em['To']=email_receiver
                em['subject']=subject
                em.set_content(body)
                context=ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
            
            count = ibm_db.fetch_assoc(prep1_stmt)
        if x>0:
            flash("Mails are sent to the customers having dues", category="success")
            return redirect(url_for('users'))
        else:
            flash("No customers with dues..", category="success")
            return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))

    
@app.route('/product',methods=['GET','POST'])
def product():
    if "user" in session:
        select_sql="SELECT PNAME,AMOUNT,CATEGORY FROM TRS01834.PRODUCTS"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        while count!=False:
            hist.append(count)
            count = ibm_db.fetch_assoc(prep1_stmt)
        print(hist)
        df=pd.json_normalize(hist)
        print(df)
        df.index = df.index + 1
        if len(df)==0:
            return render_template('products.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=" ",usr=session["user"],login=session["user"])
        records = df.to_records(index=False)
        data=list(records)
        print(data)
        print(count)
        return render_template('products.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=data,usr=session["user"],login=session["user"])
    else:
        return redirect(url_for('login'))

@app.route('/password')
def password():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    else:
        return render_template("password.html")

@app.route('/forgot',methods=['POST','GET'])
def forgot():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    elif "incorrect" in session:
        return render_template("forgot.html")
    else:
        receiver=" "
        email_sender='paymentsbook.digital@gmail.com'
        email_password='dvwbxivfnbyvrubz'
        code=generateOTP()
        usern = request.form["username"]
        session["userf"]=usern
        session["code"]=code
        select_sq="SELECT EMAILID FROM TRS01834.USER where USERNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,usern)
        ibm_db.execute(prep_stmt)
        mail = ibm_db.fetch_assoc(prep_stmt)
        receiver=mail["EMAILID"]
        email_receiver = receiver
        subject="OTP for Password Reset"
        body=f"Hello {usern}\n\nYour one time password for password reset is {code}\nPlease do not share your OTP with anyone\n\nThank you\nTeam Digital Payments Book"
        em=EmailMessage()
        em['From']=email_sender
        em['To']=email_receiver
        em['subject']=subject
        em.set_content(body)
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        return render_template("forgot.html")

@app.route('/reset',methods=['POST','GET'])
def reset():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    else:
        if "userf" in session:
            otp=request.form["OTP"]
            if otp==session["code"]:
                return render_template("reset.html")
            else:
                flash("incorrect OTP",category="error")
                session["incorrect"]='yes'
                return redirect(url_for('forgot'))
        else:
            return redirect(url_for('login'))

@app.route('/done',methods=['GET','POST'])
def done():
    if "user" in session:
        if session["user"]=='Sakshit':
            return redirect(url_for('amain'))
        else:
            return redirect(url_for('main'))
    else:
        if "userf" in session:
            password=request.form["password"]
            usern=session["userf"]
            select_sq="UPDATE TRS01834.USER SET PASSWORD=? WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, select_sq)
            ibm_db.bind_param(prep_stmt, 1,password)
            ibm_db.bind_param(prep_stmt, 2,usern)
            ibm_db.execute(prep_stmt)
            flash("Password reset successful",category="success")
            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

@app.route('/faq')
def faq():
    if "user" in session:
        return render_template("faq.html",user=session["fname"]+" "+session["lname"],login=session["user"])
    else:
        return redirect(url_for('login'))

def generateOTP() :
 
    digits = "0123456789"
    OTP = ""
 
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP

@app.route('/edit')
def edit():
    if "user" in session:
        usern=session["user"]
        select_sq="SELECT * FROM TRS01834.USER where USERNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,usern)
        ibm_db.execute(prep_stmt)
        mail = ibm_db.fetch_assoc(prep_stmt)
        receiver=mail["EMAILID"]
        fname=mail["FIRSTNAME"]
        lname=mail["LASTNAME"]
        gender=mail["GENDER"]
        phno=mail["PHNNO"]
        return render_template("edit.html",user=session["fname"]+" "+session["lname"],mail=receiver,fname=fname,lname=lname,usr=usern,gender=gender,phno=phno,login=session["user"])
    else:
        return redirect(url_for('login'))

@app.route('/update',methods=['GET','POST'])
def update():
    if "user" in session:
        x = [x for x in request.form.values()]
        print(x)
        user=session["user"]
        firstname=x[2]
        lastname=x[3]
        gender=x[4]
        phno=x[5]
        select_sq="UPDATE TRS01834.USER SET FIRSTNAME=?,LASTNAME=?,GENDER=?,PHNNO=? WHERE USERNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,firstname)
        ibm_db.bind_param(prep_stmt, 2,lastname)
        ibm_db.bind_param(prep_stmt, 3,gender)
        ibm_db.bind_param(prep_stmt, 4,phno)
        ibm_db.bind_param(prep_stmt, 5,user)
        ibm_db.execute(prep_stmt)
        if user=='Sakshit':
            flash("Profile Updated Successfully",category="success")
            return redirect(url_for('profile'))
        else:
            flash("Profile Updated Successfully",category="success")
            return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))

@app.route('/deleteuser/<usr>')
def deleteuser(usr):
    if "user" in session and session["user"]=='Sakshit':
        try:
            delete_sql="DELETE FROM TRS01834.USER WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, delete_sql)
            ibm_db.bind_param(prep_stmt, 1,usr)
            ibm_db.execute(prep_stmt)
            flash("User deleted successfully")
            return redirect(url_for('users'))
        except:
            flash("User cannot be deleted as he/she is included in the purchases",category="error")
            return redirect(url_for('product'))
    else:
        return(redirect(url_for('login')))
    

@app.route('/updatepro/<pname>')
def updatepro(pname):
    if "user" in session and session["user"]=='Sakshit':
        usern=session["user"]
        select_sq="SELECT * FROM TRS01834.PRODUCTS where PNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,pname)
        ibm_db.execute(prep_stmt)
        mail = ibm_db.fetch_assoc(prep_stmt)
        pname=mail["PNAME"]
        price=mail["AMOUNT"]
        category=mail["CATEGORY"]
        return render_template("updatepro.html",user=session["fname"]+" "+session["lname"],pname=pname,price=price,category=category,login=session["user"])
    else:
        return redirect(url_for('login'))

@app.route('/editpro',methods=['GET','POST'])
def editpro():
    if "user" in session and session["user"]=='Sakshit':
        x = [x for x in request.form.values()]
        pname=x[0]
        price=x[1]
        category=x[2]
        update_sql="UPDATE TRS01834.PRODUCTS SET AMOUNT=?,CATEGORY=? WHERE PNAME=?"
        prep_stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(prep_stmt, 1,price)
        ibm_db.bind_param(prep_stmt, 2,category)
        ibm_db.bind_param(prep_stmt, 3,pname)
        ibm_db.execute(prep_stmt)
        flash("Product edit successful")
        return redirect(url_for('product'))
    else:
        return redirect(url_for('login'))


@app.route('/deletepro/<pro>')
def deletepro(pro):
    if "user" in session and session["user"]=='Sakshit':
        try:
            delete_sql="DELETE FROM TRS01834.PRODUCTS WHERE PNAME=?"
            prep_stmt = ibm_db.prepare(conn, delete_sql)
            ibm_db.bind_param(prep_stmt, 1,pro)
            ibm_db.execute(prep_stmt)
            flash("Product deleted successfully")
            return redirect(url_for('product'))
        except:
            flash("Product cannot be deleted as it is included in the purchases",category="error")
            return redirect(url_for('product'))
    else:
        return redirect(url_for('login'))

@app.route('/change')
def change():
    if "user" in session:
        return render_template("change.html",login=session["user"],user=session["fname"]+" "+session["lname"])
    else:
        return redirect(url_for(login))

@app.route('/changePassword',methods=['GET','POST'])
def changePassword():
    if "user" in session:
        x = [x for x in request.form.values()]
        password=x[0]
        npassword=x[1]
        cpassword=x[2]
        select_sq="SELECT * FROM TRS01834.USER where USERNAME=?"
        prep_stmt = ibm_db.prepare(conn, select_sq)
        ibm_db.bind_param(prep_stmt, 1,session["user"])
        ibm_db.execute(prep_stmt)
        mail = ibm_db.fetch_assoc(prep_stmt)
        passw=mail["PASSWORD"]
        if password==passw:
            if npassword==cpassword:
                update_sql="UPDATE TRS01834.USER SET PASSWORD=? WHERE USERNAME=?"
                prep_stmt = ibm_db.prepare(conn, update_sql)
                ibm_db.bind_param(prep_stmt, 1,npassword)
                ibm_db.bind_param(prep_stmt, 2,session["user"])
                ibm_db.execute(prep_stmt)
                flash("Password reset successful")
                return redirect(url_for('change'))
            else:
                flash("Incorrect password confirmation",category="error")
                return redirect(url_for('change'))

        else:
            flash("Wrong current password",category="error")
            return redirect(url_for('change'))
    else:
        return redirect(url_for('login'))

@app.route('/feedback',methods=['GET','POST'])
def feedback():
    if "user" in session:
        x=[x for x in request.form.values()]
        email=x[0]
        uname=x[1]
        fname=x[2]
        lname=x[3]
        subject=x[4]
        message=x[5]
        email_sender='allumolu13@gmail.com'
        email_password='zctjoyjhyviwmqid'
        email_receiver = "paymentsbook.digital@gmail.com"
        subject=f"Request from user {fname+' '+lname}:{subject}"
        body=f"{message}\n\nFrom\n{fname+' '+lname}\n{email}"
        em=EmailMessage()
        em['From']=email_sender
        em['To']=email_receiver
        em['subject']=subject
        em.set_content(body)
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        email_sender='paymentsbook.digital@gmail.com'
        email_password='dvwbxivfnbyvrubz'
        receiver=email
        email_receiver=receiver
        subject="Query received!!!"
        body=f"""Thank you for reaching our contact us service.We go through the issue asap and answer your queries and we try to resolve if any problems exist\n\nThank you\nTeam Digital Payments Book"""
        em=EmailMessage()
        em['From']=email_sender
        em['To']=email_receiver
        em['subject']=subject
        em.set_content(body)
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        flash('Query submitted succcessfully,we reach you soon')
        return redirect(url_for('contactus'))
    else:
        return redirect(url_for('login'))

@app.route('/mhistory/<month>')
def mhistory(month):
    if "user" in session:
        par=month.split('+')
        month1=par[0]
        year=par[1]
        month1=months.index(month1)
        select_sql="SELECT TRS01834.PURCHASES.PID,TRS01834.PURCHASES.DATE,TRS01834.PURCHASES.QUANTITY,TRS01834.PURCHASES.PRICE,PAID FROM TRS01834.USER u,TRS01834.PURCHASES WHERE u.USERNAME=? and TRS01834.PURCHASES.USERNAME=u.USERNAME and MONTH(DATE)=? and YEAR(DATE)=?"
        prep1_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep1_stmt, 1,session["user"])
        ibm_db.bind_param(prep1_stmt, 2,month1+1)
        ibm_db.bind_param(prep1_stmt, 3,year)
        ibm_db.execute(prep1_stmt)
        count = ibm_db.fetch_assoc(prep1_stmt)
        hist=[]
        pids=[]
        while count!=False:
            hist.append(count)
            pids.append(count["PID"])
            count = ibm_db.fetch_assoc(prep1_stmt)
        print(hist)
        product=[]
        for i in pids:
            sel_sql="SELECT PNAME,COUNT FROM TRS01834.PAYMENT WHERE PID=?"
            pre_stmt=ibm_db.prepare(conn,sel_sql)
            ibm_db.bind_param(pre_stmt,1,i)
            ibm_db.execute(pre_stmt)
            count=ibm_db.fetch_assoc(pre_stmt)
            var=""
            j=0
            while count!=False:
                if j==0:
                    var+=(count["PNAME"]+"*"+str(count["COUNT"]))
                else:
                    var+=(', '+count["PNAME"]+"*"+str(count["COUNT"]))
                j+=1
                count=ibm_db.fetch_assoc(pre_stmt)
            product.append(var)
        selected_sql="SELECT PNAME FROM TRS01834.PRODUCTS"
        prep_stmt1=ibm_db.prepare(conn,selected_sql)
        ibm_db.execute(prep_stmt1)
        products = ibm_db.fetch_assoc(prep_stmt1)
        prod=[]
        while products!=False:
            prod.append(products)
            products = ibm_db.fetch_assoc(prep_stmt1)
        print(prod)
        df1=pd.json_normalize(prod)
        df1.index = df1.index + 1
        records1 = df1.to_records(index=False)
        print(records1)
        prods=list(records1)
        df=pd.json_normalize(hist)
        if len(df)==0:
            return render_template('history.html',  tables=[df.to_html()], titles=['DATE','PRODUCT','QUANTITY','PRICE','PAYMENT STATUS'],user=session["fname"]+" "+session["lname"],data=" ",prod=prods,login=session["user"],month=months[month1],year=year)
        
        df.insert(loc=2,column='product',value=product)
        print(df)
        df.index = df.index + 1
        
        records = df.to_records(index=False)
        data=list(records)

        print(count)
        return render_template('history.html',  tables=[df.to_html()], titles=[''],user=session["fname"]+" "+session["lname"],data=data,login=session["user"],month=months[month1],year=year)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if "user" in session:
        session.clear()
        flash("Logged out Successfully",category="success")
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)



