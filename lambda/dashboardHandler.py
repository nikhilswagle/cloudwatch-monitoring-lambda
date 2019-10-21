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
def add_to_dashboard(request, alarmList):
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
            dashboardBody['widgets'].extend(__create_alarm_widgets(request, alarmList, widgets))
            dashboardBodyJson = json.dumps(dashboardBody)
        else:
            logger.info('Creating new dashboard')
            widgets = []
            widgets.append(__create_text_widget(request))
            widgets.extend(__create_alarm_widgets(request, alarmList, widgets))
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
Creates widget for alarm on dashboard
'''
def __create_alarm_widgets(request, alarmList, currentWidgets):
    widgets = []
    found = False
    for alarm in alarmList:
        if len(currentWidgets) > 0:
            for currentWidget in currentWidgets:
                if currentWidget['type'] == 'metric' and currentWidget['properties']['title'] == alarm['AlarmName']:
                    logger.info('Widget already exists on dashboard')
                    found = True
                    break
        if not found:
            widgets.append(__get_alarm_widget(request, alarm))
    return widgets

def __get_alarm_widget(request, alarm):
    alarmWidget = {
        'type': 'metric',
        'width': 6,
        'height': 6,
        'properties': {
            'view': 'timeSeries',
            'stacked': False,
            'period': 300,
            'annotations': {
                'alarms': [
                    alarm['AlarmArn']
                ]
            },
            'region': request['region'],
            'title': alarm['AlarmName']
        }
    }
    return alarmWidget

'''
Creates metric widget for dashboard.
'''
def __create_metric_widget(request, currentWidgets):
    '''
    If the dashboard is newly created then metric location (x,y) is specified.
    For an existing dashboard the widget is placed automatically in the next available location. 
    '''
    widgets = []
    found = False
    widgetTitle = __get_metric_widget_title(__get_prefix(request), request['namespace'], request['metricName'])
    if len(currentWidgets) > 0:
        for currentWidget in currentWidgets:
            if currentWidget['type'] == 'metric' and currentWidget['properties']['title'] == widgetTitle:
                logger.info('Widget already exists on dashboard')
                found = True
                break
    if not found:
        widgets.append(__get_metric_widget(request, widgetTitle))
    return widgets

def __get_metric_widget(request, widgetTitle):
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
            'stat': 'SampleCount',
            'region': request['region'],
            'title': widgetTitle
        }
    }


'''
Creates text widget to be place at the top of the dashboard 
'''
def __create_text_widget(request):
    textWidget = {
        'type': 'text',
        # 'x': 0,
        # 'y': 0,
        'width': 24,
        'height': 1,
        'properties': {
            'markdown': "\n# " + request['dashboard']['name'] + "\n"
        }
    }
    return textWidget

def __get_metric_widget_title(prefix, namespace, metricName):
    alarmName = namespace + '/' + metricName
    if prefix:
        alarmName = prefix + '/' + alarmName
    return alarmName

def __get_prefix(request):
    if not 'prefix' in request:
        return ''
    else:
        return request['prefix']