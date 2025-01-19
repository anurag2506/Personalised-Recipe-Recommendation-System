import streamlit as st

st.title("Personalized Food Recommendation System 🍴")

# Getting preferences from the user
st.header("Tell us about your preferences:")
dietary_preferences = st.radio(
    "What is your dietary preference?",
    ("Vegetarian", "Vegan", "Non-Vegetarian", "Gluten-Free", "Keto", "Paleo", "No Preference")
)

# Getting the preferred cuisine 
preferred_cuisine = st.selectbox(
    "What type of cuisine do you prefer?",
    ("Indian", "Italian", "Chinese", "Mexican", "Thai", "Japanese", "Mediterranean", "American")
)

# Getting the time limit for cooking
time_limit = st.slider(
    "How much time can you spend cooking? (in minutes)",
    min_value=5, max_value=120, step=5
)

# Getting the available ingredients 
available_ingredients = st.multiselect(
    "Select the ingredients you have:",
    [
        "Tomatoes", "Onions", "Garlic", "Chicken", "Beef", "Fish", 
        "Rice", "Pasta", "Cheese", "Eggs", "Milk", "Potatoes", 
        "Carrots", "Peppers", "Spinach", "Mushrooms", "Lentils", 
        "Beans", "Yogurt", "Flour", "Butter", "Sugar"
    ]
)




# Check of all the input boxes
if st.button("Find Recipes"):
    st.subheader("Your Choices:")
    st.write(f"Dietary Preference: **{dietary_preferences}**")
    st.write(f"Preferred Cuisine: **{preferred_cuisine}**")
    st.write(f"Time Limit: **{time_limit} minutes**")
    st.write("Available Ingredients: ", ", ".join(available_ingredients))

    st.subheader("Recommended Recipes 🍲")
    st.write("This section will show personalized recipe recommendations based on your input. "
             "Connect this app to a recipe API or database for dynamic results!")