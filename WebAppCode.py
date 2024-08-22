import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go 
import altair as alt
from PIL import Image
from plotly.subplots import make_subplots

import pickle
with open('random_forest_model.pkl', 'rb') as file:
    model = pickle.load(file)
 
# ตัวแปรเก็บข้อมูลการเข้าสู่ระบบ (ในที่นี้ใช้เป็นค่าคงที่)
VALID_USERNAME = "123"
VALID_PASSWORD = "123"

# Set Page
st.set_page_config(
    page_title="Multipage App",
    page_icon="♥",
    layout="wide",
)

#Nevigative Bar
selected = option_menu(
        menu_title=None,
        options=["Home","Annual Report","Individual Report","Risk Calculated"], #Pages
        icons=  ["1-square-fill","2-square-fill","3-square-fill","4-square-fill"],
        default_index=0,
        orientation="horizontal"   
    )

if selected == "Home":
    col1, col2 = st.columns(2)
    with col1:
          st.image('Hospital room-cuate.png', use_column_width=True)
    with col2:
          st.header('Web Application for Health Examination')
          st.write('')
          



if selected == "Annual Report":
    username_placeholder = st.empty()
    password_placeholder = st.empty()
    username = username_placeholder.text_input("Username")
    password = password_placeholder.text_input("Password", type="password")
    login_button_placeholder = st.empty()
    if login_button_placeholder.button("Log in"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            username_placeholder.empty()
            password_placeholder.empty()
            login_button_placeholder.empty()
        
            st.session_state.is_logged_in = True
            # เปลี่ยนปุ่ม Log in เป็น Log out
            alt.themes.enable("default")


            st.title("Report of Annual Health Examinations")
            st.write(" : Report of annual health examinations is a dashboard that shows details about the health examination results of employees in the company from 2561 to 2563.")


            #------Data to USE
            df_61 = pd.read_excel("DataToStreamlit.xlsx", sheet_name="61")
            df_62 = pd.read_excel("DataToStreamlit.xlsx", sheet_name="62")
            df_63 = pd.read_excel("DataToStreamlit.xlsx", sheet_name="63")
            dfs = pd.concat([df_61, df_62, df_63], ignore_index=True)



            #-----Multi selection
            st.sidebar.markdown("<h1 style='text-align: center; font-size: 20px;'>Health Examination</h1>", unsafe_allow_html=True)
            st.sidebar.image('Online Doctor-cuate (1).png')

            CompanyCode_selection = st.sidebar.multiselect(
                    "**Select Company Code :**",
                    options=dfs["Company_Code"].unique(),
                    default=dfs["Company_Code"].unique(),
                )

            Employee_selection = st.sidebar.multiselect(
                    "**Select Type Employee :**",
                    options=dfs["TYPE_employee"].unique(),
                    default=dfs["TYPE_employee"].unique(),
                )

            Sex_selection = st.sidebar.multiselect(
                    "**Select Sex :**",
                    options=dfs["Sex"].unique(),
                    default=dfs["Sex"].unique(),
                )




            filter = dfs[(dfs["Company_Code"].isin(CompanyCode_selection)) &
                    (dfs["TYPE_employee"].isin(Employee_selection)) &
                    (dfs["Sex"].isin(Sex_selection))]



                #compute sum employee
            count_employ61 = filter[filter['Year'] == 2561]['No'].count()
            count_employ62 = filter[filter['Year'] == 2562]['No'].count()
            count_employ63 = filter[filter['Year'] == 2563]['No'].count()


            total1, total2, total3 = st.columns(3, gap="large")
            with total1:
                    st.info('Total Employee : 2561')
                    st.metric(label='Persons', value=f"{count_employ61:,.0f}")

            with total2:
                    st.info('Total Employee : 2562')
                    st.metric(label='Persons', value=f"{count_employ62:,.0f}")

            with total3:
                    st.info('Total Employee : 2563')
                    st.metric(label='Persons', value=f"{count_employ63:,.0f}")

#--------ความเสี่ยงและเบี้ยประกันของบริษัท
            col1, col2 = st.columns(2)         
            with col1:
                risk_hyper = dfs.groupby('Year')['ระดับไขมันรวม'].mean().reset_index() 
                risk_hyper['ระดับไขมันรวม'] *= 100

                risk_chart = px.line(
                    risk_hyper,
                    x='Year',
                    y='ระดับไขมันรวม',
                    markers=True,
                    hover_data=None,
                    title='The Average Risk of Employees Developing Hyperlipidemia Levels')    

                risk_chart.update_traces(hovertemplate='Year &nbsp;: %{x}<br>Average Risk of Hyperlipidemia&nbsp;: %{y} %')
                risk_chart.update_layout(title_x=0.1)
                risk_chart.update_xaxes(title='Year', tickvals=['2561', '2562', '2563'], fixedrange=True)
                risk_chart.update_yaxes(title='Risk of Hyperlipidemia (%)', range=[0.0, 100.0])
                st.plotly_chart(risk_chart, use_container_width=True)

            with col2:
                premium_risk = (6800 + (6800 * (risk_hyper['ระดับไขมันรวม'] / 100))) / (1 - 0.1 - 0.25 - 0.05)

                premium_chart = px.line(
                    x=risk_hyper['Year'],
                    y=premium_risk,
                    markers=True,
                    hover_data=None,
                    title='The Premium of Employees Developing Hyperlipidemia Levels')

                premium_chart.update_traces(hovertemplate='Year &nbsp;: %{x}<br>Premium&nbsp;: %{y} Bath')
                premium_chart.update_layout(title_x=0.15)
                premium_chart.update_xaxes(title='Year', tickvals=['2561', '2562', '2563'], fixedrange=True)
                premium_chart.update_yaxes(title='Premium (Bath)', range=[0.0, None])
                st.plotly_chart(premium_chart, use_container_width=True)




#--------The Examination Health Results
            col1, col2 = st.columns([2, 1])   
            with col2:
                    Year_selection = st.slider(             
                        "Select Year:",
                        min_value=min(dfs["Year"]),
                        max_value=max(dfs["Year"]),
                        value=(min(dfs["Year"]), max(dfs["Year"]))
                )
                    
                    filtered_data = dfs[dfs["Year"].between(*Year_selection) & (dfs["Company_Code"].isin(CompanyCode_selection))&
                                    (dfs["TYPE_employee"].isin(Employee_selection)) &
                                    (dfs["Sex"].isin(Sex_selection))]
                #-------Chart for each Examination
                    data_examination = filtered_data[['PE','BLOODPRESSURE','PULSE','BMI','CHO','TRI','HDL','LDL','FBS','UricAcid',
                                                'สรุปการทำงานของตับ', 'ALK.PHOSPHATASE', 'สรุปทำงานไต', 'AFP', 'CEA',
                                                'ผลเลือดจากรพ.', 'สรุปผลปัสสาวะ', 'ZincinBlood', 'NickelinBlood', 'ManganeseinBlood',
                                                'LeadinBlood', 'ChromiuminUrine', 'TolueneinUrine', 'AcetoneinUrine',
                                                'n-HexaneinUrine', 'StyreneinUrine', 'ThinnerinUrine', 'XyleneinUrine',
                                                'MethanolinUrine', 'MEKinUrine', 'MuscleHand', 'MuscleLeg', 'Ear', 'Eye',
                                                'ColourBlindness', 'Spiro', 'X-RAY', 'EKG', 'EST', 'ECHO', 'US']] 
                    exam_selection = st.selectbox(
                            "**Select Examination :**",
                            options=data_examination.columns)
                # ตรวจสอบการเลือก
                    if not exam_selection:
                        st.warning("Please select at least one examination.")
                    else:
                # กรองข้อมูลตามการเลือก
                        examination_filter = data_examination[exam_selection]

                    st.image('Doctors-cuate.png', use_column_width=True)

                # นับจำนวนค่าที่เท่ากับ 1 และ groupby ตาม 'Year' และหาผลรวม
            count_exam = examination_filter[examination_filter == 1].groupby(by=filtered_data['Year']).count()


            with col1:
                    st.write("   ")
                    st.write("#### The Examination Health Results") 
                    st.write(": The examination health results by the values ​​displayed in each section only consider employees who have passed each type of health examination.")
                    exam_chart = px.bar(count_exam,
                                    text=count_exam,
                                    color_discrete_sequence=['#E13838'],
                                    template='plotly_white')
                    
                    # สร้างแกน x และแกน y สำหรับกราฟแท่ง
                    exam_chart.update_xaxes(title='Year', tickvals=['2561', '2562', '2563'])
                    exam_chart.update_yaxes(title='Number of Abnormal Cases')

                    st.plotly_chart(exam_chart, use_container_width=True)




                #compute sum employee
            count_exemploy61 = examination_filter[(filter['Year'] == 2561) & ((examination_filter == 0) | (examination_filter == 1))].count()
            count_exemploy62 = examination_filter[(filter['Year'] == 2562) & ((examination_filter == 0) | (examination_filter == 1))].count()
            count_exemploy63 = examination_filter[(filter['Year'] == 2563) & ((examination_filter == 0) | (examination_filter == 1))].count()

            total1, total2, total3 = st.columns(3, gap="large")
            with total1:
                    st.info('Number of Employees : 2561')
                    st.metric(label=': Undergoing Health Examinations', value=f"{count_exemploy61:,.0f}")

            with total2:
                    st.info('Number of Employees : 2562')
                    st.metric(label=': Undergoing Health Examinations', value=f"{count_exemploy62:,.0f}")

            with total3:
                    st.info('Number of Employees : 2563')
                    st.metric(label=': Undergoing Health Examinations', value=f"{count_exemploy63:,.0f}")



                # สร้าง Pie Chart : examination          
            col1, col2, col3 = st.columns(3)

            with col1:
                    # กรองข้อมูลเพื่อเลือกเฉพาะค่า 0 และ 1 ในปี 2561
                    exam_piechart61 = examination_filter[(filter['Year'] == 2561) & ((examination_filter == 0) | (examination_filter == 1))]
                    exam_pie61 = px.pie(exam_piechart61,
                                        names=exam_piechart61,
                                        title='Percent of Abnormal Cases Examination : 2561',
                                        hole=0.65,
                                        color_discrete_sequence=['#E13838', '#0E4C8A'])

                    st.plotly_chart(exam_pie61, use_container_width=True)

            with col2:
                    # กรองข้อมูลเพื่อเลือกเฉพาะค่า 0 และ 1 ในปี 2562
                    exam_piechart62 = examination_filter[(filter['Year'] == 2562) & ((examination_filter == 0) | (examination_filter == 1))]
                    exam_pie62 = px.pie(exam_piechart62,
                                        names=exam_piechart62,
                                        title='Percent of Abnormal Cases Examination : 2562',
                                        hole=0.65,
                                        color_discrete_sequence=['#E13838', '#0E4C8A'])

                    st.plotly_chart(exam_pie62, use_container_width=True)

            with col3:
                    # กรองข้อมูลเพื่อเลือกเฉพาะค่า 0 และ 1 ในปี 2563
                    exam_piechart63 = examination_filter[(filter['Year'] == 2563) & ((examination_filter == 0) | (examination_filter == 1))]
                    exam_pie63 = px.pie(exam_piechart63,
                                        names=exam_piechart63,
                                        title='Percent of Abnormal Cases Examination : 2563',
                                        hole=0.65,
                                        color_discrete_sequence=['#E13838', '#0E4C8A'])

                    st.plotly_chart(exam_pie63, use_container_width=True)




#-----Personal Results
            st.markdown('#### Personal Health Examination Results')
            st.write(': The results of personal health examinations in the company.')

            ID_data = dfs[dfs["Year"].between(*Year_selection) & (dfs["Company_Code"].isin(CompanyCode_selection))&
                            (dfs["TYPE_employee"].isin(Employee_selection)) &
                            (dfs["Sex"].isin(Sex_selection))]

            col1, col2 = st.columns([2, 1])   
            with col1:
                    try:
                        id_selection = st.selectbox(
                            "**Search ID :**",
                            options=ID_data['ID']
                        )

                        if not id_selection:
                            st.warning("Please Search ID.")
                        else:
                            # กรองข้อมูลตามการเลือก
                            id_filter = ID_data.loc[ID_data['ID'] == id_selection]
                            drop_data = id_filter.drop(['Name', 'คำนำหน้า', 'ชื่อ', 'สกุล', 'Name_concatenate', 
                                                        'ชื่อไม่ตรง', 'Unnamed: 12', 'Unnamed: 38', 'Unnamed: 39'], axis=1)

                        st.write(drop_data)
                    except KeyError:
                        st.warning("No data available for the selected year range.")

            with col2:
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')
                    st.write('  ')    
                    st.image('Doctor-cuate.png', use_column_width=True)




#-----NCDs
            st.markdown('#### The Risk Factors that cause NCDs')
            st.write(': The results of health examinations that are risk factors that cause chronic non-communicable diseases (NCDs).')

                #-------Chart for each NCDs Examination
            data_ncds = filtered_data[['BLOODPRESSURE', 'BMI', 'CHO', 'TRI', 'HDL', 'LDL', 'FBS']]
            ncds_selection = st.selectbox(
                        "**Select NCDs Examination :**",
                        options=data_ncds.columns)

                # ตรวจสอบการเลือก
            if not ncds_selection:
                    st.warning("Please select at least one examination.")
            else:
                # กรองข้อมูลตามการเลือก
                    ncds_filter = data_ncds[ncds_selection]

                # นับจำนวนค่าที่เท่ากับ 1 และ groupby ตาม 'Year' และหาผลรวม
            count_ncds = ncds_filter[ncds_filter == 1].groupby(by=filtered_data['Year']).count()




                #compute
            percent_ncds61 = (ncds_filter[(ncds_filter == 1) & (filtered_data['Year'] == 2561)].sum() / ncds_filter[filtered_data['Year'] == 2561].count()) * 100
            percent_ncds62 = (ncds_filter[(ncds_filter == 1) & (filtered_data['Year'] == 2562)].sum() / ncds_filter[filtered_data['Year'] == 2562].count()) * 100
            percent_ncds63 = (ncds_filter[(ncds_filter == 1) & (filtered_data['Year'] == 2563)].sum() / ncds_filter[filtered_data['Year'] == 2563].count()) * 100

            total1, total2, total3 = st.columns(3, gap="large")
            with total1:
                    st.metric(label='Percent of Abnomal Case : 2561', value=f"{percent_ncds61:,.2f} %")

            with total2:
                    st.metric(label='Percent of Abnomal Case : 2562', value=f"{percent_ncds62:,.2f} %")

            with total3:
                    st.metric('Percent of Abnomal Case : 2563', value=f"{percent_ncds63:,.2f} %")



            col1, col2 = st.columns(2)   
            with col1:
                # สร้าง Bar Chart
                    ncds_chart = px.bar(count_ncds, 
                                    text=count_ncds,
                                    color_discrete_sequence=['#E13838'],
                                    template='plotly_white',
                                    title = 'Number of Abnormal Case')
                    ncds_chart.update_layout(title_x=0.25)

                    ncds_chart.update_xaxes(title='Year', tickvals=['2561', '2562', '2563'])
                    ncds_chart.update_yaxes(title='Number of Abnormal Cases')

                    st.plotly_chart(ncds_chart, use_container_width=True)


            with col2:
                    percent_ncds = ncds_filter[ncds_filter == 1].groupby(by=filtered_data['Year']).size() / ncds_filter.groupby(by=filtered_data['Year']).size() * 100

                    ncdsline_chart = px.line(
                        percent_ncds,
                        markers=True,
                        hover_data=None,
                        title='Percentage of Abnormal Case')
                    ncdsline_chart.update_layout(title_x=0.25)   

                    ncdsline_chart.update_traces(hovertemplate='Year &nbsp;: %{x}<br>Percent Abnormal &nbsp;: %{y} %')
                    ncdsline_chart.update_xaxes(title='Year', tickvals=['2561', '2562', '2563'])
                    ncdsline_chart.update_yaxes(title='Percentage of Abnormal Cases', range=[0.0, 100.0])

                    st.plotly_chart(ncdsline_chart, use_container_width=True)
            st.button("Log out")
        else:
            st.error("Invalid username or password")



if selected == "Individual Report":
    st.title("Individual Health Examinations Report")
    st.write(" : The results of individual health examinations of employees in the company")

    data61 = pd.read_csv("DataModel61.csv")
    data62 = pd.read_csv("DataModel62.csv")
    data63 = pd.read_csv("DataModel63.csv")
    datas = pd.concat([data61, data62, data63], ignore_index=True)

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        id_selection = st.selectbox("**Search ID :**",options=datas['ID'].unique())   
        id_filter = datas.loc[datas['ID'] == id_selection]
            
        Year_selection = st.selectbox("**Select Year :**",options=id_filter['Year'])
#----Data ที่ใช้แสดงผลข้อมูลผลการตรวจของพนักงาน    
        filter_data = id_filter[id_filter['Year'] == Year_selection]


    with col2:
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            age_container = st.container(border=True)
            age_value = filter_data['Age_Range'].iloc[0]
            age_container.write(f"**Age &nbsp;:**&nbsp; {age_value} &nbsp; years")

        with col2:
            sex_container = st.container(border=True)
            sex_value = filter_data['Gender'].iloc[0]
            if sex_value == 1:
                sex_text = "Male 👨🏻"
            else:
                sex_text = "Female 👩🏻"
            sex_container.write(f"**Gender &nbsp;:** &nbsp;{sex_text}")
             
        smoke_con = st.container(border=True)
        smoke_value = filter_data['Smoking'].iloc[0]
        if smoke_value == 1:
            smoke_text = "✅" 
        else:
            smoke_text = "❌"
        smoke_con.write(f"**Smoke &nbsp;:** &nbsp;{smoke_text}")

        drink_con = st.container(border=True)
        drink_value = filter_data['Drinking'].iloc[0]
        if drink_value == 1:
            drink_text = "✅" 
        else:
            drink_text = "❌"
        drink_con.write(f"**Drink &nbsp;:** &nbsp;{drink_text}")

    with col3:
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            weight_con = st.container(border=True)
            weight_value = filter_data['Weight'].iloc[0]
            weight_con.write(f"**Weight &nbsp;:**&nbsp; {weight_value} &nbsp;kg.")

            height_con = st.container(border=True)
            height_value = filter_data['Height'].iloc[0]
            height_con.write(f"**Height &nbsp;:**&nbsp; {height_value} &nbsp;cm.")

        with col2:
            bmi_con = st.container(border=True)
            bmi_value = filter_data['BMI'].astype(float)
            bmi = filter_data['BMI'].iloc[0]
            if (bmi_value <= 18.50).any():
                bmi_text = "Underweight"
                bmi_image = "1.png"
            elif (bmi_value <= 23.01).any():
                bmi_text = "Normal"
                bmi_image = "2.png"
            elif (bmi_value <= 25.00).any():
                bmi_text = "Overweight"
                bmi_image = "3.png"
            elif (bmi_value <= 30.00).any():
                bmi_text = "Obesity"
                bmi_image = "4.png"
            elif (bmi_value > 30.00).any():
                bmi_text = "Extream Obesity"
                bmi_image = "5.png"
            bmi_con.write(f"**Body Mass Index &nbsp;:**&nbsp; {bmi}")
            bmi_con.image(bmi_image)


    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.write("")

    with col2:
        st.write("#### The Risk Factors that cause Hyperlipidemia")
        st.write('<small>: The results of health examinations that are risk factors that cause Hyperlipidemia.</small>', unsafe_allow_html=True)
#------Select Box Examination Result
        exam_idData = id_filter[['TRI', 'FBS', 'SGOT', 'SGPT', 'ALK_PHOSPHATASE',
                                 'BUN', 'Creatinine', 'Uric_Acid']]
        
        exam_selectID = st.selectbox("**Select Examination :**",
                            options=exam_idData.columns)
        if not exam_selectID:
            st.warning("Please select at least one examination.")
        else:
            examID_filter = exam_idData[exam_selectID]
        
        value_exam = examID_filter
        IDexam_linechart = px.line(
                    x=id_filter['Year'],
                    y=value_exam,
                    markers=True,
                    title='Examination Result',
                    hover_data=None)  # กำหนดให้ไม่แสดงข้อมูลใน tooltip เลย

        IDexam_linechart.update_traces(hovertemplate='Year &nbsp;: %{x}<br>Examination Result&nbsp;: %{y}')
        IDexam_linechart.update_xaxes(title='Year of Health Examination', tickvals=['2561', '2562', '2563'], fixedrange=True)
        IDexam_linechart.update_yaxes(title='Examination Result', range=[0, None], automargin=True)
        IDexam_linechart.update_layout(title_x=0.4)

        st.plotly_chart(IDexam_linechart, use_container_width=True)



    with col3:
        st.write("")
        col1, col2 = st.columns([3,2])
        with col1:
            bp_con = st.container(border=True)
            bp_value = filter_data['BP'].iloc[0]
            if bp_value == 1:
                bp_text = "Normal" 
            elif bp_value == 2:
                bp_text = "Elevated"
            elif bp_value == 3:
                bp_text = "High"
            elif bp_value == 99:
                bp_text = "No Examination"   
            bp_con.write(f"**Blood Pressure &nbsp;:** &nbsp;{bp_text}")

            cd_con = st.container(border=True)
            cd_value = filter_data['CDISESERange'].iloc[0]
            if cd_value == 0:
                cd_text = "No chronic diseases" 
            elif cd_value == 1:
                cd_text = "Hypertension"
            elif cd_value == 2:
                cd_text = "Diabetes Mellitus"
            elif cd_value == 3:
                cd_text = "Dyslipidemia"
            elif cd_value == 4:
                cd_text = "More than 1 diseases"   
            elif cd_value == 5:
                cd_text = "Other diseases"    
            elif cd_value == 99:
                cd_text = "No Examination"                   
            cd_con.write(f"**Chronic Disease &nbsp;:** &nbsp;{cd_text}")

        with col2:
            blood_con = st.container(border=True)
            blood_value = filter_data['Blood_Test_Result'].iloc[0]
            if blood_value == 1:
                blood_text = "Abnormal" 
            elif blood_value == 0:
                blood_text = "Normal"
            elif blood_value == 9:
                blood_text = "No Examination"   
            blood_con.write(f"**Bloob Test &nbsp;:** &nbsp;{blood_text}")

            urine_con = st.container(border=True)
            urine_value = filter_data['Urinalysis_Result'].iloc[0]
            if urine_value == 1:
                urine_text = "Abnormal" 
            elif urine_value == 0:
                urine_text = "Normal"
            elif urine_value == 9:
                urine_text = "No Examination" 
            urine_con.write(f"**Urine Test &nbsp;:** &nbsp;{urine_text}")

#-------Predict Risk Individual            
        ind_feature = filter_data[['Gender', 'BP', 'Height', 'Weight', 'Smoking', 'Drinking', 'TRI', 'FBS', 'SGOT', 'SGPT', 'ALK_PHOSPHATASE', 'BUN', 'Creatinine', 'Uric_Acid', 'Urinalysis_Result', 'Blood_Test_Result', 'AgeRange', 'BMIRange', 'CDISESERange']]
        ind_feature.replace('-', np.nan, inplace=True)
        predicted_prob = model.predict_proba(ind_feature.values)
            
        prob_of_positive_class = predicted_prob[0][1]
            
        percent_risk = prob_of_positive_class * 100

        if percent_risk <= 25:
            image_risk = 'Normal.png'
        elif percent_risk <= 50:
            image_risk = 'Moderate.png'
        elif percent_risk <= 75:
            image_risk = 'High.png'
        else:
            image_risk = 'Critical.png'
        
        risk_con = st.container(border=True)
        risk_con.write(f"**Risk of Hyperlipidemia &nbsp;:** &nbsp;{percent_risk}&nbsp;%")
        risk_con.image(image_risk)



if selected == "Risk Calculated":

    st.markdown("<h1 style='text-align: center; font-size: 40px; font-weight: bold;'>The Risk and Premiums Assessment of Hyperlipidemia</h1>", unsafe_allow_html=True)

    my_form = st.form(key = "form1")
    
#-----กรอกข้อมูลเบื้องต้น
    Basicinformation = my_form.subheader(": Basic Information")

    Gender = my_form.selectbox("Gender", ("Male", "Female"), index = None,placeholder="Select...")
    AGE = my_form.selectbox("AGE", ("Less than 20 years", "21 - 30 years", "31 - 40 years", "41 - 50 years", "More than 50 years"),index = None,placeholder="Select...")
    Weight = my_form.number_input("Weight (kg.)")
    Height = my_form.number_input("Height (cm.)") 
    BMI = my_form.selectbox("BMI", ("Underweight", "Normal", "Overweight", "Obesity", "Extream Obesity"),index = None,placeholder="Select...")
    

#-----กรอกข้อมูลผลตรวจ
    Healthinformation = my_form.subheader(": Health Information")

    BP = my_form.selectbox("Blood Pressure : BP", ("Normal", "Elevated", "High"),index = None,placeholder="Select...") 
    Smoke = my_form.selectbox("Smoke", ("Smoke","Not Smoke"),index = None,placeholder="Select...")                   
    Drink = my_form.selectbox("Drink", ("Drink","Not Drink"),index = None,placeholder="Select...")
    PE = my_form.selectbox("Physical Examination : PE", ("No chronic diseases", "Hypertension", "Diabetes Mellitus", 
                                                            "Dyslipidemia", "More than 1 diseases", "Other diseases"), index = None, placeholder="Select...",)
    Tri = my_form.number_input("Triglycerides Level (mg/dL)")
    FBS = my_form.number_input("Fasting Blood Sugar : FBS (mg/dL)")
    UricAcid = my_form.number_input("Uric Acid mg/dL)")
    BUN = my_form.number_input("BUN (mg/dL)")
    CREATININE = my_form.number_input("Creatinine (mg/dL)")
    SGOT = my_form.number_input("SGOT (mg/dL)")
    SGPT = my_form.number_input("SGPT (mg/dL)")
    ALP = my_form.number_input("Alkaline Phosphatase : ALP (IU/L)")
    CBC = my_form.selectbox("Complete Blood Count : CBC", ("Abnormal", "Normal"),index = None,placeholder="Select...")
    UA = my_form.selectbox("Urine Analysis : UA", ("Abnormal", "Normal"),index = None,placeholder="Select...")

#ปุ่มสำหรับกดคำนวณ
    submit = my_form.form_submit_button(label = "Submit")

#----------condition input data
    def encode_sex(sex_text):
        if sex_text == "Female":
            return 0 
        else:
            return 1
    Sex_encode = encode_sex(Gender)

    def encode_age(age_text):
        if age_text == "Less than 20 years":
            return 0
        elif age_text == "21 - 30 years":
            return 1
        elif age_text == "31 - 40 years":
            return 2
        elif age_text == "41 - 50 years":
            return 3
        elif age_text == "More than 50 years":
            return 4
    AGE_encoded = encode_age(AGE)

    def encode_bmi(BMI_text):
        if BMI_text == "Underweight":
            return 1
        elif BMI_text == "Normal":
            return 2
        elif BMI_text == "Overweight":
            return 3
        elif BMI_text == "Obesity":
            return 4
        elif BMI_text == "Extream Obesity":
            return 5
    BMI_encoded = encode_bmi(BMI)

    def encode_bp(BP_text):
        if BP_text == "Normal":
            return 1
        elif BP_text == "Elevated":
            return 2
        elif BP_text == "High":
            return 3
    BP_encode = encode_bp(BP)

    def encode_pe(PE_text):
        if PE_text == "No chronic diseases":
            return 0
        elif PE_text == "Hypertension":
            return 1
        elif PE_text == "Diabetes Mellitus":
            return 2
        elif PE_text == "Dyslipidemia":
            return 3
        elif PE_text == "More than 1 diseases":
            return 4
        elif PE_text == "Other diseases":
            return 5
    PE_encode = encode_pe(PE)

    def encode_cbc(CBC_text):
        if CBC_text == "Normal":
            return 0
        else:
            return 1
    CBC_encode = encode_cbc(CBC)

    def encode_ua(UA_text):
        if UA_text == "Normal":
            return 0
        else:
            return 1
    UA_encode = encode_ua(UA)
       

#-------------เตรียมข้อมูลที่ input เข้ามาแล้วเอาไป predict model
    def feature(Gender, BP, Height, Weight, Smoke, Drink, Tri, FBS, SGOT, SGPT, ALP, BUN, CREATININE, UricAcid, UA, CBC, AGE, BMI, PE):
        Sex = encode_sex(Gender)
        Age = encode_age(AGE)
        Weight = float(Weight)
        Height = float(Height)
        BMI = encode_bmi(BMI)
        BP = encode_bp(BP)
        Smoke = Smoke if Smoke == 1 else 0
        Drink = Drink if Drink == 1 else 0
        PE = encode_pe(PE)
        TG = float(Tri)
        FBS = float(FBS)
        UricAcid = float(UricAcid)
        BUN = float(BUN)
        CREATININE = float(CREATININE)
        SGOT = float(SGOT)
        SGPT = float(SGPT)
        ALP = float(ALP)
        CBC = encode_cbc(CBC)
        UA = encode_ua(UA)

        return {'Sex': Sex, 'BP': BP, 'Height': Height, 'Weight': Weight, 'Smoke': Smoke, 'Drink': Drink,
                'TRI_TGBLOOD': TG, 'FBS_BLOOD': FBS, 'SGOT': SGOT, 'SGPT': SGPT, 'ALP': ALP,
                'BUN': BUN, 'CREATININE': CREATININE, 'URIC_ACID': UricAcid, 'UA': UA, 'CBC': CBC,
                'Age_Range': Age, 'BMI_Range': BMI, 'CDISESE_Range': PE}

    

#--------Import Model
    def dld_prediction(feature):
        global model
        if model is None:
            print("Model isn't loaded.")
            return None
        else:
            predicted_prob = model.predict_proba([list(feature.values())])
            prob_of_positive_class = predicted_prob[0][1]
            return prob_of_positive_class



    if submit:
        col1, col2, col3 = st.columns(3)
        with col2:
        # ทำนายและแสดงผล
            prediction_result = dld_prediction(feature(Gender, BP, Height, Weight, Smoke, Drink, Tri, FBS, SGOT, SGPT, ALP, BUN, CREATININE, UricAcid, UA, CBC, AGE, BMI, PE))
            probability_percentage = prediction_result * 100
            premium = (6800 + (6800 * prediction_result))/(1 - 0.1 - 0.25 - 0.05)
            if probability_percentage <= 25:
                image_risk = 'Normal.png'
            elif probability_percentage <= 50:
                image_risk = 'Moderate.png'
            elif probability_percentage <= 75:
                image_risk = 'High.png'
            else:
                image_risk = 'Critical.png'

            st.markdown("<h1 style='text-align: center; font-size: 30px;'>Risk of Hyperlipidemia</h1>", unsafe_allow_html=True)
            st.image(image_risk)
            st.markdown(f"<div style='font-size:20px; text-align:center; padding:10px; border:2px solid #DCDCDC; border-radius:5px; background-color:#DCDCDC; width:400px; margin: auto;'><span style='color:#2A2A2A; font-weight: bold;'>Premium: {premium:.2f} Bath<br></span></div>", 
                                unsafe_allow_html=True)