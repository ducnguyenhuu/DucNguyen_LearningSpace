#!/usr/bin/env python3
"""
Demo script to test the AI Log Analysis tool with real New Relic data.

This script demonstrates the end-to-end workflow:
1. Load configuration
2. Fetch data from New Relic API
3. Calculate health score
4. Generate and save report
"""

import sys
from datetime import datetime
from modules.config_loader import load_config
from modules.api_client import ApiClient
from modules.health_calculator import HealthCalculator
from modules.report_generator import ReportGenerator


def main():
    """Run a complete health assessment."""
    print("=" * 70)
    print("AI-Powered Log Analysis - New Relic Health Assessment")
    print("=" * 70)
    print()
    
    # Step 1: Load configuration
    print("Step 1: Loading configuration...")
    try:
        config = load_config(profile='dev')
        print(f"✓ Configuration loaded successfully")
        print(f"  - Profile: dev")
        print(f"  - Account ID: {config['account_id']}")
        print(f"  - App IDs: {config['app_ids']}")
        print()
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        print()
        print("Please edit .newrelic_config.dev.json and add your New Relic credentials:")
        print("  1. Get API Key: New Relic → Account Settings → API Keys → User Key")
        print("  2. Get Account ID: New Relic → Account Settings → Account Information")
        print("  3. Get App ID: New Relic → APM → Select your app → Settings → Application")
        sys.exit(1)
    
    # Step 2: Initialize API client
    print("Step 2: Connecting to New Relic API...")
    api_client = ApiClient(
        api_key=config['api_key'],
        account_id=config['account_id'],
        timeout=config.get('timeout', 30),
        max_retries=config.get('max_retries', 2)
    )
    
    # For demo, we'll use the first app ID
    app_id = config['app_ids'][0]
    app_name = config.get('app_name', f'app-{app_id}')
    days = config.get('days', 7)
    
    print(f"✓ API client initialized")
    print(f"  - App ID: {app_id}")
    print(f"  - Time period: Last {days} days")
    print()
    
    # Step 3: Fetch data from New Relic
    print("Step 3: Fetching metrics from New Relic...")
    print("  (This may take 30-60 seconds...)")
    try:
        # Fetch performance metrics
        print("  - Fetching performance metrics...")
        performance_data = api_client.fetch_performance_metrics(app_id, days)
        
        # Fetch error metrics
        print("  - Fetching error metrics...")
        error_data = api_client.fetch_error_metrics(app_id, days)
        
        # Fetch infrastructure metrics
        print("  - Fetching infrastructure metrics...")
        infrastructure_data = api_client.fetch_infrastructure_metrics(app_id, days)
        
        # Fetch database metrics
        print("  - Fetching database metrics...")
        database_data = api_client.fetch_database_metrics(app_id, days)
        
        # Fetch API/transaction metrics
        print("  - Fetching API/transaction metrics...")
        api_data = api_client.fetch_api_metrics(app_id, days)
        
        print(f"✓ Data fetched successfully")
        print()
    except Exception as e:
        print(f"✗ API error: {e}")
        print()
        print("Common issues:")
        print("  - Invalid API key (check .newrelic_config.dev.json)")
        print("  - Invalid account ID or app ID")
        print("  - Network connectivity issues")
        print("  - New Relic API rate limits")
        sys.exit(1)
    
    # Step 4: Calculate health score
    print("Step 4: Calculating health score...")
    calculator = HealthCalculator()
    
    # Combine all metrics
    metrics = {
        'performance': performance_data,
        'errors': error_data,
        'infrastructure': infrastructure_data,
        'database': database_data,
        'api': api_data
    }
    
    health_data = calculator.calculate_health(metrics)
    
    print(f"✓ Health score calculated: {health_data['overall_score']}/100")
    print(f"  - Status: {health_data['status']}")
    print(f"  - Critical Issues: {health_data['critical_count']}")
    print()
    
    # Step 5: Generate report
    print("Step 5: Generating health report...")
    generator = ReportGenerator()
    
    # Prepare config for report
    report_config = {
        'app_name': app_name,
        'account_id': config['account_id'],
        'app_id': app_id,
        'days': days
    }
    
    report = generator.generate_report(report_config, health_data)
    print(f"✓ Report generated ({len(report)} characters)")
    print()
    
    # Step 6: Save report
    print("Step 6: Saving report to disk...")
    filepath = generator.save_report(report, app_id=app_name)
    print()
    
    # Summary
    print("=" * 70)
    print("Assessment Complete!")
    print("=" * 70)
    print(f"Health Score: {health_data['overall_score']}/100 ({health_data['status']})")
    print(f"Report saved: {filepath}")
    print()
    print("Next steps:")
    print("  1. Open the report in VS Code to review findings")
    print("  2. Run @recommend-agent in GitHub Copilot Chat for AI-powered recommendations")
    print("  3. Implement recommended fixes")
    print()


if __name__ == '__main__':
    main()
