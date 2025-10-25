import os
import pandas as pd
import praw
import time
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__));
new_file_path = str(os.path.join(dir_path, 'data.txt'));

with open(new_file_path, 'r') as f:
    users = f.read().splitlines();

subreddits = [];
dates = [];
contents = [];
scores = [];
totscores = [];

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
    commentretrievals = 0;
    postretrievals = 0;
    retrievals = 0;
    comments = None;
    posts = None;
    usersubreddits = [];
    userdates = [];
    content = [];
    score = [];
    try:
        comments = list(user.comments.top(limit=10));
    except:
        pass;

    try:
        posts = list(user.submissions.top(limit=10));
    except:
        pass;

    if (comments == None and posts == None):
        subreddits.append(None);
        dates.append(None);
        contents.append(None);
        scores.append(None);
        totscores.append(None);
        i += 1;
        if (i%100 == 0):
            print(f"{i} users done");
        time.sleep(0.6);
        continue;

    else:
        while(retrievals<10):
            if ((comments == None or commentretrievals >= len(comments)) and (posts == None or postretrievals >= len(posts))):
                break;
            elif ((posts == None or postretrievals >= len(posts)) and commentretrievals < len(comments)):
                try:
                    nextcomment = comments[commentretrievals];
                    subreddit_to_add = nextcomment.subreddit.display_name;
                    date_to_add = datetime.fromtimestamp(nextcomment.created_utc);
                    content_to_add = nextcomment.body;
                    score_to_add = nextcomment.score;
                    usersubreddits.append(subreddit_to_add);
                    userdates.append(date_to_add.strftime('%m/%d/%y'));
                    content.append(content_to_add);
                    score.append(score_to_add);
                    commentretrievals += 1;
                    retreivals += 1;
                except:
                    commentretrievals += 1;
            elif ((comments == None or commentretrievals >= len(comments)) and postretrievals < len(posts)):
                try:
                    nextpost = posts[postretrievals];
                    subreddit_to_add = nextpost.subreddit.display_name;
                    date_to_add = datetime.fromtimestamp(nextpost.created_utc);
                    content_to_add = nextpost.title+nextpost.selftext;
                    score_to_add = nextpost.score;
                    usersubreddits.append(subreddit_to_add);
                    userdates.append(date_to_add.strftime('%m/%d/%y'));
                    content.append(content_to_add);
                    score.append(score_to_add);
                    postretrievals += 1;
                    retrievals += 1;
                except:
                    postretrievals += 1;
            else:
                commentscore = None;
                postscore = None;
                commentsub = None;
                postsub = None;
                commentdate = None;
                postdate = None;
                try:
                    nextcomment = comments[commentretrievals];
                    commentscore = nextcomment.score;
                    commentsub = nextcomment.subreddit.display_name;
                    commentdate = datetime.fromtimestamp(nextcomment.created_utc).strftime('%m/%d/%y');
                    commentcontent = nextcomment.body;
                except:
                    nextcomment = None;
                try:
                    nextpost = posts[postretrievals];
                    postscore = nextpost.score;
                    postsub = nextpost.subreddit.display_name;
                    postdate = datetime.fromtimestamp(nextcomment.created_utc).strftime('%m/%d/%y');
                    postcontent = nextpost.title+nextpost.selftext;
                except:
                    nextpost = None;
                if (nextcomment == None):
                    commentretrievals += 1;
                    continue;
                if (nextpost == None):
                    postretrievals += 1;
                    continue;
                if (postscore >= commentscore):
                    usersubreddits.append(postsub);
                    userdates.append(postdate);
                    content.append(postcontent);
                    score.append(postscore);
                    postretrievals += 1;
                else:
                    usersubreddits.append(commentsub);
                    userdates.append(commentdate);
                    content.append(commentcontent);
                    score.append(commentscore);
                    commentretrievals += 1;
                retrievals += 1;    

    i += 1;
    if (i%100 == 0):
        print(f"{i} users done");
    subreddits.append(usersubreddits);
    dates.append(userdates);
    contents.append(content);
    scores.append(score);
    totscores.append(sum(score));
    time.sleep(0.6);

data_dict = {'Username':users, 'Top Subreddits':subreddits, 'Dates':dates, 'Content':contents, 'Scores':scores, 'Top10 Scores':totscores};
df = pd.DataFrame(data_dict);
df = df.dropna().set_index('Username');
df.to_csv(str(os.path.join(dir_path, 'commentsposts.csv')));