# Monfire
_Monitor Moonfire_

This is a (very) simple Proof of Concept to monitor [Moonfire](https://github.com/scottlamb/moonfire-nvr) with Zabbix.

This follows scottlamb/moonfire-nvr#209 and scottlamb/moonfire-nvr#211

## How to

Create a `.env` file with the following:
```
MONFIRE_BASE_URL=https://moonfire.example.com
MONFIRE_USERNAME=monfire
MONFIRE_PASSWORD=xxxxx
```

Where:
- `MONFIRE_BASE_URL`: the base URL to Moonfire. `/api` will be appended automatically.
- `MONFIRE_USERNAME`: the username to use to login to Moonfire
- `MONFIRE_PASSWORD`: the password to use to login to Moonfire

Then run:

```
docker-compose up --build
```

The monitoring endpoint are available on port `8000`:
- Zabbix:
  - /api/zabbix/cameras/discovery
  - /api/zabbix/camera/<uuid>
- Prometheus:
  - /api/prometheus/metrics
