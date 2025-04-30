import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_excel("C:/Users/K139221/Downloads/Copy of incident.xlsx")

# Filter resolved and known-cause tickets
train_df = df[(df["state"] == "Resolved") & (df["Cause"] != "Cause Undetermined")].copy()

# Combine textual features
train_df["full_text"] = (
    train_df["Short description"].fillna('') + " " +
    train_df["Description"].fillna('') + " " +
    train_df["Actions taken"].fillna('')
)

# Threshold for rare causes
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
train_df['TimeBucket'] = pd.cut(train_df['Hour'], bins=[-1, 6, 12, 18, 24],
                                labels=['Night', 'Morning', 'Afternoon', 'Evening'])

# Define features and target
x_text = train_df["full_text"]
x_categorical = train_df[['Priority', 'Assignment group', 'Configuration item', 'Month', 'DayOfWeek', 'Hour', 'isWeekend', 'Quarter', 'TimeBucket']]
y = train_df["Cause"]

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
x_text_train, x_text_test, x_categorical_train, x_categorical_test, y_train, y_test = train_test_split(
    x_text, x_categorical, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Combine text and categorical
x_train = x_categorical_train.copy()
x_train["text"] = x_text_train
x_test = x_categorical_test.copy()
x_test["text"] = x_text_test

# Preprocessing
preprocessor = ColumnTransformer(transformers=[
    ('text', TfidfVectorizer(max_features=1000, stop_words='english'), 'text'),
    ('categorical', OneHotEncoder(handle_unknown='ignore'),
     ['Priority', 'Assignment group', 'Configuration item', 'Month', 'DayOfWeek', 'Hour', 'isWeekend', 'Quarter', 'TimeBucket'])
])

# Define pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('clf', RandomForestClassifier(random_state=42))
])

# Grid search parameters
param_grid = {
    'clf__n_estimators': [100, 200],
    'clf__max_depth': [None, 10, 20],
    'clf__min_samples_split': [2, 5]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=3, verbose=2, n_jobs=-1)

# Fit the model
grid_search.fit(x_train, y_train)

# Predict
y_pred = grid_search.predict(x_test)

# Evaluation
print("Best Parameters:", grid_search.best_params_)
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(12, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.tight_layout()
plt.show()
