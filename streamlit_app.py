# Import Python packages
import streamlit as st
import requests   # <--- for smoothie API calls

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

# Handle order
if st.button("Submit Order") and ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    # Insert into Snowflake
    insert_sql = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    try:
        cnx.execute(insert_sql)
        st.success(f"Your Smoothie is ordered, {name_on_order} ✅")
    except Exception as e:
        st.error(f"Failed to insert order: {e}")

    # Show nutrition info for each chosen fruit (using the API)
    for fruit_chosen in ingredients_list:
        try:
            # Example: call MySmoothieRoot API (replace with correct endpoint if needed)
            url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
            response = requests.get(url)
            data = response.json()

            # Display results in a nice table
            st.subheader(f":green_apple: Nutrition info for {fruit_chosen}")
            st.dataframe(data, use_container_width=True)

        except Exception as e:
            st.error(f"Could not fetch info for {fruit_chosen}: {e}")
