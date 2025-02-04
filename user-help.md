# Schedule Command Help

**Easily schedule messages to be sent at a future time using the `/schedule` command.**

---

## How to Schedule a Message

**Basic Format:**

```
/schedule at <time> [on <date>] message <your message>
```

- **`at <time>`**: (Required) The time you want your message to be sent.

  - You can use formats like:
    - 24-hour: `15:30`
    - 12-hour: `3:30pm`, `8am`

- **`on <date>`**: (Optional) The date you want your message to be sent.

  - Date formats you can use:
    - `2023-10-20`
    - `10/20`

  - If you don't include a date:
    - If the time is **later today**, your message will be sent **today**.
    - If the time is **has already passed today**, your message will be sent **tomorrow**.

- **`message <your message>`**: (Required) The content of the message you want to send.

---

**Examples:**

1. **Schedule for later today:**

   ```
   /schedule at 15:30 message Team meeting in 30 minutes.
   ```

2. **Schedule for tomorrow (if time is earlier than now):**

   ```
   /schedule at 9am message Good morning!
   ```

3. **Schedule for a specific date:**

   ```
   /schedule at 14:00 on 2023-10-20 message Project launch meeting.
   ```

---

## View Your Scheduled Messages

To see a list of messages you've scheduled:

```
/schedule list
```

You'll receive a list with details like message IDs, scheduled times, and content.

---

## Delete a Scheduled Message

If you want to cancel a scheduled message:

```
/schedule delete <message_id>
```

Replace `<message_id>` with the ID from your scheduled messages list.

**Example:**

```
/schedule delete 4
```

---

## Important Notes

- **Where Your Message Will Be Sent:**

  - Your scheduled message will be posted in the **same channel or direct message** where you run the `/schedule` command.

- **Time Zones:**

  - All times are based on your Mattermost time zone settings.

- **Managing Your Messages:**

  - You can only view and delete messages that **you** have scheduled.

- **If Something Goes Wrong:**

  - If your message can't be sent (for example, if the channel was deleted), we'll notify you and include the message details.

---

## Need Help?

If you have any questions or need assistance, please contact your system administrator.

---

# Happy Scheduling!

---
