import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
from time import sleep, time
import pandas as pd
import collections
import sys
import datetime


def get_client(key_file):
    token = json.load(open(key_file))
    client = WebClient(token=token['token'])
    return(client)


def get_channel_id(channel_name, client):
    for result in client.conversations_list(types="public_channel, private_channel"):
        channels = result['channels']
        for c in channels:
            if c['name'] == channel_name:
                return(c['id'])


def get_all_posts_in_channel(channel_name, client, from_date, to_date, max_pages = 5):
    channel_id = get_channel_id(channel_name, client)
    # Note that this will NOT return the full text of replies to posts.
    all_messages = []
    keep_looking = True
    page = 1
    from_date = datetime.datetime.strptime(from_date, "%m/%d/%Y").timestamp()
    to_date = datetime.datetime.strptime(to_date, "%m/%d/%Y").timestamp()
    print(from_date, to_date)
    while keep_looking == True and page < max_pages:
        if page == 1:
           result = client.conversations_history(channel=channel_id,limit=200, oldest=from_date, latest=to_date)
        else:
            result = client.conversations_history(channel=channel_id,limit=200, cursor=result['response_metadata']['next_cursor'], oldest=from_date, latest=to_date)
        all_messages = all_messages + result['messages']
        keep_looking = result['has_more']
        sleep(1)
        page +=1    
    return(all_messages)

def get_all_users_in_channel(channel_name, client):
    channel_id = get_channel_id(channel_name, client)
    users = client.conversations_members(channel=channel_id,limit=200)['members']
    uniqnames = user_id_to_uniqname(users, client)
    all_users_df = pd.DataFrame(zip(users,uniqnames), columns=['user_id','uniq_name'])
    return(all_users_df)

def get_users_who_posted(messages,return_freq=False):
    # Accepts list of message instances
    users = []
    msg_ts = []
    for msg in messages:
        if 'user' in msg.keys():
            try:
                if ( (msg['subtype']=='channel_join') | (msg['subtype']=='channel_purpose') ): 
                    continue # Don't count posts that are generated by a user being added to the channel or from the channel's creation
            except:
                users.append(msg['user'])
                msg_ts.append(msg['ts'])
    if return_freq:
        return_users = collections.Counter(users)
    else:
        return_users = set(users)
    return(return_users)


def get_users_who_replied(messages,return_freq=False):
    # Accepts list of message instances
    users = []
    for msg in messages:
        if "reply_users" in msg.keys():
            users += msg["reply_users"]
    if return_freq:
        return_users = collections.Counter(users)
    else:
        return_users = set(users)
    return(return_users)


def get_all_participants_in_channel(messages, return_freq = False):
    posters = get_users_who_posted(messages,return_freq=return_freq)
    repliers = get_users_who_replied(messages,return_freq=return_freq)
    if return_freq:
        all_participants = repliers + posters
    else:
        all_participants = posters.union(repliers)
    return(all_participants)


def user_id_to_uniqname(user_id_list, client):
    uniqnames = []
    for usr in user_id_list:
        try:
            result = client.users_info(user=usr)
            uniqnames.append(result['user']['name'])
        except:
            uniqnames.append('UNK')
            print("Unable to identify user " + usr)
    return(uniqnames)


def user_counts_to_dataframe(counter,context=None):
    df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    df = df.rename(columns={'index':'user_id', 0:'count'})
    if context:
        df['context'] = context
    return(df)


def make_post_and_reply_summary(messages):
    # Get summaries of post & reply activities
    poster_df = user_counts_to_dataframe(get_users_who_posted(messages,return_freq=True),context='post')
    reply_df = user_counts_to_dataframe(get_users_who_replied(messages, return_freq=True),context='reply')
    # Now concatenate into one big summary dataframe
    participation_df = pd.concat([poster_df,reply_df])
    participation_df['channel'] = channel_name
    # Get usernames of every participant too
    user_list=participation_df['user_id'].unique()
    uniq_name_list = user_id_to_uniqname(user_list, client)
    name_dict = dict(zip(user_list, uniq_name_list))
    participation_df['uniq_name'] = participation_df['user_id'].map(name_dict)
    return(participation_df)


def convert_activity_to_grade(): 

    # Get the student uniqnames
    if team_graded == 1: #use a manually created student team list
        team_df = pd.read_csv("course_inputs/student_team_dictionary.csv")
        team_df["uniq_name"] = team_df["email"].str.replace("@umich.edu","", regex=True)
    else: #use an automatically generated user list from the channel
        team_df = get_all_users_in_channel(channel_name, client)
        team_df["email"] = team_df["uniq_name"]+"@umich.edu"
        team_df["team"] = team_df["uniq_name"] #makes every person a member of their own "team"

    # For each group that posted a standup, give everyone in the group credit, initiating a score of zero
    standup_post_scores = {el:0 for el in team_df["uniq_name"].values}

    slack_activity = pd.read_csv("report.csv") #read in the slack channel activity
    posts = slack_activity[slack_activity["context"]=="post"]

    for poster in posts["uniq_name"].values:
        team_id = team_df[team_df["uniq_name"]==poster]["team"].values
        if len(team_id) > 0: 
            teammates = team_df[team_df["team"]==team_id[0]]["uniq_name"].values
            for student in teammates:
                score = posts[posts.uniq_name.isin(teammates)]["count"].max()
                standup_post_scores[student] = min(score, min_post)
        else:
            print("Team not found for %s" % poster) 

    # What about comments?
    comment_scores = {el:0 for el in team_df["uniq_name"].values} #initiate score at zero
    comments = slack_activity[slack_activity["context"]=="reply"]

    #for student in more_than_two_comments["uniq_name"].values:
    for student in comments["uniq_name"].values:
        if student in comment_scores:
            score = comments[comments.uniq_name==student]["count"].values[0]
            comment_scores[student] = min(score, min_reply)
        else:
            print("Did not find %s in student list." % student) 

    # Add them up!
    total_score = {}
    for student in team_df["uniq_name"].values:
        total_score[student] = (comment_scores[student]*reply_val + standup_post_scores[student]*post_val)

    # Turn it into a dataframe
    total_score_df = pd.DataFrame.from_dict(standup_post_scores, orient="index",columns=["posts"])
    total_score_df["post_val"] = post_val
    total_score_df = total_score_df.merge(pd.DataFrame.from_dict(comment_scores, orient="index",columns=["replies"]),how="left",left_index=True, right_index=True)
    total_score_df["reply_val"] = reply_val
    total_score_df = total_score_df.merge(pd.DataFrame.from_dict(total_score, orient="index",columns=["grade_points"]),how="left",left_index=True, right_index=True)
    total_score_df['grade_percent'] = 100 * (total_score_df["grade_points"] / (min_post*post_val+min_reply*reply_val))
    total_score_df['grade_percent'] = total_score_df['grade_percent'].astype("float").round(2)
    total_score_df['uniq_name'] = total_score_df.index
    total_score_df["email"] = total_score_df["uniq_name"] + "@umich.edu"
    total_score_df.reset_index()

    return total_score_df  


    

if __name__ == "__main__":
    # Looks for Slack bot arguments: a channel name and dates
    channel_name = sys.argv[1]
    from_date = sys.argv[2] if len(sys.argv) >= 3 else '01/01/2022'  # default start date
    to_date = sys.argv[3] if len(sys.argv) >= 4 else datetime.datetime.today().strftime('%m/%d/%Y')

    # Looks for an API key file
    if os.path.exists("keys.json"):
        key_file = "keys.json"
    else:
        print("Required File Missing: keys.json" )
        sys.exit() #exit if file is missing

    # Looks for course-specific arguments
    if os.path.exists("course_inputs/grade_requirements.csv"):
        grade_req_df = pd.read_csv("course_inputs/grade_requirements.csv", nrows=1)
        min_post = grade_req_df['min_post'].values[0] #the min number of posts required per person (or team)
        post_val = grade_req_df['post_val'].values[0] #the grade point value of each post
        min_reply = grade_req_df['min_reply'].values[0] #the min number of replies required per person
        reply_val = grade_req_df['reply_val'].values[0] #the grade point value of each reply
        team_graded = grade_req_df['team_graded'].values[0] #1 if team graded, 0 if not.  This allows teams to get credit for a single team member's posts.
        del grade_req_df
    else: 
        print("Required File Missing: course_inputs/grade_requirements.csv" )
        sys.exit() #exit if file is missing

    # If this course will have team grading, check that the required file exists because it will be used in a subsequent script
    if team_graded == 1:
        if os.path.exists("course_inputs/student_team_dictionary.csv"):
            pass
        else: 
            print("Required File Missing: course_inputs/student_team_dictionary.csv" )
            sys.exit() #exit if file is missing
         
    # Set the client and channel_id for the Slack API    
    client = get_client(key_file)
    channel_id = get_channel_id(channel_name, client)

    # Get messages in the channel of choice
    messages = get_all_posts_in_channel(channel_name, client, from_date, to_date)
    participation_df = make_post_and_reply_summary(messages)

    # Write to a .csv file
    participation_df.to_csv("report.csv")


    # Create and export grades
    grade_filename = "_".join([
                        'grades',
                        str(datetime.datetime.strptime(from_date, "%m/%d/%Y").day) + \
                        str(datetime.datetime.strptime(from_date, "%m/%d/%Y").strftime("%b")) + \
                        str(datetime.datetime.strptime(from_date, "%m/%d/%Y").year)[-2:],
                        'to',
                        str(datetime.datetime.strptime(to_date, "%m/%d/%Y").day) + \
                        str(datetime.datetime.strptime(to_date, "%m/%d/%Y").strftime("%b")) + \
                        str(datetime.datetime.strptime(to_date, "%m/%d/%Y").year)[-2:], 
                        channel_name                  
                        ])+".csv"

    grade_df = convert_activity_to_grade()

    grade_df.to_csv("grades/" + grade_filename)
