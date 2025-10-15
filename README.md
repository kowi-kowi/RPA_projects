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


The script connects to ServiceNow via API Servicenow.


It identifies tickets written in Swedish.

Each ticket is validated against translation rules. (if needed e-mail was send from the ticket - no API rights for me here, that is why Selenium workaround)

Eligible tickets are sent to the Microsoft Translation API.

Translated text is written back to ServiceNow and assigned to the correct support group.

**EDI**

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

**IAddress Automation Project**

📝 Description

IAddress is a Python automation tool that handles ServiceNow tickets related to electronic invoicing routing and customer data validation.
The robot validates customer and routing information, interacts with the internal IAddress system, and manages ticket statuses according to predefined business scenarios.
At the end of each day, it generates a summary report with all processed tickets and distributes it to the relevant internal stakeholders.

⚙️ Key Functions

Retrieves tickets from ServiceNow via API

Validates customer VAT/business ID against YTJ.fi

Updates routing and customer information in the internal IAddress tool (using Selenium automation)

Applies one of several predefined handling scenarios (1–8)

Updates ticket statuses and assignments in ServiceNow

Sends a daily summary report to the required recipients

🔄 Scenarios Overview
🧩 Scenario 1 – Routing Changes or Additions

a) A totally new routing has been added (either basic or scheduled)
b) Existing routing has been changed (either basic or scheduled)
c) A valid routing already exists, and no changes are required

➡️ Action: Request is set to Closed Complete by the robot.

🧾 Scenario 2 – Company Name or OVT Mismatch (YTJ check)

If there is a mismatch between the company name or OVT compared to data in YTJ.fi (checked via Business ID validation):

➡️ Action:

Robot sends a message to the customer to verify and confirm company details.

Request is set to Awaiting Customer and assigned to CS FI Customer Service.

🔁 Scenario 3 – Operator Mismatch

If there is a mismatch between the requested operator and what is currently available in Verkkolaskuosoite.fi, and it’s not routed via OpusCapita:

➡️ Action:

Robot sends a message to the customer to verify the operator information.

Request is set to Awaiting Customer and assigned to CS FI Customer Service.

🚫 Scenario 4 – Existing Routing via OpusCapita

If routing already exists via OpusCapita:

➡️ Action:

Robot informs the customer that the requested change cannot be made.

Request is set to Closed Incomplete without any further actions.

📋 Scenarios 5–8 – Return to CS with Information

If the ticket meets any of the following additional conditions, it is returned to Customer Service (CS) with context information:

Scenario	Condition	Action
5	Caller is Nordea	Return to CS with note
6	Description is not empty	Return to CS with note
7	Short description requires check	Return to CS with note
8	Attachments exist	Return to CS with note



Explanation:

requests – Communicate with ServiceNow API and YTJ.fi

selenium – Automate browser-based updates in IAddress

re, json, os, uuid, datetime – Data validation, file handling, and logging

unicodedata – Normalize customer names and routing data

time, sleep – Control script timing and avoid API overloading

🧪 Workflow

Retrieve Tickets from ServiceNow via REST API

Validate VAT/Business ID using YTJ.fi data

Check routing data and apply appropriate scenario (1–8)

Update IAddress system via Selenium (browser automation)

Update ticket status and assignment in ServiceNow

Generate daily report with all handled tickets

Send summary report to internal mailing list



📅 Daily Report Example
Ticket ID	Scenario	Customer	VAT	Action	Status	Date
INC1234567	2	Example Oy	FI1234567	Company name mismatch	Awaiting Customer	2025-10-15
