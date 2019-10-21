import requestHandler

def lambda_handler(event, context):
    requestHandler.handle_request(event, context)
    return
