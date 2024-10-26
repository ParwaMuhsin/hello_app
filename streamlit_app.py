import streamlit as st 
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

# Database connection settings
DATABASE_HOST = "130.193.210.55"  # Update as needed
DATABASE_NAME = "faar"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "ashqy100"  # Replace with your actual password 

# Function to create a database connection
def create_connection():
    connection = psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )
    return connection

# Function to fetch data from a specified query
def fetch_data(query):
    conn = create_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Function to create a SQL query based on a keyword
def create_keyword_query(keyword):
    query = f"""
    SELECT f.*, h.scientific_name, h.common_name
    FROM feature f
    JOIN host h ON f.host_id = h.host_id
    WHERE h.scientific_name ILIKE '%{keyword}%'
    OR h.common_name ILIKE '%{keyword}%'
    OR f.name ILIKE '%{keyword}%'
    """
    return query

# Function to fetch views from the database
def fetch_views():
    query = """
    SELECT table_name
    FROM information_schema.views
    WHERE table_schema = 'public';  -- Change if necessary
    """
    return fetch_data(query)

# Streamlit application layout
st.title("Development of Farm Animal Antibiotic Resistance (FAAR) Database")

# Sidebar for selecting table or view
tables_and_views = ["feature", "organism", "host", "pub", "cv", "cvterm"]
views = fetch_views()
for view in views['table_name']:
    tables_and_views.append(view)

table_name = st.sidebar.selectbox(
    "Select a Table or View",
    tables_and_views
)

# Fetching and displaying data based on selected table or view
query = f"SELECT * FROM {table_name};"
data = fetch_data(query)
st.subheader(f"{table_name.capitalize()} Data")
st.write(data)

# Adding filters for specific tables
if table_name == "feature":
    host_id = st.sidebar.number_input("Filter by Host ID", min_value=1, value=1)
    filtered_query = f"SELECT * FROM feature WHERE host_id = {host_id};"
    filtered_data = fetch_data(filtered_query)
    st.subheader("Filtered Feature Data by Host ID")
    st.write(filtered_data)

    # Adding visualization options
    if st.sidebar.checkbox("Show Feature Count by Organism"):
        if 'organism_id' in filtered_data.columns:
            organism_counts = filtered_data['organism_id'].value_counts()
            st.subheader("Feature Count by Organism")
            st.bar_chart(organism_counts)
        else:
            st.warning("The 'organism_id' column does not exist in the filtered feature data.")

    if st.sidebar.checkbox("Show Feature Distribution by Organism"):
        if 'organism_id' in filtered_data.columns:
            st.subheader("Feature Distribution by Organism")
            plt.figure(figsize=(10, 5))
            sns.histplot(filtered_data['organism_id'], bins=20, kde=True)
            st.pyplot(plt)
        else:
            st.warning("The 'organism_id' column does not exist in the filtered feature data.")

# User input for free-text search
st.subheader("Search Database by Keyword")
keyword_input = st.text_input("Enter a keyword (e.g., 'chicken'): ")

# Button to execute the keyword search
if st.button("Search"):
    if keyword_input:
        try:
            keyword_query = create_keyword_query(keyword_input)
            results = fetch_data(keyword_query)
            if not results.empty:
                st.write(results)
            else:
                st.write("No results found for the keyword.")
        except Exception as e:
            st.error(f"Error executing keyword search: {e}")
    else:
        st.write("Please enter a keyword.")

# User input for SQL query
st.subheader("Execute SQL Query")
query_input = st.text_area("Enter your SQL query (e.g., SELECT * FROM feature WHERE host_id = 1):", height=200)

# Button to execute the SQL query
if st.button("Execute Query"):
    if query_input:
        try:
            results = fetch_data(query_input)
            if not results.empty:
                st.write(results)
            else:
                st.write("No results found for the query.")
        except Exception as e:
            st.error(f"Error executing query: {e}")
    else:
        st.write("Please enter a SQL query.")

st.sidebar.header("About")
st.sidebar.text("This application allows you to explore data from the Development of Farm Animal Antibiotic Resistance (FAAR) Database.")
st.sidebar.text("It specifically focuses on antibiotic resistance-related information and protein IDs in livestock animals.")
