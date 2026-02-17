# New Relic APM Health Assessment Tool

A Python-based tool for assessing the health of applications monitored by New Relic APM. This tool collects performance metrics, analyzes health scores, and generates comprehensive reports with AI-powered insights.

## Features

- 📊 **Multi-Metric Health Analysis** - Analyzes 5 key metric categories (Performance, Errors, Infrastructure, Database, API/Transactions)
- 🔄 **Multi-Profile Configuration** - Supports separate dev and prod environments
- 📈 **Weighted Health Scoring** - 0-100 health scores with severity categorization
- 🤖 **AI-Powered Insights** - GitHub Copilot agents for analysis and code recommendations
- 📝 **Markdown Reports** - Executive summaries with actionable recommendations
- 💾 **Smart Caching** - Reduces redundant API calls with configurable cache retention

## Requirements

- **Python 3.11+** (required)
- New Relic account with APM data
- New Relic User API key (NRAK-...)
- GitHub Copilot (optional, for AI-powered insights)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-log-analysis
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure New Relic Credentials

#### Create Dev Configuration

```bash
# Copy the example template
cp .newrelic_config.example.json .newrelic_config.dev.json

# Edit with your credentials
nano .newrelic_config.dev.json
```

Update the file with your New Relic credentials:

```json
{
  "api_key": "NRAK-YOUR_NEW_RELIC_USER_KEY_HERE",
  "account_id": "1234567",
  "app_ids": ["9876543", "1111111"],
  "app_name": "my-dev-application",
  "description": "Development environment"
}
```

#### Create Prod Configuration (Optional)

```bash
cp .newrelic_config.example.json .newrelic_config.prod.json
# Edit with production credentials
```

### 5. Run Health Assessment

```bash
# Use default profile (dev) and default time period (30 days)
python crawler.py

# Specify profile and time period
python crawler.py --profile dev --days 7

# Assess specific application
python crawler.py --profile prod --app my-prod-app --days 14
```

**Note:** The crawler is not yet implemented. This is a planned feature for Epic 2.

## Configuration

### Profile Configuration Files

Configuration files are environment-specific and stored as `.newrelic_config.{profile}.json`:

- `.newrelic_config.dev.json` - Development environment
- `.newrelic_config.prod.json` - Production environment

**Required Fields:**
- `api_key` (string) - Your New Relic User API key
- `account_id` (string) - Your New Relic account ID (numeric)
- `app_ids` (array) - List of application IDs to assess
- `app_name` (string) - Application name for report generation
- `description` (string) - Optional description

### Application Defaults (config.yaml)

The `config.yaml` file contains application-wide default settings:

```yaml
api:
  timeout: 30                # API request timeout in seconds
  max_retries: 2            # Number of retry attempts for failed requests
  retry_delay: 5            # Delay between retries in seconds
  
cache:
  staleness: 3600           # Cache validity in seconds (1 hour)
  retention_days: 30        # Keep old data files for 30 days
  
logging:
  level: INFO               # Console log level (DEBUG, INFO, WARNING, ERROR)
  file_level: DEBUG         # Log file level (capture everything)
  
defaults:
  days: 30                  # Default time period for data collection
  profile: dev              # Default profile if not specified
```

**Configuration Priority:**
1. CLI arguments (highest priority)
2. Profile-specific JSON file (`.newrelic_config.{profile}.json`)
3. Application defaults (`config.yaml`)

### Time Period Options

The `--days` parameter accepts only these values:
- `3` - Last 3 days
- `7` - Last 7 days (one week)
- `14` - Last 14 days (two weeks)
- `30` - Last 30 days (one month, default)

## Project Structure

```
ai-log-analysis/
├── config.yaml                      # Application defaults
├── .newrelic_config.example.json   # Template (committed)
├── .newrelic_config.dev.json       # Dev credentials (gitignored)
├── .newrelic_config.prod.json      # Prod credentials (gitignored)
├── requirements.txt                 # Python dependencies
├── modules/                         # Core application modules
│   ├── __init__.py
│   └── config_loader.py            # Configuration loading and validation
├── agents/                          # AI agent instruction files
├── data/                           # Cached APM data (gitignored)
├── logs/                           # Application logs (gitignored)
├── reports/                        # Generated health reports
└── tests/                          # Test suite
    ├── __init__.py
    ├── test_config_loader.py
    └── test_project_structure.py
```

## Usage Examples

### Basic Usage

```bash
# Run with default settings (dev profile, 30 days)
python crawler.py

# Specify time period
python crawler.py --days 7

# Use production profile
python crawler.py --profile prod
```

### Advanced Usage

```bash
# Production assessment with 14-day window
python crawler.py --profile prod --days 14

# Override timeout for slow networks
python crawler.py --profile dev --timeout 60

# Custom application assessment
python crawler.py --profile dev --app critical-service --days 3
```

## Testing

Run the test suite to verify your setup:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_config_loader.py -v

# Run with coverage report
python3 -m pytest tests/ --cov=modules --cov-report=html
```

**Current Test Coverage:** 59 tests, 100% passing

## Troubleshooting

### Common Issues

#### Configuration Validation Errors

**Error:** `API key missing in configuration file`

**Solution:**
```bash
# Ensure you created the profile configuration file
cp .newrelic_config.example.json .newrelic_config.dev.json

# Edit and add your New Relic API key
nano .newrelic_config.dev.json
```

---

**Error:** `Account ID must be numeric. Expected format: 1234567`

**Solution:**
- Ensure `account_id` is a string containing only digits
- Example: `"account_id": "1234567"` ✅
- Invalid: `"account_id": "abc123"` ❌

---

**Error:** `app_ids must be a non-empty list`

**Solution:**
- Ensure `app_ids` is an array with at least one application ID
- Example: `"app_ids": ["9876543"]` ✅
- Invalid: `"app_ids": []` ❌

---

**Error:** `days must be one of [3, 7, 14, 30]`

**Solution:**
- Use only allowed values: 3, 7, 14, or 30
- Example: `python crawler.py --days 7` ✅
- Invalid: `python crawler.py --days 10` ❌

---

**Error:** `Profile file '.newrelic_config.prod.json' not found`

**Solution:**
```bash
# Create the missing profile configuration
cp .newrelic_config.example.json .newrelic_config.prod.json

# Edit with your production credentials
nano .newrelic_config.prod.json
```

#### Installation Issues

**Error:** `ModuleNotFoundError: No module named 'yaml'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

**Error:** `Python version mismatch`

**Solution:**
```bash
# Check Python version (must be 3.11+)
python3 --version

# If version is too old, install Python 3.11+
# macOS (using Homebrew):
brew install python@3.11

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.11
```

#### API Connection Issues

**Error:** `Connection timeout to New Relic API`

**Solution:**
- Check your internet connection
- Increase timeout in config.yaml or via CLI:
  ```bash
  python crawler.py --timeout 60
  ```
- Verify firewall settings allow HTTPS connections

---

**Error:** `Invalid API key`

**Solution:**
- Verify your API key is a User API key (starts with `NRAK-`)
- Generate a new key at: `https://one.newrelic.com/api-keys`
- Ensure the key has appropriate permissions

## Security Best Practices

**⚠️ CRITICAL SECURITY WARNINGS:**

### Never Commit API Keys

- **DO NOT** commit `.newrelic_config.*.json` files to version control
- The `.gitignore` file automatically excludes `*.json` files
- Only commit `.newrelic_config.example.json` (template with placeholders)

### Verify .gitignore Protection

```bash
# Verify JSON files are ignored
git status

# Should NOT show:
# - .newrelic_config.dev.json
# - .newrelic_config.prod.json

# Should show (if not committed):
# ?? .newrelic_config.example.json (template only)
```

### Creating Profile Configurations

**Safe Workflow:**

1. Copy the example template:
   ```bash
   cp .newrelic_config.example.json .newrelic_config.dev.json
   ```

2. Edit the new file with real credentials:
   ```bash
   nano .newrelic_config.dev.json
   ```

3. Verify it's gitignored:
   ```bash
   git status  # Should NOT appear in changes
   ```

4. Never use `git add -A` or `git add .` - always specify files explicitly

### Environment-Specific Credentials

- Use `.newrelic_config.dev.json` for development/testing
- Use `.newrelic_config.prod.json` for production assessments
- Keep credentials separate and secure
- Rotate API keys periodically

### API Key Permissions

Your New Relic User API key needs:
- ✅ Read access to APM data
- ✅ Read access to NRQL queries
- ❌ No write permissions required (read-only operation)

## AI-Powered Insights (Coming Soon)

This tool integrates with GitHub Copilot for enhanced analysis:

### Available Copilot Agents

- **@analysis-agent** - Analyzes health metrics and generates scores
- **@recommend-agent** - Provides code-specific improvement recommendations

### Usage (Planned)

```bash
# In GitHub Copilot Chat
@analysis-agent analyze the health report for critical-service

@recommend-agent suggest fixes for N+1 query issues in user-service
```

**Note:** Agent functionality requires GitHub Copilot subscription.

## Roadmap

### ✅ Completed (Epic 1)
- [x] Project structure initialization
- [x] Configuration loader with multi-profile support
- [x] Configuration validation with fail-fast
- [x] Setup documentation and templates

### 🚧 In Progress (Epic 2)
- [ ] New Relic API client with retry logic
- [ ] Performance metrics collection
- [ ] Error metrics collection
- [ ] Infrastructure metrics collection
- [ ] Database metrics collection
- [ ] API/Transaction metrics collection
- [ ] Data caching with auto-cleanup
- [ ] Comprehensive logging with progress indicators

### 📋 Planned
- **Epic 3:** Health Analysis Engine
- **Epic 4:** Report Generation
- **Epic 5:** AI Agent Integration
- **Epic 6:** Testing & Finalization

## Contributing

This is a learning project. Contributions and suggestions are welcome!

## License

[Specify your license here]

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review test suite: `python3 -m pytest tests/ -v`
3. Check logs in `/logs` directory for detailed error messages

## Changelog

### v0.1.0 (2026-02-16)
- Initial project setup
- Configuration management system
- Multi-profile environment support
- Comprehensive test suite (59 tests)
- Setup documentation

---

**Built with Python 3.11+ | Powered by New Relic APM | Enhanced by GitHub Copilot**
