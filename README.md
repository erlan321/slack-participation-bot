# slack-participation-bot
A grading tool for student participation on Slack
  
  
This repository is a modified version of an original tool created by Dr. Elle O'Brien of the University of Michigan, whose repository can be found here: https://github.com/elleobrien/participation-bot.  Many thanks to Elle for her help and advice on this project!  

This updated repository was created to give an instructor the ability to measure student participation in a Slack channel for different types of courses in the University of Michigan Masters in Applied Data Science (MADS) program.  
 - Use case #1:  In a project-oriented course, teams of students (or individual students) are expected to post periodic "stand ups" about their project, and then also review and comment/advise their fellow students.
 -  Use case #2:  In a course that requires weekly reading assignments (or similar material), and individual students are expected to post their own thoughts on the reading, and then also review and discuss the thoughts of their fellow students.

__Running the Grading tool:__
Once the repo is copied to your local drive and you have created the required input files, the grading tool can be run from a command prompt:
```
$ python bot.py <channel-name> <from-date> <to-date>
```
For example,
```
$ python bot.py siads999_fa22_course_name 08/22/2022 08/28/2022
```
__Required Input Files__
 - keys.json
   - This file contains the Bot User Oath token.  The format of this json file would look like: 
   - ```{ "token" : "xoxb-123456789123-4567891234567-abc123abc123abc123abc123a” }```
   - Instructions for creating a bot to use with this tool and how to add it to your course channel can be found here (needs a Umich email account to view): https://docs.google.com/document/d/1W4K4V7e0BbWRazkqWqvh9Lz-9JkKXVJrA3dTXoRZYAk/edit?usp=sharing
 - grade_requirements.csv
  - This file sets some values needed for grading.  An example is provided in the repository.
  - ```team_graded``` should be 1 if the students are in teams (like in a project-focused course) or 0 if individually graded.
  - ```min_post``` and ```min_reply``` are the minimum required posts and replies expected.  For instance, perhaps 1 post is required of each student, but then they are expected to make 3 responses to their classmates work.  
  - _Note:  For team grading, we allow for team posts (i.e. only 1 team member needs to post for all team members), but we assume that replies will always expected to be made individually._
  - ```post_val``` and ```reply_val``` are the grade point value for each post and reply.  Continueing the example above, perhaps we want the single post to count for half the grade and the replies to count for the other half, we could set the grade point value of posts to 15 points and the value of replies to 5 points apiece.  This is up to the discretion of the instructor.
 - student_team_dictionary


