import boto3
import logging
import urllib2
import json
import re


#setup simple logging for INFO
log = logging.getLogger()
log.setLevel(logging.DEBUG)

s3 = boto3.resource('s3')
ghe_url = 'https://github.azc.ext.hp.com/api/v3'

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
    """

def ghe_orgs(par_ghe_header):
    ghe_orgs_url = ghe_url + '/enterprise/stats/orgs'
    handler=urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request(ghe_orgs_url, headers={"Authorization" : par_ghe_header})
    log.debug (request)
    contents = json.loads(urllib2.urlopen(request).read())

    return str(contents['total_orgs']) +  ' organizations, ' +  str(contents['disabled_orgs']) + ' disabled.\n ' + str(contents['total_teams']) + '  teams with ' + str(contents['total_team_members']) + ' members.'

def ghe_users(par_ghe_header):
    ghe_users_url = ghe_url + '/enterprise/stats/users'
    handler=urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request(ghe_users_url, headers={"Authorization" : par_ghe_header})
    log.debug (request)
    contents = json.loads(urllib2.urlopen(request).read())

    return str(contents['total_users']) +  ' users, ' +  str(contents['admin_users']) + ' admins and ' + str(contents['suspended_users']) + ' suspended.'

def ghe_repos(par_ghe_header):
    ghe_repos_url = ghe_url + '/enterprise/stats/repos'
    handler=urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request(ghe_repos_url, headers={"Authorization" : par_ghe_header})
    log.debug (request)
    contents = json.loads(urllib2.urlopen(request).read())

    return str(contents['total_repos']) +  ' repositories, ' +  str(contents['root_repos']) + ' root and ' + str(contents['fork_repos']) + ' forks.\n' + str(contents['org_repos']) + ' in organizations.\n' + str(contents['total_pushes']) + ' pushes in total.\n' + str(contents['total_wikis']) + ' wikis.'

def ghe_license(par_ghe_header):
    ghe_license_url = ghe_url + '/enterprise/settings/license'
    handler=urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request(ghe_license_url, headers={"Authorization" : par_ghe_header})
    log.debug (request)
    contents = json.loads(urllib2.urlopen(request).read())

    return 'The GHE has ' + str(contents['seats']) +  'seats, and' +  str(contents['seats_used']) + ' are used, ' + str(contents['seats_available']) + ' seats available, License expires at ' + str(contents['expire_at'])

def ghe_main(command, options):
    command_only_list = {
        'orgs'    : ghe_orgs,
        'users'   : ghe_users,
        'repos'   : ghe_repos,
        'license' : ghe_license
        }
    obj = s3.Object(bucket_name='hp-wukong', key='ghe-token.txt')
    response = obj.get()
    ghe_token = response['Body'].read()
    ghe_header = 'token ' + str(ghe_token)
    log.debug ('ghe toke = ' + ghe_header)
    if (options == ''):
        if command not in command_only_list:
            return "I don't know the command '{command}'".format(command=command)
        else:
            return command_only_list[command](ghe_header);
            

def alert():
    print "alert";
    
def lambda_handler(event, context):
    feature_list = {
        'help' : show_help_and_exit,
        'ghe'  : ghe_main,
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
        
   # if feature not in feature_list:
#        return {
#            'text' : "I don't know what '{feature}' is. Perhaps you need to google it :-)".format(feature=feature)
#        }
        

    if (feature == 'help'):
        log.debug("showing help and exiting..")
        return {
            'text' : show_help_and_exit()
            }
            
    if (feature == 'ghe'):
        return {
            'text' : ghe_main(command, options)
            }
            
    if (feature == 'PROBLEM'):
        log.debug("Problem encountered")
        return {
            'text' : identify_problem(raw_args)
            }
    

        
    #define the connection
    #session = boto3.session.Session(region_name='us-west-2')
    #ec2 = session.resource('ec2')
    #ec2 = boto3.client('ec2', region_name='us-west-2')
    ec2 = boto3.resource('ec2')
    #ec2 = boto3.resource('ec2', region_name='us-west-2')

    filters = [
        {
            'Name': 'private-ip-address',
            'Values': ['running']
        }
    ]
        
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #locate all running instances
    #runningInstances = [instance.id for instance in instances]

    #print the instances for logging purposes
    #log.debug(runningInstances)
    
    
#    log.debug(resp)
    

    
    handler=urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    request = urllib2.Request("https://github.azc.ext.hp.com/api/v3/enterprise/settings/license", headers={"Authorization" : ghe_header})
    log.debug (request)
    
    contents = urllib2.urlopen(request).read()

    return {
        'text': "{0}".format(contents)
    }
