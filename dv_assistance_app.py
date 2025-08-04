# Domestic Violence AI/ML Assistance App - Improved Version

import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import hashlib
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="Safe Support Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
.crisis-banner {
    background-color: #ff4b4b;
    color: white;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    margin-bottom: 20px;
}
.quick-exit {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 999;
}
.resource-card {
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

# Crisis banner and quick exit
st.markdown("""
<div class="crisis-banner">
    🚨 <strong>CRISIS HOTLINE: 1-800-799-7233</strong> (24/7 National Domestic Violence Hotline) 🚨
</div>
""", unsafe_allow_html=True)

if st.button("🚪 Quick Exit", key="quick_exit", help="Click to quickly leave this page"):
    st.markdown('<meta http-equiv="refresh" content="0; url=https://www.weather.com">', unsafe_allow_html=True)

# Initialize session state for form clearing
if 'form_cleared' not in st.session_state:
    st.session_state.form_cleared = False

# Enhanced resource data with more realistic information
@st.cache_data
def load_resources():
    return pd.DataFrame([
        {
            "name": "Safe Haven Shelter", 
            "address": "123 Main St, New York, NY",
            "phone": "(555) 123-4567",
            "lat": 40.7128, 
            "lon": -74.0060, 
            "type": "shelter",
            "hours": "24/7",
            "website": "safehaven.org"
        },
        {
            "name": "Women's Health Center", 
            "address": "456 Oak Ave, New York, NY",
            "phone": "(555) 234-5678",
            "lat": 40.7138, 
            "lon": -74.0050, 
            "type": "health",
            "hours": "Mon-Fri 8AM-6PM",
            "website": "womenshealth.org"
        },
        {
            "name": "Food Assistance Program", 
            "address": "789 Pine St, New York, NY",
            "phone": "(555) 345-6789",
            "lat": 40.7148, 
            "lon": -74.0040, 
            "type": "food",
            "hours": "Mon-Sat 9AM-5PM",
            "website": "foodhelp.org"
        },
        {
            "name": "Legal Aid Society", 
            "address": "321 Elm St, New York, NY",
            "phone": "(555) 456-7890",
            "lat": 40.7118, 
            "lon": -74.0070, 
            "type": "legal",
            "hours": "Mon-Fri 9AM-5PM",
            "website": "legalaid.org"
        },
        {
            "name": "Crisis Counseling Center", 
            "address": "654 Maple Dr, New York, NY",
            "phone": "(555) 567-8901",
            "lat": 40.7158, 
            "lon": -74.0030, 
            "type": "counseling",
            "hours": "24/7 Hotline, Office: Mon-Fri 8AM-8PM",
            "website": "crisishelp.org"
        }
    ])

RESOURCES = load_resources()

# Enhanced ML model with better error handling and transparency
def estimate_resettlement_payment(inputs):
    """
    Estimate financial support based on needs assessment.
    This is a preliminary estimate - actual amounts depend on available funding.
    """
    try:
        base_amount = 500
        explanation = ["Base emergency support: $500"]
        
        if inputs.get("need_financial", False):
            requested = inputs.get("financial_amount", 0)
            additional = min(int(requested), 3000)
            base_amount += additional
            explanation.append(f"Additional financial need: ${additional}")
        
        if inputs.get("need_shelter", False):
            base_amount += 500
            explanation.append("Temporary housing support: $500")
        
        if inputs.get("need_food", False):
            base_amount += 300
            explanation.append("Food assistance: $300")
        
        if inputs.get("mental_health_concerns", False):
            base_amount += 400
            explanation.append("Mental health support: $400")
        
        if inputs.get("has_kids", False):
            base_amount += 500
            explanation.append("Child support services: $500")
        
        if inputs.get("unemployed", False):
            base_amount += 600
            explanation.append("Employment transition support: $600")
            
        return base_amount, explanation
    
    except Exception as e:
        st.error("Error calculating estimate. Please check your inputs.")
        return 500, ["Base emergency support: $500"]

# Improved geocoding function
@st.cache_data
def geocode_location(location_str):
    """Convert address/zip to coordinates with error handling"""
    try:
        geolocator = Nominatim(user_agent="dv_assistance_app")
        location = geolocator.geocode(location_str, timeout=10)
        if location:
            return location.latitude, location.longitude, True
        else:
            return None, None, False
    except Exception as e:
        return None, None, False

# Enhanced resource finding with better error handling
def find_nearest_resources(user_lat, user_lon, need_types, max_distance=25):
    """Find nearest resources with distance filtering and error handling"""
    if not user_lat or not user_lon:
        return []
    
    # Validate coordinates
    if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
        return []
    
    try:
        def get_distance(row):
            return geodesic((user_lat, user_lon), (row['lat'], row['lon'])).miles

        results = []
        for need in need_types:
            candidates = RESOURCES[RESOURCES['type'] == need].copy()
            if candidates.empty:
                continue
                
            candidates['distance'] = candidates.apply(get_distance, axis=1)
            candidates = candidates[candidates['distance'] <= max_distance]
            candidates = candidates.sort_values('distance')
            
            if not candidates.empty:
                results.extend(candidates.head(2).to_dict('records'))  # Top 2 per category
        
        return results
    except Exception as e:
        st.error("Error finding nearby resources. Please try again.")
        return []

# Main app interface
st.title("🛡️ Safe Support Hub")
st.markdown("*A confidential resource to help you find support and assistance*")

# Privacy notice
with st.expander("🔒 Privacy & Safety Information"):
    st.markdown("""
    **Your privacy is our priority:**
    - This form data is not permanently stored
    - Use the "Quick Exit" button if you need to leave quickly
    - Consider using a private/incognito browser window
    - Clear your browser history after use if needed
    - Location information is only used to find nearby resources
    
    **If you're in immediate danger, call 911**
    """)

# Clear form functionality
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🗑️ Clear Form"):
        st.session_state.form_cleared = True
        st.experimental_rerun()

# Form with improved validation and user experience
with st.form("victim_form", clear_on_submit=st.session_state.form_cleared):
    st.header("📋 Tell us about your situation")
    
    # Location input - safer approach
    st.subheader("📍 Location (for finding nearby resources)")
    location_input = st.text_input(
        "Enter your city, state, or zip code (e.g., 'Chicago, IL' or '60601')",
        help="We only use this to find resources near you. We don't store exact locations."
    )
    
    # Incident reporting section
    st.subheader("🚔 Police Interaction")
    reported_to_police = st.selectbox("Was the incident reported to police?", ["", "Yes", "No"])
    
    if reported_to_police == "Yes":
        police_response = st.text_area("Describe police response (optional)")
        felt_helped = st.selectbox("Did you feel helped by the police?", ["", "Yes", "No", "Somewhat"])
    else:
        police_response = ""
        felt_helped = ""
    
    # Needs assessment
    st.subheader("💰 Financial Needs")
    need_financial = st.checkbox("Do you need financial assistance?")
    
    financial_amount = 0
    financial_use = ""
    if need_financial:
        financial_amount = st.number_input(
            "Approximately how much do you need (USD)?", 
            min_value=0, 
            max_value=10000, 
            value=0,
            help="This helps us estimate potential support amounts"
        )
        financial_use = st.text_area("What would you use the funds for? (optional)")
    
    # Health and wellness
    st.subheader("🏥 Health & Wellness Needs")
    col1, col2 = st.columns(2)
    with col1:
        mental_health = st.checkbox("Mental health support needed")
        physical_health = st.checkbox("Medical care needed")
    with col2:
        need_shelter = st.checkbox("Housing/shelter needed")
        need_food = st.checkbox("Food assistance needed")
    
    # Personal situation
    st.subheader("👥 Personal Situation")
    col1, col2, col3 = st.columns(3)
    with col1:
        has_kids = st.checkbox("Caring for children")
    with col2:
        unemployed = st.checkbox("Currently unemployed")
    with col3:
        in_school = st.checkbox("Currently in school")
    
    # Submit button
    submit_btn = st.form_submit_button("🔍 Find Resources & Support", use_container_width=True)

# Process form submission
if submit_btn and location_input:
    # Show processing message
    with st.spinner("Finding resources and calculating support..."):
        # Geocode location
        user_lat, user_lon, geocode_success = geocode_location(location_input)
        
        # Compile input data
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
        
        # Calculate estimated support
        st.subheader("💵 Estimated Financial Support")
        amount, explanation = estimate_resettlement_payment(input_data)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Estimated Support", f"${amount:,}")
        with col2:
            st.success("This is a preliminary estimate based on your indicated needs.")
            with st.expander("How this was calculated"):
                for item in explanation:
                    st.write(f"• {item}")
        
        # Find and display resources
        st.subheader("📍 Nearby Resources")
        
        if geocode_success:
            # Determine needed resource types
            needs = []
            if need_shelter: needs.append("shelter")
            if mental_health or physical_health: needs.append("health")
            if need_food: needs.append("food")
            if mental_health: needs.append("counseling")
            needs.append("legal")  # Always include legal resources
            
            nearest_resources = find_nearest_resources(user_lat, user_lon, needs)
            
            if nearest_resources:
                for resource in nearest_resources:
                    st.markdown(f"""
                    <div class="resource-card">
                        <h4>🏢 {resource['name']}</h4>
                        <p><strong>Type:</strong> {resource['type'].title()}</p>
                        <p><strong>Address:</strong> {resource['address']}</p>
                        <p><strong>Phone:</strong> {resource['phone']}</p>
                        <p><strong>Hours:</strong> {resource['hours']}</p>
                        <p><strong>Distance:</strong> {resource['distance']:.1f} miles</p>
                        <p><strong>Website:</strong> <a href="https://{resource['website']}" target="_blank">{resource['website']}</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No resources found within 25 miles. Please try a different location or contact the national hotline.")
        else:
            st.error("Unable to find your location. Please check your entry and try again, or contact resources directly.")
            
        # Always show national resources
        st.subheader("🌎 National Resources")
        st.info("""
        **National Domestic Violence Hotline:** 1-800-799-7233 (24/7)
        
        **Crisis Text Line:** Text HOME to 741741
        
        **National Sexual Assault Hotline:** 1-800-656-4673
        
        **National Suicide Prevention Lifeline:** 988
        """)

elif submit_btn and not location_input:
    st.error("Please enter your location to find nearby resources.")

# Footer with additional safety information
st.markdown("---")
st.markdown("""
<small>
<strong>Safety Reminder:</strong> If you're in immediate danger, call 911. 
This tool provides estimates and resources but is not a substitute for professional help.
For technical support or to report issues with this tool, contact [support email].
</small>
""", unsafe_allow_html=True)

# Clear form state after rendering
if st.session_state.form_cleared:
    st.session_state.form_cleared = False
