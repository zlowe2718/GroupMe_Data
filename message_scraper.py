import requests
import json

base_url = "https://api.groupme.com/v3"


# gets rid of emojis in txt
def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')


# gets group id of the group specified
def get_groupID(base_url, group_name, token):
    response = requests.get(base_url + "/groups", params={"token": token})
    response = response.json()["response"]
    for group in response:
        if group["name"].lower() == group_name.lower():
            return group["id"]
    raise ValueError


# TODO: optional flag if wanted group isnt in list
# returns list of first page of groups
def get_groups(base_url, token):
    response = requests.get(base_url + "/groups", params={"token": token})
    response = response.json()["response"]
    group_list = []
    for group in response:
        group_list.append(group["name"])
    return group_list


# pulls 100 messages in the form of {reponses: {messages: {message info here}}}
def pull_messages(base_url, group_id, token, before_id=False):
    params = {"limit": 100}

    if before_id:
        params["before_id"] = before_id

    response = requests.get(base_url + "/groups/" + str(group_id) + "/messages"
                            + "?token=" + token, params=params)
    return response.json()


# TODO: check for kicked members/members who left?
# makes dictionary of members by id then nickname {id : nickname}
def current_member_IDs(base_url, group_id, token, optional_members=False):
    response = requests.get(base_url + "/groups/" + str(group_id),
                            params={"token": token, "id": group_id})
    response = response.json()["response"]["members"]
    member_dict = {}

    if type(optional_members) == list:
        # if spaces after commas then deletes those spaces
        for i in range(len(optional_members)):
            if optional_members[i][0] == " ":
                optional_members[i] = optional_members[i][1:]
        # converts all values to lowercase for better matching
        optional_members = [m.lower() for m in optional_members]
        for member in response:
            if member["nickname"].lower() in optional_members:
                # uses nickname instead of name as they are usually
                # the same value and doesn't add Groupme Notifications as a person
                # as Groupme Notifications do not have a nickname field
                member_dict[member["user_id"]] = member["nickname"][:14]
        if len(member_dict) != len(optional_members):
            raise ValueError
    else:
        for member in response:
            member_dict[member["user_id"]] = member["nickname"][:14]
    if not member_dict:
        raise ValueError
    else:
        return member_dict


def get_current_members(base_url, group_id, token):
    response = requests.get(base_url + "/groups/" + str(group_id),
                            params={"token": token, "id": group_id})
    response = response.json()["response"]["members"]
    nicknames_list = []

    for member in response:
        nicknames_list.append(member["nickname"])

    return nicknames_list


def get_all_members(messages_all_info):
    member_ids = {}
    for messages_100 in messages_all_info:
        for message in messages_100:
            if (message["sender_id"] not in member_ids
                    and message["sender_id"] != "system"
                    and message["sender_id"] != "calendar"):
                member_ids[message["sender_id"]] = message["name"]
    return member_ids

# TODO: def get_some_members(messages_all_info, member_list)


def ini_message_dict(member_dict):
    message_dict = {}
    for mem_id, name in member_dict.items():
        message_dict[name] = {"messages": 0, "images": 0, "links": 0,
                              "mentions": 0}
    return message_dict


def ini_likes_dict(member_dict):
    likes_dict = {}
    for mem_id, name in member_dict.items():
        likes_dict[name] = {"given": 0, "received": 0}
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


def is_link(message_text):
    urls = ["http", ".com", ".net", ".org"]
    return any(u in message_text for u in urls)