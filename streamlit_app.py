# Import Python packages
import streamlit as st

# Title and instructions
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")  # Streamlit Snowflake connection

# Fetch fruit options from Snowflake
try:
    # Use SQL query instead of Snowpark session
    result = cnx.query("SELECT fruit_name FROM smoothies.public.fruit_options")
    fruits = [row["FRUIT_NAME"] for row in result]
except Exception as e:
    st.error(f"Error fetching fruit options: {e}")
    fruits = []

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits,
    max_selections=5
)

# Insert order into Snowflake when button is clicked
if st.button("Submit Order") and ingredients_list:
    ingredients_string = ", ".join(ingredients_list)  # better formatting for DB
    insert_sql = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    try:
        cnx.execute(insert_sql)  # Use execute for INSERT
        st.success(f"Your Smoothie is ordered, {name_on_order} ✅")
    except Exception as e:
        st.error(f"Failed to insert order: {e}")
