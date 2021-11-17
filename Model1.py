#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 00:56:16 2021

@author: yefeng
"""

import numpy as np
import seaborn as sns
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score,classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split 
import os
for dirname, _, filenames in os.walk("/Users/yefeng/Documents/DC-capstone/Cleaned data"):
    for filename in filenames:
        print(os.path.join(dirname, filename))


q1=pd.read_csv("/Users/yefeng/Documents/DC-capstone/Cleaned data/cleaned1.csv")

# plotting barplot for target
plt.figure(figsize = (10,6))
g = sns.barplot(q1['HOSPITAL'],q1['HOSPITAL'],palette = 'Set1', estimator = lambda x:len(x)/len(q1))

# model 1

# total number of data 
len(q1)


# split to train and test data


#sklearn.cross_validation in older scikit versions
q1_model = q1.dropna(axis=0, how='any')
y = q1_model['HOSPITAL']; X = q1_model.drop(['VAERS_ID', 'HOSPITAL'], axis = 1)
data_train, data_test, labels_train, labels_test = train_test_split(X, y, test_size=0.2)

# Simple logistic regression
lr = LogisticRegression(solver='newton-cg', class_weight='balanced')
lr.fit(data_train,labels_train)

predicted = lr.predict(data_test)
cf_matrix = confusion_matrix(predicted, labels_test)
print(cf_matrix)

f1_test = f1_score(predicted, labels_test)
classification_report(predicted, labels_test)
print("Accuracy:",accuracy_score(predicted, labels_test))
print('The f1 score for the testing data:', f1_test)

#Ploting the confusion matrix

ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True, fmt='.2%', cmap='Blues')

## Display the visualization of the Confusion Matrix.
plt.show()


# Random forest
#Create a Gaussian Classifier
clf=RandomForestClassifier(n_estimators=100)

#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(data_train,labels_train)

rf_pred=clf.predict(data_test)
print("Accuracy:",accuracy_score(labels_test, rf_pred))
print("The f1 score for the testing data:",f1_score(labels_test, rf_pred))
rf_cf_matrix = confusion_matrix(rf_pred, labels_test)

rfx = sns.heatmap(rf_cf_matrix/np.sum(rf_cf_matrix), annot=True, fmt='.2%', cmap='Blues')

# feature importance
feature_imp = pd.Series(clf.feature_importances_,index=data_train.columns).sort_values(ascending=False)
sns.barplot(x=feature_imp, y=feature_imp.index)

# Add labels to your graph
plt.xlabel('Feature Importance Score')
plt.ylabel('Features')
plt.title("Visualizing Important Features")
plt.legend()
plt.show()

# export for plotting
feature_imp.to_frame().reset_index().to_csv("feature_imp.csv",index= False)
