import csv
import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Use absolute path based on script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app with correct template folder
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.json.sort_keys = False  # Disable JSON key sorting to avoid None comparison issues

# Data file location (stored in user's current working directory for portability)
DATA_DIR = os.getcwd()
CSV_FILE = os.path.join(DATA_DIR, 'finance_data.csv')

# --- Configuration ---
DAILY_EXPENSE_CATEGORIES = [
    'Tax', 'Hotel/Vacation/Travel', 'Withdraw', 'Regalo', 
    'Money Transfer', 'Refund', 'Benefit', 'Expense/Investment', 'Baby Sitter', 'Grocery', 'Membership', 'General', 'Restaurant', 'Petrol', 'Sport/Leisure'
]
INVESTMENT_INCOME_CATEGORIES = [
    'Interest/Investment'
]
ALL_CATEGORIES = DAILY_EXPENSE_CATEGORIES + INVESTMENT_INCOME_CATEGORIES + ['Monthly Salary/General']

# Ensure the CSV file exists with headers
def initialize_csv():
    """Checks if the CSV exists and creates it with headers if not."""
    if not os.path.exists(CSV_FILE):
        print(f"Creating new CSV file: {CSV_FILE}")
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'date', 'type', 'amount', 'category'])
        print("CSV file initialized with headers.")
    else:
        print(f"Using existing CSV file: {CSV_FILE}")


def load_data():
    """Loads all records from the CSV file."""
    data = []
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert amounts to float for calculation
                try:
                    row['amount'] = float(row['amount'])
                    data.append(row)
                except ValueError:
                    print(f"Skipping row due to invalid amount: {row}")
                    continue
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return []
    return data


def get_available_years(transactions):
    """Get list of years that have transaction data, sorted descending."""
    years = set()
    for t in transactions:
        try:
            date_obj = datetime.strptime(t['date'], '%Y-%m-%d')
            years.add(date_obj.year)
        except ValueError:
            continue
    # Always include current year
    years.add(datetime.now().year)
    return sorted(list(years), reverse=True)

def save_new_transaction(new_record):
    """Appends a new transaction record to the CSV file."""
    try:
        # Check if the file is empty (only headers exist)
        file_is_empty = os.path.getsize(CSV_FILE) == 0 or len(load_data()) == 0
        
        # Ensure file ends with newline before appending
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            with open(CSV_FILE, 'rb') as f:
                f.seek(-1, 2)  # Go to last byte
                if f.read(1) != b'\n':
                    # File doesn't end with newline, add one
                    with open(CSV_FILE, 'a', encoding='utf-8') as fa:
                        fa.write('\n')
        
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'date', 'type', 'amount', 'category'])
            
            # Write header only if file was just created/empty
            if file_is_empty:
                writer.writeheader()
            
            writer.writerow(new_record)
        return True
    except Exception as e:
        print(f"Error saving transaction: {e}")
        return False

def get_monthly_data(transactions, selected_year=None):
    """Aggregates transactions into monthly totals for the chart and history."""
    now = datetime.now()
    target_year = selected_year if selected_year else now.year
    monthly_aggregation = {}
    expense_categories_set = set()
    
    # Initialize all months of the target year for a complete chart
    for month in range(1, 13):
        month_key = f"{target_year}-{str(month).zfill(2)}"
        monthly_aggregation[month_key] = {
            'month': month_key, 
            'expenses': 0.0, 
            'income': 0.0, 
            'investmentIncome': 0.0,
            'netFlow': 0.0,
            'expensesByCategory': {},  # Category breakdown
        }

    for t in transactions:
        try:
            date_obj = datetime.strptime(t['date'], '%Y-%m-%d')
            amount = t['amount']
            
            if date_obj.year != target_year:
                continue
                
            month_key = f"{date_obj.year}-{str(date_obj.month).zfill(2)}"
            
            if month_key in monthly_aggregation:
                category = t.get('category') or 'Uncategorized'
                
                # Categorize based on category field and amount sign
                if category == 'Monthly Salary/General':
                    monthly_aggregation[month_key]['income'] += amount
                elif category == 'Interest/Investment':
                    monthly_aggregation[month_key]['investmentIncome'] += amount
                elif amount < 0:
                    # Negative amounts are expenses (store as positive for display)
                    expense_amount = abs(amount)
                    monthly_aggregation[month_key]['expenses'] += expense_amount
                    
                    # Track by category
                    if category not in monthly_aggregation[month_key]['expensesByCategory']:
                        monthly_aggregation[month_key]['expensesByCategory'][category] = 0.0
                    monthly_aggregation[month_key]['expensesByCategory'][category] += expense_amount
                    expense_categories_set.add(category)
                else:
                    # Other positive amounts (refunds, benefits, etc.) count as income
                    monthly_aggregation[month_key]['income'] += amount
        except ValueError:
            continue
            
    # Calculate Net Flow and filter out future months (only for current year)
    chart_data = []
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for month_key in sorted(monthly_aggregation.keys()):
        month_data = monthly_aggregation[month_key]
        month_num = int(month_key.split('-')[1])
        
        # For past years, include all months; for current year, only include up to current month
        if target_year < now.year or month_num <= now.month:
            total_income = month_data['income'] + month_data['investmentIncome']
            month_data['netFlow'] = total_income - month_data['expenses']
            month_data['name'] = month_names[month_num - 1] # Short month name for chart
            
            chart_data.append({
                'month': month_key,
                'name': month_data['name'],
                'expenses': round(month_data['expenses'], 2),
                'income': round(month_data['income'], 2),
                'investmentIncome': round(month_data['investmentIncome'], 2),
                'netFlow': round(month_data['netFlow'], 2),
                'expensesByCategory': {k: round(v, 2) for k, v in month_data['expensesByCategory'].items()},
            })

    return chart_data, sorted(list(expense_categories_set))


def calculate_metrics(transactions, selected_year=None):
    """Calculates dashboard metrics based on monthly aggregation."""
    now = datetime.now()
    target_year = selected_year if selected_year else now.year
    
    # For past years, use December as the "current" month context
    if target_year < now.year:
        reference_month = 12
    else:
        reference_month = now.month
    
    monthly_data, expense_categories = get_monthly_data(transactions, target_year)
    
    # Get the latest month with data for the selected year
    latest_month_key = f"{target_year}-{str(reference_month).zfill(2)}"
    latest_month_stats = next((m for m in monthly_data if m['month'] == latest_month_key), None)
    
    # Defaults if no month data is found
    monthly_expense_actual = latest_month_stats['expenses'] if latest_month_stats else 0.0
    monthly_income_actual = latest_month_stats['income'] if latest_month_stats else 0.0
    monthly_investment_income_actual = latest_month_stats['investmentIncome'] if latest_month_stats else 0.0

    # Calculate Annual Totals/Averages
    annual_expense_total = sum(m['expenses'] for m in monthly_data)
    annual_salary_total = sum(m['income'] for m in monthly_data)
    annual_investment_income_total = sum(m['investmentIncome'] for m in monthly_data)
    # Total Income = Salary + Investment Income
    annual_income_total = annual_salary_total + annual_investment_income_total
    months_with_data = len(monthly_data)
    
    avg_monthly_expense = annual_expense_total / months_with_data if months_with_data > 0 else 0.0
    avg_monthly_income = annual_income_total / months_with_data if months_with_data > 0 else 0.0
    
    # Days calculation - for past years use full year, for current year use days passed
    if target_year < now.year:
        days_in_period = 365
    else:
        days_in_period = (now - datetime(target_year, 1, 1)).days + 1
    
    avg_daily_expense = annual_expense_total / days_in_period if days_in_period > 0 else 0.0
    avg_weekly_expense = avg_daily_expense * 7
    
    # Projections based on averages
    total_annual_expenses_est = avg_monthly_expense * 12
    total_annual_income_est = avg_monthly_income * 12
    
    # Current/Latest month totals (combined salary + investment)
    total_monthly_income = monthly_income_actual + monthly_investment_income_actual

    
    return {
        # Annual Totals (actual sums, not projections)
        'Total Annual Expenses': annual_expense_total,
        'Total Week Expenses': avg_weekly_expense,
        'Total Day Expenses': avg_daily_expense,
        
        # Annual Actuals (Total Income = Salary + Investment)
        'Annual Income YTD': annual_income_total,
        'Annual Income Projection': total_annual_income_est,
        'Net Annual Flow': annual_income_total - annual_expense_total,
        
        # Latest Month (Total Income = Salary + Investment)
        'Total Monthly Expenses': monthly_expense_actual,
        'Monthly Income Actual': total_monthly_income,
        'Net Monthly Flow': total_monthly_income - monthly_expense_actual,
        
        'transactions': transactions,
        'monthly_data': monthly_data,
        'expense_categories': expense_categories
    }


# --- Flask Routes ---

@app.before_request
def setup_data():
    # Ensure the CSV is ready before any request
    initialize_csv()

@app.route('/')
def index():
    """Renders the main HTML application page."""
    now = datetime.now()
    transactions = load_data()
    available_years = get_available_years(transactions)
    month_names = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    return render_template('index.html', 
        expense_categories=DAILY_EXPENSE_CATEGORIES,
        investment_categories=INVESTMENT_INCOME_CATEGORIES,
        current_year=now.year,
        current_month=month_names[now.month - 1],
        available_years=available_years
    )

@app.route('/api/data', methods=['GET'])
def get_data():
    """API endpoint to fetch metrics and transaction list."""
    transactions = load_data()
    
    # Get year from query parameter, default to current year
    selected_year = request.args.get('year', type=int)
    if selected_year is None:
        selected_year = datetime.now().year
    
    available_years = get_available_years(transactions)
    metrics = calculate_metrics(transactions, selected_year)
    
    # Filter transactions for selected year and prepare for display
    filtered_transactions = []
    for t in metrics['transactions']:
        try:
            date_obj = datetime.strptime(t['date'], '%Y-%m-%d')
            if date_obj.year != selected_year:
                continue
            # Format date for display in JS
            t['date_display'] = date_obj.strftime('%b %d, %Y')
            filtered_transactions.append(t)
        except ValueError:
            t['date_display'] = t['date']
            filtered_transactions.append(t)
        # Ensure no None values in transaction dict
        for key in list(t.keys()):
            if t[key] is None:
                t[key] = '' if key != 'amount' else 0
    
    # Clean monthly_data to remove any None keys from expensesByCategory
    for month in metrics['monthly_data']:
        if 'expensesByCategory' in month:
            month['expensesByCategory'] = {
                (k if k is not None else 'Uncategorized'): v 
                for k, v in month['expensesByCategory'].items()
            }
    
    # Use all configured expense categories (not just ones with data)
    # This ensures all categories are available for filtering
    all_expense_cats = DAILY_EXPENSE_CATEGORIES.copy()
             
    # Separate dashboard metrics and historical/monthly data
    data_for_frontend = {
        'metrics': {k: round(v, 2) for k, v in metrics.items() if isinstance(v, (int, float))},
        'transactions': filtered_transactions,
        'monthly_data': metrics['monthly_data'],
        'expense_categories': all_expense_cats,
        'selected_year': selected_year,
        'available_years': available_years
    }
    
    # Use json.dumps directly to avoid Flask's sorting behavior
    from flask import Response
    return Response(
        json.dumps(data_for_frontend, sort_keys=False),
        mimetype='application/json'
    )


def get_next_id():
    """Get the next sequential ID by finding the max existing ID."""
    transactions = load_data()
    if not transactions:
        return 1
    max_id = 0
    for t in transactions:
        try:
            tid = int(t.get('id', 0))
            if tid > max_id:
                max_id = tid
        except (ValueError, TypeError):
            continue
    return max_id + 1

# Categories that should have negative amounts (expenses)
EXPENSE_CATEGORIES = [
    'Tax', 'Hotel/Vacation/Travel', 'Withdraw', 'Regalo', 
    'Money Transfer', 'Expense/Investment', 'Baby Sitter', 'Grocery', 'Membership', 'General', 'Restaurant', 'Petrol', 'Sport/Leisure'
]

@app.route('/api/add', methods=['POST'])
def add_transaction():
    """API endpoint to handle new transaction submissions."""
    data = request.json
    
    required_fields = ['type', 'amount', 'date', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        
        category = data['category']
        
        # Convert to negative if it's an expense category
        if category in EXPENSE_CATEGORIES:
            amount = -abs(amount)
            
        new_record = {
            'id': str(get_next_id()),
            'date': data['date'],
            'type': data['type'],
            'amount': f"{amount:.2f}",
            'category': category
        }
        
        if save_new_transaction(new_record):
            return jsonify({'message': 'Transaction added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to save to CSV'}), 500

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f"Internal server error: {e}"}), 500


@app.route('/details/<metric_type>')
def details(metric_type):
    """Renders the details page for a specific metric type."""
    transactions = load_data()
    now = datetime.now()
    
    # Get year from query parameter, default to current year
    selected_year = request.args.get('year', type=int)
    if selected_year is None:
        selected_year = now.year
    
    available_years = get_available_years(transactions)
    month_names = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    
    # Filter transactions based on metric type
    filtered_transactions = []
    title = ""
    color_class = ""
    
    for t in transactions:
        try:
            date_obj = datetime.strptime(t['date'], '%Y-%m-%d')
            if date_obj.year != selected_year:
                continue
                
            category = t.get('category') or 'Uncategorized'
            amount = t['amount']
            
            # Format date for display
            t['date_display'] = date_obj.strftime('%b %d, %Y')
            t['month'] = month_names[date_obj.month - 1]
            t['month_num'] = date_obj.month
            
            if metric_type == 'expenses':
                # All negative amounts (expenses)
                if amount < 0:
                    t['display_amount'] = abs(amount)
                    filtered_transactions.append(t)
                title = "Annual Expenses"
                color_class = "red"
                
            elif metric_type == 'income':
                # Monthly Salary/General, Interest/Investment, and other positive income
                if category == 'Monthly Salary/General' or category == 'Interest/Investment' or amount > 0:
                    t['display_amount'] = amount
                    filtered_transactions.append(t)
                title = "Total Income"
                color_class = "green"
                
            elif metric_type == 'investment':
                # Interest/Investment category
                if category == 'Interest/Investment':
                    t['display_amount'] = amount
                    filtered_transactions.append(t)
                title = "Investment Income"
                color_class = "cyan"
                
            elif metric_type == 'netflow':
                # All transactions for net flow view
                t['display_amount'] = amount
                filtered_transactions.append(t)
                title = "Net Flow (All Transactions)"
                color_class = "indigo"
                
        except ValueError:
            continue
    
    # Sort by date descending
    filtered_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # Group by month for summary
    monthly_summary = {}
    for t in filtered_transactions:
        month = t['month']
        if month not in monthly_summary:
            monthly_summary[month] = {'total': 0, 'count': 0, 'month_num': t['month_num']}
        monthly_summary[month]['total'] += t.get('display_amount', abs(t['amount']))
        monthly_summary[month]['count'] += 1
    
    # Sort monthly summary by month number
    monthly_summary_sorted = sorted(monthly_summary.items(), key=lambda x: x[1]['month_num'])
    
    # Calculate grand total
    grand_total = sum(t.get('display_amount', abs(t['amount'])) for t in filtered_transactions)
    
    # Get unique categories from filtered transactions
    categories_in_data = sorted(list(set(t.get('category') or 'Uncategorized' for t in filtered_transactions)))
    
    return render_template('details.html',
        title=title,
        color_class=color_class,
        transactions=filtered_transactions,
        monthly_summary=monthly_summary_sorted,
        grand_total=grand_total,
        year=selected_year,
        metric_type=metric_type,
        categories=categories_in_data,
        available_years=available_years
    )


def main():
    """Entry point for the finance-tracker command."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Finance Tracker - Personal Finance Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', '-p', type=int, default=5050, help='Port to run on (default: 5050)')
    parser.add_argument('--debug', '-d', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    initialize_csv()
    print(f"\n💰 Finance Tracker starting...")
    print(f"📊 Open your browser at: http://{args.host}:{args.port}\n")
    app.run(debug=args.debug, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
