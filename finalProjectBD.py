# # ==============================================================================
# 🛠 IMPORTS
# ==============================================================================
import duckdb
import sqlite3
import pandas as pd

# ==============================================================================
# 📂 Step 1: Create Sample Data CSV Files (500 Rows Each)
# ==============================================================================
def create_sample_csv_files():
    print("\n📌 Creating sample CSV files...")

    # Define CSV paths
    business_csv = r"C:\Users\Ido\Desktop\DB_Project\data\business.csv"
    reviews_csv = r"C:\Users\Ido\Desktop\DB_Project\data\reviews.csv"
    business_sample_csv = r"C:\Users\Ido\Desktop\DB_Project\data\business_sample.csv"
    reviews_sample_csv = r"C:\Users\Ido\Desktop\DB_Project\data\reviews_sample.csv"

    # Load full datasets
    business_df = pd.read_csv(business_csv)
    reviews_df = pd.read_csv(reviews_csv)

    # Randomly select 500 rows for sample data
    business_sample_df = business_df.sample(n=500, random_state=42)
    reviews_sample_df = reviews_df.sample(n=500, random_state=42)

    # Save sample data to new CSV files
    business_sample_df.to_csv(business_sample_csv, index=False)
    reviews_sample_df.to_csv(reviews_sample_csv, index=False)

    print("✅ Sample CSV files created successfully!")

# ==============================================================================
# 🦆 Step 2: Upload Data to DuckDB (Full & Sample Data)
# ==============================================================================
def upload_to_duckdb():
    print("\n📌 Uploading data to DuckDB...")

    # Define DuckDB database file
    db_file = 'db_file.duckdb'
    con = duckdb.connect(db_file)

    # Define CSV file paths
    business_csv = r"C:\Users\Ido\Desktop\DB_Project\data\business.csv"
    reviews_csv = r"C:\Users\Ido\Desktop\DB_Project\data\reviews.csv"
    business_sample_csv = r"C:\Users\Ido\Desktop\DB_Project\data\business_sample.csv"
    reviews_sample_csv = r"C:\Users\Ido\Desktop\DB_Project\data\reviews_sample.csv"

    # Load Full Data
    con.execute(f"CREATE TABLE IF NOT EXISTS business AS SELECT * FROM read_csv_auto('{business_csv}');")
    con.execute(f"CREATE TABLE IF NOT EXISTS reviews AS SELECT * FROM read_csv_auto('{reviews_csv}');")

    # Load Sample Data
    con.execute(f"CREATE TABLE IF NOT EXISTS business_sample AS SELECT * FROM read_csv_auto('{business_sample_csv}');")
    con.execute(f"CREATE TABLE IF NOT EXISTS reviews_sample AS SELECT * FROM read_csv_auto('{reviews_sample_csv}');")

    print("✅ Data uploaded to DuckDB successfully!")

    con.close()

# ==============================================================================
# 📊 Step 3: Execute Queries & Store Results in DuckDB
# ==============================================================================
def execute_queries_duckdb():
    print("\n📌 Executing queries and saving results in DuckDB...")

    # Connect to DuckDB
    db_file = 'db_file.duckdb'
    con = duckdb.connect(db_file)

    # Define queries
    queries = {
        "business_types": """
            WITH BusinessTypes AS (
                SELECT
                    business_id,
                    is_open,
                    CASE
                        WHEN categories LIKE '%Restaurant%' THEN 'Restaurant'
                        ELSE 'Non-Food Business'
                    END AS business_type
                FROM business
            )
            SELECT
                business_type,
                COUNT(*) AS total_businesses,
                ROUND(AVG(is_open) * 100, 2) AS survival_rate,
                ROUND(100 - (AVG(is_open) * 100), 2) AS closure_rate
            FROM BusinessTypes
            GROUP BY business_type;
        """,

        "food_types": """
            WITH FoodTypes AS (
                SELECT
                    business_id,
                    is_open,
                    stars,
                    CASE
                        WHEN categories LIKE '%Fast Food%' THEN 'Fast Food'
                        WHEN categories LIKE '%Restaurant%' THEN 'Restaurant'
                        ELSE 'Other'
                    END AS food_type
                FROM business
            )
            SELECT
                food_type,
                ROUND(AVG(stars), 2) AS avg_rating,  -- Compute the correct average rating
                ROUND(AVG(is_open) * 100, 2) AS survival_rate,
                ROUND((1 - AVG(is_open)) * 100, 2) AS closure_rate
            FROM FoodTypes
            WHERE food_type IN ('Fast Food', 'Restaurant')
            GROUP BY food_type;
        """,

        "funny_reviews": """
            WITH ReviewAnalysis AS (
                SELECT 
                    r.funny, 
                    b.is_open
                FROM reviews r
                JOIN business b ON r.business_id = b.business_id
            )
            SELECT
                CASE
                    WHEN funny = 0 THEN 'Not Funny (0)'
                    WHEN funny BETWEEN 1 AND 3 THEN 'Somewhat Funny (1-3)'
                    ELSE 'Highly Funny (4+)'
                END AS funny_category,
                ROUND(AVG(is_open) * 100, 2) AS survival_rate
            FROM ReviewAnalysis
            GROUP BY funny_category;
        """,

        "review_time_bins": """
            SELECT
                CASE
                    WHEN CAST(strftime(date, '%H') AS INTEGER) BETWEEN 6 AND 11 THEN 'Morning (06:00-11:59)'
                    WHEN CAST(strftime(date, '%H') AS INTEGER) BETWEEN 12 AND 17 THEN 'Afternoon (12:00-17:59)'
                    WHEN CAST(strftime(date, '%H') AS INTEGER) BETWEEN 18 AND 23 THEN 'Evening (18:00-23:59)'
                    ELSE 'Night (00:00-05:59)'
                END AS time_bin,
                stars,
                COUNT(*) AS review_count
            FROM reviews
            GROUP BY time_bin, stars
            ORDER BY time_bin, stars DESC;
        """,

        "food_category_hour_analysis": """ 
            WITH categorized_reviews AS (
                SELECT 
                    r.business_id,
                    EXTRACT(HOUR FROM STRPTIME(CAST(r.date AS VARCHAR), '%Y-%m-%d %H:%M:%S')) AS hour_of_day,
                    b.categories
                FROM 
                    reviews r
                JOIN 
                    business b ON r.business_id = b.business_id
                WHERE 
                    b.categories LIKE '%Burgers%' OR b.categories LIKE '%Pizza%'
            )
            SELECT 
                CASE 
                    WHEN hour_of_day BETWEEN 6 AND 11 THEN 'Morning (06:00-11:59)'
                    WHEN hour_of_day BETWEEN 12 AND 17 THEN 'Afternoon (12:00-17:59)'
                    WHEN hour_of_day BETWEEN 18 AND 23 THEN 'Evening (18:00-23:59)'
                    ELSE 'Night (00:00-05:59)'
                END AS time_of_day,
                CASE 
                    WHEN categories LIKE '%Burgers%' THEN 'Burgers'
                    WHEN categories LIKE '%Pizza%' THEN 'Pizza'
                END AS category,
                COUNT(*) AS review_count
            FROM 
                categorized_reviews
            GROUP BY 
                time_of_day, category
            ORDER BY 
                time_of_day, category;
        """
    }

    # Execute and store results in DuckDB
    for table_name, query in queries.items():
        con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS {query}")
        print(f"✅ Query results saved in DuckDB: {table_name}")

    con.close()

# ==============================================================================
# 🔄 Step 4: Transfer Data from DuckDB to SQLite
# ==============================================================================
def transfer_data_to_sqlite():
    print("\n📌 Transferring data from DuckDB to SQLite...")

    # Define SQLite file
    sqlite_file = 'db_results.sqlite'
    sqlite_con = sqlite3.connect(sqlite_file)

    # Connect to DuckDB
    duck_con = duckdb.connect('db_file.duckdb')

    # Tables to transfer
    tables_to_transfer = [
        "business_sample",
        "reviews_sample",
        "business_types",
        "food_types",
        "funny_reviews",
        "review_time_bins",
        "food_category_hour_analysis"
    ]

    for table in tables_to_transfer:
        df = duck_con.execute(f"SELECT * FROM {table}").fetchdf()
        df.to_sql(table, sqlite_con, if_exists="replace", index=False)
        print(f"✅ Transferred {table} from DuckDB to SQLite")

    # Close connections
    duck_con.close()
    sqlite_con.close()
    print("✅ All data successfully transferred to SQLite!")

# ==============================================================================
# 🚀 Run the Entire Pipeline
# ==============================================================================
if __name__ == "__main__":
    print("\n Starting the Data Processing Pipeline...")

    create_sample_csv_files()
    upload_to_duckdb()
    execute_queries_duckdb()
    transfer_data_to_sqlite()

    print("\n Data Pipeline Completed Successfully!")




