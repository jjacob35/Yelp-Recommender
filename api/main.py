from flask import Blueprint, request
from flask import Flask, render_template
from .utils.YelpRecommender import *
import logging
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import os


LOG = logging.getLogger(__name__)

main = Blueprint('main', __name__)


REC = YelpRecommender()

@main.route('/')
def inital_load():
    # return 'Hi, the server is up and running'
    return render_template('index.html')


# I don't think we need the following route, we should just let the model use the path to the filtered csv dataset
# directly

# # returns the path to csv
# @main.route('/api/getRawFilteredData')
# def get_filtered_data():
#     return 'Hello'


# trains model
@main.route('/api/trainModel')
def train():
    return 'Hello'

# Endpoint to get Recommendation for a Group of Users of an item in a list of items
# Inputs:
#    users -> Comma seperated list of user IDs, from Yelp Data
#    items -> Comma seperated list of item IDs, from Yelp Data (item in this case is a business)
# Returns:
#    Recommendation with format -> "itemID,rating_for_item"
# Example:
#    inputs:
#       users: "BvcPaFl6N8aQWcdak2v_Sg,b_-AmmH9I3lvhU7PANjFrw,OhOgtmlIWSmikT25wcWBpA,8q7-9Lv6NTlOLqnm5Yk0hg,94u9RZbO2AKAGV-sXLjX4w"
#       items: "0ja9ouEv_w8FWe1F5KMS4g,Cx8BotgsDzKFpH7zSmykkQ"
#    output:
#       recommendation: "0ja9ouEv_w8FWe1F5KMS4g,3.30"
@main.route('/api/getReccomendations', methods=['GET', 'POST'])
def getrecs():
    users = request.args.get('users').split(',')
    items = request.args.get('items').split(',')
    user_ndxs = le.transform(users) # Get the user index
    item_ndxs = le_item.transform(items) # Get the item index
    #payload is inital parameters
    item, rating = REC.getRecommendation(user_ndxs, item_ndxs)
    print(le_item.inverse_transform([item]).item())
    return "%s,%.2f" % (le_item.inverse_transform([item]).item(), rating)


# returns details of a restaurant
@main.route('/api/getRestaurantDetails', methods=['GET', 'POST'])
def get_details():
    # payload is resturant business id
    json_data = open('api/yelp_academic_dataset_business.json')
    counter = 0
    business_id = request.args.get('business_id')

    # temp_business_id = 'BYI0T3QhmYC1Y3fvxnXukg'
    found = False

    for item in json_data:
        jdata = json.loads(item)
        #print(jdata['business_id'])
        if jdata['business_id'] == business_id:
            found = True
            break
        counter += 1

    if not found:
        return 'Cannot find details for that business_id'

    print(item)

    return item
