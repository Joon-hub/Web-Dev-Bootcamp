from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.description}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        
        new_expense = Expense(description=description, amount=amount, category=category)
        db.session.add(new_expense)
        db.session.commit()
        
        return redirect(url_for('view_expenses'))
    return render_template('add_expense.html')

@app.route('/view-expenses')
def view_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('view_expenses.html', expenses=expenses)

@app.route('/summary')
def summary():
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar()
    category_totals = db.session.query(Expense.category, db.func.sum(Expense.amount)).\
        group_by(Expense.category).all()
    return render_template('summary.html', total_expenses=total_expenses, category_totals=category_totals)

@app.route('/api/expenses')
def api_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([
        {
            'id': expense.id,
            'description': expense.description,
            'amount': expense.amount,
            'category': expense.category,
            'date': expense.date.isoformat()
        } for expense in expenses
    ])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)