#!/usr/bin/env python
# coding: utf-8


import numpy as np
from itertools import chain
import pandas as pd 
import datetime
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import missingno as msno
import os
for dirname, _, filenames in os.walk("/Users/yefeng/Documents/DC-capstone/VAERSDATA"):
    for filename in filenames:
        print(os.path.join(dirname, filename))



#US=pd.read_csv("/Users/yefeng/Documents/DC-capstone/United States.csv")
v11=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2020VAERSVAX.csv")
v21=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2020VAERSDATA.csv")
v31=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2020VAERSSYMPTOMS.csv")
v12=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2021VAERSVAX.csv")
v22=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2021VAERSDATA.csv")
v32=pd.read_csv("/Users/yefeng/Documents/DC-capstone/VAERSDATA/2021VAERSSYMPTOMS.csv")




df1 = v11[v11["VAX_TYPE"]=="COVID19"].merge(v21,on="VAERS_ID").merge(v31,on="VAERS_ID")
df2 = v12[v12["VAX_TYPE"]=="COVID19"].merge(v22,on="VAERS_ID").merge(v32,on="VAERS_ID")


df = pd.concat([df1, df2])
df["VAERS_ID"].nunique()

# examine missing
# msno.bar(df, figsize=(10,10), fontsize=10)


# drop columns that are irrelevant: age in month
df.drop(columns = "ER_VISIT", inplace = True)
df.drop(columns = "CAGE_MO", inplace = True)
df.drop(columns = "RPT_DATE", inplace = True)
df.drop(columns = "V_FUNDBY", inplace = True)

# for all columns in y_col, the values are either "Y" or NaN otherwise -> replace by 1 and 0
y_cols = ["ER_ED_VISIT", "DIED", "L_THREAT", "HOSPITAL", "X_STAY", "DISABLE", "BIRTH_DEFECT", "OFC_VISIT"]

for col in y_cols:
    df[col] = np.where(df[col] == "Y", 1, 0)


# Replacing NaN value with 0 makes sense for counting of days being hospitalized
df["HOSPDAYS"].replace(np.nan, 0, inplace=True)

# Manipulate onset data variable
# Note: some of the VAX_DATE are not correct, year < 2000
# for now, eliminate VAX_DATA that are not correct
df['VAX_DATE'] = pd.to_datetime(df['VAX_DATE'])
df['ONSET_DATE'] = pd.to_datetime(df['ONSET_DATE'])
df['ONSET_DATE'] - df['VAX_DATE']

dfc = df[df['VAX_DATE'] > '2020-1-1']

# dfc["onset"] = dfc['ONSET_DATE'] - dfc['VAX_DATE']
# two are the same dfc[["onset","NUMDAYS"]]


# The first question would be can we use symptons to predict hospitalize?
# Can we identify high risk symptoms?

# Transform the symptoms dataset so that there is only one column for the symptoms

# Each entry can report 5 symptoms. so convert it to long data format for analysis
df_symptoms = pd.melt(dfc, id_vars=['VAERS_ID'], value_vars=['SYMPTOM1', 'SYMPTOM2', 'SYMPTOM3', 'SYMPTOM4', 'SYMPTOM5'], var_name='NUMBER', value_name='SYMPTOM')
df_symptoms.dropna(subset=['SYMPTOM'], inplace=True)
df_long = dfc.merge(df_symptoms, on="VAERS_ID")
df_long.columns

# export for plotting
df_long[['VAERS_ID', 'VAX_MANU', 'VAX_LOT', 'VAX_DOSE_SERIES', 'DIED', 'L_THREAT', 'HOSPITAL', 'NUMBER', 'SYMPTOM']].to_csv("long_symptoms.csv",index = False)

Counter(df_long['SYMPTOM']).most_common(50)
sym_coumt = Counter(df_long['SYMPTOM'])
# sym_coumt.dim

y = [count for tag, count in Counter(df_long['SYMPTOM']).most_common(20)]
x = [tag for tag, count in Counter(df_long['SYMPTOM']).most_common(20)]

plt.bar(x, y, color='crimson')
plt.title("Term frequencies in COVID-19 adverse symptoms")
plt.ylabel("Frequency (log scale)")
plt.yscale('log') # optionally set a log scale for the y-axis
plt.xticks(rotation=90)

# observation: most common symptoms are 'mild' symtoms
# However, it is more informative to see if symptoms are server or not
# It would make sense to category symptoms based on severity
# The categoration requires medical information
# For now, let's just seperate as 


# The second question is to see if we can use patient information to predict hospitalize

# replace strings
# for the column "HISTORY", some of the entries are "None" or "No" (as string) -> change to NaN
df["HISTORY"].replace(["None", "none", "unknown", "unsure", "Unknown", "no", 
                                "Unsure", "No", "NONE", "UNKNOWN", "N/a", "None known",
                               "None reported", "none reported", "None stated/Denied", 
                                "none known", "Medical History/Concurrent Conditions: No adverse event (No reported medical history.)",
                                "Comments: no medical history information was reported."
                                "Medical History/Concurrent Conditions: No adverse event (No reported medical history)", "None disclosed"
                               ], np.nan, inplace=True)

# for the column "CUR_ILL", some of the entries are "None" or "No" (as string) -> change to NaN
df["CUR_ILL"].replace(
    ["None", "No", "NONE", "unknown", "Unknown", "none", "no", "None known", "none known", 
     "None reported", "none reported", "UNKNOWN", "N/a", "None stated/Denied",
    "No other illness prior to vaccination or within the month prior", "NKDA", 
     "Individual was healthy prior to vaccination.", "None.", "UNK", "As noted above", "unsure", 
     "See item 12", "no acute illnesses", "No symptoms after COVID vaccinations"], 
    np.nan, inplace=True)
df["CUR_ILL"].replace("Covid 19", "COVID_19", inplace=True)

# for the column "ALLERGIES", some of the entries are "None" or "No" (as string) -> change to NaN
df["ALLERGIES"].replace(
    ["None", "none", "NKDA", "NKA", "No known allergies", "unknown", 
     "No", "Unknown", "no", "NONE", "No Known Allergies", "no known allergies",
    "nka", "None known", "NKA to medications", "No known allergies to drugs or food"], np.nan, inplace=True)

# for the column "OTHER MEDS", some of the entries are "None" or "No" (as string) -> change to NaN
df["OTHER_MEDS"].replace(["None", "none", "unknown", "Unknown", "no", "NONE", "UNKNOWN", "No"]
                                 , np.nan, inplace=True)

# examining the history, other meds, and allergy column for patient info
# other meds
# temp_res = []; temp_remove = dfc['OTHER_MEDS'].values
# [temp_res.append(x.replace(";",",").split(',')) for x in temp_remove if isinstance(x, str)]
# temp_res = list(chain.from_iterable(temp_res))
# med_res = []; 
# [med_res.append(x.strip().upper()) for x in set(temp_res)]; del temp_res


# count_med = Counter(med_res)
# count_med.most_common(20)


# y = [count for tag, count in count_med.most_common(20)]
# x = [tag for tag, count in count_med.most_common(20)]

# plt.bar(x, y, color='crimson')
# plt.title("Term frequencies in Other Medicine")
# plt.ylabel("Frequency (log scale)")
# plt.yscale('log') # optionally set a log scale for the y-axis
# plt.xticks(rotation=90)

# # history
# temp_res = []; temp_remove = dfc['HISTORY'].values
# [temp_res.append(x.replace(";",",").split(',')) for x in temp_remove if isinstance(x, str)]
# temp_res = list(chain.from_iterable(temp_res))
# his_res = []; 
# [his_res.append(x.strip().upper()) for x in set(temp_res)]; del temp_res

# count_his = Counter(his_res)
# count_his.most_common(50)

# y = [count for tag, count in count_his.most_common(20)]
# x = [tag for tag, count in count_his.most_common(20)]

# plt.bar(x, y, color='crimson')
# plt.title("Term frequencies in Chronic or long-standing health conditions")
# plt.ylabel("Frequency (log scale)")
# plt.yscale('log') # optionally set a log scale for the y-axis
# plt.xticks(rotation=90)

# # current illnesses
# temp_res = []; temp_remove = dfc['CUR_ILL'].values
# [temp_res.append(x.replace(";",",").split(',')) for x in temp_remove if isinstance(x, str)]
# temp_res = list(chain.from_iterable(temp_res))
# ill_res = []; 
# [ill_res.append(x.strip().upper()) for x in set(temp_res)]; del temp_res

# count_ill = Counter(ill_res)
# count_ill.most_common(50)

# y = [count for tag, count in count_ill.most_common(20)]
# x = [tag for tag, count in count_ill.most_common(20)]

# plt.bar(x, y, color='crimson')
# plt.title("Term frequencies in Illnesses at time of vaccination")
# plt.ylabel("Frequency (log scale)")
# plt.yscale('log') # optionally set a log scale for the y-axis
# plt.xticks(rotation=90)

# observation: 
# the patient info are manually filled in, there are many discrepancies of how to report the information
# Many reported none as NA,N/A, None....with many of different ways
# There are also many different seperaters used for reporting multiple entries for information
# Those complexity requires advanced text processing, and current examination will be limit to fewer conditions
# The selection of condition will be made by combining info from data and info from public media press

# CDC risk assessmemt suggested following considerations can be used to help individuals with a precaution to vaccination:
# risk of exposure to covid
# age, underlying medical conditions
# history of immediate allergic reaction to other vaccines


# combined with data, the following features will be considered include in the prediction of adverse event
# History: allergy to covid
# History: diabetes
# History: high blood pressure
# History: High cholesterol
# History: Heart disease
# History: Asthma
# History: Anxiety
# History: Depression
# History: Cancer
# History: Arthritis
# Covid Positive
# Allergic history
# Taking other medicine

# patient info include: 
q1 = dfc[['VAERS_ID','VAX_MANU', 'VAX_DOSE_SERIES', 'AGE_YRS', 'SEX', 'HOSPITAL', 'OTHER_MEDS','CUR_ILL', 'HISTORY','ALLERGIES']]


q1['History-Allergy'] = q1['HISTORY'].str.contains("allergy|Allergy", na=False, case=False)*1; print(sum(q1['History-Allergy']))
q1['History-Diabetes'] = q1['HISTORY'].str.contains("diabetes|Diabetes", na=False, case=False)*1; print(sum(q1['History-Diabetes']))
q1['History-HD'] = q1['HISTORY'].str.contains("heart", na=False, case=False)*1; print(sum(q1['History-HD']))
q1['History-HBP'] = q1['HISTORY'].str.contains("hypertension|high blood", na=False, case=False)*1; print(sum(q1['History-HBP']))
q1['History-HC'] = q1['HISTORY'].str.contains("High cholesterol", na=False, case=False)*1; print(sum(q1['History-HC']))
q1['History-Asthma'] = q1['HISTORY'].str.contains("Asthma", na=False, case=False)*1; print(sum(q1['History-Asthma']))
q1['History-Anxiety'] = q1['HISTORY'].str.contains("Anxiety", na=False, case=False)*1; print(sum(q1['History-Anxiety']))
q1['History-Depression'] = q1['HISTORY'].str.contains("Depression", na=False, case=False)*1; print(sum(q1['History-Depression']))
q1['History-Cancer'] = q1['HISTORY'].str.contains("Cancer", na=False, case=False)*1; print(sum(q1['History-Cancer']))
q1['History-CP'] = q1['HISTORY'].str.contains("covid positive", na=False, case=False)*1; print(sum(q1['History-CP']))
q1['History-Arthritis'] = q1['HISTORY'].str.contains("Arthritis", na=False, case=False)*1; print(sum(q1['History-Arthritis']))


q1[['CUR_ILL', 'ALLERGIES','OTHER_MEDS']] = np.where(q1[['CUR_ILL', 'ALLERGIES','OTHER_MEDS']].isnull(), 0, 1)

q1 = pd.concat([q1, pd.get_dummies(q1['SEX'])], axis=1)
q1 = pd.concat([q1, pd.get_dummies(q1['VAX_MANU'])], axis=1)
q1 = pd.concat([q1, pd.get_dummies(q1['VAX_DOSE_SERIES'])], axis=1)

q1 = q1[['VAERS_ID','HOSPITAL','AGE_YRS','OTHER_MEDS','CUR_ILL','ALLERGIES','History-Allergy','History-Diabetes','History-HD','History-HBP','History-HC','History-Asthma','History-Anxiety','History-Depression','History-Cancer','History-CP','History-Arthritis','F','M','JANSSEN','MODERNA','PFIZER\BIONTECH','1','2','3']]
q1.to_csv('cleaned1.csv',index=False)
