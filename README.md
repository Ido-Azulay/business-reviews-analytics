# Business Reviews Analytics.

An academic data analytics project developed for a Big Data Analysis elective as part of a B.Sc. in Computer Science.

The project explores relationships between business characteristics, customer reviews, ratings, and business closure using Python and SQL.

## Tech Stack

Python · Pandas · DuckDB · SQL · SQLite · Streamlit · Matplotlib · Seaborn

## Project Overview

The project consists of two main components:

### 1. Data Processing — `finalProjectBD.py`

- Reads business and customer review datasets.
- Creates sample CSV files for analysis.
- Loads and processes data using DuckDB.
- Executes analytical SQL queries.
- Exports processed results to SQLite.

### 2. Interactive Dashboard — `BDprojectDashboard.py`

An interactive Streamlit dashboard visualizing analytical results, including:

- Business survival and closure rates.
- Fast-food versus restaurant comparisons.
- Customer review ratings by time of day.
- Relationships between humor in reviews, ratings, and business outcomes.

## Running the Dashboard

**1. Install Python and the required packages:**

`pip install streamlit pandas numpy matplotlib seaborn`

**2. From the project directory, run:**

`streamlit run BDprojectDashboard.py`

The dashboard reads the included `db_results.sqlite` database.

## Data and Reproducibility

The original business and review CSV datasets are not included in this repository.

The SQLite database contains previously generated analysis results used by the dashboard.

The data processing script currently references local Windows file paths. Reproducing the full pipeline requires the original datasets and adjustments to these paths.

## Project Context

Developed as a final course project to gain practical experience in data preparation, SQL-based analysis, database workflows, and communicating analytical findings through interactive visualizations.
