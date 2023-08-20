# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:40:17 2023

@author: 12427
"""

import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from gspread_pandas import Spread,Client

from gsheetsdb import connect

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Create a Google Authentication connection object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope=scope,creds=credentials)
spreadsheetname = "application_info"
spread = Spread(spreadsheetname,client = client)

# Check the connection


sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()
#st.write(worksheet_list)

#@st.cache()
# Get our worksheet names
def worksheet_names():
    sheet_names = []   
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)  
    return sheet_names

# Get the sheet as dataframe
def load_the_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

# Update to Sheet
def update_the_spreadsheet(spreadsheetname,df):
    col = ['company_name','position','location','status',
           'sponsorship','website']
    spread.df_to_sheet(df[col],sheet = spreadsheetname,index = False,
                       replace = True)
    st.sidebar.info('Updated to GoogleSheet')


# Check whether the sheets exists
what_sheets = worksheet_names()
#st.sidebar.write(what_sheets)
ws_choice = st.sidebar.radio('Available worksheets',what_sheets)

# Load data from worksheets
df = load_the_spreadsheet(ws_choice)

#st.dataframe(df)


delete_data = False
add_data = False
update_data = False
undo_delete_data = False

def set_to_false():
    delete_data = False
    add_data = False
    update_data = False
    undo_delete_data = False

st.title('Application Follow-up APP')
#df = pd.read_csv('application_info.csv')
df = df.astype({"location": str, "sponsorship":str})

# st.dataframe(df)

refresh_form = st.sidebar.form('refresh_form')
sort_button = refresh_form.form_submit_button('Sort')
refresh_form.form_submit_button('Refresh')

if sort_button:
    df = df.sort_values(by=['company_name'], ignore_index=True)
    sort_button = False
#ADD

st.sidebar.header('Add')
add_form = st.sidebar.form('add_form')
company_name = add_form.text_input('company_name')
position = add_form.text_input('position')
location = add_form.text_input('location')
status = add_form.radio('status', 
                            ("Unknown",
                             "Submitted",
                             "Interviewed",
                             "Pass",
                             "Fail"))
sponsorship = add_form.radio('sponsorship', 
                             ("Unknown",
                              "OPT",
                              "CPT",
                              "H1B",
                              "no sponsor"))
website = add_form.text_input('website')
add_data = add_form.form_submit_button()

if add_data:
    if len(company_name)!=0 and len(position)!=0:
        new_data = {'company_name':company_name, 
                    'position':position,
                    'location':location,
                    'status':status,
                    'sponsorship':sponsorship,
                    'website':website}
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
#        df = df.append(new_data, ignore_index = True)
        #df.to_csv('application_info.csv', index = False)
        #update_the_spreadsheet('application_info',df)
        set_to_false()
    else:
        st.sidebar.info('Need Company Name/position')
        set_to_false()

existing_company = set(df['company_name'])

#DELETE

st.sidebar.header('Delete')
delete_form = st.sidebar.form('delete_form')

delete_company = delete_form.selectbox('Company Name',
                                       existing_company)
df1 = df[df['company_name']==delete_company]
refresh = delete_form.form_submit_button('Refresh')

existing_position = list(df1['position'])
delete_position = delete_form.selectbox('Position',
                                       existing_position)
delete_data = delete_form.form_submit_button('Delete')

d1 = df[(df['company_name'] == delete_company) & 
                (df['position'] == delete_position)].index[0]

if delete_data:
    df.to_csv('backup.csv', index = False)

    df.drop(index = [d1], 
            inplace = True)
    df.reset_index(drop=True,inplace = True)
    #update_the_spreadsheet('application_info',df)
    #df.to_csv('application_info.csv', index = False)
    set_to_false()
    
undo_delete_data = delete_form.form_submit_button('Undo')
if undo_delete_data:
    df = pd.read_csv('backup.csv')
    df = df.astype({"location": str})
    #update_the_spreadsheet('application_info',df)
    #df.to_csv('application_info.csv', index = False)
    set_to_false()
    

#UPDATE

# st.sidebar.header('Update')
# update_form = st.sidebar.form('Update_form')

# update_company = update_form.selectbox('Company Name',
#                                        existing_company)
# df1 = df[df['company_name']==update_company]
# update_form.form_submit_button('Refresh')

# existing_position = list(df1['position'])
# update_position = update_form.selectbox('Position',
#                                        existing_position)

# d1 = df[(df['company_name'] == update_company) & 
#                 (df['position'] == update_position)].index[0]
# status = update_form.radio('status', 
#                             ('Pass','NP','Unknown'))

# update_data = update_form.form_submit_button('Update')

# if update_data:
#     temp = df.iloc[[d1]].copy()
#     df.at[d1,'status'] = status
#     df.to_csv('application_info.csv', index = False)
#     set_to_false()
    
edited_df = st.data_editor(
    df,
    column_config={
        "status": st.column_config.SelectboxColumn(
            "status",
            help="current status",
            width="medium",
            options=[
                "Unknown",
                "Submitted",
                "Interviewed",
                "Pass",
                "Fail"
            ],
        ),
        "sponsorship": st.column_config.SelectboxColumn(
            "sponsorship",
            help="if sponsor",
            width="medium",
            options=[
                "Unknown",
                "OPT",
                "CPT",
                "H1B",
                "no sponsor"
            ],
        ),
        "location": st.column_config.TextColumn(
            "location",
            help="edit location",
            max_chars=50,
            #validate="^st\.[a-z_]+$",
        ),
        "website": st.column_config.TextColumn(
            disabled = True 
        ),
        "company_name": st.column_config.TextColumn(
            disabled = True 
        ),
        "position": st.column_config.TextColumn(
            disabled = True 
        ),
        
    },
)

#st.write('split')
#st.dataframe(edited_df)
#update_the_spreadsheet('application_info',df)
update_the_spreadsheet('application_info',edited_df)
#edited_df.to_csv('application_info.csv', index = False)

# st.dataframe(df)
# st.write(existing_company)
# st.write("""Organizations marked with an asterisk (*) 
#          have several data science-related positions on their 
#          website; please visit the respective company's careers/jobs
#          website to see what interests you!""")



# # Create a connection object.
# credentials = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"],
#     scopes=[
#         "https://www.googleapis.com/auth/spreadsheets",
#     ],
# )
# conn = connect(credentials=credentials)

# # Perform SQL query on the Google Sheet.
# # Uses st.cache_data to only rerun when the query changes or after 10 min.
# @st.cache_resource(ttl=600)
# def run_query(query):
#     rows = conn.execute(query, headers=1)
#     rows = rows.fetchall()
#     return rows

# sheet_url = st.secrets["private_gsheets_url"]
# rows = run_query(f'SELECT * FROM "{sheet_url}"')

# # Print results.
# for row in rows:
#     st.write(f"{row.company_name} has a :{row.status}:")
    
