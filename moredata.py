import os
import pandas as pd
import praw
import time
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__));
new_file_path = str(os.path.join(dir_path, 'data.txt'));

with open(new_file_path, 'r') as f:
    users = f.read().splitlines();

comment_karma = [];
post_karma = [];
total_karma = [];
years = [];

client_id = "my_client_id";
client_secret = "my_client_secret";
user_agent = "my_user_agent_name";

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)

i = 0;

for user_name in users:
    user = reddit.redditor(user_name);
    
    try:
        comment_karma.append(user.comment_karma);
    except:
        comment_karma.append(None);
    
    try:
        post_karma.append(user.link_karma);
    except:
        post_karma.append(None);
    
    try:
        total_karma.append((user.comment_karma+user.link_karma));
    except:
        total_karma.append(None);
    
    try:
        years.append(datetime.fromtimestamp(int(user.created_utc)).year);
    except:
        years.append(None);
    
    i += 1;
    if (i%100 == 0):
        print(f"{i} users done");
    time.sleep(0.6);

data_dict = {"Username":users, "Comment Karma":comment_karma, "Post Karma":post_karma, "Total Karma":total_karma, "Creation":years};
df = pd.DataFrame(data_dict);
df = df.dropna().set_index('Username');
df['Creation'] = df['Creation'].astype(int);
df['Comment Karma'] = df['Comment Karma'].astype(int);
df['Post Karma'] = df['Post Karma'].astype(int);
df['Total Karma'] = df['Total Karma'].astype(int);
df = df[df['Comment Karma'] > 0];
df = df[df['Post Karma'] > 0];
df.to_csv(str(os.path.join(dir_path, 'data.csv')))