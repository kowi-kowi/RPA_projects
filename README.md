**Swedish Ticket Translate**

📝 Description

Swedish Ticket Translate is an automation tool designed to process and translate ServiceNow tickets written in Swedish into English.
Only tickets that meet specific criteria — defined in agreement with the Swedish Service Desk — are translated.
The translation is performed using the Microsoft Translation API, and translated tickets are then automatically moved to the appropriate group in ServiceNow.

⚙️ Features

Fetches and processes Swedish tickets from ServiceNow

Checks if a ticket meets translation rules agreed with Swedish SD

Uses Microsoft Translation API for translation

Updates and moves translated tickets to the correct group in ServiceNow

Generates logs for tracking translated tickets


Key libraries explained:

requests – API communication (Microsoft Translation API, ServiceNow)

selenium – automating browser interactions with ServiceNow

re, json, os, uuid, datetime – for text processing, data management, and timestamps

unicodedata – normalization of special Swedish characters

🚀 How It Works

The script connects to ServiceNow via API.

It identifies tickets written in Swedish.

Each ticket is validated against translation rules. (if needed e-mail was send from the ticket - no API rights for me here, that is why Selenium workaround)

Eligible tickets are sent to the Microsoft Translation API.

Translated text is written back to ServiceNow and assigned to the correct support group.

***EDI ***

📝 Description

Handling EDI Tickets in ServiceNow is an automation script that simulates how customer support agents handle EDI (Electronic Data Interchange) tickets in ServiceNow.

The main goal of this tool is to automatically process EDI-related incidents by:

Identifying the EDI supplier,

Performing typical support actions such as downloading attachments,

Notifying the appropriate people or teams,

And deciding the next ticket status based on predefined business logic.

This automation helps reduce manual effort and ensures consistent handling of EDI tickets.

⚙️ Features

Automatically logs in to ServiceNow using Selenium

Scans and processes open EDI-related tickets

Extracts and identifies the EDI supplier from ticket data

Downloads attachments related to the ticket

Notifies proper stakeholders (via email, API call, or internal notes)

Updates the ticket with the correct status and assignment group

Maintains logs for auditing and traceability



Library overview:

requests – for API communication (notifications, integrations)

selenium – to automate browser interactions with ServiceNow

re, json, os, uuid, datetime – for text parsing, data storage, and time management

unicodedata – for normalizing special characters

time, sleep – to manage automation timing and delays

🚀 How It Works

The script opens ServiceNow via API.

It searches for all EDI tickets in the queue.

For each ticket, it:

Identifies the supplier name,

Downloads and saves any attachments

Notifies the appropriate people (based on supplier or ticket category),

Updates the ticket status (e.g., "In Progress", "Waiting for Supplier", "Resolved").

Logs all performed actions for transparency and tracking.