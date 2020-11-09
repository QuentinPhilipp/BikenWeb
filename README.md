# Biken Web
https://bikenapp.com/

Web version of Biken in Python using Flask. Biken was a school project of pathfinding. This was originally a software in C++ using Qt. This project is to transform the old project into a web based application. The routing is not made on my server because of performance issue. I'm using MapBox Direction API to make the calculations.

# Why did I built this ?
Mainly for fun, there are already other sites offering similar features but I wanted to develop my own version. 
It's also the first big fullstack project I'm working on, where I have to manage the web interface, the back-end, the database, the hosting, etc...

# Main features
 - Generation of **itinerary between two cities**.
 - Generation of **random circular trip** around the start point.
 - Share easily an itinerary to some friends, **you do not need to create an account to share or consult an itinerary.**
 - Exporting  created itineraries in **GPX files** ( Garmin compatibility).
 - Saving itineraries for later consultation.
 - Connect with Strava to get your past activities, edit the road, and create a GPX files from it.

# Account and login
The website support 3 different type of login. 
 - Google Login
 - Strava Login
 - Classic email and password login

I recommend using Google or Strava if you want to create an account. It use OAuth authentication and no password are send to my application. The only scope required by the application is the email address for Google and only the public information for Strava to show your past activities. However, if you prefer using your email for login it's also possible. 

No emails will be sent to your email address, it is only used as identification method. Currently the password reset is disable.

### Account binding
If you are connected with Google or with your email address and you go to "Activities" you can authenticate yourself with Strava to see your past activities. Once this is done, the Strava account is bind to your account and you will have two way to authenticate to the same account.

 
# Next features

 - Adding waypoints on the route by clicking on the map
 - Improve design
 - Use an private instance of a routing machine ( remove dependencies to tiers ). Probably OSRM to use OpenStreetMap data.
 
Want something in particular ? Propose your idea in an Issue, i'm open to all modification.

# Found a bug ? 
Feel free to open an issue or send me an email if you encountered a bug and I will try to fix it.

# Screenshots

This is some screenshots so you can see all parts of the application even without creating an account.
### One way itinerary
![Oneway itinerary](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/oneway.png)
### Round trip
![Round trip](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/roundtrip.png)
### Login
![Login page](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/Login.png)
### Profile page
![Profile page](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/profile.png)
### Activity page (not logged in with Strava)
![Activity page (not logged in with Strava)](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/strava.png)
### Activity page
![Activity page](https://github.com/QuentinPhilipp/BikenWeb/blob/master/BikenWeb/README/activities.png)

