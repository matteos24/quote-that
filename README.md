# quote-that

YOUTUBE VIDEO LINK: 

How to run our app:
- Link to GitHub Repository With All Code: https://github.com/matteos24/quote-that
- Download a ZIP File of the code, and then unzip it
- Open Visual Studio Code and open the project files in a new window
- In the Terminal, type in "pip install cs50"
- In the Terminal, type in "pip install flask-session"
- In the Terminal, type in "python -m flask run"
- You should see a line that says "* Running on http://127.0.0.1:5000" or similar
- Click on the link and you will be taken to our website, Quote That!

Starting out, you will required to register a new account, to do this, just click on the "Don't have an account yet" link below the Log In button. Once you have successfully registered your account (by adding username and password and clicking register), you will be taken to the login page again, where you should just add your just-created username and password to access the site. 

Homepage: At the start, you will see three options. Join A Group, Create A Group, Leave A Group. This webapp is structured through these groups, and each group will have a unique set of quotes and likes for people in the group to view. This way, a single user can join multiple friend groups and only post quotes in the friend groups where the quote is relevant. 

Now, you should click on "Create A Group", where, just like Register, you will create a group with a "Group Name" and Password. Be sure to save this password, as every other user that wants to join this group will need to input this password to join. Once you have created your group, you will be returned to the homepage. 

Now, you can click on the "Join A Group" button and fill out the form with information about the group you just created. If all the information is correct, you will be returned to the homepage and see a fourth button appear, with the name of the group you just joined as its label. The Leave A Group button just asks for the name of a group, and if you are a user in that group, it will remove you from it and that button will disappear from your homepage.

Group Page: This is the page where all the quotes and likes in a certain group are displayed, as well as the page where you can add a quote to be displayed in the group. 

Add a Quote: Underneath the "Add a New Quote" header, there will be a form to fill out. 
- Quote: In this input field, write the content of the quote you want to immortalize 
- Author: In this input field, write the name of the person who said the quote 
- Location: This is an optional field, so you can leave it blank but in it, you should write where the quote was said
Once you click Add Quote, you should see the quote, along with all of its requisite information appear above, on the group page. 

Liking: Every quote has two pieces of information next to the author and location. 
1) A button that, at the start, should say Like 
2) A number that, at the start, should be 0

1) Represents a way for the user to like a quote and when that button is clicked, it will turn from Like to Liked and flash red, signifying that you (the user) have liked the quote. Now, if you click the button when it displays Liked, it will turn from Liked to Like and go back to a white background, signifying that you have unliked the quote. 
2) Represents how many total users in the group have liked that quote, so when you click button 1, field 2 should either increment or decrement by 1 (depending on whether you liked or unliked the quote).

Now, you can repeat all of these activities: Creating/Joining Groups, Adding Quotes in Each Group, and Liking Quotes to your heart's content because all progress will save even if you close the application and stop the flask from running. Meaning that next time, you can begin where you left off. 

Quick Notes:
- If you create a group, you DO NOT automatically join that group, you must do this manually
- There are currently no ways to delete quotes from a group

- Matteo Salloum and Julie Lavigne 
CS50 Final Project. Web app to track quotes from different friend groups. 
