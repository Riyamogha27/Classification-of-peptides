# -*- coding: utf-8 -*-
"""Group_30.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-SOsiKsXlo2ZIB3S2WrYU-KGsoGd7hmm
"""

!pip install catboost

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from catboost import CatBoostClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, auc
import matplotlib.pyplot as plt

#  Load the training dataset
train_df = pd.read_csv('train.csv')

#  Extract peptide sequences and labels
X_train = train_df['Sequence']
y_train = train_df['Label']

#  Define a function to compute dipeptide composition features
def compute_dipeptide_composition(sequences):
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    dipeptides = [a1 + a2 for a1 in amino_acids for a2 in amino_acids]
    features = []
    for sequence in sequences:
        composition = [0] * len(dipeptides)
        for i in range(len(sequence) - 1):
            dipeptide = sequence[i:i+2]
            if dipeptide in dipeptides:
                index = dipeptides.index(dipeptide)
                composition[index] += 1
        features.append(composition)
    return np.array(features)

#  Compute dipeptide composition features for training data
X_train_feats = compute_dipeptide_composition(X_train)

#  Encode labels
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)

#  Train base models
svm_model = SVC(kernel='rbf', probability=True)  # Set probability to True for ROC AUC
svm_model.fit(X_train_feats, y_train_encoded)

rf_model = RandomForestClassifier(n_estimators=100)
rf_model.fit(X_train_feats, y_train_encoded)

catboost_model = CatBoostClassifier(iterations=1000, learning_rate=0.1, depth=6, loss_function='MultiClass')
catboost_model.fit(X_train_feats, y_train_encoded)

#  Define the meta-classifier
meta_classifier = RandomForestClassifier(n_estimators=100)

#  Stacking
base_models = [('svm', svm_model), ('rf', rf_model), ('catboost', catboost_model)]
stacking_model = StackingClassifier(estimators=base_models, final_estimator=meta_classifier)

#  Train the stacking model
stacking_model.fit(X_train_feats, y_train_encoded)

#  Load the test dataset
test_df = pd.read_csv('test.csv')

#  Extract peptide sequences from test data
X_test = test_df[' Sequence']

#  Compute dipeptide composition features for test data
X_test_feats = compute_dipeptide_composition(X_test)

#  Make predictions on the test data using the stacking model
stacking_predictions = stacking_model.predict(X_test_feats)

#  Decode labels
predicted_labels_stacking = label_encoder.inverse_transform(stacking_predictions)

#  Save predictions to a file
test_df['stacking_predicted_label'] = predicted_labels_stacking
test_df.drop(columns=[' Sequence'], inplace=True)  # Remove the 'Sequence' column
test_df.to_csv('test_predictions_stacking.csv', index=False)
print(test_df)