from joblib import dump, load
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import os

# Trained Class Encoders to map UserID and ItemID from Yelp to a number
le = load('./api/utils/userlabelenc_allData_correct.joblib') 
le_item = load('./api/utils/itemlabelenc_allData_correct.joblib')
# le = load('./userlabelenc_allData_correct.joblib') 
# le_item = load('./itemlabelenc_allData_correct.joblib')
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
# ncf_state_dict = torch.load('./ncf_all_statedict_64d300e.pt', map_location=torch.device('cpu'))
TRAINED_MODEL.load_state_dict(ncf_state_dict)
# =================================================================

# Utility Class for Interacting with the Model to get Recommendations
class YelpRecommender:
    
    def __init__(self):
        self.trained_model = TRAINED_MODEL
    
    # Computes a Group Embedding by averageing the Embeddings of the users in the group
    def getGroupEmbed(self, user_ndxs_tensor, item_ndxs_tensor):
        rawgroup = self.trained_model.user_emb(user_ndxs_tensor) # fewusers should be torch Tensor of userID_ndx's
        groupembed = torch.mean(rawgroup, 0)
        groupembed = groupembed.reshape((1,16))

        repeat_group = torch.LongTensor([])
        for _ in range(len(item_ndxs_tensor)):
            repeat_group = torch.cat((repeat_group, groupembed))

        item_embeddings = self.trained_model.item_emb(item_ndxs_tensor) # item
        cat = torch.cat((repeat_group, item_embeddings), dim=1)

        h1 = self.trained_model.relu(self.trained_model.fc1(cat))
        h2 = self.trained_model.relu(self.trained_model.fc2(h1))
        output = self.trained_model.relu(self.trained_model.output(h2))
        return output.detach().cpu().numpy()

    # Iterates through all items and predicts what the group embedding would rate an item and returns max item and predicted rating
    def getRecommendation(self, groupUserIDs, listofItems):
        userIDsTensor = torch.LongTensor(groupUserIDs)
        # maxItem = -1
        # maxRating = float('-inf')
        # itemratingtuples = []
        itemTensor = torch.LongTensor(listofItems)
        results = self.getGroupEmbed(userIDsTensor, itemTensor)
        # for item in listofItems:
        #     itemTensor = torch.LongTensor([item])
        #     pred = self.getGroupEmbed(userIDsTensor, itemTensor).item()
        #     itemratingtuples.append((item, pred))
        #     # if pred > maxRating:
        #     #     maxRating = pred
        #     #     maxItem = item
        # itemratingtuples = sorted(itemratingtuples, key=lambda x: x[1], reverse=True)
        return results#(maxItem, maxRating)
# =================================================================

if __name__ == '__main__':
    REC = YelpRecommender()
    users = ["b_-AmmH9I3lvhU7PANjFrw","OhOgtmlIWSmikT25wcWBpA","8q7-9Lv6NTlOLqnm5Yk0hg","94u9RZbO2AKAGV-sXLjX4w"]
    items = ["3ZVgig7uux9jVtEZna5NgA","5vxGL-_P9aHJg41q9sKwDQ","E8Fl7qE_y-bhRbkkdLbWNw","INLhagLkYQwtzE9auIORpQ","lrBJoSfNnM0UtLLTJ4q_Sw","qVRZMDCFVoAa3mam8adm6w","uUlgfZBhsS_uvyIJ3fk1RA"]
    user_ndxs = le.transform(users)  # Get the user index
    item_ndxs = le_item.transform(items)  # Get the item index
    itemTensor = torch.LongTensor(item_ndxs)
    print(itemTensor)
    userTensor = torch.LongTensor(user_ndxs)
    rawgroup = TRAINED_MODEL.user_emb(userTensor)
    print(rawgroup)
    groupembed = torch.mean(rawgroup, 0)
    groupembed = groupembed.reshape((1,16))
    print(groupembed)
    repeat_group = torch.LongTensor([])
    for _ in range(len(item_ndxs)):
        repeat_group = torch.cat((repeat_group, groupembed))
    print(repeat_group)
    print(repeat_group.shape)
    item_embeddings = TRAINED_MODEL.item_emb(itemTensor) # item
    print(item_embeddings)
    print(item_embeddings.shape)
    cat = torch.cat((repeat_group, item_embeddings), dim=1)
    print(cat)
    print(cat.shape)

    h1 = TRAINED_MODEL.relu(TRAINED_MODEL.fc1(cat))
    h2 = TRAINED_MODEL.relu(TRAINED_MODEL.fc2(h1))
    output = TRAINED_MODEL.relu(TRAINED_MODEL.output(h2))
    print(output.detach().cpu().numpy())