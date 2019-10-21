#! /bin/bash
set -x
export S3_CODE_BUCKET=$1
export S3_FOLDER_PREFIX=$2
export PACKAGE_NAME=$3
export PACKAGE_VERSION=$4
export STACK_NAME=$5
export AWS_REGION=$6
export PACKAGE_FILENAME="$PACKAGE_NAME-$PACKAGE_VERSION.zip"
export S3_KEY="$S3_FOLDER_PREFIX/$PACKAGE_FILENAME"

# Push lambda code to s3
cd lambda
zip $PACKAGE_FILENAME *.py dashboard-config.json
aws s3 cp $PACKAGE_FILENAME s3://$S3_CODE_BUCKET/$S3_FOLDER_PREFIX/ \
--region $AWS_REGION

# Create/Update cloudformation stack
cd ../cloudformation
sed -i "s/<LambdaCodeS3BucketName>/$S3_CODE_BUCKET/g" cf-emr-monitoring.json
sed -i "s|<LambdaCodeS3Key>|$S3_KEY|g" cf-emr-monitoring.json

export varStackEntry=$(aws cloudformation list-stacks \
--region $AWS_REGION | grep "\"StackName\": \"$STACK_NAME\"")

echo $varStackEntry

if [ $(echo $varStackEntry | awk '{print length}') -gt 0 ]
then
    # Stack exists
    aws cloudformation update-stack \
    --stack-name $STACK_NAME \
    --template-body "file://cf-logfilter-metrics-monitoring.yml" \
    --parameters "file://cf-logfilter-metrics-monitoring.json" \
    --region $AWS_REGION \
    --capabilities CAPABILITY_NAMED_IAM

    aws cloudformation wait stack-update-complete \
    --stack-name $STACK_NAME \
    --region $AWS_REGION
else
    # Stack does not exist
    aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body "file://cf-logfilter-metrics-monitoring.yml" \
    --parameters "file://cf-logfilter-metrics-monitoring.json" \
    --region $AWS_REGION \
    --capabilities CAPABILITY_NAMED_IAM

    aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $AWS_REGION
fi