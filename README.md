# 💰 Finance Tracker

A beautiful, modern personal finance dashboard built with Flask and vanilla JavaScript. Track your income, expenses, and savings with interactive charts and detailed reports.

**Powered by Daniele Grassi**

---

## ✨ Features

- **📊 Interactive Dashboard** - View your financial health at a glance with real-time metrics
- **📈 Visual Charts** - Toggle between bar charts and pie charts for expense breakdown
- **🗓️ Year Selection** - Switch between years to compare financial data
- **🏷️ Category Filtering** - Filter expenses by category to understand spending patterns
- **📅 Monthly Breakdown** - Click on any month to filter transactions and charts
- **💾 CSV Storage** - Simple, portable data storage in CSV format
- **🎨 Modern UI** - Clean, responsive design with Tailwind CSS

---

## 📸 Screenshots

### Dashboard Overview
The main dashboard shows key financial metrics including:
- Total Income (Annual & Monthly)
- Total Expenses (Annual & Monthly)
- Net Flow (Savings)
- Weekly Average Spending

### Interactive Charts
- **Bar Chart**: Visualize monthly income vs expenses with stacked categories
- **Pie Chart**: See expense breakdown by category

### Category Filters
Filter your view by:
- Income types (Salary, Investment Income)
- Expense categories (Grocery, Restaurant, Travel, etc.)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

#### Option 1: Install as a Package (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/finance-tracker.git
   cd finance-tracker
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the application**
   ```bash
   pip install .
   ```
   
   Or for development (editable mode):
   ```bash
   pip install -e .
   ```

4. **Run the application**
   ```bash
   finance-tracker
   ```

5. **Open your browser**
   ```
   http://127.0.0.1:5050
   ```

#### Option 2: Run Directly

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/yourusername/finance-tracker.git
   cd finance-tracker
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python finance_tracker.py
   ```

### Command Line Options

```bash
finance-tracker --help
```

| Option | Description |
|--------|-------------|
| `--host` | Host to bind to (default: 127.0.0.1) |
| `--port`, `-p` | Port to run on (default: 5050) |
| `--debug`, `-d` | Run in debug mode |

**Examples:**
```bash
# Run on a different port
finance-tracker -p 8080

# Run accessible from network
finance-tracker --host 0.0.0.0

# Run in debug mode
finance-tracker --debug
```

---

## 📖 Usage

### Adding Transactions

1. Click the **"Add New Transaction"** button
2. Fill in the details:
   - **Transaction Type**: Description of the transaction
   - **Amount**: The amount in euros (always enter positive values)
   - **Date**: When the transaction occurred
   - **Category**: Select from predefined categories
3. Click **"Save Transaction"**

### Viewing Reports

- **Year Selector**: Use the dropdown in the header to switch between years
- **Monthly Filter**: Click on any month in the "Monthly Snapshot" table to filter
- **Chart Toggle**: Switch between Bar and Pie charts using the buttons
- **Category Filters**: Click category buttons to show/hide specific expense types

### Understanding the Metrics

| Metric | Description |
|--------|-------------|
| **Total Income** | Sum of all salary and investment income for the year |
| **Total Expenses** | Sum of all expenses for the year |
| **Net Flow** | Income minus Expenses (your savings) |
| **Weekly Average** | Average weekly spending based on year-to-date data |

---

## 🏷️ Expense Categories

The following expense categories are available:

| Category | Description |
|----------|-------------|
| 💼 Tax | Tax payments |
| ✈️ Hotel/Vacation/Travel | Travel and vacation expenses |
| 💵 Withdraw | Cash withdrawals |
| 🎁 Regalo | Gifts |
| 💸 Money Transfer | Bank transfers |
| 📈 Expense/Investment | Investment contributions |
| 👶 Baby Sitter | Childcare expenses |
| 🛒 Grocery | Supermarket and food shopping |
| 📱 Membership | Subscriptions and memberships |
| 🏷️ General | General purchases |
| 🍽️ Restaurant | Dining out |
| ⛽ Petrol | Fuel expenses |
| 🏃 Sport/Leisure | Sports and leisure activities |
| ↩️ Refund | Refunds (counted as income) |
| 🎁 Benefit | Benefits received (counted as income) |

---

## 📁 Project Structure

```
finance-tracker/
├── finance_tracker.py    # Main Flask application
├── finance_data.csv      # Transaction data (gitignored)
├── pyproject.toml        # Package configuration
├── requirements.txt      # Python dependencies (alternative)
├── MANIFEST.in           # Package manifest
├── LICENSE               # MIT License
├── templates/
│   ├── index.html        # Main dashboard
│   └── details.html      # Detailed transaction view
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript
- **Styling**: Tailwind CSS (via CDN)
- **Charts**: Chart.js
- **Storage**: CSV file

---

## 🔒 Privacy

Your financial data is stored locally in `finance_data.csv`. This file is automatically excluded from git via `.gitignore` to protect your sensitive information.

---

## 📝 CSV Format

The data is stored in a simple CSV format:

```csv
id,date,type,amount,category
1,2025-01-27,Income,5095.00,Monthly Salary/General
2,2025-01-03,Tax,-8.55,Tax
3,2025-01-16,Hotel Refund,229.00,Refund
```

- **Positive amounts**: Income (salary, refunds, benefits)
- **Negative amounts**: Expenses

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Daniele Grassi**

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Lightweight WSGI web application framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Chart.js](https://www.chartjs.org/) - Simple yet flexible JavaScript charting

---

<p align="center">
  Made with ❤️ for personal finance management
</p>
