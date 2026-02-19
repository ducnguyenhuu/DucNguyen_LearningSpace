"""
Unit tests for report_generator module.

Tests the ReportGenerator class including report generation,
executive summary, metadata sections, metric breakdowns,
findings, recommendations, and file saving.
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from modules.report_generator import ReportGenerator


class TestReportGeneratorInitialization(unittest.TestCase):
    """Test ReportGenerator initialization."""
    
    def test_init_creates_instance(self):
        """Test that ReportGenerator can be instantiated."""
        generator = ReportGenerator()
        self.assertIsInstance(generator, ReportGenerator)


class TestInputValidation(unittest.TestCase):
    """Test input validation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.valid_health_data = {
            "overall_score": 75,
            "status": "Good",
            "status_emoji": "🟡",
            "category_scores": {
                "performance": 80,
                "errors": 70,
                "infrastructure": 75,
                "database": 70,
                "api": 80
            },
            "findings": []
        }
        self.valid_config = {
            "days": 7,
            "new_relic": {
                "account_id": "12345",
                "api_key": "secret"
            }
        }
    
    def test_validate_inputs_with_valid_data(self):
        """Test validation passes with valid inputs."""
        # Should not raise exception
        self.generator._validate_inputs(self.valid_health_data, self.valid_config)
    
    def test_validate_inputs_missing_overall_score(self):
        """Test validation fails when overall_score is missing."""
        invalid_data = self.valid_health_data.copy()
        del invalid_data["overall_score"]
        
        with self.assertRaises(ValueError) as cm:
            self.generator._validate_inputs(invalid_data, self.valid_config)
        
        self.assertIn("overall_score", str(cm.exception))
    
    def test_validate_inputs_missing_status(self):
        """Test validation fails when status is missing."""
        invalid_data = self.valid_health_data.copy()
        del invalid_data["status"]
        
        with self.assertRaises(ValueError) as cm:
            self.generator._validate_inputs(invalid_data, self.valid_config)
        
        self.assertIn("status", str(cm.exception))
    
    def test_validate_inputs_missing_findings(self):
        """Test validation fails when findings is missing."""
        invalid_data = self.valid_health_data.copy()
        del invalid_data["findings"]
        
        with self.assertRaises(ValueError) as cm:
            self.generator._validate_inputs(invalid_data, self.valid_config)
        
        self.assertIn("findings", str(cm.exception))
    
    def test_validate_inputs_missing_days_config(self):
        """Test validation fails when days is missing from config."""
        invalid_config = {"new_relic": {"account_id": "12345"}}
        
        with self.assertRaises(ValueError) as cm:
            self.generator._validate_inputs(self.valid_health_data, invalid_config)
        
        self.assertIn("days", str(cm.exception))


class TestHeaderGeneration(unittest.TestCase):
    """Test report header generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_generate_header_with_app_name(self):
        """Test header includes application name."""
        header = self.generator._generate_header("my-api-service")
        
        self.assertIn("# Health Assessment:", header)
        self.assertIn("my-api-service", header)
    
    def test_generate_header_format(self):
        """Test header uses markdown H1 format."""
        header = self.generator._generate_header("test-app")
        
        self.assertTrue(header.startswith("# "))


class TestExecutiveSummaryGeneration(unittest.TestCase):
    """Test executive summary generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.health_data = {
            "overall_score": 58,
            "status": "Warning",
            "status_emoji": "🟠",
            "findings": [
                {"severity": "Critical", "issue": "High CPU"},
                {"severity": "Critical", "issue": "Slow queries"},
                {"severity": "Warning", "issue": "High error rate"}
            ]
        }
        self.config = {"days": 7}
    
    def test_executive_summary_includes_score(self):
        """Test executive summary includes overall health score."""
        summary = self.generator._generate_executive_summary(
            self.health_data, self.config, None, None
        )
        
        self.assertIn("58/100", summary)
        self.assertIn("Warning", summary)
        self.assertIn("🟠", summary)
    
    def test_executive_summary_includes_critical_count(self):
        """Test executive summary includes count of critical issues."""
        summary = self.generator._generate_executive_summary(
            self.health_data, self.config, None, None
        )
        
        self.assertIn("**Critical Issues Found:** 2", summary)
    
    def test_executive_summary_includes_assessment_period(self):
        """Test executive summary includes assessment period."""
        summary = self.generator._generate_executive_summary(
            self.health_data, self.config, None, None
        )
        
        self.assertIn("Assessment Period:", summary)
        self.assertIn("7 days", summary)
    
    def test_executive_summary_with_date_range(self):
        """Test executive summary includes date range when provided."""
        start = datetime(2026, 2, 11, 10, 0, 0)
        end = datetime(2026, 2, 18, 10, 0, 0)
        
        summary = self.generator._generate_executive_summary(
            self.health_data, self.config, start, end
        )
        
        self.assertIn("2026-02-11", summary)
        self.assertIn("2026-02-18", summary)
    
    def test_executive_summary_with_zero_critical_issues(self):
        """Test executive summary with no critical issues."""
        health_data = self.health_data.copy()
        health_data["findings"] = [
            {"severity": "Warning", "issue": "Minor issue"}
        ]
        
        summary = self.generator._generate_executive_summary(
            health_data, self.config, None, None
        )
        
        self.assertIn("**Critical Issues Found:** 0", summary)
    
    def test_executive_summary_excellent_status(self):
        """Test executive summary with excellent status."""
        health_data = {
            "overall_score": 95,
            "status": "Excellent",
            "status_emoji": "🟢",
            "findings": []
        }
        
        summary = self.generator._generate_executive_summary(
            health_data, self.config, None, None
        )
        
        self.assertIn("95/100", summary)
        self.assertIn("Excellent", summary)
        self.assertIn("🟢", summary)


class TestMetadataGeneration(unittest.TestCase):
    """Test metadata section generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.config = {
            "new_relic": {
                "account_id": "1234567",
                "api_key": "secret-key"
            },
            "days": 7
        }
    
    def test_metadata_includes_account_id(self):
        """Test metadata includes New Relic account ID."""
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, None, None, None
        )
        
        self.assertIn("New Relic Account ID:", metadata)
        self.assertIn("1234567", metadata)
    
    def test_metadata_includes_app_id(self):
        """Test metadata includes application ID."""
        metadata = self.generator._generate_metadata_section(
            "production-api", self.config, None, None, None
        )
        
        self.assertIn("Application ID:", metadata)
        self.assertIn("production-api", metadata)
    
    def test_metadata_includes_iso_timestamp(self):
        """Test metadata includes ISO 8601 timestamp."""
        with patch("modules.report_generator.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2026, 2, 18, 15, 30, 45)
            
            metadata = self.generator._generate_metadata_section(
                "my-app", self.config, None, None, None
            )
            
            self.assertIn("Assessment Timestamp:", metadata)
            self.assertIn("2026-02-18T15:30:45Z", metadata)
    
    def test_metadata_with_collection_duration_minutes(self):
        """Test metadata includes data collection duration in minutes."""
        start = datetime(2026, 2, 18, 10, 0, 0)
        end = datetime(2026, 2, 18, 10, 12, 0)
        
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, start, end, None
        )
        
        self.assertIn("Data Collection Duration:", metadata)
        self.assertIn("12 minutes", metadata)
    
    def test_metadata_with_collection_duration_seconds(self):
        """Test metadata includes data collection duration in seconds for short durations."""
        start = datetime(2026, 2, 18, 10, 0, 0)
        end = datetime(2026, 2, 18, 10, 0, 45)
        
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, start, end, None
        )
        
        self.assertIn("45 seconds", metadata)
    
    def test_metadata_fresh_cache_status(self):
        """Test metadata shows fresh data when cache_age is None."""
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, None, None, None
        )
        
        self.assertIn("Cache Status:", metadata)
        self.assertIn("Fresh data", metadata)
    
    def test_metadata_cached_seconds(self):
        """Test metadata shows cache age in seconds."""
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, None, None, 45
        )
        
        self.assertIn("Cached data (45 seconds old)", metadata)
    
    def test_metadata_cached_minutes(self):
        """Test metadata shows cache age in minutes."""
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, None, None, 300
        )
        
        self.assertIn("Cached data (5 minutes old)", metadata)
    
    def test_metadata_cached_hours(self):
        """Test metadata shows cache age in hours."""
        metadata = self.generator._generate_metadata_section(
            "my-app", self.config, None, None, 7200
        )
        
        self.assertIn("Cached data (2 hours old)", metadata)
    
    def test_metadata_missing_account_id(self):
        """Test metadata handles missing account ID gracefully."""
        config = {"days": 7}
        
        metadata = self.generator._generate_metadata_section(
            "my-app", config, None, None, None
        )
        
        self.assertIn("N/A", metadata)


class TestFullReportGeneration(unittest.TestCase):
    """Test complete report generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.health_data = {
            "overall_score": 75,
            "status": "Good",
            "status_emoji": "🟡",
            "category_scores": {
                "performance": 80,
                "errors": 70,
                "infrastructure": 75,
                "database": 70,
                "api": 80
            },
            "findings": [
                {
                    "severity": "Warning",
                    "category": "errors",
                    "issue": "Elevated error rate",
                    "metric": "error_rate",
                    "value": "6%"
                }
            ]
        }
        self.config = {
            "days": 7,
            "new_relic": {
                "account_id": "12345",
                "api_key": "secret"
            }
        }
    
    @patch("modules.report_generator.logger")
    def test_generate_report_basic(self, mock_logger):
        """Test basic report generation returns markdown string."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config
        )
        
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
    
    def test_generate_report_includes_header(self):
        """Test generated report includes header."""
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config
        )
        
        self.assertIn("# Health Assessment: my-api", report)
    
    def test_generate_report_includes_executive_summary(self):
        """Test generated report includes executive summary."""
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config
        )
        
        self.assertIn("## Executive Summary", report)
        self.assertIn("75/100 🟡 Good", report)
    
    def test_generate_report_includes_metadata(self):
        """Test generated report includes metadata section."""
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config
        )
        
        self.assertIn("## Assessment Metadata", report)
        self.assertIn("12345", report)
    
    def test_generate_report_with_collection_times(self):
        """Test report generation with collection timestamps."""
        start = datetime(2026, 2, 18, 10, 0, 0)
        end = datetime(2026, 2, 18, 10, 15, 0)
        
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config,
            collection_start=start, collection_end=end
        )
        
        self.assertIn("2026-02-18", report)
        self.assertIn("15 minutes", report)
    
    def test_generate_report_with_cache_age(self):
        """Test report generation with cache age."""
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config,
            cache_age=600
        )
        
        self.assertIn("Cached data (10 minutes old)", report)
    
    def test_generate_report_invalid_health_data(self):
        """Test report generation fails with invalid health_data."""
        invalid_data = {"overall_score": 75}  # Missing required fields
        
        with self.assertRaises(ValueError):
            self.generator.generate_report(invalid_data, "my-api", self.config)
    
    def test_generate_report_invalid_config(self):
        """Test report generation fails with invalid config."""
        invalid_config = {"new_relic": {"account_id": "123"}}  # Missing days
        
        with self.assertRaises(ValueError):
            self.generator.generate_report(
                self.health_data, "my-api", invalid_config
            )
    
    @patch("modules.report_generator.logger")
    def test_generate_report_logs_info(self, mock_logger):
        """Test report generation logs info messages."""
        self.generator.generate_report(
            self.health_data, "my-api", self.config
        )
        
        # Verify INFO logging was called
        info_calls = [call for call in mock_logger.info.call_args_list]
        self.assertTrue(len(info_calls) > 0)
    
    def test_generate_report_sections_separated(self):
        """Test report sections are properly separated."""
        report = self.generator.generate_report(
            self.health_data, "my-api", self.config
        )
        
        # Sections should be separated by double newlines
        sections = report.split("\n\n")
        self.assertGreater(len(sections), 2)


class TestReportFormatting(unittest.TestCase):
    """Test markdown formatting of reports."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.health_data = {
            "overall_score": 92,
            "status": "Excellent",
            "status_emoji": "🟢",
            "category_scores": {},
            "findings": []
        }
        self.config = {
            "days": 14,
            "new_relic": {"account_id": "999"}
        }
    
    def test_report_uses_markdown_headers(self):
        """Test report uses proper markdown header syntax."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config
        )
        
        # Should have H1 and H2 headers
        self.assertIn("# Health", report)
        self.assertIn("## Executive", report)
        self.assertIn("## Assessment", report)
    
    def test_report_uses_bold_formatting(self):
        """Test report uses markdown bold formatting for key metrics."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config
        )
        
        self.assertIn("**Overall Health Score:**", report)
        self.assertIn("**Assessment Period:**", report)
        self.assertIn("**Critical Issues Found:**", report)
    
    def test_report_uses_bullet_points(self):
        """Test metadata section uses markdown bullet points."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config
        )
        
        # Metadata should use bullet points
        metadata_section = report.split("## Assessment Metadata")[1]
        self.assertIn("- **", metadata_section)


class TestMetricBreakdownSections(unittest.TestCase):
    """Test detailed metric breakdown sections."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.metrics = {
            'performance': {
                'response_time': 450,
                'throughput': 1200,
                'apdex_score': 0.85
            },
            'errors': {
                'error_rate': 0.03,
                'error_count': 150,
                'error_types': ['NullPointerException', 'TimeoutException', 'IOException']
            },
            'infrastructure': {
                'cpu_usage': 0.75,
                'memory_usage': 0.82,
                'disk_io': 25.5
            },
            'database': {
                'query_time': 85,
                'slow_queries': 5,
                'connection_pool_usage': 0.65,
                'database_calls': 250
            },
            'transactions': {
                'transaction_time': 425,
                'external_calls': 50,
                'external_latency': 150,
                'api_endpoints': ['/api/users', '/api/products', '/api/orders']
            }
        }
        self.category_scores = {
            'performance': 80,
            'errors': 70,
            'infrastructure': 75,
            'database': 68,
            'api': 72
        }
        self.health_data = {
            "overall_score": 73,
            "status": "Good",
            "status_emoji": "🟡",
            "category_scores": self.category_scores,
            "findings": []
        }
        self.config = {
            "days": 7,
            "new_relic": {"account_id": "12345"}
        }
    
    def test_performance_section_includes_score(self):
        """Test performance section includes category score."""
        section = self.generator._generate_performance_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("## Performance Metrics", section)
        self.assertIn("Score: 80/100", section)
        self.assertIn("🟢", section)  # Good score emoji
    
    def test_performance_section_includes_response_time(self):
        """Test performance section includes response time with threshold."""
        section = self.generator._generate_performance_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("**Response Time:** 450 ms", section)
        self.assertIn("threshold: <500ms", section)
        self.assertIn("🟢", section)  # Healthy indicator
    
    def test_performance_section_red_indicator_for_slow_response(self):
        """Test performance section shows red indicator for slow response time."""
        slow_metrics = {'performance': {'response_time': 800, 'throughput': 100, 'apdex_score': 0.4}}
        
        section = self.generator._generate_performance_section(
            slow_metrics, self.category_scores
        )
        
        self.assertIn("800 ms 🔴", section)
    
    def test_performance_section_includes_apdex(self):
        """Test performance section includes Apdex score."""
        section = self.generator._generate_performance_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("**Apdex Score:** 0.85", section)
        self.assertIn("target: >0.8", section)
    
    def test_error_section_includes_error_rate(self):
        """Test error section includes error rate as percentage."""
        section = self.generator._generate_error_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("## Error Metrics", section)
        self.assertIn("**Error Rate:** 3.0%", section)
        self.assertIn("threshold: <5%", section)
    
    def test_error_section_lists_error_types(self):
        """Test error section lists top error types."""
        section = self.generator._generate_error_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("Top Error Types:", section)
        self.assertIn("NullPointerException", section)
        self.assertIn("TimeoutException", section)
    
    def test_error_section_limits_error_types(self):
        """Test error section limits error types to top 5."""
        many_errors = {'errors': {
            'error_rate': 0.1,
            'error_count': 1000,
            'error_types': ['Error1', 'Error2', 'Error3', 'Error4', 'Error5', 'Error6', 'Error7']
        }}
        
        section = self.generator._generate_error_section(
            many_errors, self.category_scores
        )
        
        # Should include first 5
        self.assertIn("Error1", section)
        self.assertIn("Error5", section)
    
    def test_infrastructure_section_includes_cpu(self):
        """Test infrastructure section includes CPU usage."""
        section = self.generator._generate_infrastructure_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("## Infrastructure Metrics", section)
        self.assertIn("**CPU Usage:** 75.0%", section)
        self.assertIn("threshold: <80%", section)
    
    def test_infrastructure_section_includes_memory(self):
        """Test infrastructure section includes memory usage."""
        section = self.generator._generate_infrastructure_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("**Memory Usage:** 82.0%", section)
        self.assertIn("threshold: <85%", section)
    
    def test_infrastructure_section_red_indicator_high_cpu(self):
        """Test infrastructure section shows red indicator for high CPU."""
        high_cpu = {'infrastructure': {'cpu_usage': 0.85, 'memory_usage': 0.5, 'disk_io': 10}}
        
        section = self.generator._generate_infrastructure_section(
            high_cpu, self.category_scores
        )
        
        self.assertIn("85.0% 🔴", section)
    
    def test_database_section_includes_query_time(self):
        """Test database section includes average query time."""
        section = self.generator._generate_database_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("## Database Metrics", section)
        self.assertIn("**Average Query Time:** 85 ms", section)
        self.assertIn("threshold: <100ms", section)
    
    def test_database_section_includes_slow_queries(self):
        """Test database section includes slow queries count."""
        section = self.generator._generate_database_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("**Slow Queries Count:** 5", section)
    
    def test_database_section_pool_usage_warning(self):
        """Test database section shows warning for high pool usage."""
        high_pool = {'database': {
            'query_time': 50,
            'slow_queries': 0,
            'connection_pool_usage': 0.95,
            'database_calls': 100
        }}
        
        section = self.generator._generate_database_section(
            high_pool, self.category_scores
        )
        
        self.assertIn("95.0% 🔴", section)
        self.assertIn("⚠️ High pool usage", section)
    
    def test_database_section_n_plus_one_warning(self):
        """Test database section shows N+1 warning for high call count."""
        high_calls = {'database': {
            'query_time': 50,
            'slow_queries': 0,
            'connection_pool_usage': 0.5,
            'database_calls': 1500
        }}
        
        section = self.generator._generate_database_section(
            high_calls, self.category_scores
        )
        
        self.assertIn("1,500", section)
        self.assertIn("⚠️ High call count suggests possible N+1", section)
    
    def test_api_section_includes_transaction_time(self):
        """Test API section includes transaction time."""
        section = self.generator._generate_api_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("## API/Transaction Metrics", section)
        self.assertIn("**Average Transaction Time:** 425 ms", section)
    
    def test_api_section_includes_external_calls(self):
        """Test API section includes external calls count."""
        section = self.generator._generate_api_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("**External Calls Count:** 50", section)
    
    def test_api_section_lists_endpoints(self):
        """Test API section lists active endpoints."""
        section = self.generator._generate_api_section(
            self.metrics, self.category_scores
        )
        
        self.assertIn("Active Endpoints:", section)
        self.assertIn("/api/users", section)
        self.assertIn("/api/products", section)
    
    def test_api_section_limits_endpoints(self):
        """Test API section limits endpoints to top 10."""
        many_endpoints = {'transactions': {
            'transaction_time': 300,
            'external_calls': 10,
            'external_latency': 100,
            'api_endpoints': [f'/api/endpoint{i}' for i in range(15)]
        }}
        
        section = self.generator._generate_api_section(
            many_endpoints, self.category_scores
        )
        
        # Should include first 10
        self.assertIn("/api/endpoint0", section)
        self.assertIn("/api/endpoint9", section)
    
    def test_generate_report_includes_metric_sections(self):
        """Test full report includes all metric breakdown sections."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config, metrics=self.metrics
        )
        
        self.assertIn("## Performance Metrics", report)
        self.assertIn("## Error Metrics", report)
        self.assertIn("## Infrastructure Metrics", report)
        self.assertIn("## Database Metrics", report)
        self.assertIn("## API/Transaction Metrics", report)
    
    def test_generate_report_without_metrics_omits_sections(self):
        """Test report without metrics doesn't include metric sections."""
        report = self.generator.generate_report(
            self.health_data, "test-app", self.config
        )
        
        self.assertNotIn("## Performance Metrics", report)
        self.assertNotIn("## Error Metrics", report)


class TestScoreEmojiHelper(unittest.TestCase):
    """Test score emoji helper method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_excellent_score_green_emoji(self):
        """Test excellent score (80-100) returns green emoji."""
        self.assertEqual(self.generator._get_score_emoji(100), "🟢")
        self.assertEqual(self.generator._get_score_emoji(85), "🟢")
        self.assertEqual(self.generator._get_score_emoji(80), "🟢")
    
    def test_good_score_yellow_emoji(self):
        """Test good score (60-79) returns yellow emoji."""
        self.assertEqual(self.generator._get_score_emoji(79), "🟡")
        self.assertEqual(self.generator._get_score_emoji(70), "🟡")
        self.assertEqual(self.generator._get_score_emoji(60), "🟡")
    
    def test_warning_score_orange_emoji(self):
        """Test warning score (40-59) returns orange emoji."""
        self.assertEqual(self.generator._get_score_emoji(59), "🟠")
        self.assertEqual(self.generator._get_score_emoji(50), "🟠")
        self.assertEqual(self.generator._get_score_emoji(40), "🟠")
    
    def test_critical_score_red_emoji(self):
        """Test critical score (0-39) returns red emoji."""
        self.assertEqual(self.generator._get_score_emoji(39), "🔴")
        self.assertEqual(self.generator._get_score_emoji(20), "🔴")
        self.assertEqual(self.generator._get_score_emoji(0), "🔴")


class TestMissingMetricHandling(unittest.TestCase):
    """Test handling of missing or None metric values."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.category_scores = {'performance': 50, 'errors': 50, 'infrastructure': 50, 'database': 50, 'api': 50}
    
    def test_performance_section_with_none_values(self):
        """Test performance section handles None values gracefully."""
        metrics = {'performance': {'response_time': None, 'throughput': None, 'apdex_score': None}}
        
        section = self.generator._generate_performance_section(metrics, self.category_scores)
        
        self.assertIn("Response Time:** N/A", section)
        self.assertIn("Throughput:** N/A", section)
        self.assertIn("Apdex Score:** N/A", section)
    
    def test_error_section_with_none_values(self):
        """Test error section handles None values gracefully."""
        metrics = {'errors': {'error_rate': None, 'error_count': None, 'error_types': None}}
        
        section = self.generator._generate_error_section(metrics, self.category_scores)
        
        self.assertIn("Error Rate:** N/A", section)
        self.assertIn("Total Errors:** N/A", section)
        self.assertIn("Top Error Types:** N/A", section)
    
    def test_infrastructure_section_with_none_values(self):
        """Test infrastructure section handles None values gracefully."""
        metrics = {'infrastructure': {'cpu_usage': None, 'memory_usage': None, 'disk_io': None}}
        
        section = self.generator._generate_infrastructure_section(metrics, self.category_scores)
        
        self.assertIn("CPU Usage:** N/A", section)
        self.assertIn("Memory Usage:** N/A", section)
        self.assertIn("Disk I/O:** N/A", section)
    
    def test_database_section_with_none_values(self):
        """Test database section handles None values gracefully."""
        metrics = {'database': {'query_time': None, 'slow_queries': None, 'connection_pool_usage': None, 'database_calls': None}}
        
        section = self.generator._generate_database_section(metrics, self.category_scores)
        
        self.assertIn("Average Query Time:** N/A", section)
        self.assertIn("Slow Queries Count:** N/A", section)
        self.assertIn("Connection Pool Usage:** N/A", section)
        self.assertIn("Database Calls:** N/A", section)
    
    def test_api_section_with_none_values(self):
        """Test API section handles None values gracefully."""
        metrics = {'transactions': {'transaction_time': None, 'external_calls': None, 'external_latency': None, 'api_endpoints': None}}
        
        section = self.generator._generate_api_section(metrics, self.category_scores)
        
        self.assertIn("Average Transaction Time:** N/A", section)
        self.assertIn("External Calls Count:** N/A", section)
        self.assertIn("External Service Latency:** N/A", section)
        self.assertIn("Active Endpoints:** N/A", section)


class TestFindingsSection(unittest.TestCase):
    """Test findings section generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_findings_section_with_critical_issues(self):
        """Test findings section displays critical issues correctly."""
        findings = [
            {
                'severity': 'Critical',
                'category': 'performance',
                'issue': 'High response time',
                'metric': 'response_time',
                'value': '1250ms',
                'threshold': '<500ms',
                'impact': 'Users experiencing slow page loads'
            },
            {
                'severity': 'Critical',
                'category': 'errors',
                'issue': 'Elevated error rate',
                'metric': 'error_rate',
                'value': '8%',
                'threshold': '<5%',
                'impact': 'Significant user-facing errors'
            }
        ]
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("## Findings & Issues", section)
        self.assertIn("### 🔴 Critical Issues (2)", section)
        self.assertIn("**High response time**", section)
        self.assertIn("Metric: response_time", section)
        self.assertIn("Current Value: 1250ms", section)
        self.assertIn("Threshold: <500ms", section)
        self.assertIn("Impact: Users experiencing slow page loads", section)
    
    def test_findings_section_with_warnings(self):
        """Test findings section displays warnings correctly."""
        findings = [
            {
                'severity': 'Warning',
                'category': 'database',
                'issue': 'High database calls',
                'metric': 'database_calls',
                'value': '250',
                'threshold': '<100',
                'impact': 'Possible N+1 query pattern'
            }
        ]
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("### 🟠 Warnings (1)", section)
        self.assertIn("**High database calls**", section)
        self.assertIn("Metric: database_calls", section)
    
    def test_findings_section_with_info(self):
        """Test findings section displays info items correctly."""
        findings = [
            {
                'severity': 'Info',
                'category': 'overall',
                'issue': 'All metrics within healthy ranges',
                'metric': 'overall_health',
                'value': '95'
            }
        ]
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("### 🟢 Info (1)", section)
        self.assertIn("**All metrics within healthy ranges**", section)
    
    def test_findings_section_with_mixed_severities(self):
        """Test findings section groups and displays mixed severities."""
        findings = [
            {'severity': 'Critical', 'issue': 'Critical issue', 'metric': 'm1', 'value': 'v1'},
            {'severity': 'Warning', 'issue': 'Warning 1', 'metric': 'm2', 'value': 'v2'},
            {'severity': 'Warning', 'issue': 'Warning 2', 'metric': 'm3', 'value': 'v3'},
            {'severity': 'Info', 'issue': 'Info item', 'metric': 'm4', 'value': 'v4'}
        ]
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("### 🔴 Critical Issues (1)", section)
        self.assertIn("### 🟠 Warnings (2)", section)
        self.assertIn("### 🟢 Info (1)", section)
    
    def test_findings_section_with_no_issues(self):
        """Test findings section with empty findings list."""
        findings = []
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("### 🔴 Critical Issues (0)", section)
        self.assertIn("No critical issues detected", section)
        self.assertIn("### 🟠 Warnings (0)", section)
        self.assertIn("No warnings", section)
        self.assertIn("### 🟢 Info (0)", section)
        self.assertIn("All metrics within healthy ranges", section)
    
    def test_findings_section_without_optional_fields(self):
        """Test findings section handles missing optional fields."""
        findings = [
            {
                'severity': 'Critical',
                'issue': 'Issue without threshold',
                'metric': 'some_metric',
                'value': 'some_value'
                # No threshold or impact
            }
        ]
        
        section = self.generator._generate_findings_section(findings)
        
        self.assertIn("**Issue without threshold**", section)
        self.assertIn("Metric: some_metric", section)
        self.assertIn("Current Value: some_value", section)
        self.assertNotIn("Threshold:", section)
        self.assertNotIn("Impact:", section)
    
    def test_full_report_includes_findings(self):
        """Test full report includes findings section."""
        health_data = {
            "overall_score": 75,
            "status": "Good",
            "status_emoji": "🟡",
            "category_scores": {},
            "findings": [
                {'severity': 'Warning', 'issue': 'Test issue', 'metric': 'test', 'value': '100'}
            ]
        }
        config = {"days": 7, "new_relic": {"account_id": "123"}}
        
        report = self.generator.generate_report(health_data, "test-app", config)
        
        self.assertIn("## Findings & Issues", report)
        self.assertIn("**Test issue**", report)


class TestRecommendationsSection(unittest.TestCase):
    """Test recommendations section generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_recommendations_section_includes_header(self):
        """Test recommendations section includes proper header."""
        section = self.generator._generate_recommendations_section()
        
        self.assertIn("## Recommendations", section)
    
    def test_recommendations_section_includes_agent_note(self):
        """Test recommendations section includes @recommend-agent note."""
        section = self.generator._generate_recommendations_section()
        
        self.assertIn("@recommend-agent", section)
        self.assertIn("GitHub Copilot Chat", section)
        self.assertIn("AI-powered code-specific recommendations", section)
    
    def test_recommendations_section_includes_placeholder(self):
        """Test recommendations section includes priority recommendations placeholder."""
        section = self.generator._generate_recommendations_section()
        
        self.assertIn("### Priority Recommendations", section)
        self.assertIn("*(Recommendations will be added by @recommend-agent based on this assessment)*", section)
    
    def test_full_report_includes_recommendations(self):
        """Test full report includes recommendations section."""
        health_data = {
            "overall_score": 75,
            "status": "Good",
            "status_emoji": "🟡",
            "category_scores": {},
            "findings": []
        }
        config = {"days": 7, "new_relic": {"account_id": "123"}}
        
        report = self.generator.generate_report(health_data, "test-app", config)
        
        self.assertIn("## Recommendations", report)
        self.assertIn("@recommend-agent", report)


class TestReportSaving(unittest.TestCase):
    """Test report file saving functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        # Create temporary directory for test reports
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_report_creates_file(self):
        """Test save_report creates file successfully."""
        report_content = "# Test Report\n\nThis is a test."
        
        filepath = self.generator.save_report(report_content, "test-app", self.test_dir)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.isfile(filepath))
    
    def test_save_report_correct_filename_format(self):
        """Test save_report uses correct filename format."""
        with patch('modules.report_generator.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2026, 2, 18, 15, 30, 45)
            
            filepath = self.generator.save_report("Test", "my-app", self.test_dir)
            
            expected_filename = "health-report-my-app-2026-02-18-153045.md"
            self.assertTrue(filepath.endswith(expected_filename))
    
    def test_save_report_no_colons_in_filename(self):
        """Test save_report generates filename without colons for filesystem compatibility."""
        filepath = self.generator.save_report("Test", "app123", self.test_dir)
        
        filename = os.path.basename(filepath)
        self.assertNotIn(":", filename)
    
    def test_save_report_creates_directory(self):
        """Test save_report creates reports directory if it doesn't exist."""
        new_dir = os.path.join(self.test_dir, "reports")
        self.assertFalse(os.path.exists(new_dir))
        
        filepath = self.generator.save_report("Test", "test-app", new_dir)
        
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
    
    def test_save_report_content_written_correctly(self):
        """Test save_report writes correct content to file."""
        report_content = "# Health Report\\n\\nThis is the full report content."
        
        filepath = self.generator.save_report(report_content, "test-app", self.test_dir)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            written_content = f.read()
        
        self.assertEqual(written_content, report_content)
    
    def test_save_report_returns_correct_path(self):
        """Test save_report returns full path to saved file."""
        filepath = self.generator.save_report("Test", "my-app", self.test_dir)
        
        self.assertTrue(filepath.startswith(self.test_dir))
        self.assertTrue(filepath.endswith(".md"))
        self.assertIn("health-report-my-app-", filepath)
    
    @patch('modules.report_generator.logger')
    def test_save_report_logs_success(self, mock_logger):
        """Test save_report logs INFO and DEBUG messages."""
        self.generator.save_report("Test content", "test-app", self.test_dir)
        
        # Verify INFO logging
        info_calls = [call for call in mock_logger.info.call_args_list]
        self.assertTrue(any("saved successfully" in str(call) for call in info_calls))
        
        # Verify DEBUG logging for file size
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        self.assertTrue(any("Report size:" in str(call) and "bytes" in str(call) for call in debug_calls))
    
    def test_save_report_prints_confirmation(self):
        """Test save_report prints confirmation message."""
        with patch('builtins.print') as mock_print:
            filepath = self.generator.save_report("Test", "test-app", self.test_dir)
            
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            self.assertIn("✓ Report generated:", call_args)
            self.assertIn(filepath, call_args)
    
    def test_save_report_multiple_reports_same_app(self):
        """Test save_report creates unique filenames for same app."""
        filepath1 = self.generator.save_report("Report 1", "my-app", self.test_dir)
        
        # Wait a second to ensure different timestamp
        import time
        time.sleep(1)
        
        filepath2 = self.generator.save_report("Report 2", "my-app", self.test_dir)
        
        self.assertNotEqual(filepath1, filepath2)
        self.assertTrue(os.path.exists(filepath1))
        self.assertTrue(os.path.exists(filepath2))
    
    def test_save_report_filesystem_safe_app_id(self):
        """Test save_report handles app IDs with special characters."""
        # App IDs should already be sanitized, but test handles them
        filepath = self.generator.save_report("Test", "my-app-123", self.test_dir)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertIn("my-app-123", filepath)


if __name__ == "__main__":
    unittest.main()
