#HQtrivia Google Bot
This is a bot that helps you google HQTrivia questions. 

##Warning
The code here is for running on ubuntu while playing HQ on an iPhone. The code is setup specific and will not work without on most setups without modifications. Furthermore, code quality is very low since this bot was created as a first learning project.

Also this bot relies heavily on tools from the GoogleCloud API, so you will need to obtain an api key. 
##How it works 
* When your iPhone is plugged in to your machine, use ifuse-media to gain read access to the directory on your iPhone where images are stored.
* The bot then crops the image to isolate text.
* Text is obtained from the cropped image using Google Vision API and then formatted.
* Entites are extracted from the text using Google Language API.  
* Question answer combinations are google searched simultaneously using Google CSE API.
* The search results are then parsed and occurences of entities are counted.
* Entities are grouped by salience scores and the weight to assign each salience score group is predetermined by a linear learning model.
* The overall score for each answer is then determined by summing over (#number of occurrences of entities with a given salience score)\*(weight assigned to salience score)
* The score of each answer is returned.

## Using the bot
After connecting your iPhone, run main6.py and take a screenshot of an HQtrivia question. The score assigned to each answer will be returned after 5-7 seconds. 

