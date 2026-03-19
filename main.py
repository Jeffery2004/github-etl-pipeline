import mysql.connector
import requests
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

def convert_date(date_str):
    if date_str is None:
        return None
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

url = "https://api.github.com/users/Jeffery2004/repos"
response = requests.get(url)

if response.status_code != 200:
    print("Error:", response.status_code)
    print(response.text)
    exit()

repos = response.json()

insert_query = """
INSERT IGNORE INTO github_repos 
(repo_id, username, repo_name, language, stars, forks, created_at, pushed_at, repo_url)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for repo in repos:
    repo_data = (
        repo["id"],
        repo["owner"]["login"],
        repo["name"],
        repo["language"],
        repo["stargazers_count"],
        repo["forks_count"],
        convert_date(repo["created_at"]),
        convert_date(repo["pushed_at"]),
        repo["html_url"]
    )

    cursor.execute(insert_query, repo_data)

conn.commit()
print("All repos inserted successfully:", len(repos))

cursor.close()
conn.close()

df=pd.DataFrame(repos)
df.to_csv('github_repos.csv', index=False)
print("loaded data from csv")