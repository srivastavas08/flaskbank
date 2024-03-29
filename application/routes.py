from application import app, db
from flask import render_template, request, json, Response, redirect, flash, url_for, session
from application.forms import LoginForm, RegisterForm, Newcustomer
from application.models import User, newcustomer, HelperCustomer, BankTransfers
import random
from random import randint
from datetime import datetime, timezone 
import time

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
        cashier_flag = check_if_cashier(email)

        if user and user.get_password(password):
            flash(f"{user.first_name}, You are successfully logged in", "success")
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            session['email'] = user.email
            session['cashier_flag'] = cashier_flag
            return redirect('/index')
        else:
            flash("Sorry! something went wrong", "danger")
    return render_template("login.html", title="Login", form=form, login=True)


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


@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route("/api/")
@app.route("/api/<ssnid>")
def api(ssnid): #if no data is passed to idx it will take none
    if not session.get('username'):
        return redirect(url_for('index'))
    helper_class = HelperCustomer()
    target_customer_object = helper_class.get_customer_for_update(ssnid)

    if ssnid==None :
        jdata=target_customer_object
    else:
        jdata=target_customer_object
        jdata = create_customer_account_dict(jdata)
    return render_template('view.html', data=jdata, api=True)


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

        now_date = datetime.now(timezone.utc)
        accounttype = 'NaN'
        status      = 'Active'
        accbalance = float(0)
        msg = 'Account created successfully'

        customer = newcustomer(ssn_id=ssn_id,cust_id=cust_id, name=name, age=age, address= address1 + address2, state=state, city=city, accounttype = accounttype, accbalance = accbalance, msg = msg, last_action = now_date, status=status)
        customer.save()

        flash("Customer creation initiated successfully","success")
        return redirect(url_for('index'))
    return render_template('create_customer.html', title="New Customer", form=form, createCust=True)

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
            # print(custName, custAge, custAddress)
            try:
                now_date = datetime.now(timezone.utc)
                target_customer_object.update(
                    age = custAge,
                    name = custName,
                    address = custAddress,
                    msg = "successfully updated",
                    last_action = now_date
                )
                target_customer_object.save()
                # msg = 'success'
            except:
                flash("Sorry! something went wrong", "danger")
                # msg = 'Sorry! something went wrong'
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
        trans_id = random.randint(10**1, 10**12-1)

        helper_class = HelperCustomer()
        target_customer_object = helper_class.get_customer_using_custid(custid)
        if(len(target_customer_object) > 0 and not None):
            current_balance = target_customer_object.accbalance
            new_balance = current_balance + depAmt
            msg = f'account created with balance{new_balance}'
            try:
                now_date = datetime.now(timezone.utc)
                target_customer_object.update(
                    accounttype = acctype,
                    accbalance = new_balance,
                    msg = msg,
                    last_action = now_date,
                    transaction_id = trans_id
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
                now_date = datetime.now(timezone.utc)
                target_customer_object.update(accounttype = "NaN",accbalance = float(0),msg = "account deleted",last_action = now_date)
                target_customer_object.save()
                flash("delete successful", "success")
            except:
                flash("delete unsuccessful", "danger")
                return render_template('delete_account.html') 
    return render_template('delete_account.html')

# customer search
@app.route('/customer_search', methods=['GET', 'POST'])
@app.route('/customer_search/', methods=['GET', 'POST'])

def custSearch(custid=None, ssnid=None):
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
            # print(f'current: {current_ssnid}, form_ssnid:{ssnid}')
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
            data_dict = create_account_dict_display(target_customer_object)
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

        transfer_object = BankTransfers()
        now_date = datetime.now(timezone.utc)

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
                trans_id = random.randint(10**1, 10**12-1)
                now_date = datetime.now(timezone.utc)
                msg = f'successfully deposited {depAmt}'
                target_customer_object.update(accbalance = new_balance, msg = msg,last_action = now_date)
                target_customer_object.save()
                flash(f"deposit successful, balance is {new_balance}", "success")
                transfer_object.from_cust_id = custid
                transfer_object.to_cust_id = custid
                transfer_object.transaction_amt = depAmt
                transfer_object.transaction_date = now_date
                transfer_object.transaction_type = 'deposit'
                transfer_object.transaction_id = trans_id
                transfer_object.save()
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

        transfer_object = BankTransfers()
        now_date = datetime.now(timezone.utc)

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
                trans_id = random.randint(10**1, 10**12-1)
                now_date = datetime.now(timezone.utc)
                msg = f"successfully withdrawed {depAmt}"
                target_customer_object.update(accbalance = new_balance, msg = msg, last_action = now_date)
                target_customer_object.save()
                transfer_object.from_cust_id = custid
                transfer_object.to_cust_id = custid
                transfer_object.transaction_amt = depAmt
                transfer_object.transaction_date = now_date
                transfer_object.transaction_type = 'withdraw'
                transfer_object.transaction_id = trans_id
                transfer_object.save()
                flash(f"withdraw successful, balance is {new_balance}", "success")
            except:
                flash(f"withdraw unsuccessful, balance is {target_customer_object.accbalance}", "danger")
                return render_template('withdraw_money.html')
            
        
            return render_template('withdraw_money.html')
        return render_template('withdraw_money.html')

# Transfer money
@app.route('/transfer_money', methods=['GET', 'POST'])
def transferMoney():

    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('transfer_money.html')
    if request.method == "POST":
        # ssnid = request.form.get('accid', type = int)

        source_custid = request.form.get('source_custid', type = int)
        source_accounttype = request.form.get('source_accounttype')

        # ssnid = request.form.get('accid', type = int)
        target_custid = request.form.get('target_custid', type = int)
        target_accounttype = request.form.get('target_accounttype')

        depAmt = request.form.get('depAmt', type = float)

        transfer_object = BankTransfers()
        now_date = datetime.now(timezone.utc)

        helper_class = HelperCustomer()

        source_customer_object = helper_class.get_customer_using_custid(source_custid)
        target_customer_object = helper_class.get_customer_using_custid(target_custid)
        
        target_current_acctype = target_customer_object.accounttype
        source_customer_acctype = source_customer_object.accounttype

        if(target_current_acctype != target_accounttype or source_customer_acctype != source_accounttype):
            flash(f"wrong account type selected, redirected", "danger")
            return render_template('transfer_money.html')

        if(len(target_customer_object)>0 and len(source_customer_object)>0 and target_customer_object is not None and source_customer_object is not None):
            target_current_balance = target_customer_object.accbalance
            source_current_balance = source_customer_object.accbalance

            target_new_balance = target_current_balance + depAmt
            source_new_balance = source_current_balance - depAmt

            if(source_new_balance <= 0):
                flash(f"transfer unsuccessful, source balance is low, reduce transfer amount", "danger")
                return render_template('transfer_money.html')

            try:
                trans_id = random.randint(10**1, 10**12-1)
                now_date = datetime.now(timezone.utc)
                target_msg = f"successfully recieved {depAmt}"
                source_msg = f"successfully transfered {depAmt}"

                target_customer_object.update(accbalance = target_new_balance, msg = target_msg, last_action = now_date)
                source_customer_object.update(accbalance = source_new_balance, msg = source_msg, last_action = now_date)

                target_customer_object.save()
                source_customer_object.save()

                transfer_object.from_cust_id = source_custid
                transfer_object.to_cust_id = target_custid
                transfer_object.transaction_amt = depAmt
                transfer_object.transaction_date = now_date
                transfer_object.transaction_type = 'transfer'
                transfer_object.transaction_id = trans_id
                transfer_object.save()
                flash(f"successfully transfered,source balance is {source_new_balance},target balance is {target_new_balance}", "success")
            except:
                flash(f"transfer unsuccessful", "danger")
                return render_template('transfer_money.html')
        return render_template('transfer_money.html')
    return render_template('transfer_money.html')

# Print/View Statements
@app.route('/print_stm', methods=['GET', 'POST'])
def printStm():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('print_stm.html')
    if request.method == "POST":
        custid = request.form.get('custid', type = int)
        deserialized_bank_transfer = []

        for x in BankTransfers.objects(to_cust_id=custid):
            tmp = create_customer_transaction_dict(x)
            deserialized_bank_transfer.append(tmp)
        return render_template('print_stm.html',data=deserialized_bank_transfer)
    return render_template('print_stm.html')

# customer status
@app.route('/customer_status', methods=['GET', 'POST'])
def custStatus():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        deserialized_bank_transfer = []
        for x in newcustomer.objects():
            tmp = create_customer_account_dict(x)
            deserialized_bank_transfer.append(tmp)
        print(deserialized_bank_transfer)
        return render_template('customer_status.html',data=deserialized_bank_transfer)

    
# Account status
@app.route('/account_status', methods=['GET', 'POST'])
def accStatus():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        deserialized_bank_transfer = []
        for x in newcustomer.objects():
            tmp = create_customer_account_dict(x)
            deserialized_bank_transfer.append(tmp)
        print(deserialized_bank_transfer)
        return render_template('account_status.html',data=deserialized_bank_transfer)

########################################################################################################
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
    # data_dict["Account Type"] = target_customer_object.accounttype
    # data_dict["Account Balance"] = target_customer_object.accbalance
    data_dict["Message"] = target_customer_object.msg 

    return data_dict

def create_account_dict_display(target_customer_object):
    data_dict = {}
    data_dict["SSN ID"] = target_customer_object.ssn_id
    data_dict["Customer ID"] = target_customer_object.cust_id
    data_dict["Name"] = target_customer_object.name
    # data_dict["Address"] = target_customer_object.address
    # data_dict["State"] = target_customer_object.state
    # data_dict["City"] = target_customer_object.city
    data_dict["Account Balance"] = target_customer_object.accbalance
    data_dict["Account Type"] = target_customer_object.accounttype
    data_dict["Account Status"] = "Active"
    data_dict["Message"] = target_customer_object.msg 

    if(target_customer_object.accounttype == "NaN" or target_customer_object.accounttype is None):
        data_dict["Account Type"] = "Not created"
        data_dict["Account Status"] = "Inactive"
        data_dict["Account Balance"] = 0    
    return data_dict

def create_customer_account_dict(target_customer_object):
    data_dict = {}
    data_dict["SSNID"] = target_customer_object.ssn_id
    data_dict["CustomerID"] = target_customer_object.cust_id
    data_dict["Name"] = target_customer_object.name
    data_dict["Address"] = target_customer_object.address
    data_dict["State"] = target_customer_object.state
    data_dict["City"] = target_customer_object.city
    data_dict["AccountBalance"] = target_customer_object.accbalance
    data_dict["AccountType"] = target_customer_object.accounttype
    data_dict["AccountStatus"] = "Active"
    data_dict["Message"] = target_customer_object.msg 
    data_dict["LastUpdated"] = target_customer_object.last_action

    if(target_customer_object.accounttype == "NaN" or target_customer_object.accounttype is None):
        data_dict["AccountType"] = "Not created"
        data_dict["AccountStatus"] = "Inactive"
        data_dict["AccountBalance"] = 0    
    return data_dict

def create_customer_transaction_dict(target_tranfer_object):
    data_dict = {}
    data_dict["from_cust_id"] = target_tranfer_object.from_cust_id
    data_dict["to_cust_id"] = target_tranfer_object.to_cust_id
    data_dict["transaction_date"] = target_tranfer_object.transaction_date
    data_dict["transaction_amt"] = target_tranfer_object.transaction_amt
    data_dict["transaction_type"] = target_tranfer_object.transaction_type
    data_dict["transaction_id"] = target_tranfer_object.transaction_id
    return data_dict


def check_if_cashier(email):
    is_cashier_flag = 0
    email = str(email).strip().lower()
    email = email.split('@')[1]
    email = email.split('.')[0]
    if (email == 'cashier' or email == 'teller'):
        # print('YES')
        is_cashier_flag = 1
    return is_cashier_flag

def format_dates(date1):
    d1 = time.strptime(date1, "%Y-%m-%d")
    return d1


###########################################################


# Statements by date
@app.route('/date_stm', methods=['GET', 'POST'])
def dateStm():
    if not session.get('username'):
        return redirect(url_for('index'))
    cashier_flag = check_if_cashier(session.get('email'))
    if(cashier_flag != 1):
        flash(f"unprivilaged access, login with cashier/teller account", "danger")
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('date_stm.html')
    if request.method == "POST":
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        custid = request.form.get('custid', type = int)
        print(from_date)
        deserialized_bank_transfer = []

        from_date = format_dates(from_date)
        to_date = format_dates(to_date)

        for x in BankTransfers.objects(to_cust_id=custid):
            tmp_date = str(x.transaction_date).split(' ')[0]
            tmp_date = format_dates(tmp_date)
            if( tmp_date > from_date and tmp_date <= to_date):
                tmp = create_customer_transaction_dict(x)
                deserialized_bank_transfer.append(tmp)
        return render_template('date_stm.html', data=deserialized_bank_transfer, datestm=True)
    return render_template('date_stm.html')

    
