from application import app, db
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.forms import LoginForm, RegisterForm, Newcustomer
from application.models import User, Course, Enrollment, newcustomer, HelperCustomer
from random import randint

@app.route("/")
@app.route("/index") #all these will redirect to a single function index
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/login", methods=['GET','POST'])
def login():

    if session.get('username'):
            return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.objects(email=email).first()

        if user and user.get_password(password):
            flash(f"{user.first_name}, You are successfully logged in", "success")
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            session['email'] = user.email
            return redirect('/index')
        else:
            flash("Sorry! something went wrong", "danger")
    return render_template("login.html", title="Login", form=form, login=True)

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term = None):
    if term is None:
        term = "Spring 2019"
    classes = Course.objects.order_by("-courseID")
    return render_template("courses.html", courseData=classes, courses = True, term=term )

@app.route("/register", methods=['POST','GET'])
def register():

    if session.get('username'):
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user_id     = User.objects.count()
        user_id    += 1
        

        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data

        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form, register=True)

@app.route("/enrollment", methods=["GET","POST"])
def enrollment():

    if not session.get('username'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')
    
    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id,courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")

    classes = list( User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))
    
    
    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)



@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route("/api/")
@app.route("/api/<idx>")
def api(idx=None): #if no data is passed to idx it will take none
    if idx==None :
        jdata=courseData
    else:
        jdata=courseData[int(idx)]
    return Response(json.dumps(jdata), mimetype="application/json")
   
@app.route('/user')
def user():
    #User( user_id= 1, first_name="Jacques", last_name="Blazewicz", email="jblazewicz0@posterous.com", password="k9doaly").save()
    #User( user_id= 2, first_name="Budd", last_name="Zellick", email="bzellick1@uol.com.br", password="kik8N0cyKG" ).save()
    users = User.objects.all()
    return render_template("user.html", users=users)


# create customer
@app.route('/create_customer', methods=['GET', 'POST'])
def createCust():
    if not session.get('username'):
        return redirect(url_for('index'))

    form = Newcustomer()
    if form.validate_on_submit():
        rn = generate_unique()
        ssn_id     = newcustomer.objects.count() + 158000000 + rn
        ssn_id    += 1
        cust_id    = newcustomer.objects.count() + 100000001 + rn
        cust_id   +=1
        

        name       = form.name.data
        age        = form.age.data
        address1    = form.address1.data
        address2    = form.address2.data
        state      = form.state.data
        city       = form.city.data

        accounttype = 'NaN'
        accbalance = float(0)

        customer = newcustomer(ssn_id=ssn_id,cust_id=cust_id, name=name, age=age, address= address1 + address2, state=state, city=city, accounttype = accounttype, accbalance = accbalance)
        customer.save()

        flash("Customer creation initiated successfully","success")
        return redirect(url_for('index'))
    return render_template('create_customer.html', title="New_Customer", form=form, createCust=True)

# update customer
@app.route('/update_customer', methods=['GET', 'POST'])
def updateCust():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('update_customer.html')
    if request.method == 'POST':
        ssnid  = request.form['ssnID']
        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_for_update(ssnid)

        if(len(target_customer_object) > 0 and not None):
            custName = request.form['custName']
            custAddress = request.form['custAddress']
            custAge = request.form['custAge']
            print(custName, custAge, custAddress)
            try:
                target_customer_object.update(
                    age = custAge,
                    name = custName,
                    address = custAddress
                )
                target_customer_object.save()
                msg = 'success'
            except:
                flash("Sorry! something went wrong", "danger")
                msg = 'Sorry! something went wrong'
                return render_template('update_customer.html')
        flash("update successful", "success")
        return render_template('update_customer.html')
    return render_template('update_customer.html')
  
# delete customer
@app.route('/delete_customer', methods=['GET', 'POST'])
def deleteCust():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('delete_customer.html')
    if request.method == 'POST':
        ssnid  = request.form['ssnID']
        custid = request.form['custID']
        custname = request.form['custName']
        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_for_delete(ssnid, custid, custname)
        if(len(target_customer_object) > 0 and not None):
            try:
                target_customer_object.delete()
                flash("delete successful", "success")
            except:
                flash("delete unsuccessful", "danger")
                return render_template('delete_customer.html') 
    return render_template('delete_customer.html')

# customer status
@app.route('/customer_status', methods=['GET', 'POST'])
def custStatus():
    return render_template('customer_status.html')

# create customer account
@app.route('/create_account', methods=['GET', 'POST'])
def createAcc():
    if not session.get('username'):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('create_account.html')
    if request.method == 'POST':
        custid  = request.form['custid']
        depAmt = request.form.get('depAmt', type = float)
        acctype = request.form.get('accounttype')

        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        if(len(target_customer_object) > 0 and not None):
            current_balance = target_customer_object.accbalance
            new_balance = current_balance + depAmt
            try:
                target_customer_object.update(
                    accounttype = acctype,
                    accbalance = new_balance
                )
                target_customer_object.save()
                flash("created successful", "success")
            except:
                flash("created unsuccessful", "danger")
                return render_template('create_account.html')

        return render_template('create_account.html')

# delete customer account
@app.route('/delete_account', methods=['GET', 'POST'])
def deleteAcc():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('delete_account.html')
    if request.method == 'POST':
        accid  = request.form['accid']
        acctype = request.form.get('accounttype')
        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(accid)
        current_acctype = target_customer_object.accounttype
        if(current_acctype != acctype):
            flash(f"{acctype} does not exist, redirected", "danger")
            return render_template('delete_account.html')

        if(len(target_customer_object) > 0 and not None):
            try:
                target_customer_object.update(accounttype = "NaN",accbalance = float(0))
                target_customer_object.save()
                flash("delete successful", "success")
            except:
                flash("delete unsuccessful", "danger")
                return render_template('delete_account.html') 
    return render_template('delete_account.html')

# Account status
@app.route('/account_status', methods=['GET', 'POST'])
def accStatus():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('delete_account.html')
    if request.method == 'POST':
        pass
    return render_template('account_status.html')

# customer search
@app.route('/customer_search', methods=['GET', 'POST'])
def custSearch():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('customer_search.html')
    if request.method == 'POST':
        custid = request.form.get('custid', type=int)
        ssnid = request.form.get('ssnid',type = int)
        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        if(len(target_customer_object)>0 and target_customer_object is not None):
            current_ssnid = target_customer_object.ssn_id
            print(f'current: {current_ssnid}, form_ssnid:{ssnid}')
            if(current_ssnid != ssnid):
                flash(f"{ssnid} is wrong, redirected", "danger")
                return render_template('customer_search.html')
            data_dict = create_customer_dict_display(target_customer_object)
            return render_template('customer_search.html', data=data_dict)
    return render_template('customer_search.html')

# Account search
@app.route('/account_search', methods=['GET', 'POST'])
def accSearch():
    if not session.get('username'):
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('account_search.html')
    if request.method == 'POST':
        custid = request.form.get('custid', type=int)
        ssnid = request.form.get('ssnid',type = int)
        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        if(len(target_customer_object)>0 and target_customer_object is not None):
            current_ssnid = target_customer_object.ssn_id
            if(current_ssnid != ssnid):
                flash(f"{ssnid} is wrong, redirected", "danger")
                return render_template('account_search.html')
            if(target_customer_object.accounttype == 'NaN' or target_customer_object.accounttype == None):
                flash(f"account doesnt exist for Account ID: {custid}", "danger")
                return render_template('account_search.html')
            data_dict = create_customer_dict_display(target_customer_object)
            return render_template('account_search.html', data=data_dict)
    return render_template('account_search.html')

# Deposit money
@app.route('/deposit_money', methods=['GET', 'POST'])
def depositMoney():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('deposit_money.html')
    if request.method == "POST":
        ssnid = request.form.get('accid', type = int)
        custid = request.form.get('custid', type = int)
        acctype = request.form.get('accounttype')
        depAmt = request.form.get('depAmt', type = float)

        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        current_acctype = target_customer_object.accounttype
        if(current_acctype != acctype):
            flash(f"{acctype} does not exist, redirected", "danger")
            return render_template('deposit_money.html')
        if(len(target_customer_object)>0 and target_customer_object is not None):
            current_ssnid = target_customer_object.ssn_id
            if(current_ssnid != ssnid):
                flash(f"{ssnid} is wrong, redirected", "danger")
                return render_template('deposit_money.html')
            current_balance = target_customer_object.accbalance
            new_balance = current_balance + depAmt
            try:
                target_customer_object.update(accbalance = new_balance)
                target_customer_object.save()
                flash(f"deposit successful, Updated balance is {new_balance}", "success")
            except:
                flash(f"deposit unsuccessful, balance is {target_customer_object.accbalance}", "danger")
                return render_template('deposit_money.html')
        
            return render_template('deposit_money.html')
        return render_template('deposit_money.html')

# withdraw money
@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdrawMoney():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('withdraw_money.html')
    if request.method == "POST":
        ssnid = request.form.get('accid', type = int)
        custid = request.form.get('custid', type = int)
        acctype = request.form.get('accounttype')
        depAmt = request.form.get('depAmt', type = float)

        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        current_acctype = target_customer_object.accounttype
        if(current_acctype != acctype):
            flash(f"{acctype} does not exist, redirected", "danger")
            return render_template('withdraw_money.html')
        if(len(target_customer_object)>0 and target_customer_object is not None):
            current_ssnid = target_customer_object.ssn_id
            if(current_ssnid != ssnid):
                flash(f"{ssnid} is wrong, redirected", "danger")
                return render_template('withdraw_money.html')
            current_balance = target_customer_object.accbalance
            new_balance = current_balance - depAmt
            if(new_balance <= 0):
                flash(f"withdrawal unsuccessful, balance is low, reduce withdrawal amount", "danger")
                return render_template('withdraw_money.html')

            try:
                target_customer_object.update(accbalance = new_balance)
                target_customer_object.save()
                flash(f"withdraw successful, updated balance is {new_balance}", "success")
            except:
                flash(f"deposit unsuccessful, balance is {target_customer_object.accbalance}", "danger")
                return render_template('withdraw_money.html')
        
            return render_template('withdraw_money.html')
        return render_template('withdraw_money.html')

# Transfer money
@app.route('/transfer_money', methods=['GET', 'POST'])
def transferMoney():
    return render_template('transfer_money.html')

# Print/View Statements
@app.route('/print_stm', methods=['GET', 'POST'])
def printStm():
    return render_template('print_stm.html')

# Statements by date
@app.route('/date_stm', methods=['GET', 'POST'])
def dateStm():
    return render_template('date_stm.html')


# helper functions
def generate_unique():
    rn = randint(10, 99)
    return rn

def create_customer_dict_display(target_customer_object):
    data_dict = {}
    data_dict["SSN ID"] = target_customer_object.ssn_id
    data_dict["Customer ID"] = target_customer_object.cust_id
    data_dict["Name"] = target_customer_object.name
    data_dict["Address"] = target_customer_object.address
    data_dict["State"] = target_customer_object.state
    data_dict["City"] = target_customer_object.city
    data_dict["Account Type"] = target_customer_object.accounttype
    data_dict["Account Balance"] = target_customer_object.accbalance

    return data_dict

def check_if_cashier(email):
    is_cashier_flag = 0
    email = str(email).strip().lower()
    email = email.split('@')[1]
    email = email.split('.')[0]
    if (email == 'cashier' or email == 'teller'):
        print('YES')
        is_cashier_flag = 1
    return is_cashier_flag


