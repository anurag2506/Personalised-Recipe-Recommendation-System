import streamlit as st
import cohere  # type: ignore

co = cohere.ClientV2("Q8mY5CRKzgiNqzIMjeT1Ed24tSukj0bFcn8lbtp7")

if "cohere_model" not in st.session_state:
    st.session_state["cohere_model"] = "command-r-plus-08-2024"

if "messages" not in st.session_state:
    st.session_state.messages = []

def food_recommendation_section():
    st.title("Personalized Food Recommendation System 🍴")

    # Getting preferences from the user
    st.header("Tell us about your preferences:")
    dietary_preferences = st.radio(
        "What is your dietary preference?",
        ("Vegetarian", "Vegan", "Non-Vegetarian", "No Preference")
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

def get_context_based_streamed_response(query):
    system_message = """ Give very user-friendly and precise(not too long) answers to the queries asked."""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]
    # Start the Cohere streaming chat
    response = co.chat_stream(model=st.session_state["cohere_model"], messages=messages)
    streamed_response = ""
    for event in response:
        if event.type == "content-delta":
            streamed_response += event.delta.message.content.text
            yield event.delta.message.content.text

# Display the chatbot section
def chatbot_section():
    st.title("Your Food Recipe Recommender Bot")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me anything!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant's response using Cohere
        with st.chat_message("assistant"):
            response_container = st.empty()  # Placeholder for streaming
            response_text = ""
            for streamed_text in get_context_based_streamed_response(prompt):
                response_text += streamed_text
                response_container.markdown(response_text)  # Update streamed content dynamically

        # Add assistant's response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# Main function to run both sections
def main():
    # Sidebar navigation
    st.sidebar.title("Select Section")
    page = st.sidebar.radio("Choose a section:", ("Food Recommendation", "Chatbot"))

    if page == "Food Recommendation":
        food_recommendation_section()
    elif page == "Chatbot":
        chatbot_section()

if __name__ == "__main__":
    main()
