import config

ghe_url = config.config["ghe_url"]

def ghe_monitor(par_options):
    if len(par_options) < 2:
        return 'There should be 2 parameter for monitor command.\n For example: monitor cpu 1d'
    monitor_type = par_options[0]
    monitor_time = par_options[1]
    log.debug ('monitor_type :' + str(monitor_type))
    log.debug ('monitor_time :' + str(monitor_time))
    s3_gragh_url = 'https://s3.amazonaws.com/hp-wukong/' + str(monitor_type) + '_' + str(monitor_time) + '.png'
    return s3_gragh_url

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
        'license' : ghe_license,
        'monitor' : ghe_monitor
        }
    log.debug ('command :' + str(command))
    log.debug ('options :' + str(options))
    obj = s3.Object(bucket_name=config.config["hp-wukong"], key=config.config["ghe_token_file"])
    response = obj.get()
    ghe_token = response['Body'].read()
    ghe_header = 'token ' + str(ghe_token)
    log.debug ('ghe toke = ' + ghe_header)
    if (options == ''):
        if command not in command_only_list:
            return "I don't know the command '{command}'".format(command=command)
        else:
            return command_only_list[command](ghe_header);
    else:
        return command_only_list[command](options);
