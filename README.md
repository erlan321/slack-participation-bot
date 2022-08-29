# slack-participation-bot
A grading tool for student participation on Slack
  
  
This repository is a modified version of an original tool created by Dr. Elle O'Brien of the University of Michigan, whose repository can be found here: https://github.com/elleobrien/participation-bot.  Many thanks to Elle for her help and advice on this project!  

This updated repository was created to give an instructor the ability to measure student participation in a Slack channel for different types of courses in the University of Michigan Masters in Applied Data Science (MADS) program.  
 - In a project-oriented course, teams of students (or individual students) are expected to post periodic "stand ups" about their project on Slack, and then also review and comment/advise their fellow students' stand ups.
 -  In a course that requires weekly reading assignments (or a similar weekly material review) where individual students are expected to post their own thoughts on the reading on Slack, and then also review and discuss the thoughts of their fellow students.

This repository can be copied to your local drive by
```$ git clone https://github.com/erlan321/slack-participation-bot```

__Running the Grading tool:__
Once the repo is copied to your local drive and you have created the required input files, the grading tool can be run from a command prompt:
```
$ python bot.py <channel-name> <from-date> <to-date>
```
For example,
```
$ python bot.py siads999_fa22_course_name 08/22/2022 08/28/2022
```
__Input Files__
 - __keys.json (required)__
   - This file contains the Bot User Oath token.  The format of this json file would look like: 
   - ```{ "token" : "xoxb-123456789123-4567891234567-abc123abc123abc123abc123a” }```
   - Instructions for creating a bot to use with this tool and how to add it to your course channel can be found here (needs a Umich email account to view): https://docs.google.com/document/d/1W4K4V7e0BbWRazkqWqvh9Lz-9JkKXVJrA3dTXoRZYAk/edit?usp=sharing
 - __grade_requirements.csv (required)__
   - This file sets some values needed for grading.  An example is provided in the repository.
   - ```team_graded``` should be 1 if the students are in teams (like in a project-focused course) or 0 if individually graded.
    - If set to 1, a student_team_directory needs to be created (see below).
    - If set to 0, the tool will be able to use the Slack channel's membership to get a list of the course's students. 
   - ```min_post``` and ```min_reply``` are the minimum required posts and replies expected.  For instance, perhaps 1 post is required of each student, but then they are expected to make 3 responses to their classmates work.  
   - _Note:  For team grading, we allow for team posts (i.e. only 1 team member needs to post for all team members), but we assume that replies will always expected to be made individually._
   - ```post_val``` and ```reply_val``` are the grade point value for each post and reply.  Continuing the example above, perhaps we want the single post to count for half the grade and the replies to count for the other half, we could set the grade point value of posts to 15 points and the value of replies to 5 points apiece.  This is up to the discretion of the instructor.
 - __student_team_dictionary.csv (optional)__
   - This file is only needed if ``team_graded``` is set to 1.  If this is the case, the tool will need to see team assignments for each student.  
   - The example provided in the repository is based off of a download from Coursera of the students in the class, but the only important columns are ```email``` and ```team```.  As long as this file has these two columns filled out, the tool will be able to run successfully.  
   - _Note that the ```email``` column contains the Umich email.  This will allow our Slack Bot to match each student's uniqname to their identity in the Slack channel._





