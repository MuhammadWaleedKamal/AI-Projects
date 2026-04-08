import pickle, streamlit as st, json, warnings
from streamlit_lottie import st_lottie

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Pakistan Houses Price Prediction",
    layout="wide",
)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.header("Predicting House Prices in Pakistan", divider="orange")
    st.write(
"""<h4>Description:<h4/>

<p style="font-size:17px;">This project focuses on building a predictive model to estimate house prices in Pakistan using historical real estate data. The goal is to identify key factors that influence property prices such as location, area (sq. ft.), number of bedrooms and bathrooms etc. By applying machine learning techniques, the project aims to provide accurate price predictions that can help buyers, sellers, and investors make informed real estate decisions.<p/>

<p style="font-size:17px;">The workflow involves data collection, cleaning, exploratory data analysis (EDA), feature engineering, and training models such as Random Forest (You can see on Github). The performance of different models is compared to determine the best approach for prediction.
<p/>""", unsafe_allow_html=True)

with open("animation.json", "r") as f:
    lottie_animation = json.load(f)

with col2:  
    st_lottie(
        lottie_animation,
        speed=1,
        reverse=False,
        loop=True,
        quality="low",
        height=500,
        width=None,
        key="wow",
    )

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    bed = st.number_input("Bedrooms", min_value=1, max_value=6)
    
with col2:
    bath = st.number_input("Bathrooms", min_value=1, max_value=7)
    
with col3:
    area = st.text_input("Area sq-ft", placeholder="1000")



if area.isnumeric():
    area = int(area)

elif "." in area:
    new_area = area.split(sep=".")

    if len(new_area) == 2:
        if int(new_area[1][0]) >= 5:
            area = int(new_area[0]) + 1
    
        else: 
            area = int(new_area[0])
    
    else:
        st.error('Invalid Number')
        area = 0
        

with open("location.json") as f:
    city = json.load(f)

city_list = []
for key, value in city.items():
    city_list.append(key)
    
    
select_city = st.selectbox("City", options=city_list, placeholder="Karachi")
select_location = st.selectbox("Location", options=city[select_city], placeholder="Karachi")

with open("city_location.json") as f:
    city_location_data = json.load(f)
    
city_dict = city_location_data["city"][select_city]
location_dict = city_location_data["location"][select_location]

with open("MyLinearModel", "rb") as f:
    load_model = pickle.load(f)

if st.button("Predict"):
    if bed and bath and area:
        pred = load_model.predict([[city_dict, location_dict, area, bath, bed]])
        
        st.write(f"<p style='font-size: 25px;'>The Price is {round(pred[0], ndigits=1)}<p/>", unsafe_allow_html=True)


