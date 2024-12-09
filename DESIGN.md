A “design document” for your project in the form of a Markdown file called DESIGN.md that discusses, technically, how you implemented your project and why you made the design decisions you did. Your design document should be at least several paragraphs in length. Whereas your documentation is meant to be a user’s manual, consider your design document your opportunity to give the staff a technical tour of your project underneath its hood.

Backend:
The heart of Quote That!'s backend lies in the five databases that contain all of the information for the website to function. 
1) Users
- Contains the usernames and password hashes for all users that are registered in Quote That!
2) Groups
- Contains the groupnames and password hashes for all groups that are created in Quote That!
3) Additions
- Database that tracks whenever a user joins or leaves a group. Tracks that user's ID, the group ID they are interacting with, and a value: 1 if that user is joining a group OR -1 if that user is leaving a group. 
4) Quotes
- Contains the content, author, location, group ID, time of creation, and how many likes a quote has for every quote across all groups in Quote That!
5) Likes
- Database that tracks whenever a user likes or unlikes a quote. Tracks that user's ID, the quote ID they are interacting with, and a value: 1 if that user is liking the quote OR -1 if that user is unliking the quote. 

The Users and Groups tables are pretty self-explanatory and mimic the the behaviors of tables in the Finance CS50 project. Now, Additions and Likes are very useful tables because they allow the program to track which groups a certain user is a part of and which quotes a certain user has liked. 
The software does this by running a SQL command like this:
"SELECT id FROM quotes WHERE id IN (SELECT quote_id FROM likes WHERE user_id = ? GROUP BY quote_id HAVING SUM(like_value) > 0)", session["user_id"]), where the key part is that the only quote_id's that are selected are those who's values sum to a number greater than 0, which means only the quotes that the user has liked more than unliked, or, equivalently, only the quotes that the user is currently liking. This behavior is exactly the same for the group joining. 

This allows the program to easily display user-specific data to multiple users and is a key component of how our backend meshes with our frontend. 

Now, we heavily used Jinja to create dynamic web pages, such as the group page and the home page as it is impossible to know exactly how many quotes are in a group or how many groups a certain user has joined. In addition, another really interesting way we used Jinja was to automatically generate routes in flask. An example can be seen here, taken from our homepage:
<a href="{{ url_for('group_page', group_id=group['id']) }}" class="group-card">{{ group.name }}</a>
This uses jinja to automatically generate a new URL for the group page depending on the group page's ID, which is invaluable when trying to display different webpages for different groups a user has joined. 

Another unique way we used Jinja was for the structure of our Like/Liked buttons. Essentially, we used the previous database trick to track whether or not a certain quote was liked by a user and then used Jinja to dynamically change the class of the button between 'like-button' and 'liked' depending on what the databases said. Then, this interacted with our CSS to change the color of the button and its text based on the class of the button, for dynamic color changes. 

Overall, we started our project by designing our databases and then structuring all of our goals based off of our possible database interactions, which gave our project a very solid foundation :)


Frontend:
In terms of the user interface, we have multiple html files in the templates folder that we used to make our website look more aesthetically pleasing. We first decided to design a color palette and a logo that would match with this color palette in order to make the entire website more cohesive and professional-looking as a whole.

First, we began by designing “layout.html”, that provides the formatting for the website in general. In this file, we included the fonts we wanted to use, “Poppins” from Google, in this case, as our target audience is generally young adults and we felt this fit best with the vibe we wanted for our website. We also defined a navigation bar that includes our logo (that, when clicked, leads to the login page if there is no session open and to the homepage, index.html, otherwise). The navigation bar also includes the logout button for security measures, and only appears when a session is open. Moreover, we made this navigation bar collapsible so that it formats nicely on all devices.

We will now give a brief overview of each .html page:
	•	apology.html leads to the amazing grumpy cat, that we felt was too nostalgic to let go of;
	•	create.html defines the page where users can create a new group. It is a form that takes in inputs a group name, password, and password confirmation;
	•	group.html is the quote book itself. It shows the various quotes with the author and location (if applicable) and “No quotes in this group yet.” if that is the case. We decided to make the backgrounds of the quotes alternating to help distinguish the quotes from each other. We also right-aligned the authors to make it seem more like a typical gallery of quotes. We also implemented a function to like quotes;
	•	index.html is the main homepage, where users can see all the groups they are in, as well as can create a group, join a group, or leave a group. We were heavily inspired by the Goodnotes user interface as it is very intuitive, simple, and clean;
	•	join.html is very similar to create.html, defining the page where users can join a new group. It asks users for the group name and the password;
	•	leave.html is also very similar to both join.html and create.html, defining the page where users can leave a group they are in. We made sure to error check so that users can’t leave a group they are not in. We also defined our databases so that they can rejoin a group they leave if they so desire;
	•	login.html is the main homepage when there is no session open. It welcomes new users to the site, and allows for new users to register through the small “Don’t have an account yet?” typical of most websites. It asks for the username and the corresponding password, and accounts for all necessary error checks;
	•	register.html is what new users are led to upon clicking “Don’t have an account yet?”

Overall, we tried to make the user interface as intuitive as possible. Since most people are so familiar with technology and modern websites, we tried to get inspired by other sites as much as possible so that our website would be very easy to use. Moreover, we tried to choose a color scheme that would appeal to most audiences: trendy, but not overly colorful so that some people are repelled. We chose something elegant and professional, but also a little bubbly and exciting to reflect the informality of the uses of our app.

