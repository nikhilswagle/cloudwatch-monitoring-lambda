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
    try:
        response = client.put_metric_alarm(
            AlarmName=request['metricAlarm']['alarmName'],
            AlarmDescription=request['metricAlarm']['alarmDescription'],
            ActionsEnabled=bool(request['metricAlarm']['actionsEnabled']),
            AlarmActions=request['metricAlarm']['alarmActions'],
            MetricName=request['metricName'],
            Namespace=request['namespace'],
            Statistic=request['metricAlarm']['statistic'],
            Period=request['metricAlarm']['period'],
            # Unit=request['metricAlarm']['unit'],
            EvaluationPeriods=request['metricAlarm']['evaluationPeriods'],
            DatapointsToAlarm=request['metricAlarm']['datapointsToAlarm'],
            Threshold=request['metricAlarm']['threshold'],
            ComparisonOperator=request['metricAlarm']['comparisonOperator'],
            TreatMissingData=request['metricAlarm']['treatMissingData'],
            # EvaluateLowSampleCountPercentile=request['metricAlarm']['evaluateLowSampleCountPercentile'],
            Tags=request['metricAlarm']['tags']
        )
        logger.info(response)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_stack())
    return response
