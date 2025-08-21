import streamlit as st
import requests

st.title("🥤 Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- Smoothie name ---
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# --- Snowflake connection ---
cnx = st.connection("snowflake")

# --- Fetch fruit options from Snowflake ---
try:
    fruits_df = cnx.query("SELECT fruit_name FROM smoothies.public.fruit_options")
    fruits = fruits_df.iloc[:, 0].dropna().astype(str).tolist()
except Exception as e:
    st.error(f"Error fetching fruit options: {e}")
    fruits = []

# --- User picks ingredients ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits,
    max_selections=5
)

# --- Submit order ---
if st.button("Submit Order") and ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    # Escape quotes for SQL safety
    name_safe = (name_on_order or "").replace("'", "''")
    ingredients_safe = ingredients_string.replace("'", "''")

    insert_sql = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_safe}', '{name_safe}')
    """

    try:
        cnx.execute(insert_sql)
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
    except Exception as e:
        st.error(f"Failed to insert order: {e}")

    # --- For each fruit, fetch nutrition info ---
    for fruit_chosen in ingredients_list:
        try:
            st.subheader(f"{fruit_chosen} Nutrition Information")

            # Fruityvice API
            fruityvice_response = requests.get(
                f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}", timeout=10
            )
            fruityvice_response.raise_for_status()
            fruityvice_data = fruityvice_response.json()

            # Normalize JSON to table form
            if "nutritions" in fruityvice_data:
                # Expand nutrition into rows
                nutrition = fruityvice_data["nutritions"]
                rows = [{"name": fruit_chosen, **nutrition}]
                st.dataframe(rows, use_container_width=True)
            else:
                st.warning(f"No nutrition data available for {fruit_chosen}")

        except Exception as e:
            st.warning(f"Could not fetch info for {fruit_chosen}: {e}")

# --- Show all fruit options ---
if fruits:
    st.write("Available fruit options:")
    st.dataframe(fruits_df, use_container_width=True)
