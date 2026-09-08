# ITCS 6190/8190 - Assignment 1: Containers with Docker

This project sets up a multi-container stack using Docker Compose consisting of a PostgreSQL database and a Python application. The database is initialized and seeded with trip data, while the Python service connects via service DNS, computes aggregated statistics, prints the summary to standard output, and persists the results to a mounted volume.

# Quickstart & Commands

Run the entire pipeline (cleans old volumes, builds images, runs containers, generates output):

make

Alternatively, launch using Docker Compose directly:

docker compose up --build

Stop containers and clean up mounted volume data:

make clean

Or stop containers without removing generated files:

docker compose down

# Output

```
{
  "total_trips": 6,
  "avg_fare_by_city": [
    {
      "city": "San Francisco",
      "avg_fare": 20.25
    },
    {
      "city": "New York",
      "avg_fare": 19.0
    },
    {
      "city": "Charlotte",
      "avg_fare": 16.25
    }
  ],
  "top_by_minutes": [
    {
      "id": 6,
      "city": "San Francisco",
      "minutes": 28,
      "fare": 29.3
    },
    {
      "id": 4,
      "city": "New York",
      "minutes": 26,
      "fare": 27.1
    },
    {
      "id": 2,
      "city": "Charlotte",
      "minutes": 21,
      "fare": 20.0
    },
    {
      "id": 1,
      "city": "Charlotte",
      "minutes": 12,
      "fare": 12.5
    },
    {
      "id": 5,
      "city": "San Francisco",
      "minutes": 11,
      "fare": 11.2
    },
    {
      "id": 3,
      "city": "New York",
      "minutes": 9,
      "fare": 10.9
    }
  ]
}
```
# Output Locations

The final calculation results are exported directly to disk:
* Host Location: ./out/summary.json
* Container Location: /out/summary.json

# Troubleshooting

* Database Not Ready (psycopg.OperationalError): The Python script implements connection retry logic (connect_with_retry) alongside a Docker Compose healthcheck on the db service. If the container fails to connect, verify the database credentials match between compose.yml and app/main.py.
* Permission Issues on ./out/: If the container cannot create or write to /out/summary.json, ensure your host user has write permissions on the local directory or execute make clean to reset the volume mount point.
* Port Conflicts: The database service runs strictly on the internal Docker network without host port mappings, so host port 5432 does not need to be freed.
