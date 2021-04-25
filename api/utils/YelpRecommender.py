from joblib import dump, load
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import os

# Trained Class Encoders to map UserID and ItemID from Yelp to a number
le = load('./api/utils/userlabelenc_allData_correct.joblib') 
le_item = load('./api/utils/itemlabelenc_allData_correct.joblib')
# =================================================================

# PyTorch Neural Collaborative Filtering Model Implementation
EMBEDDING_SIZE = 16
HIDDEN_SIZE = 64

class NCF(nn.Module):

  def __init__(self):
    torch.manual_seed(0)
    np.random.seed(0)
    super(NCF, self).__init__()

    self.user_emb = nn.Embedding(len(le.classes_), EMBEDDING_SIZE)
    self.item_emb = nn.Embedding(len(le_item.classes_), EMBEDDING_SIZE)
    self.fc1 = nn.Linear(EMBEDDING_SIZE * 2, HIDDEN_SIZE)
    self.fc2 = nn.Linear(HIDDEN_SIZE, HIDDEN_SIZE)
    self.output = nn.Linear(HIDDEN_SIZE, 1)
    self.relu = nn.ReLU()

  def forward(self, data_tuple):
    userIDs, itemIDs = data_tuple
    user_embeddings = self.user_emb(userIDs)
    item_embeddings = self.item_emb(itemIDs)
    cat = torch.cat((user_embeddings, item_embeddings), dim=1)
    h1 = self.relu(self.fc1(cat))
    h2 = self.relu(self.fc2(h1))
    output = self.relu(self.output(h2))
    return output
# =================================================================

# Load Trained Model from Exported State Dictionary
TRAINED_MODEL = NCF()
ncf_state_dict = torch.load('./api/utils/ncf_all_statedict_64d300e.pt', map_location=torch.device('cpu'))
TRAINED_MODEL.load_state_dict(ncf_state_dict)
# =================================================================

# Utility Class for Interacting with the Model to get Recommendations
class YelpRecommender:
    
    def __init__(self):
        self.trained_model = TRAINED_MODEL
    
    # Computes a Group Embedding by averageing the Embeddings of the users in the group
    def getGroupEmbed(self, groupUserIDs, item):
        rawgroup = self.trained_model.user_emb(groupUserIDs) # fewusers should be torch Tensor of userID_ndx's
        groupembed = torch.mean(rawgroup, 0)
        groupembed = groupembed.reshape((1,16))

        item_embeddings = self.trained_model.item_emb(item) # item
        cat = torch.cat((groupembed, item_embeddings), dim=1)

        h1 = self.trained_model.relu(self.trained_model.fc1(cat))
        h2 = self.trained_model.relu(self.trained_model.fc2(h1))
        output = self.trained_model.relu(self.trained_model.output(h2))
        return output.detach().cpu().numpy()

    # Iterates through all items and predicts what the group embedding would rate an item and returns max item and predicted rating
    def getRecommendation(self, groupUserIDs, listofItems):
        userIDsTensor = torch.LongTensor(groupUserIDs)
        # maxItem = -1
        # maxRating = float('-inf')
        itemratingtuples = []
        for item in listofItems:
            itemTensor = torch.LongTensor([item])
            pred = self.getGroupEmbed(userIDsTensor, itemTensor).item()
            itemratingtuples.append((item, pred))
            # if pred > maxRating:
            #     maxRating = pred
            #     maxItem = item
        itemratingtuples = sorted(itemratingtuples, key=lambda x: x[1], reverse=True)
        return itemratingtuples#(maxItem, maxRating)
# =================================================================