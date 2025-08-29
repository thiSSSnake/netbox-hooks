# Netbox-Zabbix Sync Microservice

This is a FastAPI-based microservice designed to synchronize device information between Netbox and Zabbix. The service listens for webhooks from Netbox and processes `create`, `update`, and `delete` events to perform the corresponding actions in Zabbix.

## Overview

The microservice receives webhooks from Netbox, triggered by device-related events (`create`, `update`, `delete`). Based on the event type, it executes the necessary business logic to keep Zabbix in sync with Netbox device data.

## Features

- Receives and processes Netbox webhooks for device events.
- Synchronizes device information with Zabbix.
- Configurable via environment variables.
- Deployable using Docker and Docker Compose.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized deployment)
- Netbox instance with webhook support
- Zabbix instance with API access
- Access to configure webhooks in Netbox

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd netbox-zabbix-sync
```

### 2. Configure Environment Variables

Create a `.env` file in the project root and configure the required environment variables. Example:

```env
# Netbox Configuration
NB_HOST=https://your-netbox-instance.com
NB_TOKEN=your_netbox_api_token

# Zabbix Configuration
ZB_HOST=https://your-zabbix-instance.com
ZB_USER=your_zabbix_username
ZB_PASSWORD=your_zabbix_password
```

### 3. Deploy with Docker Compose

A `docker-compose.yml` file is provided to run the microservice in a Docker container.

1. Ensure Docker and Docker Compose are installed.
2. Build and start the service:

```bash
docker-compose up -d
```

The microservice will be available at `http://localhost:8000` (or the port specified in `docker-compose.yml`).

### 4. Configure Netbox Webhook

To enable synchronization, you need to configure a webhook in Netbox to send device-related events to the microservice.

1. In Netbox, navigate to **Admin > Webhooks**.
2. Create a new webhook with the following settings:
   - **Name**: Netbox-Zabbix Sync
   - **Content Types**: Select `dcim.device` (for devices).
   - **Events**: Check `Create`, `Update`, and `Delete`.
   - **URL**: Set to `http://<microservice-host>:8000/webhook` (replace `<microservice-host>` with the appropriate host).
   - **HTTP Method**: POST
   - **Secret**: Use the same `WEBHOOK_SECRET` value from your `.env` file.
   - **Enabled**: Check to enable the webhook.
3. Save the webhook.

### 5. Verify Setup

- Trigger a `create`, `update`, or `delete` event for a device in Netbox.
- Check the microservice logs to ensure the webhook is received and processed:

```bash
docker-compose logs
```

- Verify that the corresponding changes are reflected in Zabbix.

## Project Structure

```
netbox-hooks/
├── .env.example          # Example environment configuration
├── docker-compose.yml    # Docker Compose configuration
├── app/                  # Source code for the FastAPI microservice
│   ├── main.py           # Main FastAPI application
│   ├── netbox/           # Netbox dir
        ├── api_client.py # API Client for NetBox
        ├── endpoints.py  # Endpoint logic
        ├── schemas.py    # Pydantic models
        ├── services.py   # Buisnes logic
        ├── middleware.py # Custom middleware
│   ├── zabbix/           # Zabbix dir
        ├── api_client.py # API Client for Zabbix
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Running Locally (Without Docker)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the FastAPI application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- **POST /webhook**: Receives and processes Netbox webhooks.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License.