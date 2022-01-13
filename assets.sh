#!/bin/bash

export AWS_PROFILE=prod

do_cmd ()
{
    echo ================
    echo cmd: $1 
    echo
    eval $1
    echo ================
}

do_cmd_csv ()
{
    cmd="$1 | jq -r '.[] | @csv'"
    echo ================
    echo cmd: $cmd 
    echo
    eval $cmd
    echo ================
}

# generate list of assets in Route53
audit_route53 ()
{
    echo "<============================>"
    echo "begin Route 53"
    echo

    do_cmd_csv "aws route53 list-hosted-zones --query 'HostedZones[].[Name, Id]'"
    do_cmd_csv "aws route53 list-resource-record-sets --hosted-zone-id Z04797781GCE407DWNDCT --query 'ResourceRecordSets[*][Name,Type,AliasTarget.DNSName]'"

    echo
    echo " end Route53"
    echo "<============================>"
}

audit_ec2 ()
{
    echo "<============================>"
    echo "begin instances"
    echo

    do_cmd "aws ec2 describe-instances --region us-east-1 --query 'Reservations[*].Instances[*].[InstanceId,Tags]'"
    do_cmd "aws ec2 describe-instances --region us-east-2 --query 'Reservations[*].Instances[*].[InstanceId,Tags]'"

    echo
    echo " end instances"
    echo "<============================>"
}

audit_elbv2()
{
    echo "<============================>"
    echo "begin ELBv2"
    echo

    do_cmd "aws elbv2 describe-load-balancers --region us-east-1 --query 'LoadBalancers[*].[LoadBalancerName,DNSName]' | jq -r '.[] | @csv'"
    echo
    do_cmd "aws elbv2 describe-load-balancers --region us-east-2 --query 'LoadBalancers[*].[LoadBalancerName,DNSName]' | jq -r '.[] | @csv'"

    echo
    echo " end ELBv2"
    echo "<============================>"


}



audit_route53
audit_ec2
audit_elbv2

