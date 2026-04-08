import streamlit as st
import joblib
import warnings
warnings.filterwarnings("ignore")

st.header("Customer Churn Prediction")

rec = st.slider(
    label="Recency",
    min_value=0,
    max_value=10,
    step=1,
    key="Recency"
)

fre = st.slider(
    label="Frequency",
    min_value=0,
    max_value=10,
    step=1,
    key="Frequency"
)

mon = st.slider(
    label="Monetry",
    min_value=0,
    max_value=10,
    step=1,
    key="Monetry"
)

city = {
    'Lahore': 3.0,
    'Karachi': 2.0,
    'Rawalpindi': 6.0,
    'Multan': 4.0,
    'Islamabad': 1.0,
    'Peshawar': 5.0,
    'Faisalabad': 0.0
}

list_city = []

for i, j in city.items():
    list_city.append(i)

choose = st.selectbox(label="City", key="City", options=list_city, )

pre = joblib.load("Customer_Churn_prediction.pkl")

st.subheader("Will Customer Buy Again ?")
ent = st.button(label="Enter")

if ent:
    if rec >= 0 and rec <=2:
        text = "No"
        st.write(f'<p style="font-size: 30px">{text}</p>', unsafe_allow_html=True)
    
    else:
        prediction = pre.predict([[rec, fre, mon, city[choose]]])
        # st.write(list(prediction)[0])
        prediction = list(prediction)[0]
        st.write(f'<p style="font-size: 30px">{prediction}</p>', unsafe_allow_html=True)