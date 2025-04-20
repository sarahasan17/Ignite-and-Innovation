import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

from xgboost import XGBClassifier

# Load dataset
df = pd.read_excel("Final_Incident_Report_With_Application_IDs.xlsx")

# Filter relevant tickets
train_df = df[(df["state"] == "Resolved") & (df["Cause"] != "Cause Undetermined")].copy()

# Combine text fields
train_df["full_text"] = (
    train_df["Short description"].fillna('') + " " +
    train_df["Description"].fillna('') + " " +
    train_df["Actions taken"].fillna('')
)

# Combine rare causes
cause_counts = train_df['Cause'].value_counts()
rare_causes = cause_counts[cause_counts < 100].index
train_df['Cause'] = train_df['Cause'].apply(lambda x: 'Other' if x in rare_causes else x)

# Extract temporal features
train_df['Opened'] = pd.to_datetime(train_df['Opened'])
train_df['Month'] = train_df['Opened'].dt.month
train_df['DayOfWeek'] = train_df['Opened'].dt.dayofweek
train_df['Hour'] = train_df['Opened'].dt.hour
train_df['isWeekend'] = train_df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
train_df['Quarter'] = train_df['Opened'].dt.quarter
train_df['TimeBucket'] = pd.cut(
    train_df['Hour'],
    bins=[-1, 6, 12, 18, 24],
    labels=['Night', 'Morning', 'Afternoon', 'Evening']
)

# Feature sets
x_text = train_df["full_text"]
x_categorical = train_df[['Priority', 'Assignment group', 'Configuration item', 'Month', 'DayOfWeek', 'Hour', 'isWeekend', 'Quarter', 'TimeBucket']]
y = train_df["Cause"]

# Train-test split
x_text_train, x_text_test, x_categorical_train, x_categorical_test, y_train, y_test = train_test_split(
    x_text, x_categorical, y, test_size=0.2, random_state=42, stratify=y
)

# Combine text and categorical into a single dataframe
x_train = x_categorical_train.copy()
x_train["text"] = x_text_train
x_test = x_categorical_test.copy()
x_test["text"] = x_text_test

# Preprocessing
numeric_features = ['Month', 'DayOfWeek', 'Hour', 'isWeekend', 'Quarter']
categorical_features = ['Priority', 'Assignment group', 'Configuration item', 'TimeBucket']

preprocessor = ColumnTransformer(transformers=[
    ('text', TfidfVectorizer(max_features=2000, stop_words='english', ngram_range=(1, 2), min_df=5, max_df=0.9), 'text'),
    ('categorical', OneHotEncoder(handle_unknown='ignore'), categorical_features),
    ('numeric', StandardScaler(), numeric_features)
])

# Pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42))
])

# Hyperparameter tuning
param_grid = {
    'classifier__n_estimators': [100, 200],
    'classifier__max_depth': [3, 5],
    'classifier__learning_rate': [0.1, 0.3]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='f1_weighted', verbose=2, n_jobs=-1)
grid_search.fit(x_train, y_train)

# Best estimator
best_model = grid_search.best_estimator_

# Predictions
y_pred = best_model.predict(x_test)

# Evaluation report
print("Classification Report:\n")
print(classification_report(y_test, y_pred))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred, labels=best_model.classes_)
plt.figure(figsize=(12, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=best_model.classes_,
            yticklabels=best_model.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.tight_layout()
plt.show()
