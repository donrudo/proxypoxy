import json
import sys
import boto3

class Cloud:
    ec2 = None
    username = None
    def __init__(self, username=None):
        self.ec2 = boto3.client("ec2")
        self.username = username
    
    def create_instance(self, amid):
        self.ec2.create_instances(ImageId='', MinCount=1, MaxCount=1)
    
    def destroy_instance(self, amid):
        self.ec2.create_instances(ImageId='', MinCount=1, MaxCount=1)

    def getPublicAddress(self):
        """
        Returns the public ip address from the first instance found
        """
        reservations = self.list_instances()
        instances = reservations["Reservations"][0]["Instances"]
        
        ip_address = None
        for instance in instances:
            if instance["PublicIpAddress"] != "":
                ip_address = instance["PublicIpAddress"]
                break
        return ip_address

    def list_instances(self):
        data = self.ec2.describe_instances()
        return data
    
    def debug(self,req):
        print("status", req.status, file=sys.stderr)
        print("ratelimit-remaining:", req.getheader("ratelimit-remaining"), file=sys.stderr)
        print("ratelimit-limit:", req.getheader("ratelimit-limit"), file=sys.stderr)
        print("ratelimit-reset:", req.getheader("ratelimit-reset"), file=sys.stderr)
