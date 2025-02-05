# Backend Specification for Message Scheduling Service

## Overview

This document provides a detailed specification of the backend REST service that supports the `/schedule` slash command in Mattermost. The service is responsible for parsing user commands, scheduling messages, storing scheduled messages, and ensuring messages are posted at the correct times.

---

## Architecture Components

1. **REST API Endpoint**

   - Receives slash command requests from Mattermost.
   - Validates incoming requests.

2. **Command Parser**

   - Parses the command text to extract parameters.
   - Validates required parameters (`at` and `message`).
   - Interprets optional parameters (`on`).

3. **Scheduler Service**

   - Schedules tasks to post messages at the specified times.
   - Handles time zone conversions using the user's Mattermost time zone.

4. **Data Storage**

   - Stores scheduled messages with associated metadata.
   - Ensures persistence and reliability.

5. **Message Posting Service**

   - Posts messages to Mattermost channels or direct messages via the API.

6. **Error Handling and Notifications**

   - Handles errors in command parsing and message posting.
   - Sends notifications to users in case of failures.

---

## REST API Endpoint

- **Endpoint URL:** Configured in Mattermost slash command settings.
- **HTTP Method:** `POST`
- **Content-Type:** `application/x-www-form-urlencoded`

### Request Parameters

- **`text`**: The command text entered by the user after `/schedule`.
- **`user_id`**: The Mattermost user ID of the requester.
- **`channel_id`**: The ID of the channel or direct message where the command was executed.
- **`team_id`**: The ID of the team.
- **Additional context**: Other relevant data provided by Mattermost.

---

## Command Parsing

### Parsing Logic

1. **Extract Parameters:**

   - **`at` Time**: Required. Extract the time following the `at` keyword.
   - **`on` Date**: Optional. If present, extract the date following the `on` keyword.
   - **`message` Content**: Required. Extract the message following the `message` keyword.

2. **Validation:**

   - Ensure the `at` keyword and time are present.
   - Validate time format.
   - If `on` date is provided, validate date format.
   - Ensure `message` content is present.

3. **Time Zone Handling:**

   - Retrieve the user's time zone from their Mattermost profile via the API.
   - Convert the scheduled time to UTC for storage and scheduling.

4. **Date Determination:**

   - If `on` is omitted:
     - Compare the specified `at` time with the current time in the user's time zone.
     - If the `at` time is in the future today, set the date to today.
     - If the `at` time is in the past today, set the date to tomorrow.

---

## Scheduling Messages

### Data Model

- **Scheduled Message Record:**

  - `message_id`: Unique identifier.
  - `user_id`: ID of the user who scheduled the message.
  - `channel_id`: ID where the message will be posted.
  - `post_at`: DateTime in UTC when the message should be posted.
  - `message_content`: The message to be posted.
  - `time_zone`: The user's time zone identifier.

### Storage

- Use a persistent data store (e.g., database) to save scheduled messages.
- Ensure data integrity and handle concurrent access.

### Task Scheduling

- Use a reliable scheduler or task queue (e.g., cron job, job queue system).
- Schedule tasks to execute at `post_at` UTC time.
- Ensure the scheduler handles daylight saving changes and time zone differences.

---

## Posting Messages

### Process Flow

1. **At Scheduled Time:**

   - Retrieve the scheduled message from the data store.
   - Use the Mattermost API to post the message to `channel_id`.

2. **Mattermost API Interaction:**

   - **Endpoint:** `/posts`
   - **Method:** `POST`
   - **Authentication:** Use a bot token with appropriate permissions.
   - **Payload:**

     - `channel_id`: Where to post.
     - `message`: The content of the message.

3. **Success Handling:**

   - Upon successful posting, remove the message from the scheduled messages data store.

### Error Handling

- **Posting Failures:**

  - If the message fails to post (e.g., channel no longer exists), send a direct message to `user_id` with failure details.

- **Retry Logic:**

  - Optionally implement retries for transient errors (e.g., network issues).

---

## Listing Scheduled Messages

- **Endpoint Handling:**

  - When `/schedule list` is received, query the data store for all scheduled messages where `user_id` matches the requester.

- **Data Returned:**

  - For each message, return:
    - `message_id`
    - `post_at` (converted to time zone stored with the message)
    - `channel_id` (resolve to channel name or participants)
    - `message_content`

- **Response Formatting:**

  - Format the response according to the UX specification.

---

## Deleting Scheduled Messages

### Validation

- Ensure the `message_id` provided exists and `user_id` matches the requester.

### Deletion Process

- Remove the scheduled message from the data store.
- Confirm deletion to the user with appropriate messaging.

---

## Security and Permissions

- **Authentication:**

  - Verify requests come from authorized Mattermost instances.
  - Use tokens or signatures provided by Mattermost to validate the request.

- **Authorization:**

  - Users can only manage their own scheduled messages.
  - The bot account must have permissions to post in all channels and direct messages.

---

## Error Handling

- **Invalid Commands:**

  - Return user-friendly error messages as per the UX specification.

- **System Failures:**

  - Log errors for debugging.
  - Notify administrators of critical failures.

- **User Notifications:**

  - Inform users of any issues that prevent their messages from being posted.

---

## Logging

- **Logging:**

  - Log all incoming requests, scheduled messages, and posting activities.
  - Include timestamps and relevant identifiers.

---

## Assumptions

- **User Time Zone Accuracy:**

  - Users have correctly set their time zones in Mattermost.

- **Bot Availability:**

  - The bot service remains operational to post messages as scheduled.

---
