#!/usr/bin/env python3
"""
Test script for all translation endpoints
This script tests all the dynamic endpoints with sample data
"""

import requests
import json
import yaml
import csv
import io
import sys
import uuid
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port
API_KEY = "default_key"  # From the init script
BATCH_SIZE = 10  # Number of parallel requests per endpoint

# Global progress tracking
progress_lock = threading.Lock()
active_requests = 0
completed_requests = 0
total_requests = 0
request_status = {}  # Track status of each request

# Sample data for different endpoints
SAMPLE_DATA = {
    "default": {
        "input": {
            "order_id": "SW-20250318-001",
            "customer": {
                "customer_id": "CUST-1001",
                "name": "Luke Skywalker",
                "email": "luke@rebelalliance.com",
                "phone": "+1234567890",
                "shipping_address": {
                    "street": "77 Jedi Temple Way",
                    "city": "Coruscant",
                    "sector": "Core Worlds",
                    "postal_code": "SW77",
                    "planet": "Coruscant"
                }
            },
            "order_date": "2025-03-18T14:30:00Z",
            "status": "Processing",
            "items": [
                {
                    "item_id": "ITEM-0001",
                    "name": "Lightsaber - Blue",
                    "category": "Weapons",
                    "price": 199.99,
                    "quantity": 1,
                    "total": 199.99
                }
            ],
            "total_amount": 655.46,
            "notes": "May the Force be with you!"
        },
        "content_type": "json"
    },
    
    "xml-to-json": {
        "input": """<?xml version="1.0" encoding="UTF-8"?>
<order id="12345" status="pending">
    <customer>
        <name>John Doe</name>
        <email>john.doe@example.com</email>
        <address>
            <street>123 Main St</street>
            <city>Anytown</city>
            <state>CA</state>
            <zipCode>90210</zipCode>
        </address>
    </customer>
    <items>
        <item id="item1" quantity="2" price="29.99">
            <name>Widget A</name>
            <description>High-quality widget</description>
        </item>
        <item id="item2" quantity="1" price="49.99">
            <name>Widget B</name>
            <description>Premium widget</description>
        </item>
    </items>
    <total>109.97</total>
    <orderDate>2024-01-15</orderDate>
</order>""",
        "content_type": "xml"
    },
    
    "yaml-to-json": {
        "input": """# Order configuration
order:
  id: 12345
  status: pending
  customer:
    name: John Doe
    email: john.doe@example.com
    address:
      street: 123 Main St
      city: Anytown
      state: CA
      zipCode: 90210
  
  items:
    - id: item1
      quantity: 2
      price: 29.99
      name: Widget A
      description: High-quality widget
    - id: item2
      quantity: 1
      price: 49.99
      name: Widget B
      description: Premium widget
  
  total: 109.97
  orderDate: 2024-01-15

# Additional metadata
metadata:
  createdBy: system
  version: 1.0
  tags:
    - order
    - customer
    - items""",
        "content_type": "yaml"
    },
    
    "json-to-yaml": {
        "input": {
            "order": {
                "id": "12345",
                "status": "pending",
                "customer": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "address": {
                        "street": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "zipCode": "90210"
                    }
                },
                "items": [
                    {
                        "id": "item1",
                        "quantity": 2,
                        "price": 29.99,
                        "name": "Widget A",
                        "description": "High-quality widget"
                    },
                    {
                        "id": "item2",
                        "quantity": 1,
                        "price": 49.99,
                        "name": "Widget B",
                        "description": "Premium widget"
                    }
                ],
                "total": 109.97,
                "orderDate": "2024-01-15"
            },
            "metadata": {
                "createdBy": "system",
                "version": "1.0",
                "tags": ["order", "customer", "items"]
            }
        },
        "content_type": "json"
    },
    
    "csv-to-json": {
        "input": """name,email,age,city,country
John Doe,john.doe@example.com,30,New York,USA
Jane Smith,jane.smith@example.com,25,London,UK
Bob Johnson,bob.johnson@example.com,35,Toronto,Canada
Alice Brown,alice.brown@example.com,28,Sydney,Australia
Charlie Wilson,charlie.wilson@example.com,32,Berlin,Germany""",
        "content_type": "csv"
    }
}

def update_progress(request_id, status, endpoint_key):
    """Update progress tracking with thread safety"""
    global active_requests, completed_requests, request_status
    
    with progress_lock:
        if status == "started":
            active_requests += 1
            request_status[request_id] = {
                "status": "🔄 Executing",
                "start_time": time.time(),
                "endpoint": endpoint_key
            }
        elif status == "completed":
            active_requests -= 1
            completed_requests += 1
            if request_id in request_status:
                request_status[request_id]["status"] = "✅ Completed"
                request_status[request_id]["end_time"] = time.time()
        
        # Print current progress
        print(f"\r📊 Progress: {completed_requests}/{total_requests} completed, {active_requests} active | ", end="")
        if active_requests > 0:
            active_list = [f"#{req_id}" for req_id, info in request_status.items() 
                         if info["status"] == "🔄 Executing"]
            print(f"Active: {', '.join(active_list)}", end="")
        print("", end="", flush=True)

def add_random_field(data, content_type):
    """Add a random field to the input data to prevent caching"""
    random_id = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    
    if content_type == "json":
        if isinstance(data, dict):
            data["_random_id"] = random_id
            data["_timestamp"] = timestamp
            data["_cache_buster"] = f"test_{timestamp}_{random_id[:8]}"
        return data
    elif content_type == "xml":
        # Add random attributes to the root element
        if "<order" in data:
            data = data.replace('<order', f'<order random_id="{random_id}" timestamp="{timestamp}"')
        elif "<" in data:
            # Find the first tag and add attributes
            lines = data.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('<') and not line.strip().startswith('<?xml'):
                    tag_name = line.strip().split()[0][1:]  # Remove < and get tag name
                    if tag_name.endswith('>'):
                        tag_name = tag_name[:-1]
                    lines[i] = line.replace(f'<{tag_name}', f'<{tag_name} random_id="{random_id}" timestamp="{timestamp}"')
                    break
            data = '\n'.join(lines)
        return data
    elif content_type == "yaml":
        # Add random fields at the end
        data += f"\n# Random fields to prevent caching\n_random_id: {random_id}\n_timestamp: {timestamp}\n_cache_buster: test_{timestamp}_{random_id[:8]}"
        return data
    elif content_type == "csv":
        # Add a random row
        data += f"\nRandom User,random_{random_id[:8]}@test.com,{timestamp % 100},{random_id[:8]},Test Country"
        return data
    else:
        return data

def test_single_request(endpoint_key, sample_data, request_id):
    """Test a single request with random fields added and progress tracking"""
    global request_status
    
    url = f"{BASE_URL}/api/translate/{endpoint_key}"
    
    # Update progress - request started
    update_progress(request_id, "started", endpoint_key)
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add random fields to prevent caching
    modified_input = add_random_field(sample_data["input"], sample_data["content_type"])
    
    # Prepare payload
    payload = {
        "body": modified_input,
        "content_type": sample_data["content_type"]
    }
    
    try:
        # Make the request with timing
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        # Calculate response time
        response_time = end_time - start_time
        
        # Update progress - request completed
        update_progress(request_id, "completed", endpoint_key)
        
        return {
            "request_id": request_id,
            "endpoint": endpoint_key,
            "status_code": response.status_code,
            "response_time": response_time,
            "success": response.status_code == 200,
            "error": response.text if response.status_code != 200 else None,
            "start_time": start_time,
            "end_time": end_time
        }
        
    except requests.exceptions.ConnectionError:
        update_progress(request_id, "completed", endpoint_key)
        return {
            "request_id": request_id,
            "endpoint": endpoint_key,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": "Connection Error - Make sure the Django server is running on localhost:8000",
            "start_time": time.time(),
            "end_time": time.time()
        }
    except Exception as e:
        update_progress(request_id, "completed", endpoint_key)
        return {
            "request_id": request_id,
            "endpoint": endpoint_key,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": f"Exception: {str(e)}",
            "start_time": time.time(),
            "end_time": time.time()
        }

def test_endpoint_batch(endpoint_key, sample_data):
    """Test an endpoint with a batch of parallel requests"""
    global total_requests
    
    print(f"\n{'='*60}")
    print(f"Testing endpoint: {endpoint_key} with {BATCH_SIZE} parallel requests")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/translate/{endpoint_key}"
    print(f"URL: {url}")
    print(f"Content-Type: {sample_data['content_type']}")
    print(f"Input size: {len(str(sample_data['input']))} characters")
    print(f"Batch size: {BATCH_SIZE}")
    
    # Track total time for all requests
    batch_start_time = time.time()
    
    # Create tasks for parallel execution
    tasks = []
    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        # Submit all requests
        for i in range(BATCH_SIZE):
            future = executor.submit(test_single_request, endpoint_key, sample_data, i + 1)
            tasks.append(future)
        
        # Collect results as they complete
        results = []
        for future in as_completed(tasks):
            result = future.result()
            results.append(result)
            
            # Print individual result with timing details
            status_icon = "✅" if result["success"] else "❌"
            timing_info = f"Time: {result['response_time']:.3f}s" if result['response_time'] else "Time: N/A"
            print(f"\nRequest {result['request_id']:2d}: {status_icon} "
                  f"Status: {result['status_code'] or 'N/A'} "
                  f"{timing_info}")
            
            if not result["success"] and result["error"]:
                print(f"         Error: {result['error']}")
    
    # Calculate total time for all requests
    batch_end_time = time.time()
    total_time_all_requests = batch_end_time - batch_start_time
    
    # Calculate statistics
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    print(f"\n📊 Batch Results for {endpoint_key}:")
    print(f"   Total requests: {len(results)}")
    print(f"   Successful: {len(successful_requests)}")
    print(f"   Failed: {len(failed_requests)}")
    print(f"   Total batch time: {total_time_all_requests:.3f}s")
    
    if successful_requests:
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
        min_response_time = min(r["response_time"] for r in successful_requests)
        max_response_time = max(r["response_time"] for r in successful_requests)
        total_individual_time = sum(r["response_time"] for r in successful_requests)
        
        print(f"   Average response time per request: {avg_response_time:.3f}s")
        print(f"   Min response time per request: {min_response_time:.3f}s")
        print(f"   Max response time per request: {max_response_time:.3f}s")
        print(f"   Total time for individual requests: {total_individual_time:.3f}s")
        print(f"   Parallel efficiency: {(total_individual_time/total_time_all_requests)*100:.1f}%" if total_time_all_requests > 0 else "N/A")
    
    if failed_requests:
        print(f"   Failed requests: {len(failed_requests)}")
        for failed in failed_requests:
            print(f"     Request {failed['request_id']}: {failed['error']}")
    
    return results

def main():
    """Main function to test all endpoints with parallel batches"""
    global total_requests, active_requests, completed_requests, request_status
    
    print("🚀 Starting endpoint tests with parallel batches...")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Batch size per endpoint: {BATCH_SIZE}")
    
    # Calculate total requests
    total_requests = len(SAMPLE_DATA) * BATCH_SIZE
    active_requests = 0
    completed_requests = 0
    request_status = {}
    
    # Track overall timing
    overall_start_time = time.time()
    all_results = {}
    all_individual_times = []
    
    print(f"\n📋 Total requests to execute: {total_requests}")
    print("Starting execution...\n")
    
    # Test all endpoints
    for endpoint_key, sample_data in SAMPLE_DATA.items():
        results = test_endpoint_batch(endpoint_key, sample_data)
        all_results[endpoint_key] = results
        
        # Collect individual request times
        for result in results:
            if result["response_time"] is not None:
                all_individual_times.append(result["response_time"])
    
    # Calculate overall timing
    overall_end_time = time.time()
    total_time_all_requests = overall_end_time - overall_start_time
    total_individual_time = sum(all_individual_times)
    
    # Print final summary
    print(f"\n{'='*60}")
    print("🎉 All batch tests completed!")
    print(f"{'='*60}")
    
    total_requests_executed = sum(len(results) for results in all_results.values())
    total_successful = sum(len([r for r in results if r["success"]]) for results in all_results.values())
    total_failed = total_requests_executed - total_successful
    
    print(f"📈 Final Summary:")
    print(f"   Total requests executed: {total_requests_executed}")
    print(f"   Total successful: {total_successful}")
    print(f"   Total failed: {total_failed}")
    print(f"   Success rate: {(total_successful/total_requests_executed)*100:.1f}%" if total_requests_executed > 0 else "N/A")
    print(f"   Total execution time: {total_time_all_requests:.3f}s")
    print(f"   Total time for individual requests: {total_individual_time:.3f}s")
    print(f"   Overall parallel efficiency: {(total_individual_time/total_time_all_requests)*100:.1f}%" if total_time_all_requests > 0 else "N/A")
    
    if all_individual_times:
        avg_individual_time = sum(all_individual_times) / len(all_individual_times)
        min_individual_time = min(all_individual_times)
        max_individual_time = max(all_individual_times)
        print(f"   Average individual request time: {avg_individual_time:.3f}s")
        print(f"   Min individual request time: {min_individual_time:.3f}s")
        print(f"   Max individual request time: {max_individual_time:.3f}s")
    
    print(f"\n📊 Per-endpoint results:")
    for endpoint_key, results in all_results.items():
        successful = len([r for r in results if r["success"]])
        print(f"   {endpoint_key}: {successful}/{len(results)} successful")

if __name__ == "__main__":
    main() 