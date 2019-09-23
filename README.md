# minesweeper-API
API test

## The Game
The classic game of [Minesweeper](https://en.wikipedia.org/wiki/Minesweeper_(video_game)

### How to play with swagger?
1) on https://minesweeper-adorda.herokuapp.com/api/v1/docs
2) go to api section and use the POST api/v1/users to create a new user, only mandatory fields are username and password
3) go to api-token-auth section and get token with POST /api-token-auth with user and password
4) Authorize with the button at the top to the right, you will see a field with a tip that says api_key, there you put "Token yourToken" without quotes
5) create a new game on api section with POST api/v1/games you will find the example model there
6) make a mark on the game with PUT api/v1/games
7) get some game information with GET api/v1/games/{game_id}

## Features
The following is a list of items (prioritized from most important to least important) we wish to see:
* Design and implement  a documented RESTful API for the game (think of a mobile app for your API)
* Implement an API client library for the API designed above. Ideally, in a different language, of your preference, to the one used for the API
* When a cell with no adjacent mines is revealed, all adjacent squares will be revealed (and repeat)
* Detect when game is over
* Persistence
* Time tracking
* Ability to start a new game and preserve/resume the old ones
* Ability to select the game parameters: number of rows, columns, and mines
* Ability to support multiple users/accounts
 
## Deliverables:
* The game on heroku https://minesweeper-adorda.herokuapp.com/api/v1/docs
* SDK repository: https://github.com/angdmz/minesweeper-sdk


## Install on docker
```sh
cd /project/folder
docker build -t msapi .
docker-compose up -d
cp minesweeper/local_settings_dev_docker.py minesweeper/local_settings.py
docker run -d --rm --name msapi -v $(pwd):/opt/project -w /opt/project msapi python manage.py migrate
docker run -d --rm --name msapi -v $(pwd):/opt/project -w /opt/project -p 8000:8000 msapi python manage.py runserver 0.0.0.0:8000
```

Why not raise the application with docker-compose? for easier restart when developing and integration to PyCharm


## Some decisions:
I went for Django as a framework for it is a simple tool for developing web and REST APIs, and used heroku for deploy in cloud because it's easy too

Used swagger for documentation for the API, because it's the easiest and most common implementation of OpenApi, and allowed me to automatically generate client SDK which made that part really easy
