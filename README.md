# slack-participation-bot
A grading tool for student participation on Slack
  
  
This repository is a modified version of an original tool created by Dr. Elle O'Brien of the University of Michigan, whose repository can be found here: https://github.com/elleobrien/participation-bot.  Many thanks to Elle for her help and advice on this project!  

This updated repository was created to give an instructor the ability to measure student participation in a Slack channel for different types of courses in the University of Michigan Masters in Applied Data Science (MADS) program.  
 - Use case #1:  In a project-oriented course, teams of students (or individual students) are expected to post periodic "stand ups" about their project, and then also review and comment/advise their fellow students.
 -  Use case #2:  In a course that requires weekly reading assignments (or similar material), and individual students are expected to post their own thoughts on the reading, and then also review and discuss the thoughts of their fellow students.

__Running the Grading tool:__
```
$ python bot.py <channel-name> <from-date> <to-date>
```

For example,
```
$ python bot.py siads999_ss22_test_channel 08/22/2022 08/28/2022
```
 - channel_name, from_date, to_date:
  -  The grading tool 
 - 
 - keys.json
   - This file contains the Bot User Oath token

https://docs.google.com/document/d/1W4K4V7e0BbWRazkqWqvh9Lz-9JkKXVJrA3dTXoRZYAk/edit?usp=sharing


