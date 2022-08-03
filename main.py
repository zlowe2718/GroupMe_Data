#main exceutable
import message_scraper as ms 
import requests
import json
import plotting_setup as ps
import matplotlib
import matplotlib.pyplot as plt

base_url = "https://api.groupme.com/v3"

#starts prompting user for information
#asks for user token
while True:
    try:
        token = input("Enter your token id: ")
        ms.get_groups(base_url, token)
        break
    except KeyError:
        print("Please enter a valid token")
    
#asks for a group in the list
while True:
    try:
        group = input("Please select a group from the list" + str(ms.get_groups(base_url, token)) + ": ")
        group_id = ms.get_groupID(base_url, group, token)
        break
    except ValueError:
        print("Please enter a group from the list. You may have spelled one wrong")

while True:
    try:
        #asks for members to evaulate
        members = input("Please enter group members as a list to evaulate as comma separated values.\
                        Leave blank for all current members, or write 'all' for all members "
                        + str(ms.get_current_members(base_url, group_id, token)) + ":")
        all_members = False
    
        if "," in members:
            member_id_dict = ms.current_member_IDs(base_url, group_id, token, members.split(","))
        elif members == "all":
            all_members = True
            member_id_dict = ms.current_member_IDs(base_url,group_id, token)
        elif members == "":
            member_id_dict = ms.current_member_IDs(base_url,group_id, token)
        else:
            member_id_dict = ms.current_member_IDs(base_url, group_id, token, members.split(","))
        break
    except (KeyError, ValueError):
        print("You may have spelled a member wrong.  Please enter in the form of member1, member2 etc.")

message_dict = ms.ini_message_dict(member_id_dict)
likes_dict = ms.ini_likes_dict(member_id_dict)
likes_per_mess_type = ms.ini_message_dict(member_id_dict)

#message total to pull all messages in groups of 100
message_total = ms.pull_messages(base_url, group_id, token)["response"]["count"]
last_message_id = False

#ordered by {how many likes : how many messages recieved that many likes}
#ie {Zach : {likes_2:4}} would mean 4 messages recieved 2 likes for user Zach
#{name : {likes_0 : #messages, likes_1 : #messages}} etc.
bayesian_dict = ms.ini_bay_dict(member_id_dict)

#max_likes for bayesian calculation based off of max likes ever recieved in chat

max_likes = len(bayesian_dict)


#crux of data collection, features to add should be placed here
for i in range(message_total // 100 + 1):
    responseJson = ms.pull_messages(base_url, group_id, token, last_message_id)["response"]

    #data collection for 100 messages at a time start
    for message in responseJson["messages"]:
        #Adds member if all members are selected and if the member is no longer currently in the chat
        if (not message["sender_id"] in member_id_dict and all_members and not message["sender_id"] == "system"
         and not message["sender_id"] == "calendar") or (not message["sender_id"] in member_id_dict 
         and message["name"] in members):
            #establishes new member in the approved members list and limits to 13 characters
            member_id_dict[message["sender_id"]] = message["name"][:14]

            #initializes new member in the established dictionaries
            message_dict[message["name"][:14]] = {"messages" : 0, "images" : 0, "links" : 0, "mentions" : 0}
            likes_dict[message["name"][:14]] = {"given" : 0,"received" : 0}
            likes_per_mess_type[message["name"][:14]] = {"messages" : 0, "images" : 0, "links" : 0, "mentions" : 0}

            #updates bayesian dictionary for new member
            ms.add_name_to_bay_dict(bayesian_dict, message["name"][:14])

        # this is for updating total likes in chat and updating the bayesian dictionary respectively
        if len(message["favorited_by"]) > max_likes:
            max_likes = len(message["favorited_by"])
            #checks to see if it exists in case a user was inputted who hasn't 
            #shown up in the messages log yet
            if len(bayesian_dict) != 0:
                ms.add_extra_likes_field(bayesian_dict, max_likes)

        #add extra likes to bayesian dictionary after new user has been added
        #and there were more likes than fields currently
        if len(bayesian_dict) != 0:
            if len(list(bayesian_dict.values())[0]) < max_likes:
                ms.add_extra_likes_field(bayesian_dict, max_likes)

        #this segment is for messages data and likes recieved
        if message["sender_id"] in member_id_dict:          
            name = member_id_dict[message["sender_id"]]
            if name in message_dict:
                num_likes = len(message["favorited_by"])
                ms.add_to_dict(likes_dict, name, "received", num_likes)
                ms.add_to_dict(bayesian_dict, name, "likes_" + str(num_likes), 1)


                #adds images sent to total count and keeps track of likes per image
                if len(message["attachments"]) != 0:
                    for attachment in message["attachments"]:
                        if attachment["type"] == "image":
                            ms.add_to_dict(message_dict, name, "images", 1)
                            ms.add_to_dict(likes_per_mess_type, name, "images", len(message["favorited_by"]))

                        elif attachment["type"] == "mentions":
                            ms.add_to_dict(message_dict, name, "mentions", len(attachment["user_ids"]))
                            ms.add_to_dict(likes_per_mess_type, name, "mentions", len(message["favorited_by"]))             
                        

                #checks for links and adds to total sent and likes recieved for links
                elif ms.is_link(message["text"]):
                    ms.add_to_dict(message_dict, name, "links", message["text"].count("http"))
                    ms.add_to_dict(likes_per_mess_type, name, "links", len(message["favorited_by"]))
                
                #otherwise it is a standard message and does the same as above
                else:
                    ms.add_to_dict(message_dict, name, "messages", 1)
                    ms.add_to_dict(likes_per_mess_type, name, "messages", len(message["favorited_by"]))

        #adds given likes to each person by checking who liked a post
        if len(message["favorited_by"]) != 0:
            
            for send_id in message["favorited_by"]:
                #since favorited_by field is listed by sender_id we need to cross reference
                #it to the member_id_dict to get the actual name
                if send_id in member_id_dict:
                    ms.add_to_dict(likes_dict, member_id_dict[send_id], "given", 1)

    #updates last message id to pull next 100 messages at the next iteration
    last_message_id = ms.get_last_message_id(responseJson)

print("all messages evaluated")

#start plotting
plt.close()

#just need the names so any dictionary would work
label = ps.set_labels(message_dict)

#initializes lists for plotting y values of bar charts
bay_likes = []
message_by_type = [[] for _ in range(4)]
message_likes_by_type = [[] for _ in range(4)]
message_ratios = [[] for _ in range(4)]
likes_by_type = [[] for _ in range(2)]

message_label = ["messages", "images", "links", "mentions"]
likes_label = ["received", "given"]

#sets values in lists for each name or x-value in labels list 
for name in label:
    bay_likes.append(round(ps.bayesian_rating(bayesian_dict,name),2))

    for i in range(4):
        message_by_type[i].append(message_dict[name][message_label[i]])
        message_likes_by_type[i].append(likes_per_mess_type[name][message_label[i]])
        try:
            message_ratios[i].append(round(likes_per_mess_type[name][message_label[i]]/message_dict[name][message_label[i]],2))
        except ZeroDivisionError:
            message_ratios[i].append(0)

    for i in range(2):
        likes_by_type[i].append(likes_dict[name][likes_label[i]])

#plots
fig, ax = plt.subplots()
fig.set_size_inches(14.4, 8.9)
ps.rects_per_type(message_by_type, message_label, fig, ax)
ps.set_title_and_others("Total Messages Sent by Type", label, fig, ax)

fig1, ax1 = plt.subplots()
fig1.set_size_inches(14.4, 8.9)
ps.rects_per_type(message_likes_by_type, message_label, fig1, ax1)
ps.set_title_and_others("Total Likes Recieved by Type", label, fig1, ax1)

fig2, ax2 = plt.subplots()
fig2.set_size_inches(14.4, 8.9)
ps.rects_per_type(message_ratios, message_label, fig2, ax2)
ps.set_title_and_others("Likes per Message Ratio by Type", label, fig2, ax2)

fig3, ax3 = plt.subplots()
fig3.set_size_inches(14.4, 8.9)
ps.rects_per_type(likes_by_type, likes_label, fig3, ax3)
ps.set_title_and_others("Likes Recived and Given by Person", label, fig3, ax3)

fig4, ax4 = plt.subplots()
fig4.set_size_inches(14.4, 8.9)
ps.rects(bay_likes, "Score", fig4, ax4)
ps.set_title_and_others("Bayesian Score of Likes", label, fig4, ax4)

plt.show()