data = {} #this holds all the data from STELUM, PULSE, and .eig files during the session
#this is actually necessary as a dcc.Store only has only ~10MB of data if storage_type == "session"
#which is clearly cooked for .eig files...
graph_options = {}