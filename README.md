# dxcTask

* This CloudFormation template sets up a Lambda function that is triggered by a custom resource. The Lambda function performs operations based on the request type, such as:

* **Create**: Reads a parameter from AWS Systems Manager (SSM) Parameter Store, writes it to a file, and uploads this file to an S3 bucket.
* **Delete**: Deletes the file from the specified S3 bucket.

* The Lambda function is triggered by a custom resource of type Custom::MyCustomResource, which uses the Lambda function to handle requests. The template also sets up the necessary IAM role with permissions required for the Lambda function to operate, including permissions for logging, accessing SSM parameters, and interacting with S3.


* When the CloudFormation stack is deleted, the custom resource triggers the Lambda function with a Delete request. As a result, the Lambda function will:

* Delete the parameter.json file from the S3 bucket.
This ensures that any resources created during the stack's lifecycle are cleaned up properly, helping to avoid orphaned resources and potential issues in your AWS environment.
