# ==============================================================================
# 🛠 IMPORTS
# ==============================================================================
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==============================================================================
# 📂 Function to Load Data from SQLite
# ==============================================================================
def load_data(query):
    """Fetch data from the SQLite database and return as a Pandas DataFrame."""
    conn = sqlite3.connect("db_results.sqlite")  # Connect to the SQLite database
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==============================================================================
# 🎨 Custom Styling Functions
# ==============================================================================
def highlight_rows(s):

    """Apply color based on conditions for the 'stars' column."""
    if s.name == "stars":
        return [f"background-color: {'yellow' if v >= 4 else 'lightcoral'}; color: black;" for v in s]
    return ["color: black;"] * len(s)  # Ensuring black text for all other rows

def highlight_columns(df):
    """Apply alternating background colors to columns (except 'stars') while keeping text black."""
    colors = ["#D4E6F1", "#FAD7A0", "#A9DFBF", "#E8DAEF", "#F5B7B1"]  # Different colors for columns
    styles = {}
    col_list = [col for col in df.columns if col != "stars"]  # Exclude 'stars' from general column coloring

    for i, col in enumerate(col_list):
        styles[col] = [f"background-color: {colors[i % len(colors)]}; color: black;"] * len(df)

    return pd.DataFrame(styles)

# ==============================================================================
# 🏢 Business & Reviews Sample Data Visualization
# ==============================================================================
st.title("📊 Business & Reviews Data Analysis")

# ==============================================================================
# Paragraph intro to tables
# ==============================================================================
st.subheader("About the Data")

st.write("""
This dashboard presents a **500-row sample** from a larger dataset, containing business details 
and customer reviews. The dataset includes a variety of businesses, including restaurants and 
non-food establishments, allowing us to analyze trends in customer feedback and business performance. 
Through these tables and visualizations, we aim to uncover meaningful insights such as survival and 
closure rates, the impact of humor in reviews, and variations in customer ratings over different times of the day.
""")

# Load Sample DataFrames
df_business = load_data("SELECT * FROM business_sample")
df_reviews = load_data("SELECT * FROM reviews_sample")

# Apply styling
if "stars" in df_business.columns:
    styled_business = df_business.style.apply(highlight_rows, subset=["stars"]).apply(highlight_columns, axis=None)
else:
    styled_business = df_business.style.apply(highlight_columns, axis=None)

if "stars" in df_reviews.columns:
    styled_reviews = df_reviews.style.apply(highlight_rows, subset=["stars"]).apply(highlight_columns, axis=None)
else:
    styled_reviews = df_reviews.style.apply(highlight_columns, axis=None)

# Display Sample Tables
st.subheader("⦁ Business Sample Data")
st.dataframe(styled_business)

st.subheader("⦁ Reviews Sample Data")
st.dataframe(styled_reviews)

st.markdown("---")

# ======================================================================
# Story line:
st.subheader("⦁ The Story Behind the Data")

st.write("""
The success of a business depends on many factors—industry type, customer perception, and how people express their 
experiences in reviews. This dashboard explores business survival rates, customer satisfaction, differences in customer 
behavior throughout the day, and the impact of reviews to uncover key insights.

By analyzing patterns based on time of day and specific business types, we can identify trends that help businesses 
refine their strategies and predict customer behavior. Reviews play a crucial role in business success, offering 
insights into what needs improvement and what is working well. Interestingly, factors such as humor in reviews, the time
 they are posted, and the type of business they describe can reveal deeper connections between customer engagement and 
 business outcomes.

This analysis highlights the importance of having a well-defined strategy before launching any business. Understanding customer behavior through data-driven insights enables businesses to target and attract customers more effectively, ultimately leading to smarter decision-making and long-term success.
""")

st.markdown("---")

# ======================================================================
# 📊 Business Types: Survival & Closure Rates (Seaborn Plot)
# ======================================================================
# -------------------
# Streamlit UI
st.title("⦁ Business Types: Survival & Closure Rates")
st.subheader("Comparing Restaurants & Non-Food Businesses")

st.write("""
    This analysis explores the differences in survival and closure rates between restaurants and non-food businesses. 
    Do restaurants struggle more to stay open compared to other businesses?  
    By comparing these rates, we aim to uncover trends in business longevity across different industries.
""")
# -------------------


# Load data (Updated with closure and survival rates)
df_business_types = load_data("SELECT business_type, survival_rate, closure_rate FROM business_types")

# Melt data for Seaborn (convert wide to long format for better visualization)
df_melted = df_business_types.melt(id_vars=["business_type"],
                                   value_vars=["survival_rate", "closure_rate"],
                                   var_name="Rate Type",
                                   value_name="Percentage")

# Set up the figure
fig, ax = plt.subplots(figsize=(8, 6))

# Create the Seaborn bar plot
sns.barplot(
    x="business_type",
    y="Percentage",
    hue="Rate Type",
    data=df_melted,
    palette=["#1f77b4", "#ff7f0e"]  # Blue for Survival, Orange for Closure
)

# Add value labels on each bar
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f%%", label_type="edge", fontsize=12, padding=3)

# Formatting the chart
plt.xlabel("Business Type", fontsize=14)
plt.ylabel("Percentage (%)", fontsize=14)
plt.title("Comparison of Survival & Closure Rates by Business Type", fontsize=16)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title="Rate Type")
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Display the plot in Streamlit
st.pyplot(fig)

st.subheader("⦁ Insights")
st.write("""  
From this analysis, we see that non-food businesses have a significantly higher survival rate compared to restaurants.  
Despite the popularity of dining out, restaurants face higher closure rates, possibly due to high operational costs, market competition, or changing consumer preferences.  
This suggests that while restaurants can thrive, maintaining long-term success is more challenging in the food industry.  
""")

st.markdown("---")

# ==============================================================================
# 📊 Interactive Graph: Business Performance Comparison (Fast Food vs Restaurants)
# ==============================================================================
# -------------------

# Streamlit UI
st.title("⦁ Fast Food vs. Restaurants")
st.subheader("Survival, Closure & Ratings Analysis")

st.write("""
    This query examines whether customer ratings influence the closure rates of restaurants and fast food businesses. 
    Are fast food places more likely to shut down compared to full-service restaurants?
    By comparing ratings and closure rates, we aim to uncover meaningful insights. 
""")

# -------------------


# Load food type statistics
query = "SELECT food_type, avg_rating, survival_rate, closure_rate FROM food_types;"
df_food = load_data(query)

# User selection for metric to display
option = st.selectbox("Select a Metric to Compare:", ["Survival Rate", "Closure Rate", "Average Rating"])

# Mapping selected metric to dataframe column
metric_mapping = {
    "Survival Rate": "survival_rate",
    "Closure Rate": "closure_rate",
    "Average Rating": "avg_rating"
}
selected_metric = metric_mapping[option]

# Plot bar chart
fig, ax = plt.subplots(figsize=(8, 6))
bars = plt.bar(df_food["food_type"], df_food[selected_metric], color=["#1f77b4", "#ff7f0e"])

# Add values on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 2), ha='center', va='bottom', fontsize=12, fontweight='bold')

# Labels and title
plt.xlabel("Business Type", fontsize=14)
plt.ylabel(option, fontsize=14)
plt.title(f"Comparison of {option} Between Fast Food & Restaurants", fontsize=16)
plt.ylim(0, max(df_food[selected_metric]) + 5)  # Adjust y-axis limit for clarity
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Display the plot in Streamlit
st.pyplot(fig)

st.subheader("⦁ Insights")
st.write("""  
From this analysis, we see that while restaurants generally receive higher customer ratings, they also have a lower survival rate and a higher closure rate compared to fast food businesses.  
This suggests that despite earning better reviews, factors such as operational costs, competition, or industry challenges may contribute to their shorter lifespan.  
""")

st.markdown("---")
# ==============================================================================
# ⭐ Review Count by Star Rating and Time of Day
# ==============================================================================
# Streamlit UI
st.title("⦁ Reviews analyses by time of day")
st.subheader("Differences in Review Ratings by Time of Day")

# Explanation of the query
st.write("""  
This analysis explores how customer ratings vary throughout the day.  
Are people more generous with their reviews in the morning, or do they rate businesses more critically at night?  
By examining review trends across different time periods, we can identify patterns in customer sentiment and engagement.  
""")


# Load the review time bin data
df_time_bins = load_data("SELECT * FROM review_time_bins")

# List of available time bins + 'All' option
time_bins = ['All'] + df_time_bins['time_bin'].unique().tolist()

# Streamlit selectbox for selecting the time_bin or 'All'
selected_time_bin = st.selectbox("Select Time of Day:", time_bins)

# Filter data based on the selected time_bin
if selected_time_bin != 'All':
    filtered_data = df_time_bins[df_time_bins['time_bin'] == selected_time_bin]
else:
    filtered_data = df_time_bins  # If 'All' is selected, use all data

# Pivot the DataFrame for better visualization
df_pivot = filtered_data.pivot(index="time_bin", columns="stars", values="review_count").fillna(0)

# Plotting the results
fig, ax = plt.subplots(figsize=(10, 6))
df_pivot.plot(kind="bar", stacked=True, colormap="viridis", ax=ax)

# Labeling the plot
plt.xlabel("Time of Day", fontsize=14)
plt.ylabel("Number of Reviews", fontsize=14)
plt.title(f"Distribution of Star Ratings for {selected_time_bin}" if selected_time_bin != 'All' else "Distribution of Star Ratings for All Time Bins", fontsize=16)
plt.xticks(rotation=25)
plt.legend(title="Stars")
plt.grid(axis="y", linestyle="--", alpha=0.5)


# Display the plot in Streamlit
st.pyplot(fig)

st.subheader("⦁ Insights")
st.write("""  
There is not a strong correlation between the time of day and the review scores that reviewers give to businesses. 
However, it is evident that people tend to leave reviews more often in the evening and night hours, while fewer reviews 
are given in the morning. Additionally, around 45% of the reviews are 5-star ratings.  
""")

st.markdown("---")
# ==============================================================================
# 🍔 Normal Matplotlib Plot: Review Trends for Burgers & Pizza Over Time
# ==============================================================================

# -------------------
# Streamlit UI
st.subheader("Reviews by Time of Day for different categories")

# Explanation of the query
st.write("""  
This analysis compares the number of reviews for burger and pizza businesses at different times of the day—morning, 
afternoon, evening, and night—to identify patterns in customer activity.
""")

# -------------------

# Load data
df_food_hour = load_data("SELECT * FROM food_category_hour_analysis")

# Pivot the data for better visualization
df_pivot_food = df_food_hour.pivot(index="time_of_day", columns="category", values="review_count").fillna(0)

# Sorting time of day in correct order
time_order = ["Morning (06:00-11:59)", "Afternoon (12:00-17:59)", "Evening (18:00-23:59)", "Night (00:00-05:59)"]
df_pivot_food = df_pivot_food.reindex(time_order)

# Creating the plot
fig, ax = plt.subplots(figsize=(10, 6))
df_pivot_food.plot(kind="bar", colormap="Set2", ax=ax)

# Labeling the plot
plt.xlabel("Time of Day", fontsize=14)
plt.ylabel("Number of Reviews", fontsize=14)
plt.title("Burgers & Pizza Reviews by Time of Day", fontsize=16)
plt.xticks(rotation=25)
plt.legend(title="Category")
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Display the plot in Streamlit
st.pyplot(fig)

st.subheader("⦁ Insights")
st.write("""  
You can see that the review times are similar, but there is a noticeable trend: during the day, people tend to leave 
more reviews for burger businesses than pizza places. However, at night, the trend shifts, with more reviews being 
written for pizza businesses than for burger spots.
""")

st.markdown("---")


# ==============================================================================
# 🤣 Humor Impact on Business Survival (Seaborn Line Plot)
# ==============================================================================
# Streamlit UI
st.title("⦁ Humor in Reviews & Business Survival")
st.subheader("Can We Predict Ratings Based on Review Funniness?")

st.write("""
    This analysis explores whether the level of humor in customer reviews is linked to business survival rates.  
    Do funnier reviews indicate better ratings, or is there no clear connection?  
    By comparing survival rates across different levels of review humor, we aim to uncover potential patterns.  
""")

# Load data
df_funny_reviews = load_data("SELECT * FROM funny_reviews")

# **Define correct order for funny categories**
funny_order = ["Not Funny (0)", "Somewhat Funny (1-3)", "Highly Funny (4+)"]

# **Convert the column to categorical with the correct order**
df_funny_reviews["funny_category"] = pd.Categorical(df_funny_reviews["funny_category"], categories=funny_order, ordered=True)

# Create Seaborn line plot
fig, ax = plt.subplots(figsize=(8, 6))
sns.lineplot(
    x="funny_category",
    y="survival_rate",
    data=df_funny_reviews,
    marker="o",  # Adds dots at each data point
    linewidth=2.5,
    color="royalblue"
)

# Formatting the plot
plt.xlabel("Review Funniness Level", fontsize=14)
plt.ylabel("Survival Rate (%)", fontsize=14)
plt.title("Does Humor in Reviews Impact Business Survival?", fontsize=16)
plt.ylim(80.5, 83.5)  # Adjust y-axis range

# **Set y-axis ticks to increment by 0.5**
plt.yticks(np.arange(80.5, 83.6, 0.5))

plt.grid(axis="y", linestyle="--", alpha=0.5)

# Add value labels to each point
for i, row in df_funny_reviews.iterrows():
    plt.text(i, row["survival_rate"] + 0.1, f"{row['survival_rate']}%", ha='center', fontsize=12, fontweight='bold')

# Display the plot in Streamlit
st.pyplot(fig)

st.subheader("⦁ Insights")
st.write("""  
From this analysis, we observe that the funnier the reviews, the lower the business survival rate.  
Businesses with "Not Funny" reviews have the highest survival rate, while those with highly funny reviews tend to struggle more.  
This could suggest that humorous reviews are often tied to negative or sarcastic customer experiences, which may indicate dissatisfaction.  
It seems that while funny reviews entertain, they may also highlight issues that impact a business’s long-term success.  
""")

st.markdown("---")
