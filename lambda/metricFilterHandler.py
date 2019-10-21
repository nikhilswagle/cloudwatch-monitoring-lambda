import logging
import traceback
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)
client = boto3.client('logs')

'''
Creates a metric filter for specified log group in cloudwatch. 
'''
def create_metric_filter(request, logGroupName):
    response=None
    try:
        response = client.put_metric_filter(
            logGroupName=logGroupName,
            filterName=request['filterName'],
            filterPattern=request['filterPattern'],
            metricTransformations=[
                {
                    'metricName': request['metricName'],
                    'metricNamespace': request['namespace'],
                    'metricValue': '1',
                    'defaultValue': 0
                }
            ]
        )
        logger.info(response)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_stack())
    return response

'''
Deletes specified metric filter
'''
def delete_metric_filter(request, logGroupName):
    describeResponse = {}
    deleteResponse = None
    try:
        describeResponse = client.describe_metric_filters(
            logGroupName=logGroupName,
            filterNamePrefix=request['filterName']
        )
        if len(describeResponse['metricFilters']) > 0:
            deleteResponse = client.delete_metric_filter(
                logGroupName=logGroupName,
                filterName=request['filterName']
            )
            logger.info(deleteResponse)
        else:
            deleteResponse = 'Metric filter not found: '+request['filterName']
            logger.info(deleteResponse)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_stack())
    return deleteResponse