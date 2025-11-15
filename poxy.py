#!/usr/bin/python3

import json
import sys
from pprint import pprint
import digitalocean  
import aws
import ssh

def load_config(configfile):
    """
    Loads the given cloud config provided and will return an object for the configured cloud
    """
    if configfile =="":
        print("Error: Configuration file not provided")
        sys.exit(1)
    
    __cloud = None
    with open(configfile) as data_file:    
        data = json.load(data_file)
    
    return data

data = load_config(sys.argv[1])
proxy = ssh.Proxy(data["socks"]["key"]["private"], data["socks"]["port"])

#######
# The Cloud object is used to get the details about the running instances and
# it is also used to get the public address to which the proxy will be 
# connecting to.
#######
if data["aws"]["username"] != "":
    cloud = aws.Cloud( data["aws"]["username"])
elif data["digitalocean"]["token"] != "":
    cloud = digitalocean.Cloud(data["digitalocean"]["token"], data["digitalocean"]["username"])

if cloud == None:
    print("Error Initializing Cloud")
    sys.exit(1)

###
#   WIP: 
#     Verify if there is an instance to be used, if not, then create the 
#     smallest possible instance syncronously and return the IP Address
###
ip_address = cloud.getPublicAddress()

######
# connects to the instance and opens the specified port, 
# then waits until ssh exits to finish the script execution.
######
proxy.connect( cloud.username, ip_address, data["socks"]["port"]) 
proxy.just_wait()

#####
#   TODO:
#       If the instance used was created by the script, destroy it and
#       destroy any linked resource too before finishing the script.
#           async ways (applicable if the script was restarted): 
#               - look for hash-ed tags.
#               - look for hashed name of the instance.
#####
