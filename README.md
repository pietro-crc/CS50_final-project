# YT scraper
#### Video Demo:  <https://youtu.be/AF6MTgawSsk>
#### Description: YouTube Sentiment Analysis Project

#### Objective:

The objective of this project is to analyze the sentiment of YouTube comments in order to understand how people feel about a particular video.

Methodology:

The project uses Python to scrape the comments from YouTube videos.
The comments are then analyzed using a sentiment analysis algorithm to determine whether they are positive, negative, or neutral. The results of the analysis are then visualized using 4 charts.
Stanza NLP for sentiment analisys.
hugging face mrm8488/t5-base-finetuned-emotion for the emotion analisys.

Data:

The project will use a dataset of YouTube comments collected from a you tube channel.
The dataset will be collected using a Python script that scrapes the comments from the YouTube videos.

Sentiment Analysis Algorithm:

The project will use a sentiment analysis algorithm to determine the sentiment of each comment. The algorithm will use a lexicon of positive and negative words to identify the sentiment of each word. The sentiment of the entire comment will then be determined based on the sentiment of the individual words.


Specific Details:

The project will analyze a representative sample of 10 videos from each channel, selected to cover the entire time period. The time period will be determined by stratified sampler algorithms.

The project will use a sentiment analysis algorithm that has been shown to be accurate in previous studies. The algorithm will be evaluated using a held-out dataset of YouTube comments that were not used to train the algorithm (stanza).

1-The script first scrapes the YouTube channel that the user has selected. The script uses the selenium to retrieve the data.
2- The script then selects 10 videos from the channel. The videos are selected not randomly, but evenly from all video of the channel.
3- The script then iterates through the 10 videos, scraping up to 100 comments from each video. The comments are scraped using the YouTube API.
4- The scraped comments are then saved to a database. The database is used to store the comments for later analysis.
5- Once all of the videos have been scraped, the script analyzes the sentiment of the comments.
6- The results of the sentiment analysis are then displayed on a web page. The web page shows the sentiment of the comments by video.

The project uses multithreading to speed up the scraping of the comments. The scraping of each video is performed in a separate thread. This allows the script to scrape multiple videos at the same time.


Additional Details:

The project is still in its early stages, but it has the potential to be a valuable tool for understanding public opinion.

Potential Applications:

The results of this project could be used by businesses, organizations, and individuals to understand how their content is being received by the public. This information could be used to improve the quality of content, identify areas for improvement, and target specific audiences.
