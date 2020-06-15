from application import app, db
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.forms import LoginForm, RegisterForm, Newcustomer
from application.models import User, Course, Enrollment, newcustomer

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
        ssn_id     = newcustomer.objects.count() + 158000000
        ssn_id    += 1
        cust_id    = newcustomer.objects.count() + 100000001
        cust_id   +=1
        

        name       = form.name.data
        age        = form.age.data
        address1    = form.address1.data
        address2    = form.address2.data
        state      = form.state.data
        city       = form.city.data

        customer = newcustomer(ssn_id=ssn_id,cust_id=cust_id, name=name, age=age, address= address1 + address2, state=state, city=city)
        customer.save()

        flash("Customer creation initiated successfully","success")
        return redirect(url_for('index'))
    return render_template('create_customer.html', title="New_Customer", form=form, createCust=True)

# update customer
@app.route('/update_customer', methods=['GET', 'POST'])
def updateCust():
    if not session.get('username'):
        return redirect(url_for('index'))
    
    update_handle = UpdateCustomer()
    db_table = update_handle.get_db()

    form = Newcustomer()
    if form.validate_on_submit():

        ssn_id     = form.ssn_id.data
        name       = form.name.data


        user_details = db_table.find ({"ssn_id": ssn_id})

        # myquery = { "ssn_id": ssn_id }
        if(name is not None):
            newvalues = { "$set": { "name": name } }
            db_table.update_one(user_details,newvalues )

    return render_template('update')
    
    

# delete customer
@app.route('/delete_customer', methods=['GET', 'POST'])
def deleteCust():
    return render_template('delete_customer.html')

# customer status
@app.route('/customer_status', methods=['GET', 'POST'])
def custStatus():
    return render_template('customer_status.html')

# create customer
@app.route('/create_account', methods=['GET', 'POST'])
def createAcc():
    return render_template('create_account.html')

# create customer
@app.route('/delete_account', methods=['GET', 'POST'])
def deleteAcc():
    return render_template('delete_account.html')

# Account status
@app.route('/account_status', methods=['GET', 'POST'])
def accStatus():
    return render_template('account_status.html')

# customer search
@app.route('/customer_search', methods=['GET', 'POST'])
def custSearch():
    return render_template('customer_search.html')

# Account search
@app.route('/account_search', methods=['GET', 'POST'])
def accSearch():
    return render_template('account_search.html')

# Deposit money
@app.route('/deposit_money', methods=['GET', 'POST'])
def depositMoney():
    return render_template('deposit_money.html')

# withdraw money
@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdrawMoney():
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