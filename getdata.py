import praw
import os
import time

client_id = "my_client_id";
client_secret = "my_client_secret";
user_agent = "my_user_agent_name";

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)

data_list = set();

for submission_id in reddit.subreddit('all').top():
    print("New post started")
    submission = reddit.submission(submission_id);
    comments = submission.comments.list();
    print("Retrieved comments");
    for comment in comments:
        if isinstance(comment, praw.models.Comment):
            author = comment.author;
            if (author is not None) and (author.name not in data_list):
                data_list.add(author.name);

dir_path = os.path.dirname(os.path.realpath(__file__));
new_file_path = str(os.path.join(dir_path, 'data.txt'));

with open(new_file_path, 'w') as f:
    for user in data_list:
        f.write(f"{user}\n");