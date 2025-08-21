# Import Python packages
import streamlit as st

# Title and instructions
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")

# Fetch fruit options from Snowflake
try:
    # Use query() for SELECT statements - this returns a DataFrame
    result = cnx.query("SELECT fruit_name FROM smoothies.public.fruit_options")
    fruits = result['FRUIT_NAME'].tolist()  # Convert DataFrame column to list
    st.write("Available fruits:", fruits)  # Debug info
except Exception as e:
    st.error(f"Error fetching fruit options: {e}")
    fruits = []

# Only show multiselect if we have fruits
if fruits:
    # Multiselect for ingredients
    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruits,
        max_selections=5
    )

    # Insert order into Snowflake when button is clicked
    if st.button("Submit Order") and ingredients_list and name_on_order:
        ingredients_string = ", ".join(ingredients_list)
        
        # Use session.sql() for INSERT statements
        session = cnx.session()
        insert_sql = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        
        try:
            # Use session.sql().collect() for INSERT/UPDATE/DELETE operations
            session.sql(insert_sql).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
        except Exception as e:
            st.error(f"Failed to insert order: {e}")
    
    elif st.button("Submit Order") and (not ingredients_list or not name_on_order):
        if not name_on_order:
            st.warning("Please enter your name!")
        if not ingredients_list:
            st.warning("Please select at least one ingredient!")
else:
    st.warning("No fruit options available. Please check your database connection.")