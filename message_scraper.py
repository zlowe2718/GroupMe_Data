import requests, json

base_url = "https://api.groupme.com/v3"

#gets rid of emojis in txt
def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
#gets group id of the group specified
def get_groupID(base_url, group_name, token):
	response = requests.get(base_url + "/groups", params = {"token" : token})
	response = response.json()["response"]
	for group in response:
		if group["name"] == group_name:
			return group["id"]
	return -1

#TODO: optional flag if wanted group isnt in list	
#returns list of first page of groups
def get_groups(base_url, token):
	response = requests.get(base_url + "/groups", params = {"token" : token})
	response = response.json()["response"]
	group_list = []
	for group in response:
		group_list.append(group["name"])
	return group_list
#group messages in dictionary {reponses: {messages: {want info here}}} form
def pull_messages(base_url, group_id, token, before_id = False):
	if not before_id:
		response = requests.get(base_url + "/groups/" + str(group_id) + "/messages" + "?token=" + token, params = {"limit" : 100})
		return response.json()
	else:
		response = requests.get(base_url + "/groups/" + str(group_id) + "/messages" + "?token=" + token , params = {"limit" : 100, "before_id" : before_id})
		return response.json()

#TODO: check for kicked members/members who left?		
#makes dictionary of members by id then nickname {id : nickname}
def current_member_IDs(base_url, group_id, token, optional_members = False):
	response = requests.get(base_url + "/groups/" + str(group_id), params = {"token" : token, "id" : group_id})
	response = response.json()["response"]["members"]
	member_dict = {}
	#if spaces after commas then deletes those spaces
	
	for i in range(len(optional_members)):
		if optional_members[i][0] == " ":
			optional_members[i] = optional_members[i][1:]
	if type(optional_members) == list:
		for member in response:	
			if member["nickname"] in optional_members:
				#uses nickname instead of name as they are usually the same value and doesn't add Groupme as a person
				#as Groupme does not have a nickname field
				member_dict[member["user_id"]] = member["nickname"][:14]
	else:
		for member in response:
			member_dict[member["user_id"]] = member["nickname"][:14]
	return member_dict


def ini_message_dict(member_dict):
	message_dict = {}
	for mem_id, name in member_dict.items():
		message_dict[name] = {"messages" : 0, "images" : 0, "links" : 0, "mentions" : 0}
	return message_dict

def ini_likes_dict(member_dict):
	likes_dict = {}
	for mem_id, name in member_dict.items():
		likes_dict[name] = {"given" : 0,"recieved" : 0}
	return likes_dict

def ini_bay_dict(member_dict):
	bay_dict = {}
	for mem_id, name in member_dict.items():
		bay_dict[name] = {}
		for i in range(len(member_dict) + 1):
			bay_dict[name]["likes_" + str(i)] = 0
	return bay_dict

def add_extra_likes_field(bay_dict, new_max):
	value = list(bay_dict.values())[0]
	current_val_len = len(value)
	for name in bay_dict:
		for i in range(current_val_len, new_max + 1):
			bay_dict[name]["likes_" + str(i)] = 0 


def add_name_to_bay_dict(bay_dict, new_name):
	bay_dict[new_name] = {}
	value = list(bay_dict.values())[0]
	for i in range(len(value)):
		bay_dict[new_name]["likes_" + str(i)] = 0

def add_to_dict(d, name, keyword, increment):
	d[name][keyword] += increment

def get_last_message_id(json):
	return json["messages"][-1]["id"]
