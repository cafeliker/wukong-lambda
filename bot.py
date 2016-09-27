import boto3
import logging
import urllib2
import json
import ghe.ghe_command
import aws.self_healing
import config


#setup simple logging for INFO
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# shows the help page
def show_help_and_exit():
    return """
    ```

    help                              -   Print this help page
    ghe orgs                          -   Lists orgs using github enterprise
    ghe users                         -   List github enterprise users
    ghe repos                         -   List github enterprise reposes
    ghe license                       -   Show github enterprise license status
    ghe monitor cpu [1d,1w,1mon]      -   Show the cpu monitor graph of github enterprise servers
    ghe monitor memory [1d,1w,1mon]   -   Show the memory monitor graph of github enterprise servers
    ```
    """


def lambda_handler(event, context):
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
            'text' : ghe.ghe_command.ghe_main(command, options)
            }
            
    if (feature == 'PROBLEM'):
        log.debug("Problem encountered")
        return {
            'text' : aws.self_healing.identify_problem(raw_args)
            }

    if (feature == 'RECOVERY'):
        log.debug("Recover encountered")
        return {
            'text' : "I'm very happy that you're back up again :-)"
            }
        
    return {
        'text': "{0}".format("Sorry, I didn't understand. Please use Wukong help") 
    }
