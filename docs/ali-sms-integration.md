# Alibaba Cloud SMS Integration Guide

Log in to Alibaba Cloud Console, enter the "SMS Service" page: https://dysms.console.aliyun.com/overview

## Step 1: Add Signature
![Steps](images/alisms/sms-01.png)
![Steps](images/alisms/sms-02.png)

After the above steps, you will get a signature, please write it to the Management Console parameter, `aliyun.sms.sign_name`

## Step 2: Add Template
![Steps](images/alisms/sms-11.png)

After the above steps, you will get a template code, please write it to the Management Console parameter, `aliyun.sms.sms_code_template_code`

Note: The signature needs to wait 7 business days, and can only be sent successfully after the operator reports successfully.

Note: The signature needs to wait 7 business days, and can only be sent successfully after the operator reports successfully.

Note: The signature needs to wait 7 business days, and can only be sent successfully after the operator reports successfully.

You can wait until the report is successful, then continue with the following operations.

## Step 3: Create SMS Account and Enable Permissions

Log in to Alibaba Cloud Console, enter the "Access Control" page: https://ram.console.aliyun.com/overview?activeTab=overview

![Steps](images/alisms/sms-21.png)
![Steps](images/alisms/sms-22.png)
![Steps](images/alisms/sms-23.png)
![Steps](images/alisms/sms-24.png)
![Steps](images/alisms/sms-25.png)

After the above steps, you will get access_key_id and access_key_secret, please write them to the Management Console parameters, `aliyun.sms.access_key_id`, `aliyun.sms.access_key_secret`
## Step 4: Enable Mobile Registration Function

1. Normally, after filling in all the above information, there will be this effect. If not, some step may be missing

![Steps](images/alisms/sms-31.png)

2. Enable allowing non-administrator users to register, set parameter `server.allow_user_register` to `true`

3. Enable mobile registration function, set parameter `server.enable_mobile_register` to `true`
![Steps](images/alisms/sms-32.png)
