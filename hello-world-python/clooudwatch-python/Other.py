attribute_value = {
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": "arn:aws:lambda:ap-south-1:577683050298:function:ec2_cloudwatch_sns",
        "Principal": {
            "Service": "events.amazonaws.com"
        },
        "Condition": {
            "ArnLike": {
                "AWS:SourceArn": "cw_rule_arn"
            }
        },
        "Sid": "TrustCWEToInvokeMyLambdaFunction"
    }