import csv
import boto3

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
