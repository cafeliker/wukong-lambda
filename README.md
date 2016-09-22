# wukong-lambda

This is a bot service named wukong and running in AWS Lambda. After a little technical investigation, we decided to use Python than NodeJS as the Lambda funtion runtime.


Slack room is at https://huaguomountain.slack.com.

## Installation
1. Clone this repo and zip the codes
2. Create a Lambda function with runtime Python 2.7, and upload the zip package and choose Handler as bot.lambda_handler, and then select a Role with AWS S3 and EC2 access
3. Create an API Gateway API
4. Create a method of type: POST
5. Select Integration Type: Lambda
6. Select the region in which you created your Lambda function
7. Select the Lambda Function you created
8. Click "Integration Request"
9. At the bottom of this Page select "Add mapping Template"
10. For content type please specify: "application/x-www-form-urlencoded"
11. Insert the template code below into the text field for the template. This code converts a URL Encoded form post into JSON for your Lambda function to parse
12. Deploy your API
13. In Slack, Go to Team settings
14. From the Menu, choose Configure Apps
15. Select Custom Integrations in the left menu
16. Select Outgoing Webhooks
17. Choose Add Configuration -> Add Outgoing WebHooks integration, and pick a trigger word (e.g. wukong) for your Bot
18. In URL, put the URL created by your API Gateway Deployment
19. Go back Custom Integrations page, and select Incoming WebHooks
20. Choose Add Configuration, and select Post to Channel, e.g. #general, then click Add Incoming WebHooks integration
21. Use the generated WebHook URL in the Nagios configuration to allow Nagios send the messages to Slack channel. 

#### Template code for Integration Request:
```
## convert HTML POST data or HTTP GET query string to JSON
 
## get the raw post data from the AWS built-in variable and give it a nicer name
#if ($context.httpMethod == "POST")
 #set($rawAPIData = $input.path('$'))
#elseif ($context.httpMethod == "GET")
 #set($rawAPIData = $input.params().querystring)
 #set($rawAPIData = $rawAPIData.toString())
 #set($rawAPIDataLength = $rawAPIData.length() - 1)
 #set($rawAPIData = $rawAPIData.substring(1, $rawAPIDataLength))
 #set($rawAPIData = $rawAPIData.replace(", ", "&"))
#else
 #set($rawAPIData = "")
#end
 
## first we get the number of "&" in the string, this tells us if there is more than one key value pair
#set($countAmpersands = $rawAPIData.length() - $rawAPIData.replace("&", "").length())
 
## if there are no "&" at all then we have only one key value pair.
## we append an ampersand to the string so that we can tokenise it the same way as multiple kv pairs.
## the "empty" kv pair to the right of the ampersand will be ignored anyway.
#if ($countAmpersands == 0)
 #set($rawPostData = $rawAPIData + "&")
#end
 
## now we tokenise using the ampersand(s)
#set($tokenisedAmpersand = $rawAPIData.split("&"))
 
## we set up a variable to hold the valid key value pairs
#set($tokenisedEquals = [])
 
## now we set up a loop to find the valid key value pairs, which must contain only one "="
#foreach( $kvPair in $tokenisedAmpersand )
 #set($countEquals = $kvPair.length() - $kvPair.replace("=", "").length())
 #if ($countEquals == 1)
  #set($kvTokenised = $kvPair.split("="))
  #if ($kvTokenised[0].length() > 0)
   ## we found a valid key value pair. add it to the list.
   #set($devNull = $tokenisedEquals.add($kvPair))
  #end
 #end
#end
 
## next we set up our loop inside the output structure "{" and "}"
{
#foreach( $kvPair in $tokenisedEquals )
  ## finally we output the JSON for this pair and append a comma if this isn't the last pair
  #set($kvTokenised = $kvPair.split("="))
 "$util.urlDecode($kvTokenised[0])" : #if($kvTokenised[1].length() > 0)"$util.urlDecode($kvTokenised[1])"#{else}""#end#if( $foreach.hasNext ),#end
#end
}
```

## Reference:
The AWS competition information can be found at http://awschatbot.devpost.com/
