import json
import urllib3
import boto3
import os

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    request_type = event['RequestType']
    bucket_name = event['ResourceProperties']['BucketName'] 

    if request_type == 'Delete':
        try:
            # Delete the file from S3
            s3_client.delete_object(Bucket=bucket_name, Key='parameter.json')

            #Send a Succeess response to CloudFormation
            send_response(event, context, "SUCCESS", {
                "Message": "File Deleted from S3 Bucket Successfully!"
            })
        except Exception as e:
            # Send a Failure response to CloudFormation
            send_response(event, context, "FAILED", {
                "Message": str(e)                      
            })
        return

    try:
        ssm_client = boto3.client('ssm')
        
        #Get the Parameter name from the event
        parameter_name = event['ResourceProperties']['ParameterName']

        #Read parameter from Parameter Store
        parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        parameter_value= parameter['Parameter']['Value']
        
        #Write parameter to a file
        jsonData = f'{{"{parameter_name}":"{parameter_value}"}}'
        file_path = '/tmp/parameter.json'
        with open(file_path,'w') as file:
            file.write(jsonData)
        
        #upload the file to S3
        s3_client.upload_file(file_path,bucket_name,'parameter.json')
        
        #Send a success response to CloudFormation
        send_response(event, context, "SUCCESS", {
            "Message": "File uploaded to S3 successfully!"
        })
    except Exception as e:
        #Send a Failure response to CloudFormation
        send_response(event, context, "FAILED", {
            "Message": str(e)
        })

http = urllib3.PoolManager()

def send_response(event, context, responseStatus, responseData,physicalResourceId=None, noEcho=False, reason=None):
    responseUrl = event['ResponseURL']
    print(responseUrl)
    responseBody = {
        'Status' : responseStatus,
        'Reason' : reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
        'PhysicalResourceId' : physicalResourceId or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : noEcho,
        'Data' : responseData
    }

    json_responseBody = json.dumps(responseBody)
    print("Response body:")
    print(json_responseBody)
    
    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }
      

    try:
        response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
        print("Status code:", response.status)

    except Exception as e:

        print("send(..) failed executing http.request(..):", e)
