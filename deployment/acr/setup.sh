#!/bin/bash

if [ ! -f ../tf.config.private.sh ]; then
    echo "tf.config.private.sh file not found!"
    exit 1
fi

# Load environment variables defined by user
. ../tf.config.private.sh

# Check for an environment variable name if it exists and exit if not
check_variable_exists () {
    declare variable_name="$1"
    declare variable_value=$(printf '%s\n' "${!variable_name}")
    if [[ -z "${variable_value}" ]]; then
        echo "${variable_name} environment variable doesn't exists";
        exit 1;
    fi
}

check_variable_exists "ARM_SUBSCRIPTION_ID"
check_variable_exists "ARM_CLIENT_ID"
check_variable_exists "ARM_CLIENT_SECRET"
check_variable_exists "ARM_TENANT_ID"
check_variable_exists "ARM_ENVIRONMENT"
check_variable_exists "STORAGE_ACCOUNT_NAME"
check_variable_exists "ARM_ACCESS_KEY"

# The tfstate file will be upload to azure storage to maintain consistency and future destruction of the resources.
az storage container create -n tfstate --account-name $STORAGE_ACCOUNT_NAME --account-key $ARM_ACCESS_KEY

# Initializing and deploying terraform deployment
terraform init -backend-config="storage_account_name=$STORAGE_ACCOUNT_NAME"
terraform workspace select acr || terraform workspace new acr && \
terraform plan -out out.plan
terraform apply out.plan