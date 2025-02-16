import streamlit as st
import cohere
import pandas as pd
from recipe_graph import RecipeRecommendationSystem, recommend_recipes

co = cohere.ClientV2("Q8mY5CRKzgiNqzIMjeT1Ed24tSukj0bFcn8lbtp7")


if "cohere_model" not in st.session_state:
    st.session_state["cohere_model"] = "command-r-plus-08-2024"

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_data
def load_data():
    df = pd.read_csv('recipe_details.csv')
    recommender = RecipeRecommendationSystem(df)
    return df, recommender.get_recipe_nodes()
df, recipe_nodes = load_data()

@st.cache_data
def get_structured_response(recipe_insights, preparation_steps):
    system_message = """You are an expert Chef who has been in the Culinary Industry for over 30 years.
                        I want you to structure the recipe insights into a well-structured paragraph(not too long) and also
                        provide precise steps to prepare the dish in the stipulated time period mentioned."""

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"Recipe Insights: {recipe_insights}\n\nPreparation Steps: {preparation_steps}"}
    ]
    
    response = co.chat(model='command-r-plus-08-2024', messages=messages)
    return response.message.content[0].text

def get_chatbot_response(query):
    system_message = """Give very user-friendly and precise(not too long) answers to the queries asked."""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]
    response = co.chat_stream(model=st.session_state["cohere_model"], messages=messages)
    streamed_response = ""
    for event in response:
        if event.type == "content-delta":
            streamed_response += event.delta.message.content.text
            yield event.delta.message.content.text

def food_recommendation_section():
    st.title("Personalized Food Recommendation System 🍕🍔")

    st.header("Tell us about your preferences:")
    dietary_preferences = st.radio(
        "What is your dietary preference?",
        ("Vegetarian", "Vegan", "Non-Vegetarian", "No Preference")
    )
    preferred_cuisine = st.selectbox(
        "What type of cuisine do you prefer?",
        ("Indian", "Italian", "Chinese", "Mexican", "Thai", "Japanese", "Mediterranean", "American")
    )
    time_limit = st.slider(
        "How much time can you spend cooking? (in minutes)",
        min_value=5, max_value=120, step=5
    )
    ingredients_list = [
    "agave nectar", "allspice", "almonds", "anchovy", "anise", "apple", "apricot", 
    "artichoke", "asparagus", "avocado", "bacon", "baking powder", "baking soda", 
    "bamboo shoots", "banana", "barbecue sauce", "barley", "basil", "bay leaf", 
    "bean sprouts", "beef", "beer", "beetroot", "bell pepper", "black beans", 
    "black pepper", "blackberry", "blueberry", "bok choy", "brandy", "bread crumbs", 
    "broccoli", "brown sugar", "brussels sprouts", "buckwheat", "butter", "buttermilk", 
    "cabbage", "canola oil", "cardamom", "carrot", "cashews", "cauliflower", "cayenne", 
    "celery", "cheese", "cherry", "chicken", "chickpeas", "chili powder", "chives", 
    "chocolate", "cilantro", "cinnamon", "clam", "clove", "cocoa powder", "coconut", 
    "coconut oil", "cod", "coffee", "coriander", "corn", "corn oil", "cornstarch", 
    "cottage cheese", "couscous", "crab", "cranberry", "cream", "cream cheese", 
    "cucumber", "cumin", "curry powder", "date", "dill", "duck", "eggplant", "eggs", 
    "farro", "fennel", "fenugreek", "fig", "fish sauce", "five spice", "flour", 
    "food coloring", "garam masala", "garlic", "gelatin", "ghee", "ginger", 
    "grape", "grapefruit", "green beans", "halibut", "ham", "heavy cream", 
    "hoisin sauce", "honey", "hot sauce", "kale", "ketchup", "kidney beans", 
    "kiwi", "lamb", "lasagna", "leek", "lemon", "lemongrass", "lentils", "lettuce", 
    "lima beans", "lime", "lobster", "macadamia", "mango", "maple syrup", "marjoram", 
    "mayonnaise", "milk", "mint", "molasses", "mushroom", "mussels", "mustard", 
    "nectarine", "noodles", "nutmeg", "oats", "okra", "olive oil", "onion", 
    "orange", "oregano", "oyster", "oyster sauce", "papaya", "paprika", "parsley", 
    "parsnip", "pasta", "peach", "peanut oil", "peanuts", "pear", "peas", "pecans", 
    "pepper", "pesto", "pine nuts", "pineapple", "pistachios", "plum", "pomegranate", 
    "pork", "potato", "powdered sugar", "prosciutto", "pumpkin", "quinoa", "radish", 
    "raspberry", "red pepper flakes", "red wine", "rice", "rice noodles", "rosemary", 
    "rum", "saffron", "sage", "sake", "salmon", "salsa", "sardines", "sausage", 
    "scallop", "semolina", "sesame oil", "shallot", "sherry", "shrimp", "soy sauce", 
    "spaghetti", "spinach", "squash", "sriracha", "star anise", "strawberry", 
    "sunflower oil", "sweet potato", "tabasco", "tarragon", "teriyaki sauce", 
    "thyme", "tilapia", "tomato", "tuna", "turkey", "turmeric", "turnip", 
    "vanilla extract", "veal", "vegetable oil", "vinegar", "vodka", "walnuts", 
    "watercress", "watermelon", "white pepper", "white sugar", "white wine", 
    "worcestershire sauce", "yeast", "yogurt", "zucchini"
]
    
    available_ingredients = st.multiselect(
        "Select the ingredients you have:",
        ingredients_list
    )

    if st.button("Find Recipes"):
        st.subheader("Your Choices:")
        st.write(f"Dietary Preference: **{dietary_preferences}**")
        st.write(f"Preferred Cuisine: **{preferred_cuisine}**")
        st.write(f"Time Limit: **{time_limit} minutes**")
        st.write("Available Ingredients: ", ", ".join(available_ingredients))

        user_preferences = {
            'ingredients': available_ingredients,
            'cuisine': preferred_cuisine,
            'dietary_preference': dietary_preferences,
            'available_time': time_limit
        }

        # Load recipe data
        df = pd.read_csv('recipe_details.csv')
        recommender = RecipeRecommendationSystem(df)
        recipe_nodes = recommender.get_recipe_nodes()
        recommendations = recommend_recipes(recipe_nodes, user_preferences)

        st.subheader("Recommended Recipes 🍲")
        for rec in recommendations:
            st.write(f"**{rec['recipe_name']}**")
            st.write(f"Match Score: {rec['match_score']}%")
            recipe_insights = rec['details']['recipe_details'].get('ingredients', 'No ingredients available')
            preparation_steps = rec['details']['recipe_details'].get('preparation_steps', 'No steps available')

            structured_response = get_structured_response(recipe_insights, preparation_steps)
            st.write(f"**Structured Recipe Insights & Steps:**\n{structured_response}")
            st.write("\n---")

def chatbot_section():
    st.title("Your Food Recipe Recommender Bot")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_container = st.empty()
            response_text = ""
            for streamed_text in get_chatbot_response(prompt):
                response_text += streamed_text
                response_container.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

def main():
    st.sidebar.title("Select Section")
    page = st.sidebar.radio("Choose a section:", ("Food Recommendation", "Chatbot"))
    food_recommendation_section() if page == "Food Recommendation" else chatbot_section()

if __name__ == "__main__":
    main()
