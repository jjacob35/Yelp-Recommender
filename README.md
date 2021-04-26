# Yelp-Recommender
Georgia Tech CSE 6242 Final Project

## To run the application

1) Open the templates/index.html file in your browser located at templates/index.html
2) Enter zipcode in text-box 
  - Ex. 30305
4) Enter names in the second text-box 
 - Ex. "Brian Contreras,Suzanne Glover,Cindy Coleman"
5) Map is updated with pins 

## If AWS fails go ahead use Docker as an alternative

1) Make sure is docker installed
2) go to directory that the dockerfile is located at, i.e Yelp-Recommender/
3) docker build -t cse6242:yelprec .
4) docker run -d -p 5000:5000 cse6242:yelprec
5) change variable BASE_URL in index.html to "http://127.0.0.1"


