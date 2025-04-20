import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

from xgboost import XGBClassifier
from scipy.stats import uniform, randint

# Load dataset
df = pd.read_excel("C:/Users/K139221/Downloads/incident.xlsx")

# Filter relevant tickets
train_df = df[(df["State"] == "Resolved") & (df["Cause"] != "Cause Undetermined")].copy()

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

# Label encode target
label_encoder = LabelEncoder()
train_df['Cause_encoded'] = label_encoder.fit_transform(train_df['Cause'])

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
y = train_df["Cause_encoded"]

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

# Hyperparameter tuning with RandomizedSearchCV
param_dist = {
    'classifier__n_estimators': randint(100, 300),
    'classifier__max_depth': randint(3, 10),
    'classifier__learning_rate': uniform(0.05, 0.3),
    'classifier__subsample': uniform(0.5, 0.5),
    'classifier__colsample_bytree': uniform(0.5, 0.5),
    'classifier__gamma': uniform(0, 0.5),
    'classifier__min_child_weight': randint(1, 6)
}

random_search = RandomizedSearchCV(
    pipeline,
    param_distributions=param_dist,
    n_iter=25,
    cv=3,
    scoring='f1_weighted',
    verbose=2,
    random_state=42,
    n_jobs=-1
)

random_search.fit(x_train, y_train)
best_model = random_search.best_estimator_

# Predictions
y_pred = best_model.predict(x_test)
y_pred_labels = label_encoder.inverse_transform(y_pred)
y_test_labels = label_encoder.inverse_transform(y_test)

# Evaluation report
print("Classification Report:\n")
print(classification_report(y_test_labels, y_pred_labels))

# Confusion Matrix
cm = confusion_matrix(y_test_labels, y_pred_labels, labels=label_encoder.classes_)
plt.figure(figsize=(12, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.tight_layout()
plt.show()
