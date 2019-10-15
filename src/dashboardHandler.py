import boto3
import logging
import traceback
import json

client = boto3.client('cloudwatch')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

'''
Add metric to specified dashboard. If dashboard does not exists, then there will be one created.
'''
def add_to_dashboard(request):
    dashboardBodyJson = None
    try:
        listDashboardResp = client.list_dashboards(
            DashboardNamePrefix=request['dashboard']['name']
        )
        logger.info(listDashboardResp)
        if len(listDashboardResp['DashboardEntries']) > 0:
            logger.info('Dashboard exists')
            getDashboardResp = client.get_dashboard(
                DashboardName=request['dashboard']['name']
            )
            dashboardBody = json.loads(getDashboardResp['DashboardBody'])
            widgets = dashboardBody['widgets']
            dashboardBody['widgets'].append(__create_metric_widget(request, False))
            dashboardBodyJson = json.dumps(dashboardBody)
        else:
            logger.info('Creating new dashboard')
            widgets = []
            widgets.append(__create_text_widget(request))
            widgets.append(__create_metric_widget(request, True))
            dashboardBody = {
                'periodOverride': 'inherit',
                'widgets': widgets
            }
            dashboardBodyJson = json.dumps(dashboardBody)
        createResponse = client.put_dashboard(
            DashboardName=request['dashboard']['name'],
            DashboardBody=dashboardBodyJson
        )
        logger.info(createResponse)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_stack())

'''
Creates metric widget for dashboard.
'''
def __create_metric_widget(request, isNewDashboard):
    '''
    If the dashboard is newly created then metric location (x,y) is specified.
    For an existing dashboard the widget is placed automatically in the next available location. 
    '''
    metricWidget = {
        'type': 'metric',
        'width': 6,
        'height': 6,
        'properties': {
            'metrics': [
                [ request['namespace'], request['metricName'] ]
            ],
            'view': 'timeSeries',
            'stacked': False,
            'period': 300,
            'stat': request['dashboard']['widget']['stat'],
            'region': request['dashboard']['widget']['region'],
            'title': request['dashboard']['widget']['title']
        }
    }
    if isNewDashboard:
        metricWidget['x']=0
        metricWidget['y']=3
    return metricWidget

'''
Creates text widget to be place at the top of the dashboard 
'''
def __create_text_widget(request):
    textWidget = {
        'type': 'text',
        'x': 0,
        'y': 0,
        'width': 12,
        'height': 3,
        'properties': {
            'markdown': "\n## Generic Error Dashboard\nThis dashboard has been created programmatically through lambda **arn:aws:lambda:us-east-1:847104828221:function:cloudwatch-monitor-lambda**\n\nPlease refrain from modifying it manually.\n"
        }
    }
    return textWidget

