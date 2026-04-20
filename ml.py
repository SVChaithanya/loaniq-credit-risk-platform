import pandas as pd
import joblib
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score



df = pd.read_csv(r"C:\Users\surya\ML_Project\loan.csv")

df["fico_mean"] = (df["fico_range_low"] + df["fico_range_high"]) / 2

bad_status = [
    "Charged Off",
    "Default",
    "Late (31-120 days)",
    "Late (16-30 days)",
    "Does not meet the credit policy. Status:Charged Off"
]

good_status = [
    "Fully Paid",
    "Current",
    "In Grace Period",
    "Does not meet the credit policy. Status:Fully Paid"
]

df = df[df["loan_status"].isin(bad_status + good_status)]
df["target"] = df["loan_status"].apply(lambda x: 1 if x in bad_status else 0)


FEATURES = [
    "loan_amnt",
    "annual_inc",
    "dti",
    "fico_mean",
    "int_rate",
    "term",
    "grade",
    "purpose"
]

X = df[FEATURES]
y = df["target"]


numeric_features = ["loan_amnt", "annual_inc", "dti", "fico_mean", "int_rate"]
categorical_features = ["term", "grade", "purpose"]

preprocessor = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), numeric_features),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]), categorical_features)
])

model = lgb.LGBMClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    class_weight="balanced",
    random_state=42
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

pipeline.fit(X_train, y_train)

roc = roc_auc_score(y_test, pipeline.predict_proba(X_test)[:, 1])
print("ROC-AUC:", roc)

joblib.dump(pipeline, "model.pkl")
joblib.dump(FEATURES, "features.pkl")

print(" Model saved correctly")
