import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

df = pd.read_csv("data/spam_dataset.csv")
X = df["text"]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

pipe = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB()),
])
pipe.fit(X_train, y_train)

preds = pipe.predict(X_test)
print(f"accuracy={accuracy_score(y_test, preds):.4f}  f1={f1_score(y_test, preds, pos_label='spam'):.4f}")

joblib.dump(pipe, "data/model.joblib")
print("Saved model to data/model.joblib")
