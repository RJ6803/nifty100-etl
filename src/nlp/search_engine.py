import sqlite3
import pandas as pd
import re

# ==========================================
# CONFIGURATION
# ==========================================

DATABASE = "data/nifty100.db"

# ==========================================
# LOAD SEARCH INDEX
# ==========================================

conn = sqlite3.connect(DATABASE)

nlp_index = pd.read_sql(
    "SELECT * FROM nlp_search_index",
    conn
)

conn.close()

# ==========================================
# PREPROCESS
# ==========================================

nlp_index["search_text"] = (
    nlp_index["search_text"]
    .fillna("")
    .str.lower()
)

# ==========================================
# SEARCH FUNCTION
# ==========================================

def search(query, top_n=10):
    """
    Simple keyword search over the NLP index.
    """

    query = query.lower()

    keywords = re.findall(r"[a-z0-9]+", query)

    if len(keywords) == 0:
        return pd.DataFrame()

    results = nlp_index.copy()

    results["score"] = 0

    for word in keywords:

        results["score"] += (
            results["search_text"]
            .str.contains(word, regex=False)
            .astype(int)
        )

    results = (
        results[
            results["score"] > 0
        ]
        .sort_values(
            "score",
            ascending=False
        )
        .head(top_n)
    )

    return results[
        [
            "company_id",
            "company_name",
            "year",
            "score"
        ]
    ]

# ==========================================
# INTERACTIVE TEST
# ==========================================

if __name__ == "__main__":

    while True:

        query = input("\nSearch (or 'exit'): ")

        if query.lower() == "exit":
            break

        result = search(query)

        if result.empty:

            print("\nNo matching companies found.")

        else:

            print("\nResults\n")

            print(result.to_string(index=False))