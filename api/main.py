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
import urllib.request
import pandas as pd
import pandasql as ps

LOG = logging.getLogger(__name__)

main = Blueprint('main', __name__)

REC = YelpRecommender()

data = pd.read_csv('data/business_list.csv')
name_map = pd.read_csv('data/list_of_names.csv')


@main.route('/')
def inital_load():
    return 'Hi, the server is up and running'
    # return render_template('../templates/index.html')



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
    users_names = request.args.get('users').split(',')
    users = [list(name_map.loc[name_map['name'] == name]["userID"])[0] for name in users_names]
    items = request.args.get('items').split(',')
    numRes = int(request.args.get('n'))
    user_ndxs = le.transform(users)  # Get the user index
    item_ndxs = le_item.transform(items)  # Get the item index
    # payload is inital parameters
    recs = REC.getRecommendation(user_ndxs, item_ndxs)
    # item, rating = REC.getRecommendation(user_ndxs, item_ndxs)
    # print(le_item.inverse_transform([item]).item())
    # data = pd.read_csv('data/business_list.csv')
    preds_list = list(recs.reshape((1,len(item_ndxs)))[0])
    business_rating = []
    for i in range(len(preds_list)):
        business_rating.append((items[i], preds_list[i]))

    business_rating = sorted(business_rating, key=lambda x:x[1], reverse=True)
    print(business_rating)
    out_json = {}
    for i in range(numRes):
        if i == len(business_rating):
            break
        new_business_id, rating = business_rating[i]
        # new_business_id = le_item.inverse_transform([item]).item()
        q1 = """SELECT * FROM data WHERE business_id = '{}' """.format(new_business_id)
        result = ps.sqldf(q1, globals())
        json_result = result.to_dict()
        json_result["reccomendation_level"] = float(rating)
        out_json[new_business_id] = json_result
    # print(out_json)

    # json_result_dict = {}
    # json_result_dict["info"] = json_result
    # json_result["reccomendation_level"] = float(rating)


    return out_json


# Endpoint to get Details for a Resturant
# Inputs:
#    business_id -> business_id
# Returns:
#    JSON with specific details on that business
# Example:
#    inputs:
#       business_id: "BYI0T3QhmYC1Y3fvxnXukg"
@main.route('/api/getRestaurantDetails', methods=['GET', 'POST'])
def get_details():
    # payload is resturant business id
    business_id = request.args.get('business_id')


    counter = 0

    found = False
    q1 = """SELECT * FROM data WHERE business_id = '{}' """.format(business_id)
    result = ps.sqldf(q1, globals())
    json_result = result.to_json()
    if result.shape[0] == 0:
        return 'Cannot find details for that business_id'

    return json_result


# Endpoint to get All Valid Locations For A specific zip-code
# Inputs:
#    zip-code -> zip-code
# Returns:
#    JSON with a bunch of resturant business IDs
# Example:
#    inputs:
#       business_id: 30305
@main.route('/api/getLocationsBasedOnZipcode', methods=['GET', 'POST'])
def getLocations():
    zipcode = request.args.get('zipcode')

    # data = pd.read_csv('data/business_list.csv')
    q1 = """SELECT * FROM data WHERE postal_code = '{}' """.format(zipcode)

    result = ps.sqldf(q1, globals())
    result = result['business_id']
    json_result = result.to_json()
    if result.shape[0] == 0:
        return 'Cannot find Enough Locations for that Zipcode'

    return json_result
