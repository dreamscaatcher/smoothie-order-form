# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!  """)

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your smoothie will be :', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)

# Convert Snowpark DataFrame to pandas DataFrame, then to list
pd_df = my_dataframe.to_pandas()
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['fruit_name'].tolist(),  # Convert to list for multiselect
    max_selections=5
)

if ingredients_list:
   
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Using proper SQL parameterization would be more secure, but keeping your format
    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')    
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")