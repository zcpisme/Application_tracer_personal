# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 16:40:17 2023

@author: 12427
"""

import pandas as pd
import streamlit as st


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
df = pd.read_csv('application_info.csv')
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
        df = df.append(new_data, ignore_index = True)
        df.to_csv('application_info.csv', index = False)
        set_to_false()
    else:
        st.write('Need Company Name/position')
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
    df.to_csv('application_info.csv', index = False)
    set_to_false()
    
undo_delete_data = delete_form.form_submit_button('Undo')
if undo_delete_data:
    df = pd.read_csv('backup.csv')
    df = df.astype({"location": str})
    df.to_csv('application_info.csv', index = False)
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
            disabled = False 
        ),
        "company_name": st.column_config.TextColumn(
            disabled = True 
        ),
        "position": st.column_config.TextColumn(
            disabled = True 
        ),
        
    },
)

edited_df.to_csv('application_info.csv', index = False)

# st.dataframe(df)
# st.write(existing_company)
st.write("Organizations marked with an asterisk (*) have several data science-related positions on their website; please visit the respective company's careers/jobs website to see what interests you!")