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
    result = cnx.query("SELECT fruit_name FROM smoothies.public.fruit_options")
    fruits = result['FRUIT_NAME'].tolist()
except Exception as e:
    st.error(f"Error fetching fruit options: {e}")
    fruits = []

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits,
    max_selections=5
)

# Single button with all logic inside
if st.button("Submit Order"):
    if not name_on_order:
        st.warning("Please enter your name!")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient!")
    else:
        ingredients_string = ", ".join(ingredients_list)
        session = cnx.session()
        insert_sql = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        
        try:
            session.sql(insert_sql).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
        except Exception as e:
            st.error(f"Failed to insert order: {e}")


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
