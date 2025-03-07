from flask import Flask, request, redirect, url_for, render_template, jsonify
import mysql.connector
import logging
from datetime import datetime

app = Flask(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'project',
    'password': 'project@123',
    'database': 'mini_project'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT branch.branch_ID, branch_name, location, employee.first_name as manager_name FROM branch JOIN employee ON branch.manager_id = employee.employee_ID')
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', branches=branches)

@app.route('/branch_bikes/<int:branch_id>')
def branch_bikes(branch_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT employee_id, first_name, last_name, email, ph_no FROM employee WHERE employee_ID = (SELECT manager_id FROM branch WHERE branch_id = %s)', (branch_id,))
    manager = cursor.fetchone()
    cursor.execute('SELECT bike_ID, name, colour, CC, MRP, image FROM bike WHERE branch_id = %s', (branch_id,))
    bikes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('branch_bikes.html', manager=manager, bikes=bikes, branch_id=branch_id)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    bike_id = request.args.get('bike_id')
    branch_id = request.args.get('branch_id')

    if request.method == 'POST':
        first_name = request.form['first_name']
        phone_number = request.form['phone_number']
        payment_method = request.form['payment_method']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT customer_ID FROM customer WHERE first_name = %s AND ph_no = %s', (first_name, phone_number))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customer_ID']
        else:
            last_name = request.form['last_name']
            email = request.form['email']
            address = request.form['address']
            dob = request.form['DOB']

            cursor.execute('INSERT INTO customer (first_name, last_name, email, address, D_O_B, ph_no) VALUES (%s, %s, %s, %s, %s, %s)',
                           (first_name, last_name, email, address, dob, phone_number))
            customer_id = cursor.lastrowid

        purchase_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO purchase (bike_id, payment, customer_id, purchase_date, quantity) VALUES (%s, %s, %s, %s, 1)', 
                       (bike_id, payment_method, customer_id, purchase_date))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        return render_template('customer.html', bike_id=bike_id, branch_id=branch_id)

@app.route('/emp', methods=['GET', 'POST'])
def emp():
    if request.method == 'POST':
        first_name = request.form['first_name']
        phone_number = request.form['phone_number']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT employee_ID, first_name, last_name, email FROM employee WHERE first_name = %s AND ph_no = %s', (first_name, phone_number))
        employee = cursor.fetchone()

        if employee:
            employee_details = {
                'employee_id': employee['employee_ID'],
                'first_name': employee['first_name'],
                'last_name': employee['last_name'],
                'email': employee['email']
            }
            return render_template('employee_details.html', employee=employee_details)
        else:
            return "Not a valid employee"
    else:
        return render_template('emp_id.html')

@app.route('/add_bike', methods=['GET'])
def add_bike_form():
    return render_template('add_bike.html')

@app.route('/add_bike', methods=['POST'])
def add_bike():
    cc = request.form['cc']
    colour = request.form['colour']
    branch_id = request.form['branch_id']
    mrp = request.form['mrp']
    name = request.form['name']
    year = request.form['year']

    # Generate the image attribute
    image = f'images/{name.replace(" ", "_")}.jpg'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'INSERT INTO bike (CC, colour, branch_id, MRP, name, year, image) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (cc, colour, branch_id, mrp, name, year, image)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))


@app.route('/add_employee')
def add_employee_form():
    return render_template('add_employee.html')

@app.route('/add_employee', methods=['POST'])
def add_employee():
    fname = request.form['first_name']
    lname = request.form['last_name']
    branch_id = request.form['branch_id']
    DOB = request.form['dob']
    ph_no = request.form['ph_no']
    salary = request.form['salary']
    mail = request.form['email']
    address = request.form['add']
    start_date = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT branch_name FROM branch WHERE branch_ID = %s',
        (branch_id,)
    )
    branch = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if branch:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'INSERT INTO employee (first_name, last_name, email, address, D_O_B, ph_no, salary, branch_ID, start_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (fname, lname, mail, address, DOB, ph_no, salary, branch_id, start_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        return "Branch ID is not valid"



@app.route('/add_branch')
def add_branch_form():
    return render_template('add_branch.html')

@app.route('/add_branch', methods=['POST'])
def add_branch():
    Bname = request.form['name']
    Badd = request.form['add']
    mgrID = request.form['ID']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT first_name FROM employee WHERE employee_ID = %s',
        (mgrID,)
    )
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if employee:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'INSERT INTO branch (branch_name, location, manager_id) VALUES (%s, %s, %s)',
            (Bname, Badd, mgrID)
        )
        cursor.execute(
            'SELECT branch_ID FROM branch WHERE branch_name = %s AND manager_id = %s',
            (Bname, mgrID)
        )
        branch = cursor.fetchone()

        cursor.execute(
            'UPDATE employee SET branch_ID = %s WHERE employee_ID = %s',
            (branch['branch_ID'], mgrID)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))  # Redirect to a suitable page after success
    else:
        return "Employee ID is not valid"




if __name__ == '__main__':
    app.run(debug=True)
