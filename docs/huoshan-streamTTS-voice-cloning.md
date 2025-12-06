# Management Console Volcano Double Streaming Speech Synthesis + Voice Cloning Configuration Tutorial

This tutorial is divided into 4 phases: Preparation Phase, Configuration Phase, Cloning Phase, and Usage Phase. It mainly introduces the process of configuring Volcano Double Streaming Speech Synthesis + Voice Cloning through the Management Console.

## Phase 1: Preparation Phase
The super administrator first pre-opens the Volcano Engine service and obtains App Id and Access Token. By default, Volcano Engine will give away one voice resource. This voice resource needs to be copied to this project.

If you want to clone multiple voices, you need to purchase and open multiple voice resources. Just copy each voice resource's Voice ID (S_xxxxx) to this project. Then assign them to system accounts for use. The detailed steps are as follows:

### 1. Open Volcano Engine Service
Visit https://console.volcengine.com/speech/app to create an application in Application Management, check Speech Synthesis Large Model and Voice Replication Large Model.

### 2. Get Voice Resource ID
Visit https://console.volcengine.com/speech/service/9999 to copy three items, which are App Id, Access Token, and Voice ID (S_xxxxx). As shown in the figure

![Get Voice Resource](images/image-clone-integration-01.png)

## Phase 2: Configure Volcano Engine Service

### 1. Fill in Volcano Engine Configuration

Log in to the Management Console with super administrator account, click [Model Configuration] at the top, then click [Speech Synthesis] on the left side of the Model Configuration page, search and find "Volcano Double Streaming Speech Synthesis", click Edit, fill in your Volcano Engine's `App Id` into the [Application ID] field, fill in `Access Token` into the [Access Token] field. Then save.

### 2. Assign Voice Resource ID to System Account

Log in to the Management Console with super administrator account, click [Voice Cloning] at the top, [Voice Resources].

Click the Add button, select "Volcano Double Streaming Speech Synthesis" in [Platform Name];

Fill in your Volcano Engine's Voice Resource ID (S_xxxxx) in [Voice Resource ID], press Enter after filling in;

Select the system account you want to assign to in [Owner Account], you can assign it to yourself. Then click Save

## Phase 3: Cloning Phase

If after logging in, click [Voice Cloning] at the top > [Voice Cloning], it displays [Your account has no voice resources, please contact the administrator to assign voice resources], it means you haven't assigned voice resources to this account in Phase 2. Then go back to Phase 2 and assign voice resources to the corresponding account.

If after logging in, click [Voice Cloning] at the top > [Voice Cloning], you can see the corresponding voice list. Please continue.

In the list, you will see the corresponding voice list. Select one of the voice resources, click the [Upload Audio] button. After uploading, you can listen to the voice or extract a segment of the voice. After confirmation, click the [Upload Audio] button.
![Upload Audio](images/image-clone-integration-02.png)

After uploading audio, in the list you will see the corresponding voice will change to "Pending Replication" status. Click the [Replicate Now] button. Wait 1~2 seconds for the result to return.

If replication fails, please hover the mouse over the "Error Information" icon, it will display the reason for failure.

If replication succeeds, in the list you will see the corresponding voice will change to "Training Successful" status. At this time, you can click the edit button in the [Voice Name] column to modify the name of the voice resource for easy selection and use later.

## Phase 4: Usage Phase

Click [Agent Management] at the top, select any agent, click the [Configure Role] button.

Select "Volcano Double Streaming Speech Synthesis" for Speech Synthesis (TTS). In the list, find the voice resource with "Cloned Voice" in the name (as shown in the figure), select it, click Save.
![Select Voice](images/image-clone-integration-03.png)

Next, you can wake up Xiaozhi and have a conversation with it.
