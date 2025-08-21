import streamlit as st
import requests

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Streamlit Snowflake connection
cnx = st.connection("snowflake")

# --- Fetch fruit options (DataFrame -> list) ---
try:
    fruits_df = cnx.query("SELECT fruit_name FROM smoothies.public.fruit_options")
    # Robustly take the first (and only) column, regardless of case
    fruits = fruits_df.iloc[:, 0].dropna().astype(str).tolist()
except Exception as e:
    st.error(f"Error fetching fruit options: {e}")
    fruits = []

# --- Let user choose up to 5 ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits,
    max_selections=5
)

# --- Submit order ---
if st.button("Submit Order") and ingredients_list:
    # Build a nice ingredients string
    ingredients_string = ", ".join(ingredients_list)

    # VERY simple escaping of single quotes for SQL string literals
    name_safe = (name_on_order or "").replace("'", "''")
    ingredients_safe = ingredients_string.replace("'", "''")

    insert_sql = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_safe}', '{name_safe}')
    """

    try:
        cnx.execute(insert_sql)   # use execute for INSERT/UPDATE/DELETE
        st.success(f"Your Smoothie is ordered, {name_on_order} ✅")
    except Exception as e:
        st.error(f"Failed to insert order: {e}")

    # --- For-loop: fetch and show info per fruit via API ---
    for fruit in ingredients_list:
        try:
            # Example endpoint; replace with your actual API
            url = f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
            r = requests.get(url, timeout=10)
            r.raise_for_status()

            st.subheader(f"🍏 Info for {fruit}")
            # Use st.json so any JSON shape displays safely
            st.json(r.json())
            # If you prefer a table and the API returns a flat dict or list of dicts:
            # st.dataframe(r.json(), use_container_width=True)

        except Exception as e:
            st.warning(f"Could not fetch info for {fruit}: {e}")

# Optional: show the fruit options table for reference
if fruits:
    st.write("Available fruit options:")
    st.dataframe(fruits_df, use_container_width=True)
