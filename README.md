# HQtrivia Google Bot
This is a bot that helps you google HQTrivia questions. It was written in early spring 2018.

## Warning
The code here is for running on Ubuntu while playing HQ on an iPhone. The code is setup specific and will not work on most setups without modifications. Furthermore, code quality is very low since this bot was created as a first learning project.

This bot relies heavily on tools from the GoogleCloud API, so you will need to obtain an api key. 

## How it works 
* When your iPhone is connected to your Ubuntu machine, use ifuse-media to gain read access to the directory on your iPhone where images are stored.
* Use `python3 main6.py` to run the bot. 
* While running, take a screenshot of an HQtrivia question.
* The image is cropped to isolate text.
* Text is obtained from the cropped image using Google Vision API and then formatted.
* Entites are extracted from the text using Google Language API.  
* Question answer combinations are google searched simultaneously using Google CSE API.
* The search results are then parsed and occurences of entities are counted.
* Entities are grouped by salience scores and the weight to assign each salience score group is predetermined by a linear learning model.
* The overall score for each answer is then determined by summing over (#number of occurrences of entities with a given salience score)\*(weight assigned to salience score)
* The score of each answer is returned within 7 seconds of the screenshot. (May vary with internet speed.)

## To do 
* Refactor code.
* Make more general in order to function out of the box.
* Improve dataset for better learning.
