import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the BASE_URL from environment variables
base_url = os.getenv("BASE_URL", "http://localhost:8000")

# Set page configuration
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Add a title and description
st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
    }
    .title {
        font-size: 30px;
        font-weight: bold;
        color: #4CAF50;
    }
    .subtitle {
        font-size: 16px;
        color: #555;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #777;
        margin-top: 50px;
    }
    </style>
    <div class="main">
        <h1 class="title">📊 Customer Churn Prediction</h1>
        <p class="subtitle">Predict customer churn probability based on their details.<br>
        Fill out the form below to check if a customer is likely to churn.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch metadata from FastAPI
def fetch_entities(endpoint):
    try:
        result = requests.get(f"{base_url}/api/entities/{endpoint}")
        if result.status_code == 200:
            return result.json()
        else:
            st.error(f"❌ Error: Could not fetch {endpoint} entities. Please check the API service.")
            return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

geography_entities = fetch_entities("geography")
gender_entities = fetch_entities("gender")

# User Inputs
with st.form("user_input_form"):
    st.write("### Customer Details")

    CreditScore = st.number_input("📊 Credit Score:", min_value=300, max_value=900, value=650, step=10)

    # Geography Input
    if geography_entities:
        geography_options = [item['value'] for item in geography_entities['geography']]
        selected_geography = st.selectbox("🌍 Geography:", geography_options)

        # One-hot encoding for geography
        Geography_France, Geography_Germany, Geography_Spain = 0, 0, 0
        if selected_geography == "France":
            Geography_France = 1
        elif selected_geography == "Germany":
            Geography_Germany = 1
        elif selected_geography == "Spain":
            Geography_Spain = 1

    # Gender Input
    if gender_entities:
        gender_options = [item['label'] for item in gender_entities['gender']]
        selected_gender = st.radio("👤 Gender:", gender_options, horizontal=True)
        Gender = next(item['value'] for item in gender_entities['gender'] if item['label'] == selected_gender)

    Age = st.number_input("🎂 Age:", min_value=18, max_value=100, value=35, step=1)
    Tenure = st.slider("📅 Tenure (Years):", min_value=0, max_value=10, value=5, step=1)
    Balance = st.number_input("💰 Balance:", min_value=0.0, value=50000.0, step=1000.0)
    NumOfProducts = st.slider("🛒 Number of Products:", min_value=1, max_value=4, value=1, step=1)
    HasCrCard = st.radio("💳 Has Credit Card?", ["Yes", "No"], horizontal=True)
    IsActiveMember = st.radio("🏆 Active Member?", ["Yes", "No"], horizontal=True)
    EstimatedSalary = st.number_input("💵 Estimated Salary:", min_value=0.0, value=60000.0, step=5000.0)

    # Convert Yes/No to 1/0
    HasCrCard = 1 if HasCrCard == "Yes" else 0
    IsActiveMember = 1 if IsActiveMember == "Yes" else 0

    # Submit button
    submitted = st.form_submit_button("Predict 🚀")

if submitted:
    # Prepare input data
    data = {
        "CreditScore": CreditScore,
        "Geography_France": Geography_France,
        "Geography_Germany": Geography_Germany,
        "Geography_Spain": Geography_Spain,
        "Gender": Gender,
        "Age": Age,
        "Tenure": Tenure,
        "Balance": Balance,
        "NumOfProducts": NumOfProducts,
        "HasCrCard": HasCrCard,
        "IsActiveMember": IsActiveMember,
        "EstimatedSalary": EstimatedSalary
    }

    # Make API request
    api_url = f"{base_url}/api/predict"
    with st.spinner("Fetching prediction..."):
        response = requests.post(api_url, json=data)

    # Display the prediction result
    if response.status_code == 200:
        prediction = response.json()["churn_prediction"]
        if prediction == 1:
            st.error("⚠️ This customer is **likely to churn**.")
        else:
            st.success("✅ This customer is **not likely to churn**.")
        st.balloons()
    else:
        st.error("❌ Error: Could not fetch prediction. Please check the API services.")

    # Footer
    st.markdown(
        """
        <div class="footer">
            Made with ❤️ using Streamlit.
        </div>
        """,
        unsafe_allow_html=True,
    )
