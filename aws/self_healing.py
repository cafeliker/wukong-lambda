import logging
import boto3
import re

def start_instance(instance):
    try:
        log.info("Starting instance " + instance.id)
        log.info("Waiting for instance to stop")
        instance.wait_until_stopped()
        log.info("Finish waiting. Instance presumably stopped")
        instance.start()
        log.info("Finish running start instance")
        return 'starting the ec2 instance {0} with IP address {1}'.format(instance.id, instance.private_ip_address)
    except Exception, e2:
        log.error("Unable to start instance " + instance.id)
        error2 = "Error2: %s" % str(e2)
        return 'start the ec2 instance ' + instance.id + ' failed: ' + error2


# starts a machine given the IP address of the machine
def start_machine(ip):
    
    # Filter criteria 
    filters = [
        {
            'Name'  : 'private-ip-address',
            'Values': [ip]
        }
    ]
    
    ec2 = boto3.resource('ec2')
    filtered = ec2.instances.filter(Filters=filters)
    #return start_instance(filtered[0]);
    # Should return only 1 instance, but we need to use for loop
    # as we can't access individual array element
    for instance in filtered:
       return start_instance(instance)
        
    


# identify what problem we have and what instance is causing the problem
def identify_problem(err_msg):
    regex_str = r'^PROBLEM Service Alert: (.*) for ghe-primary \((.*)\) is (.+): (.*)'
    regex = re.compile(regex_str)
    match = regex.search(err_msg)
    if match:
        what = match.group(1)
        ip = match.group(2)
        severity = match.group(3)
        msg = match.group(4)
        return start_machine(ip)
        print "What - {0}".format(what);
        print "IP/Hostname - {0}".format(ip)
        print "severity - {0}".format(severity)
        print "msg - {0}".format(msg)
    else:
        return "No match : Unable to find in {0}".format(err_msg)



