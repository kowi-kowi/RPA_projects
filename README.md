"# RPA_projects" 

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

The script connects to ServiceNow via Selenium.

It identifies tickets written in Swedish.

Each ticket is validated against translation rules.

Eligible tickets are sent to the Microsoft Translation API.

Translated text is written back to ServiceNow and assigned to the correct support group.
