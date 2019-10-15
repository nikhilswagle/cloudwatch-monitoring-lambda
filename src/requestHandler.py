import logging
import traceback
import json
import boto3
from . import metricFilterHandler
from . import metricAlarmHandler
from . import dashboardHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)
client = boto3.client('logs')

'''
Handle lambda event
'''
def handle_request(event, context):
    nextToken = None
    while True:
        logGroupsResp = ''
        try:
            if nextToken == None:
                logGroupsResp = client.describe_log_groups(
                    logGroupNamePrefix = event['logGroupNamePrefix']
                )
            else:
                logGroupsResp = client.describe_log_groups(
                    logGroupNamePrefix = event['logGroupNamePrefix'],
                    nextToken = nextToken
                )
            logger.info(logGroupsResp)
        except Exception as e:
            logger.error(e)
            logger.error(traceback.print_stack())
            return
        
        metricFilterResp = None
        if event['eventName'] == 'create-metric-filter':
            for logGroup in logGroupsResp['logGroups']:
                # Create metric filter
                metricFilterHandler.create_metric_filter(event, logGroup['logGroupName'])
            if 'metricAlarm' in event:
                # Create metric alarm
                metricAlarmHandler.create_metric_alarm(event)
            if 'dashboard' in event:
                # Add metric to dashboard
                dashboardHandler.add_to_dashboard(event)
        elif event['eventName'] == 'delete-metric-filter':
            for logGroup in logGroupsResp['logGroups']:
                metricFilterHandler.delete_metric_filter(event, logGroup['logGroupName'])
        else:
            logger.error("Invalid event name")
        if 'nextToken' in logGroupsResp:
            nextToken = logGroupsResp['nextToken']
        else:
            return
    return

# def __build_dashboard_request(event):
#     request = {
#         'dashboards': [
#             {
#                 'name': event['dashboard']['name']
#             }   
#         ]
#     }