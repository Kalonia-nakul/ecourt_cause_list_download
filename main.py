import streamlit as st
import requests
import json
import bs4
import datetime


def get_state(base_url , session ):
    response = session.get(f"{base_url}?p=cause_list/")
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    state = soup.find(id = "sess_state_code")
    options = state.find_all("option")
    all_state = {}
    for option in options:
        all_state[option.text] = option['value']
    return all_state



def get_district(  base_url , session , payload ):
    response = session.post(f"{base_url}?p=casestatus/fillDistrict" , data=payload)
    dist = bs4.BeautifulSoup(response.json()['dist_list'], "html.parser")
    all_district = {}
    for option in dist.find_all('option'):
        all_district[option.text] = option['value']
    return all_district , response.json()['app_token']



def get_complex(base_url , session , payload ):
    response = session.post(f"{base_url}?p=casestatus/fillcomplex" , data=payload)
    complex = bs4.BeautifulSoup(response.json()['complex_list'], "html.parser")
    all_complex = {}
    for option in complex.find_all('option'):
        all_complex[option.text] = option['value']
    return all_complex , response.json()['app_token']


def get_causelist(base_url , session , payload ):
    response = session.post(f"{base_url}?p=cause_list/fillCauseList" , data=payload)
    cause = bs4.BeautifulSoup(response.json()['cause_list'], "html.parser")
    all_cause = {}
    for option in cause.find_all('option'):
        all_cause[option.text] = option['value']
    return all_cause , response.json()['app_token']



def set_data(base_url , session, payload ):
    response = session.post(f"{base_url}?p=casestatus/set_data" , data=payload)
    return response.json()['app_token']

def get_html(base_url , session , payload ):
    response = session.post(f"{base_url}?p=cause_list/submitCauseList" , data=payload)
    try :
        with open(f'{payload['court_name_txt']}.html', 'w') as file:
            file.write(response.json()['case_data'])
    except KeyError:
        st.error("Causelist not found...")


def main():

    #initializing main variables
    session = requests.Session()
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    payload = {
        'ajax_req' : 'true'
    }

    # getting all state
    all_state = get_state(base_url , session)

    # heading and selecting state
    st.title("Ecause list downloader...")
    selected_state = st.selectbox("Select State", list(all_state.keys()))
    payload['state_code'] = all_state[selected_state]


    # getting all district in selected state
    all_district , app_token = get_district(  base_url , session , payload )


    # selecting district
    selected_district = st.selectbox("Select District", list(all_district.keys()))
    payload['dist_code'] = all_district[selected_district]
    payload['app_token'] = app_token


    #getting all complex in selected district
    all_complex , app_token = get_complex(base_url , session ,  payload )

    #selecting complex
    selected_complex = st.selectbox("Select Complex", list(all_complex.keys()))
    payload['complex_code'] = all_complex[selected_complex]
    payload['app_token'] = app_token



    #set data
    app_token  = set_data(base_url , session, payload)
    payload['app_token'] = app_token
    try :
        payload['court_complex_code'] = payload['complex_code'].split('@')[0]
        payload['est_code'] = payload['complex_code'].split('@')[1]
    except IndexError:
        print("fill court complex....")
    del payload['complex_code']




    #getting all cause list name
    all_cause , app_token = get_causelist(base_url , session, payload)


    #selecting a cause list
    selected_cause = st.selectbox("Select Cause", list(all_cause.keys()))
    payload['app_token'] = app_token
    payload['court_name_txt'] = selected_cause
    payload['CL_court_no'] = all_cause[selected_cause]

    #set date
    selected_date = st.date_input("Select Date", datetime.date.today())
    payload['causelist_date'] = selected_date.strftime("%d-%m-%Y")


    #set criminal or civil
    choice = {'criminal' : 'cri' , 'civil' : 'civ'}
    selected_choice = st.selectbox("Select Choice", list(choice.keys()))
    payload['cicri'] = choice[selected_choice]


    x = st.button("Download Cause")
    if x :
        get_html(base_url , session , payload )
        st.success("Download Complete...")


main()

