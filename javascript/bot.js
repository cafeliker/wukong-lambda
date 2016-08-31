var botBuilder = require('claudia-bot-builder'),
    excuse = require('huh');

var util = require("util");
var AWS = require('aws-sdk');
AWS.config.region = 'eu-west-1';

var ec2 = new AWS.EC2();

module.exports = botBuilder(function (request) {
  console.log('Loading handler....');
  console.log('new ec2 object = ' + util.inspect(ec2));

  var params = {
    DryRun: false,
    Filters: [
      {
        Name: 'instance-state-name',
        Values: [
          'running'
        ]
      }
    ]
  };

  ec2.describeInstances(params, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else     console.log(data);           // successful response
  });

  return 'working in progress';
});
