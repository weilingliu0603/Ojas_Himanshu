import flask
import sqlite3
from flask import request
from datetime import datetime

app = flask.Flask(__name__)


@app.route('/')
def home():
    return flask.render_template('index.html')


@app.route('/employee')
def employee():
    return flask.render_template('employee.html')


@app.route('/customer')
def customer():
    return flask.render_template('haircut.html')


@app.route('/administrat', methods=['POST'])  # Choosing Action
def administrat():
    connection = sqlite3.connect('shop.db')
    data = request.form
    if data['choice'] == "Update member details":
        return flask.render_template('updatemember.html')
    elif data['choice'] == "View daily transactions":
        daily = {}
        data = connection.execute("SELECT `Date` FROM `Transactions`;")
        for row in data: daily[row[0]] = []
        for date in daily:
            data = connection.execute(
                "SELECT m.Name, t.`Total Amount`, t.`Invoice Number` FROM Member m, Transactions t WHERE t.Date = '{}' AND m.ID = t.MemberID;".format(
                    date))
            for row in data: daily[date].append(row)
        return flask.render_template('dailytransactions.html', daily = daily)
    elif data['choice'] == "View monthly sales revenue":
        months = {1:'Janauary',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        monthly_sales = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
        data = connection.execute("SELECT Date, `Total Amount` FROM Transactions")
        for row in data:
            month = int(row[0].split('-')[1])
            monthly_sales[month] += int(row[1])
        return flask.render_template('monthlysales.html', monthly_sales=monthly_sales, months=months)
    elif data['choice'] == "View member's transaction history":
        return flask.render_template('memberhistory.html')


@app.route('/update', methods=['POST'])
def update():
    connection = sqlite3.connect('shop.db')
    data = request.form
    ID = data['ID']
    for att in data:
        if att == "ID":
            continue
        if data[att] != "":
            newvalue = "'" + data[att] + "'"
            with connection:
                connection.execute("UPDATE Member " +
                                   "SET " + att + " = " + newvalue + " WHERE ID = " + ID)
    return flask.render_template('done.html')


@app.route('/viewhistory', methods=['POST'])
def viewhistory():
    connection = sqlite3.connect('shop.db')
    data = request.form
    memberID = int(data['ID'])
    data = connection.execute(
        'SELECT `Invoice Number`, `Total Amount` FROM Transactions WHERE MemberID = ' + str(memberID) + ";")
    return flask.render_template('memberhistorydata.html', data=data)


@app.route('/member')
def member():
    return flask.render_template('member.html')


@app.route('/booking', methods=['POST'])
def booking():
    date = datetime.today().strftime('%Y-%m-%d')
    date = "'" + date + "'"
    ID = request.form
    ID = ID['ID']
    data = request.form.getlist("servies")
    print("Data: ", data)
    connection = sqlite3.connect('shop.db')
    total = 0
    for service in data:
        value = "'" + service + "'"
        with connection:
            cursor = connection.execute("SELECT Price FROM 'Service Details' WHERE Type = " + value).fetchall()
            for row in cursor:
                total += row[0]

    with connection:
        connection.execute("INSERT INTO Transactions(Date, MemberID, 'Total Amount')" +
                           "VALUES(" +
                           date + ", " +
                           ID + ", " +
                           str(total) +
                           ")")
        cursor = connection.execute("SELECT seq FROM 'sqlite_sequence' WHERE name = 'Transactions'").fetchall()
        invoiceNum = cursor[0]
        invoiceNum = invoiceNum[0]

    for service in data:
        value = "'" + service + "'"
        print("Service:", value)
        print("invoice:", invoiceNum)
        with connection:
            connection.execute("INSERT INTO Orders VALUES(" + str(invoiceNum) + ", " + value + ")")

    # Webpage shows 'done' in done.html, same as update member details, maybe should be customised
    return flask.render_template('done.html')


@app.route('/nonmember')
def nonmember():
    return flask.render_template('nonmember.html')


@app.route('/membership', methods=['POST'])
def membership():
    connection = sqlite3.connect('shop.db')
    data = request.form
    Name = "'" + data['Name'] + "'"
    Gender = "'" + data['Gender'] + "'"
    Email = "'" + data['Email'] + "'"
    Contact = "'" + data['Contact'] + "'"
    Address = "'" + data['Address'] + "'"

    with connection:    
        connection.execute("INSERT INTO Member(Name, Gender, Email, Contact, Address) " +
                           "VALUES(" +
                           Name + ", " +
                           Gender + ", " +
                           Email + ", " +
                           Contact + ", " +
                           Address +
                           ")")

    return flask.render_template("done.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

