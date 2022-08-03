# GroupMe_Data
Outputs data on groupme chat messages

Prompts user for api key, then group to analyze, then current users or all users to look at.

Evaluates messages sent by person by message type (i.e. message, image, or link), then evaluates how many likes were recieved for that message type. Plots all data in bar graphs using matplotlib.
Also plots a bayesian score for each person which factors in how many messages recieved higher like counts.  I.e. if the most amount of likes any message got was 10, this score evaluates how many messages got zero likes, one like, two likes, ..., ten likes for each user, so that users with a higher amount of messages with more likes will rank higher as opposed to total likes / total message average.
