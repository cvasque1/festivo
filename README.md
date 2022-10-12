*NOTE: This app is currently under development and still needs to gain production approval from Spotify for it to be accessible to anyone not given direct access by me.
https://festivo.herokuapp.com/*

# Festivo

#### Description:
Festivo is a free Spotify-powered app that recommends you artists from any lineup based on your most listened-to artists.

#### Stack:
Flask, Python, HTML, CSS, Javascript, Heroku hosting

## About:
I, as many people, love to listen to music and experience it live! I enjoy going to various music festivals and always tell myself that I'll listen to all the artists on a given lineup to discover new acts... but never really get around to doing it. Lineups can have more than a hundred artists so to facilitate lineup exploration, I created Festivo!
Using Spotify's API, Festivo fetches a user's top artist data to generate a list of artists that a user might enjoy at a given festival! Not to say that this list of recommended artists will be all you need to listen to, but it's a great starting point for discovering new artists in an upcoming festival :)

## Festivo Showcase:
![](https://github.com/cvasque1/festivo/blob/master/festivo_gifs/festivo_home-page.gif)

![](https://github.com/cvasque1/festivo/blob/master/festivo_gifs/festivo_recommended.gif)

![](https://github.com/cvasque1/festivo/blob/master/festivo_gifs/festivo_recommended-3.gif)

![](https://github.com/cvasque1/festivo/blob/master/festivo_gifs/festivo_recommended-2.gif)


## Future Implementations:
This project is my main tool for learning new technologies, languages, frameworks, etc. As I learn more about programming, I'll add more features to Festivo.
For now, here's what I have planned and am working on:
1. User Authentication/User profiles
2. Backend Server (Likely switch from Flask -> Django)
	- Enables storage of a plethora of information which can then be used for other features.
	- Store: User's top-artists, recommended artists (for any festival), friend list (other users).
		- Storing top-artist data enables faster generation of recommended artists since it reduces number of API calls. Data would be refreshed every couple of weeks.
		- Storing a users recommended artists would enable users to quickly revisit recommended lists.
		- By creating a friend network between users, one could see and compare the recommended artists between one another. Go checkout a new artists together at the festival :)
3. ANY Festival Option
	- If a festival is not up on the website, this gives user the opportunity to get recommendations for any festival (or list of artists!). Two ways to go about it right now.
		- Use an image processing API for text extraction where user's can upload an festival lineup poster and get recommendations as such.
		- User uploads a list of artists and get a list of recommendations from that.
			


	

