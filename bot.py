import boto3
import logging
import urllib2
import json
import re
import wukong.ghe_command
import config


#setup simple logging for INFO
log = logging.getLogger()
log.setLevel(logging.DEBUG)

s3 = boto3.resource('s3')

# Starts a instance given an Amazon instance
def start_instance(instance):
    try:
        log.info("Starting instance " + instance.id)
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


# shows the help page
def show_help_and_exit():
    return """
    help          -   print this help page
    ghe orgs      -   Lists orgs using GHEs
    ghe users     -   List github users
    ghe repos     -   List github reposes
    ghe license   -   Show Github license status
    ghe monitor cpu [1d,1w,1mon]   -   Show the cpu monitor gragh of github server
    ghe monitor memory [1d,1w,1mon]   -   Show the memory monitor gragh of github server
    """


def alert():
    print "alert";
    
def lambda_handler(event, context):
    feature_list = {
        'help' : show_help_and_exit,
        'alert': alert
        }
    #assert context
    #log.debug(event)
    bot_event = event

    trigger_word = bot_event['trigger_word']
    raw_text = bot_event['text']
    raw_args = raw_text.replace(trigger_word, '').strip()

    args = raw_args.split()
    log.debug("[lambda_handler] args:{0}".format(args))
    
    if len(args) >= 1:
        feature = args[0]

    command = None
    if len(args) >= 2:
        command = args[1]

    options = ''
    if len(args) >= 3:
        options = args[2:]

    log.debug("[lambda_handler] feature:'{0}' command:'{1}' options:'{2}'".format(
        feature, command, options))
        
    log.debug ('feature: ' + str(feature))

    if (feature == 'help'):
        log.debug("showing help and exiting..")
        return {
            'text' : show_help_and_exit()
            }
            
    if (feature == 'ghe'):
        return {
            'text' : wukong.ghe_command.ghe_main(command, options)
            }
            
    if (feature == 'PROBLEM'):
        log.debug("Problem encountered")
        return {
            'text' : identify_problem(raw_args)
            }
        
    return {
        'text': "{0}".format('sorry, it is too complex for me...')
    }
