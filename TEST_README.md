# Endpoint Testing Script

This script tests all the dynamic translation endpoints with sample data.

## Prerequisites

1. Make sure your Django server is running on `localhost:8000`
2. Install the test dependencies:
   ```bash
   pip install -r test_requirements.txt
   ```

## Running the Tests

```bash
python test_endpoints.py
```

## What the Script Tests

The script tests all 5 endpoints with appropriate sample data:

### 1. Default Endpoint (`default`)
- **Input**: JSON order data (Star Wars themed)
- **Output**: XML format
- **Engine**: Dynamic

### 2. XML to JSON Endpoint (`xml-to-json`)
- **Input**: XML order data
- **Output**: JSON format
- **Engine**: Dynamic

### 3. YAML to JSON Endpoint (`yaml-to-json`)
- **Input**: YAML order configuration
- **Output**: JSON format
- **Engine**: Dynamic

### 4. JSON to YAML Endpoint (`json-to-yaml`)
- **Input**: JSON order data
- **Output**: YAML format
- **Engine**: Dynamic

### 5. CSV to JSON Endpoint (`csv-to-json`)
- **Input**: CSV user data
- **Output**: JSON array of objects
- **Engine**: Dynamic

## Sample Data

The script includes realistic sample data for each endpoint:

- **Star Wars order data** for JSON to XML conversion
- **XML order structure** with customer and items
- **YAML configuration** with nested structures
- **CSV user data** with multiple records

## Expected Output

For each endpoint, the script will:
1. Show the endpoint being tested
2. Display request details (URL, content type, input size)
3. Show response status and headers
4. Display the formatted output based on content type
5. Indicate success (✅) or failure (❌)

## Configuration

You can modify these variables in the script:
- `BASE_URL`: The base URL of your Django server (default: `http://localhost:8000`)
- `API_KEY`: The API key for authentication (default: `default_key`)

## Troubleshooting

- **Connection Error**: Make sure your Django server is running
- **Authentication Error**: Verify the API key is correct
- **404 Error**: Check that the endpoints are properly configured in the database
- **500 Error**: Check Django server logs for detailed error information 