import csv
import boto3
from botocore.exceptions import ClientError
import pdb
#pdb.set_trace()
#interact

path = '/Users/pog/Desktop/csvproject/TESTTAG3.csv'
csv_container = []

#Create connection to the EC2 API
session = boto3.Session(profile_name='pythontest')
ec2_session = session.resource('ec2')

#Open csv and store into csv_container variable
with open(path, 'rt') as f:
    reader = csv.reader(f)
    for row in reader:
        csv_container.append(row)

#Store the number of keys into a var called tag_keys and values in tag_values
tag_keys = csv_container[0][1:]
tag_values = csv_container[1:]

instance_list = []
for x in csv_container[1:]:
    instance_list.append(x[0])

tag_key_length = len(tag_keys) + 1
row_number = 0



client = boto3.client('ec2')
#Check if instances specified in CSV exist in the account and store any instances beginning with mc- or ams- int to a dictionary.
try:
    response = client.describe_instances(InstanceIds=instance_list,
        Filters=[{
            'Name':'tag:Name',
            'Values': ['mc-*','ams-*']}])
except ClientError as e:
    print(e)
except:
    print("One or more instances provided in the csv could not be found. Please check to see that the instance IDs provided are correct and that they exist within this region.")

#Creates a list called ams_infra_list that will be used to compare against csv list:
ams_instance_list = response['Reservations'][0:]
ams_infra_list = []

for ams_list_item in ams_instance_list:
    ams_infra_list.append(ams_list_item['Instances'][0]['InstanceId'])

#Creates list'csv_instanceid_list' to compare with ams_infra_list to for name tag checking:
csv_instance_container = csv_container[1:]
csv_instanceid_list = []

for csv_instance in csv_instance_container:
    csv_instanceid_list.append(csv_instance[0])

#If there are any instances that exist in both lists AND there is a tag key for "Name" in the csv then exit the script with information.
if (csv_instanceid_list and ams_infra_list) and ('Name' in tag_keys):
    print (('''You cannot change the tag key "Name" for the following instances:
{0}''').format(csv_instanceid_list and ams_infra_list))
    exit()
else:
    print('passed check')



#Defines function to set the tag on an instance
def create_tags(instance_id, key, value):
    ec2 = boto3.resource('ec2')
    ec2.create_tags(Resources=[instance_id], Tags=[{'Key':key, 'Value':value}])

for instance_id in instance_list:
    row_number = row_number + 1
    y = 1
    while y != tag_key_length:
        create_tags(instance_id=instance_id, key=csv_container[0][y], value=csv_container[row_number][y])
        y = y + 1


code.amazon.com/reviews
code.amazon.com create package at bottom.
code.amazon.com/packages/

1.Check CSV format
2. Display a sample of the changes before executing.
