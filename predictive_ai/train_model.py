
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, accuracy_score

df = pd.read_csv("reading_features.csv")

features = [
    "avg_sentence_length",
    "avg_word_length",
    "long_word_ratio",
    "unique_word_ratio"
]

# Temporary readability-based labels.
# These are heuristics, NOT independently verified difficulty labels.
def assign_difficulty(row):
    score = (
        row["avg_sentence_length"] * 0.4
        + row["avg_word_length"] * 3
        + row["long_word_ratio"] * 20
    )

    if score < 22:
        return "Easy"
    elif score < 30:
        return "Medium"
    return "Hard"

df["difficulty"] = df.apply(assign_difficulty, axis=1)

print("Difficulty distribution:")
print(df["difficulty"].value_counts())

X = df[features]
y = df["difficulty"]

# Split by book so pages from the same book
# don't appear in both training and testing.
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=df["book"])
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nModel accuracy:", accuracy_score(y_test, predictions))
print("\nClassification report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

joblib.dump(
    {"model": model, "features": features},
    "reading_difficulty_model.joblib"
)

print("\nModel saved successfully!")
