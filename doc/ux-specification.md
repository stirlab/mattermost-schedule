# User Experience Specification for Message Scheduling Slash Command

## Overview

This document provides a detailed specification of the user interface (UX) for the message scheduling feature implemented via the Mattermost slash command `/schedule`. The goal is to offer users a simple, intuitive way to schedule messages to be sent at a future time.

---

## Slash Command Functionality

### 1. Schedule a New Message

**Command Format:**

```
/schedule at <time> [on <date>] message <your message>
```

- **`at <time>`**: (Required) Specifies the time when the message should be sent.

  - Acceptable time formats include:
    - 24-hour format: `HH:MM` (e.g., `15:30`)
    - 12-hour format with am/pm: `H:MMam` or `H:MMpm` (e.g., `3:30pm`), `Ham` or `Hpm` (e.g., `3pm`)

- **`on <date>`**: (Optional) Specifies the date when the message should be sent.

  - If omitted:
    - If the specified `at` time is **in the future today**, the message is scheduled for **today**.
    - If the specified `at` time is **in the past today**, the message is scheduled for **tomorrow**.

  - Acceptable date formats include:
    - `YYYY-MM-DD` (e.g., `2023-10-20`)
    - `MM/DD` (e.g., `10/20`)

- **`message <your message>`**: (Required) The content of the message to be sent.

**Examples:**

1. **Schedule for later today:**

   ```
   /schedule at 15:30 message Team meeting in 30 minutes.
   ```

2. **Schedule for tomorrow (time is in the past today):**

   ```
   /schedule at 09:00 message Good morning!
   ```

3. **Schedule on a specific date:**

   ```
   /schedule at 14:00 on 2023-10-20 message Project launch meeting.
   ```

### 2. List Scheduled Messages

**Command:**

```
/schedule list
```

- Displays all messages scheduled by the user.
- Each entry includes:
  - **Message ID**
  - **Scheduled Date and Time** (including the user's time zone)
  - **Posting Location** (channel or direct message)
  - **Message Content**

### 3. Delete a Scheduled Message

**Command:**

```
/schedule delete <message_id>
```

- Users can delete only the messages they have scheduled.
- Removes the message from the schedule and confirms deletion.

---

## User Interface Elements

### Confirmation Messages

- Upon successfully scheduling a message, the system sends a confirmation to the user including:

  - **Message ID**
  - **Scheduled Date and Time** with time zone
  - **Posting Location**:
    - For channels: `#channel-name` (e.g., `#general`)
    - For direct messages: `Direct Message with [Participant Names]`
  - **Message Content**

**Example:**

```
✅ **Message Scheduled Successfully!**

**Message ID:** 4

**Scheduled For:** 🗓 Today at 15:30 (Eastern Time)

**Post To:** #general

**Message Content:**

> Team meeting in 30 minutes.

Use `/schedule list` to view all your scheduled messages.
```

### Listing Messages

- The `/schedule list` command returns a formatted list of the user's scheduled messages.
- Messages are separated by horizontal lines for clarity.

**Example:**

```
📋 **Your Scheduled Messages**

---

**ID:** 4

**Scheduled For:** 🗓 Today at 15:30 (Eastern Time)

**Post To:** #general

**Message Content:**

> Team meeting in 30 minutes.

---

**ID:** 5

**Scheduled For:** 🗓️ 2023-10-20 at 14:00 (Eastern Time)

**Post To:** Direct Message with Bob, Charlie

**Message Content:**

> Project launch meeting.

---

To delete a message, use `/schedule delete <message_id>`.
```

### Deletion Confirmation

- Upon deleting a message, the user receives a confirmation message.

**Example:**

```
🗑 **Message Deleted Successfully**

**Deleted Message ID:** 5
```

### Error Messages and Notifications

- **Missing `at` Keyword:**

  ```
  ❌ **Error: Missing 'at' Keyword**

  The 'at' keyword is required to specify the time when the message should be sent.

  **Correct Format:**

  /schedule at <time> [on <date>] message <your message>

  Please try again.
  ```

- **Invalid Time Format:**

  ```
  ❌ **Error: Invalid Time Format**

  The time specified after 'at' is invalid or not recognized.

  **Acceptable Time Formats:**

  - `HH:MM` (e.g., `15:30`)
  - `H:MMam` / `H:MMpm` (e.g., `3:30pm`)
  - `Ham` / `Hpm` (e.g., `3pm`)

  **Example:**

  /schedule at 15:00 message Meeting time updated.

  Please try again.
  ```

- **Unauthorized Deletion Attempt:**

  ```
  ❌ **Error: Unauthorized Action**

  You cannot delete scheduled messages created by other users.

  **Message ID:** 7 does not belong to you.

  Please verify the message ID and try again.
  ```

- **Failed Message Posting Notification:**

  ```
  ⚠️ **Failed to Post Scheduled Message**

  **Message ID:** 4

  **Scheduled For:** 🗓️ Today at 15:30 (Eastern Time)

  **Post To:** #general

  **Message Content:**

  > Team meeting in 30 minutes.

  **Reason:** The channel #general no longer exists or is inaccessible.

  Please check the channel status and reschedule the message if necessary.
  ```

---

## Time Zone Handling

- The user's Mattermost time zone setting is used for scheduling and displayed in all messages.

---

## User Permissions and Security

- **Message Ownership:** Users can manage only their own scheduled messages.
- **Posting Permissions:** The bot has permission to post in all channels and direct messages.
- **Validation:** The system ensures users cannot delete or alter messages scheduled by others.

---

## Assumptions

- **Consistent Time Settings:** All users have accurate time zones set in their Mattermost profiles.
- **Bot Reliability:** The bot service is always available to post messages at scheduled times.

---
