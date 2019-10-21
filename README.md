# logfilter-metrics-monitoring-lambda
This lambda is an automated solution to do the following tasks
1. Create cloudwatch metric filters from specified log groups
2. Create custom metrics based on filters applied in step 1
3. Create alarms for the metrics
4. Add metrics to a dashboard (if the dashboard does not exists a new one is created)

This lambda can be invoked via a JSON request to create custom metrics based on cloudwatch logs and perform some basic monitoring on those metrics. The sample-request.json request has been provided.
Typical use cases include below
1. Monitoring error occurrences based on cloudwatch or cloudtrail logs.
2. Filtering logs based on custom patterns to get insight into application logs.
