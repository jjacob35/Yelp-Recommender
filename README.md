# Yelp-Recommender
Georgia Tech CSE 6242 Final Project



DESCRIPTION

This package contains everything related to our CS 6242 Yelp Recommender Project. The /api/ folder contains the core part of our backend of our project. Our API is written in main.py and that's where you'll find the implementation of all of our requests. Inside /api/utils/ folder you can find the code for our reccomendation model. Under /static you will find our styling sheet and under /templates you will find our html file which is used to open and use our application. The preprocessing.ipynb file contains our pyspark code to filter out data in the dataset. In addition, we also have a Dockerfile in the repository just in case th API needs to be run locally. Lastly /data folder contains the filtered datasets that our API uses.


INSTALLATION

Thankfully due to hosting our API on AWS Elastic Compute Service (ECS), we were easily able to host our API on the cloud so no installation is needed. However if AWS fails, here are the instructions to start locally hosted version of our API through docker.

1) Make sure is docker installed
2) change variable BASE_URL in index.html to "http://127.0.0.1"
3) go to directory that the dockerfile is located at, i.e Yelp-Recommender/
4) In termimal run "docker build -t cse6242:yelprec ."
5) Then in terminal run "docker run -d -p 5000:5000 cse6242:yelprec"


EXECUTION

1) Open the templates/index.html file in your browser located at templates/index.html
2) Enter zipcode in text-box 
  - Ex. "30305"
4) Enter names in the second text-box 
 - Ex. "Brian Contreras,Suzanne Glover,Cindy Coleman"
5) Map is updated with pins after 1-2 minutes (locally run server will run faster)

Dataset Used: 
https://www.kaggle.com/yelp-dataset/yelp-dataset?select=yelp_academic_dataset_business.json
