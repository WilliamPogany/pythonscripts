#!/usr/bin/env python3

""" Creates tags on EC2 instaces specified in a csv file. This requires that
you have programmatic access configured via aws cli(aws configure) AND that the
csv file be formatted properly as such: Cell A1 should be labled
"InstnaceID". Row 1 must include the tag keys AND
Column 1 must include the instance ID which you would like to apply the changes
to. *** See below example ***

Example of csv format:

InstanceID,	            <key>,	    <key>,	    <key>,
i-017ee0e7cf79dc66e,	<value>,	<value>,	<value>,
i-0a811d28f3b9365ef,	<value>,	<value>,	<value>,
i-04c0c3d38a4ef3708,	<value>,    <value>,	<value>,
i-06dd7584077005c74,	<value>,	<value>,	<value>

In addition, this script will check to see if the Name tag on AMS intances
does not get changed. Finally, it will display a sample of the changes to ensure
that the csv and the values provided are what is intended.

Required IAM Permissions:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:CreateTags"
            ],
            "Resource": "*"
        }
    ]
}
"""


import csv
import boto3
from botocore.exceptions import ClientError
import argparse
import pdb


def ec2_client():
    """Create connection to the EC2 API"""
    session = boto3.Session(profile_name='pythontest')
    return session.resource('ec2')


def open_csv(path):
    """Open csv and store into csv_container variable"""
    csv_container = []
    with open(path, 'rt', encoding = "ISO-8859-1") as f:
        reader = csv.reader(f)
        for row in reader:
            csv_container.append(row)
    return csv_container


def create_instance_list(csv_container):
    """Create list from csv."""
    instance_list = []
    for x in csv_container[1:]:
        instance_list.append(x[0])
    return instance_list


def check_for_ams_infra(instance_list):
    """Check if instances specified in CSV exist in the account and store any
    instances beginning with mc- or ams- into to a dictionary.
    """
    response = {}
    try:
        client = boto3.client('ec2')
        response = client.describe_instances(
            InstanceIds=instance_list,
            Filters=[{
                'Name':'tag:Name',
                'Values': ['mc-*','ams-*']}]
            )
        return response
    except ClientError as e:
        print(e)
    except:
        print("One or more instances provided in the csv could not be found. \
        Please check to see that the instance IDs provided are correct and  \
        that they exist within this region.")


def check_for_ams_tags(response, csv_container):
    """Check to make sure instances that are AMS infrucstructre do not have
     their tags mutated.
    """

    # Creates a list called ams_infra_list that will be used to compare against
    # csv list:
    ams_instance_list = response['Reservations'][0:]
    ams_infra_list = []

    for ams_list_item in ams_instance_list:
        ams_infra_list.append(ams_list_item['Instances'][0]['InstanceId'])

    # Creates list'csv_instanceid_list' to compare with ams_infra_list to for
    # name tag checking:
    csv_instance_container = csv_container[1:]
    csv_instanceid_list = []

    for csv_instance in csv_instance_container:
        csv_instanceid_list.append(csv_instance[0])

    # If there are any instances that exist in both lists AND there is a tag
    # key for "Name" in the csv then exit the script with information.
    tag_keys = csv_container[0][1:]

    if (csv_instanceid_list and ams_infra_list) and ('Name' in tag_keys):
        print (('''You cannot change the tag key "Name" for the following instances:
    {0}''').format(csv_instanceid_list and ams_infra_list))
        exit()
    else:
        print(" ")
        print('passed check')
        print(" ")
    return tag_keys


def display_sample_changes(tag_keys, csv_container):
    """Display a sample of the changes that are going to be made once applied."""
    print('To ensure that the CSV has been formated correctly this tool will \
display a sample of the changes it is going to make.')
    print(" ")
    tag_values = csv_container[1:]
    print(('The following changes will be applied to instance {0}. Please \
verify that this sample are the intended changes.').format(tag_values[0][0]))
    sample_of_changes = dict(zip(tag_keys, tag_values[0][1:]))

    print("Key\t\tValue")
    num = 0
    for i in sample_of_changes:
        num = num + 1
        print("{}\t\t{}".format(i,sample_of_changes[i]))
        if num != 4:
            input("Press Enter to continue...")
        else:
            break

    answer = input("If the sample looks correct press Y to execute these \
changes: ")
    if answer.lower() == 'y':
        print('Executing changes')
    else:
        exit()


def tag_function(instance_id, key, value):
    """Defines function to set the tag on an instance"""
    ec2 = boto3.resource('ec2')
    ec2.create_tags(Resources=[instance_id], Tags=[{'Key':key, 'Value':value}])


def create_tags(tag_keys, instance_list, csv_container):
    """Creates the tags on EC2 instances specfied."""
    tag_key_length = len(tag_keys) + 1
    row_number = 0

    for instance_id in instance_list:
        row_number = row_number + 1
        y = 1
        while y != tag_key_length:
            tag_function(
                instance_id=instance_id,
                key=csv_container[0][y],
                value=csv_container[row_number][y]
                        )
            y = y + 1

def main():
    path = input("Enter the absolute path of the csv file:")
    ec2_session = ec2_client()
    csv_container = open_csv(path)
    instance_list = create_instance_list(csv_container)
    response = check_for_ams_infra(instance_list)
    tag_keys = check_for_ams_tags(response, csv_container)
    display_sample_changes(tag_keys, csv_container)
    create_tags(tag_keys, instance_list, csv_container)

if __name__ == "__main__":
    # execute only if run as a script
    main()
