# Fire Evacuation Module

Emergency evacuation checklist for Odoo with web interface.

## Features

- Aggregates people from visitors and employee attendance
- Web-based checklist at `/fire/evacuation/new`
- Mark people as safe with status tracking

## Installation

1. Copy to addons directory
2. Install module
3. Navigate to `/fire/evacuation/new`

## Dependencies

- `base`, `website`, `hr_attendance`, `visitor_management`

## Usage

1. Enter site name → Click "Start Evacuation"
2. System loads all people at location
3. Mark each person as OK when accounted for
4. Use "Reload" to refresh the list

## License

LGPL-3