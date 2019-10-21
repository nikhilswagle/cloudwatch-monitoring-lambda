#! /bin/bash
set -x
export S3_CODE_BUCKET=$1
export S3_FOLDER_PREFIX=$2
export PACKAGE_NAME=$3
export PACKAGE_VERSION=$4
export STACK_NAME=$5
export PACKAGE_FILENAME="$PACKAGE_NAME-$PACKAGE_VERSION.zip"
export S3_KEY="$S3_FOLDER_PREFIX/$PACKAGE_FILENAME"

# Check if the stack exists
export varStackEntry=$(aws cloudformation list-stacks \
--stack-name $STACK_NAME \
--region $AWS_REGION | grep '"StackName": "$STACK_NAME"')

if [ $(echo $varStackEntry | awk '{print length}') -gt 0 ]
then
    # Delete cloudformation stack
    aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $AWS_REGION

    # Wit till the delete operation is complete
    aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $AWS_REGION
else
    echo "$STACK_NAME stack does not exist!"
fi

# Remove lambda package code from s3
aws s3 rm s3://$S3_CODE_BUCKET/$S3_KEY --region $AWS_REGION