
# Domestic Violence AI/ML Assistance App

import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.linear_model import LinearRegression
import json

# Mock resource data (normally would query a real database or API)
RESOURCES = pd.DataFrame([
    {"name": "Safe Haven Shelter", "lat": 40.7128, "lon": -74.0060, "type": "shelter"},
    {"name": "Women’s Health Center", "lat": 40.7138, "lon": -74.0050, "type": "health"},
    {"name": "Food Assistance Program", "lat": 40.7148, "lon": -74.0040, "type": "food"},
])

# Placeholder ML model to determine payment amount
def estimate_resettlement_payment(inputs):
    base_amount = 500
    if inputs["need_financial"]:
        base_amount += min(int(inputs["financial_amount"] or 0), 3000)
    if inputs["need_shelter"]:
        base_amount += 500
    if inputs["need_food"]:
        base_amount += 300
    if inputs["mental_health_concerns"]:
        base_amount += 400
    if inputs["has_kids"]:
        base_amount += 500
    if inputs["unemployed"]:
        base_amount += 600
    return base_amount

# Find nearest resources
def find_nearest_resources(user_lat, user_lon, need_types):
    def get_distance(row):
        return geodesic((user_lat, user_lon), (row['lat'], row['lon'])).miles

    results = []
    for need in need_types:
        candidates = RESOURCES[RESOURCES['type'] == need].copy()
        candidates['distance'] = candidates.apply(get_distance, axis=1)
        candidates.sort_values('distance', inplace=True)
        if not candidates.empty:
            results.append(candidates.iloc[0])
    return results

# Streamlit UI
st.title("Domestic Violence Assistance AI App")

with st.form("victim_form"):
    st.header("Tell us about your situation")
    user_lat = st.number_input("Your Latitude", format="%f")
    user_lon = st.number_input("Your Longitude", format="%f")

    reported_to_police = st.selectbox("Was the incident reported to police?", ["Yes", "No"])
    police_response = st.text_area("Describe police response")
    felt_helped = st.selectbox("Did you feel helped by the police?", ["Yes", "No"])

    need_financial = st.checkbox("Do you need financial help?")
    financial_amount = st.text_input("How much do you need (USD)?", "")
    financial_use = st.text_area("What do you need the funds for?")

    mental_health = st.checkbox("Do you have mental health concerns?")
    physical_health = st.checkbox("Do you have other health concerns?")
    need_shelter = st.checkbox("Do you need shelter or housing?")
    need_food = st.checkbox("Do you need food support?")

    has_kids = st.checkbox("Do you have kids with you?")
    unemployed = st.checkbox("Are you currently unemployed?")
    in_school = st.checkbox("Are you currently in school?")

    submit_btn = st.form_submit_button("Submit")

if submit_btn:
    input_data = {
        "reported_to_police": reported_to_police,
        "police_response": police_response,
        "felt_helped": felt_helped,
        "need_financial": need_financial,
        "financial_amount": financial_amount,
        "financial_use": financial_use,
        "mental_health_concerns": mental_health,
        "physical_health_concerns": physical_health,
        "need_shelter": need_shelter,
        "need_food": need_food,
        "has_kids": has_kids,
        "unemployed": unemployed,
        "in_school": in_school,
    }

    st.subheader("Estimated Resettlement Support")
    amount = estimate_resettlement_payment(input_data)
    st.success(f"You may be eligible to receive up to ${amount} in financial support.")

    st.subheader("Suggested Local Resources")
    needs = []
    if need_shelter: needs.append("shelter")
    if mental_health or physical_health: needs.append("health")
    if need_food: needs.append("food")

    nearest_resources = find_nearest_resources(user_lat, user_lon, needs)
    for res in nearest_resources:
        st.write(f"**{res['name']}** - {res['type'].capitalize()} ({res['distance']:.1f} miles away)")
