import boto3
import logging
import traceback

client = boto3.client('cloudwatch')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

'''
Creates alarm for metric specified in the event
'''
def create_metric_alarm(request):
    alarmList = []
    try:
        alarmName = __get_alarm_name(__get_prefix(request), request['namespace'], request['metricName'])
        client.put_metric_alarm(
            AlarmName=alarmName,
            AlarmDescription=request['metricAlarm']['alarmDescription'],
            ActionsEnabled=True,
            AlarmActions=request['metricAlarm']['notificationTopic'],
            MetricName=request['metricName'],
            Namespace=request['namespace'],
            Statistic='Sum',
            Period=300,
            # Unit=request['metricAlarm']['unit'],
            EvaluationPeriods=1,
            DatapointsToAlarm=1,
            Threshold=request['metricAlarm']['threshold'],
            ComparisonOperator=request['metricAlarm']['comparisonOperator'],
            TreatMissingData='missing',
            # EvaluateLowSampleCountPercentile=request['metricAlarm']['evaluateLowSampleCountPercentile'],
            Tags=request['metricAlarm']['tags']
        )
        alarmList = __get_alarm_details_by_alarm_names(alarmNameList=[alarmName])
        logger.info(alarmList)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_stack())
    return alarmList

def delete_metric_alarm(request):
    alarmName = __get_alarm_name(__get_prefix(request), request['metricNamespace'], request['metricName'])
    response = client.delete_alarms(
        AlarmNames=[
            alarmName
        ]
    )
    return response


def __get_alarm_details_by_alarm_names(alarmNameList):
    response = client.describe_alarms(
        AlarmNames=alarmNameList
    )
    return response['MetricAlarms']

def __get_alarm_name(prefix, namespace, metricName):
    alarmName = namespace + '/' + metricName
    if prefix:
        alarmName = prefix + '/' + alarmName
    return alarmName

def __get_prefix(request):
    if not 'prefix' in request:
        return ''
    else:
        return request['prefix']