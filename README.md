## Project Status

**This project is no longer under active development.**

The application successfully reached its intended functional scope and remains publicly available as an open-source reference implementation.

Developers interested in extending the project are welcome to fork the repository and continue development independently.

---

## Features

### Authentication & Security

* User Registration
* Secure Login & Logout
* Password Hashing
* Session Management
* Password Reset Support

### Banking Operations

* Account Creation & Management
* Deposit Funds
* Withdraw Funds
* Transfer Funds Between Accounts
* Transaction History Tracking
* Account Status Management

### Administrative Controls

* Admin Dashboard
* User Management
* Account Monitoring
* Fraud Alert Review
* Audit Log Inspection

### Fraud Detection

* Rule-Based Fraud Detection
* Machine Learning-Based Anomaly Detection
* Isolation Forest Implementation
* Suspicious Transaction Identification
* Fraud Alert Generation

### Reporting & Analytics

* Transaction History Reports
* Banking Activity Analytics
* PDF Statement Generation
* Dashboard Statistics

---

## Technology Stack

### Backend

* Python
* Flask
* SQLAlchemy ORM
* Flask-Login
* Flask-WTF
* Werkzeug

### Database

* SQLite

### Machine Learning

* Scikit-Learn
* Isolation Forest
* Pandas
* NumPy
* Joblib

### Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript

### Reporting

* ReportLab

---

## Machine Learning Fraud Detection

The system incorporates an Isolation Forest anomaly detection model to identify potentially fraudulent banking activity.

The fraud detection module analyzes transaction behavior patterns and flags unusual activity based on:

* Transaction Amount
* Transaction Frequency
* Transaction Timing
* Transaction Distribution Patterns

Generated alerts are surfaced through the administration dashboard for further review.

---

## Project Structure

```text
smartbank/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── utils/
│
├── ml/
│   └── fraud_detection.py
│
├── reports/
│
├── tests/
│
├── requirements.txt
│
└── run.py
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<your-username>/smartbank-secure-banking-system.git
cd smartbank-secure-banking-system
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python run.py
```

---

## Key Learning Outcomes

* Full-Stack Web Development
* Database Design & Management
* Authentication & Authorization
* Banking Transaction Processing
* Fraud Detection Systems
* Machine Learning Integration
* Audit Logging
* Analytics Dashboards
* PDF Report Generation

---

## Future Improvements

Potential enhancements for future contributors:

* Two-Factor Authentication (2FA)
* Email Verification
* Docker Support
* REST API Documentation
* CI/CD Pipelines
* Advanced Fraud Detection Models
* Mobile Application Integration
* Real-Time Notifications

---

## Screenshots

Screenshots can be added here after deployment:

* Login Page
* User Dashboard
* Transaction History
* Fraud Detection Dashboard
* Admin Panel

---

## License

This project is intended for educational, learning, and portfolio purposes.

Feel free to fork, modify, and extend the system.
