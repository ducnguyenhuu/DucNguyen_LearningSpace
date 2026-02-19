"""
Report Generation Module for AI Log Analysis System.

This module generates executive-ready markdown reports with health assessments,
metric breakdowns, and actionable findings.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ReportGenerator:
    """
    Generates health assessment reports in markdown format.
    
    The ReportGenerator creates professional, executive-ready reports that include:
    - Executive summary with overall health score
    - Assessment metadata and data collection information
    - Detailed metric breakdowns by category (generated in subsequent stories)
    - Findings and recommendations (generated in subsequent stories)
    """
    
    def __init__(self):
        """Initialize the ReportGenerator."""
        logger.debug("[DEBUG] [report_generator] ReportGenerator initialized")
    
    def generate_report(
        self,
        health_data: Dict[str, Any],
        app_id: str,
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
        collection_start: Optional[datetime] = None,
        collection_end: Optional[datetime] = None,
        cache_age: Optional[int] = None
    ) -> str:
        """
        Generate a comprehensive health assessment report in markdown format.
        
        Args:
            health_data: Health scoring results from HealthCalculator.calculate_health_score()
                Expected keys: overall_score, status, status_emoji, category_scores, findings
            app_id: New Relic application ID or name
            config: Configuration dictionary containing:
                - new_relic.account_id: New Relic account ID
                - new_relic.api_key: API key (not included in report)
                - days: Assessment period in days
            metrics: Optional raw metrics dictionary from ApiClient
            collection_start: Optional data collection start timestamp
            collection_end: Optional data collection end timestamp
            cache_age: Optional age of cached data in seconds (None = fresh data)
        
        Returns:
            Markdown-formatted report string
        
        Raises:
            ValueError: If required fields are missing from health_data or config
        """
        logger.info(f"[INFO] [report_generator] Generating health report for app: {app_id}")
        
        # Validate required fields
        self._validate_inputs(health_data, config)
        
        # Build report sections
        report_sections = []
        
        # Header and executive summary
        report_sections.append(self._generate_header(app_id))
        report_sections.append(self._generate_executive_summary(
            health_data, config, collection_start, collection_end
        ))
        report_sections.append(self._generate_metadata_section(
            app_id, config, collection_start, collection_end, cache_age
        ))
        
        # Metric breakdown sections (if metrics provided)
        if metrics:
            logger.debug("[DEBUG] [report_generator] Generating metric breakdown sections")
            category_scores = health_data.get('category_scores', {})
            
            report_sections.append(self._generate_performance_section(metrics, category_scores))
            report_sections.append(self._generate_error_section(metrics, category_scores))
            report_sections.append(self._generate_infrastructure_section(metrics, category_scores))
            report_sections.append(self._generate_database_section(metrics, category_scores))
            report_sections.append(self._generate_api_section(metrics, category_scores))
        
        # Findings and recommendations sections
        findings = health_data.get('findings', [])
        report_sections.append(self._generate_findings_section(findings))
        report_sections.append(self._generate_recommendations_section())
        
        # Combine all sections
        report = "\n\n".join(report_sections)
        
        logger.info("[INFO] [report_generator] Health report generated successfully")
        logger.debug(f"[DEBUG] [report_generator] Report length: {len(report)} characters")
        
        return report
    
    def _validate_inputs(self, health_data: Dict[str, Any], config: Dict[str, Any]) -> None:
        """
        Validate that required fields are present in inputs.
        
        Args:
            health_data: Health scoring results dictionary
            config: Configuration dictionary
        
        Raises:
            ValueError: If required fields are missing
        """
        # Validate health_data
        required_health_fields = ["overall_score", "status", "status_emoji", "findings"]
        missing_fields = [f for f in required_health_fields if f not in health_data]
        if missing_fields:
            raise ValueError(f"Missing required health_data fields: {missing_fields}")
        
        # Validate config
        if "days" not in config:
            raise ValueError("Missing required config field: days")
        
        logger.debug("[DEBUG] [report_generator] Input validation passed")
    
    def _generate_header(self, app_id: str) -> str:
        """
        Generate report header with application name.
        
        Args:
            app_id: Application identifier
        
        Returns:
            Markdown header string
        """
        header = f"# Health Assessment: {app_id}"
        logger.debug(f"[DEBUG] [report_generator] Generated header for app: {app_id}")
        return header
    
    def _generate_executive_summary(
        self,
        health_data: Dict[str, Any],
        config: Dict[str, Any],
        collection_start: Optional[datetime],
        collection_end: Optional[datetime]
    ) -> str:
        """
        Generate executive summary section with key health metrics.
        
        Args:
            health_data: Health scoring results
            config: Configuration with assessment period
            collection_start: Data collection start time
            collection_end: Data collection end time
        
        Returns:
            Markdown-formatted executive summary
        """
        logger.debug("[DEBUG] [report_generator] Generating executive summary")
        
        overall_score = health_data["overall_score"]
        status = health_data["status"]
        status_emoji = health_data["status_emoji"]
        findings = health_data["findings"]
        days = config.get("days", 7)
        
        # Count critical issues
        critical_count = sum(1 for f in findings if f.get("severity") == "Critical")
        
        # Format assessment period
        if collection_start and collection_end:
            start_date = collection_start.strftime("%Y-%m-%d")
            end_date = collection_end.strftime("%Y-%m-%d")
            period_text = f"{days} days ({start_date} to {end_date})"
        else:
            period_text = f"{days} days"
        
        # Build executive summary
        summary_lines = [
            "## Executive Summary",
            "",
            f"**Overall Health Score:** {overall_score}/100 {status_emoji} {status}",
            "",
            f"**Assessment Period:** {period_text}",
            "",
            f"**Critical Issues Found:** {critical_count}"
        ]
        
        summary = "\n".join(summary_lines)
        logger.debug(f"[DEBUG] [report_generator] Executive summary: Score={overall_score}, Status={status}, Critical={critical_count}")
        
        return summary
    
    def _generate_metadata_section(
        self,
        app_id: str,
        config: Dict[str, Any],
        collection_start: Optional[datetime],
        collection_end: Optional[datetime],
        cache_age: Optional[int]
    ) -> str:
        """
        Generate report metadata section with assessment details.
        
        Args:
            app_id: Application identifier
            config: Configuration dictionary
            collection_start: Data collection start time
            collection_end: Data collection end time
            cache_age: Age of cached data in seconds (None = fresh)
        
        Returns:
            Markdown-formatted metadata section
        """
        logger.debug("[DEBUG] [report_generator] Generating metadata section")
        
        # Get configuration values
        account_id = config.get("new_relic", {}).get("account_id", "N/A")
        
        # Generate assessment timestamp (current time)
        assessment_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Calculate data collection duration
        if collection_start and collection_end:
            duration_seconds = (collection_end - collection_start).total_seconds()
            duration_minutes = int(duration_seconds / 60)
            duration_text = f"{duration_minutes} minutes" if duration_minutes > 0 else f"{int(duration_seconds)} seconds"
        else:
            duration_text = "N/A"
        
        # Determine cache status
        if cache_age is None:
            cache_status = "Fresh data (collected on-demand)"
        elif cache_age < 60:
            cache_status = f"Cached data ({cache_age} seconds old)"
        elif cache_age < 3600:
            cache_minutes = int(cache_age / 60)
            cache_status = f"Cached data ({cache_minutes} minutes old)"
        else:
            cache_hours = int(cache_age / 3600)
            cache_status = f"Cached data ({cache_hours} hours old)"
        
        # Build metadata section
        metadata_lines = [
            "## Assessment Metadata",
            "",
            f"- **New Relic Account ID:** {account_id}",
            f"- **Application ID:** {app_id}",
            f"- **Assessment Timestamp:** {assessment_timestamp}",
            f"- **Data Collection Duration:** {duration_text}",
            f"- **Cache Status:** {cache_status}"
        ]
        
        metadata = "\n".join(metadata_lines)
        logger.debug(f"[DEBUG] [report_generator] Metadata: account={account_id}, app={app_id}, duration={duration_text}")
        
        return metadata
    
    def _generate_performance_section(
        self,
        metrics: Dict[str, Any],
        category_scores: Dict[str, int]
    ) -> str:
        """
        Generate performance metrics section.
        
        Args:
            metrics: Raw metrics dictionary from ApiClient
            category_scores: Category scores from health_data
        
        Returns:
            Markdown-formatted performance section
        """
        logger.debug("[DEBUG] [report_generator] Generating performance section")
        
        # Get performance score and emoji
        score = category_scores.get('performance', 0)
        emoji = self._get_score_emoji(score)
        
        # Get performance metrics
        perf = metrics.get('performance', {})
        response_time = perf.get('response_time')
        throughput = perf.get('throughput')
        apdex = perf.get('apdex_score')
        
        # Build section
        section = f"## Performance Metrics (Score: {score}/100 {emoji})\n\n"
        
        # Response time
        if response_time is not None:
            rt_indicator = "🟢" if response_time < 500 else "🔴"
            section += f"- **Response Time:** {response_time:.0f} ms {rt_indicator} (threshold: <500ms)\n"
        else:
            section += "- **Response Time:** N/A\n"
        
        # Throughput
        if throughput is not None:
            section += f"- **Throughput:** {throughput:.0f} rpm\n"
        else:
            section += "- **Throughput:** N/A\n"
        
        # Apdex score
        if apdex is not None:
            apdex_indicator = "🟢" if apdex >= 0.8 else "🟡" if apdex >= 0.5 else "🔴"
            section += f"- **Apdex Score:** {apdex:.2f} {apdex_indicator} (target: >0.8)\n"
        else:
            section += "- **Apdex Score:** N/A\n"
        
        return section
    
    def _generate_error_section(
        self,
        metrics: Dict[str, Any],
        category_scores: Dict[str, int]
    ) -> str:
        """
        Generate error metrics section.
        
        Args:
            metrics: Raw metrics dictionary from ApiClient
            category_scores: Category scores from health_data
        
        Returns:
            Markdown-formatted error section
        """
        logger.debug("[DEBUG] [report_generator] Generating error section")
        
        # Get error score and emoji
        score = category_scores.get('errors', 0)
        emoji = self._get_score_emoji(score)
        
        # Get error metrics
        errors = metrics.get('errors', {})
        error_rate = errors.get('error_rate')
        error_count = errors.get('error_count')
        error_types = errors.get('error_types')
        
        # Build section
        section = f"## Error Metrics (Score: {score}/100 {emoji})\n\n"
        
        # Error rate
        if error_rate is not None:
            error_rate_pct = error_rate * 100
            rate_indicator = "🟢" if error_rate < 0.05 else "🔴"
            section += f"- **Error Rate:** {error_rate_pct:.1f}% {rate_indicator} (threshold: <5%)\n"
        else:
            section += "- **Error Rate:** N/A\n"
        
        # Total errors
        if error_count is not None:
            section += f"- **Total Errors:** {error_count:,}\n"
        else:
            section += "- **Total Errors:** N/A\n"
        
        # Error types
        if error_types and len(error_types) > 0:
            section += "- **Top Error Types:**\n"
            for error_type in error_types[:5]:  # Limit to top 5
                section += f"  - {error_type}\n"
        else:
            section += "- **Top Error Types:** N/A\n"
        
        return section
    
    def _generate_infrastructure_section(
        self,
        metrics: Dict[str, Any],
        category_scores: Dict[str, int]
    ) -> str:
        """
        Generate infrastructure metrics section.
        
        Args:
            metrics: Raw metrics dictionary from ApiClient
            category_scores: Category scores from health_data
        
        Returns:
            Markdown-formatted infrastructure section
        """
        logger.debug("[DEBUG] [report_generator] Generating infrastructure section")
        
        # Get infrastructure score and emoji
        score = category_scores.get('infrastructure', 0)
        emoji = self._get_score_emoji(score)
        
        # Get infrastructure metrics
        infra = metrics.get('infrastructure', {})
        cpu_usage = infra.get('cpu_usage')
        memory_usage = infra.get('memory_usage')
        disk_io = infra.get('disk_io')
        
        # Build section
        section = f"## Infrastructure Metrics (Score: {score}/100 {emoji})\n\n"
        
        # CPU usage
        if cpu_usage is not None:
            cpu_pct = cpu_usage * 100
            cpu_indicator = "🟢" if cpu_usage < 0.8 else "🔴"
            section += f"- **CPU Usage:** {cpu_pct:.1f}% {cpu_indicator} (threshold: <80%)\n"
        else:
            section += "- **CPU Usage:** N/A\n"
        
        # Memory usage
        if memory_usage is not None:
            mem_pct = memory_usage * 100
            mem_indicator = "🟢" if memory_usage < 0.85 else "🔴"
            section += f"- **Memory Usage:** {mem_pct:.1f}% {mem_indicator} (threshold: <85%)\n"
        else:
            section += "- **Memory Usage:** N/A\n"
        
        # Disk I/O
        if disk_io is not None:
            section += f"- **Disk I/O:** {disk_io:.1f} MB/s\n"
        else:
            section += "- **Disk I/O:** N/A\n"
        
        return section
    
    def _generate_database_section(
        self,
        metrics: Dict[str, Any],
        category_scores: Dict[str, int]
    ) -> str:
        """
        Generate database metrics section.
        
        Args:
            metrics: Raw metrics dictionary from ApiClient
            category_scores: Category scores from health_data
        
        Returns:
            Markdown-formatted database section
        """
        logger.debug("[DEBUG] [report_generator] Generating database section")
        
        # Get database score and emoji
        score = category_scores.get('database', 0)
        emoji = self._get_score_emoji(score)
        
        # Get database metrics
        db = metrics.get('database', {})
        query_time = db.get('query_time')
        slow_queries = db.get('slow_queries')
        pool_usage = db.get('connection_pool_usage')
        db_calls = db.get('database_calls')
        
        # Build section
        section = f"## Database Metrics (Score: {score}/100 {emoji})\n\n"
        
        # Query time
        if query_time is not None:
            qt_indicator = "🟢" if query_time < 100 else "🔴"
            section += f"- **Average Query Time:** {query_time:.0f} ms {qt_indicator} (threshold: <100ms)\n"
        else:
            section += "- **Average Query Time:** N/A\n"
        
        # Slow queries
        if slow_queries is not None:
            sq_indicator = "🟢" if slow_queries == 0 else "🔴"
            section += f"- **Slow Queries Count:** {slow_queries:,} {sq_indicator}\n"
        else:
            section += "- **Slow Queries Count:** N/A\n"
        
        # Connection pool usage
        if pool_usage is not None:
            pool_pct = pool_usage * 100
            pool_indicator = "🟢" if pool_usage < 0.9 else "🔴"
            section += f"- **Connection Pool Usage:** {pool_pct:.1f}% {pool_indicator} (threshold: <90%)\n"
            if pool_usage >= 0.9:
                section += "  - ⚠️ High pool usage - Consider increasing pool size or investigating connection leaks\n"
        else:
            section += "- **Connection Pool Usage:** N/A\n"
        
        # Database calls
        if db_calls is not None:
            section += f"- **Database Calls:** {db_calls:,.0f}\n"
            if db_calls > 100:
                section += "  - ⚠️ High call count suggests possible N+1 query patterns\n"
        else:
            section += "- **Database Calls:** N/A\n"
        
        return section
    
    def _generate_api_section(
        self,
        metrics: Dict[str, Any],
        category_scores: Dict[str, int]
    ) -> str:
        """
        Generate API/Transaction metrics section.
        
        Args:
            metrics: Raw metrics dictionary from ApiClient
            category_scores: Category scores from health_data
        
        Returns:
            Markdown-formatted API section
        """
        logger.debug("[DEBUG] [report_generator] Generating API/Transaction section")
        
        # Get API score and emoji
        score = category_scores.get('api', 0)
        emoji = self._get_score_emoji(score)
        
        # Get transaction metrics
        trans = metrics.get('transactions', {})
        transaction_time = trans.get('transaction_time')
        external_calls = trans.get('external_calls')
        external_latency = trans.get('external_latency')
        api_endpoints = trans.get('api_endpoints')
        
        # Build section
        section = f"## API/Transaction Metrics (Score: {score}/100 {emoji})\n\n"
        
        # Transaction time
        if transaction_time is not None:
            tt_indicator = "🟢" if transaction_time < 500 else "🔴"
            section += f"- **Average Transaction Time:** {transaction_time:.0f} ms {tt_indicator} (threshold: <500ms)\n"
        else:
            section += "- **Average Transaction Time:** N/A\n"
        
        # External calls
        if external_calls is not None:
            section += f"- **External Calls Count:** {external_calls:,}\n"
        else:
            section += "- **External Calls Count:** N/A\n"
        
        # External latency
        if external_latency is not None:
            el_indicator = "🟢" if external_latency < 200 else "🔴"
            section += f"- **External Service Latency:** {external_latency:.0f} ms {el_indicator} (threshold: <200ms)\n"
        else:
            section += "- **External Service Latency:** N/A\n"
        
        # API endpoints
        if api_endpoints and len(api_endpoints) > 0:
            section += "- **Active Endpoints:**\n"
            for endpoint in api_endpoints[:10]:  # Limit to top 10
                section += f"  - {endpoint}\n"
        else:
            section += "- **Active Endpoints:** N/A\n"
        
        return section
    
    def _get_score_emoji(self, score: int) -> str:
        """
        Get emoji indicator based on score.
        
        Args:
            score: Health score (0-100)
        
        Returns:
            Emoji string (🟢🟡🟠🔴)
        """
        if score >= 80:
            return "🟢"
        elif score >= 60:
            return "🟡"
        elif score >= 40:
            return "🟠"
        else:
            return "🔴"
    
    def _generate_findings_section(self, findings: list) -> str:
        """
        Generate findings and issues section grouped by severity.
        
        Args:
            findings: List of finding dictionaries from HealthCalculator
                Expected keys: severity, category, issue, metric, value
        
        Returns:
            Markdown-formatted findings section
        """
        logger.debug("[DEBUG] [report_generator] Generating findings section")
        
        section = "## Findings & Issues\n\n"
        
        # Group findings by severity
        critical = [f for f in findings if f.get('severity') == 'Critical']
        warnings = [f for f in findings if f.get('severity') == 'Warning']
        info = [f for f in findings if f.get('severity') == 'Info']
        
        # Critical issues
        if critical:
            section += f"### 🔴 Critical Issues ({len(critical)})\n\n"
            for finding in critical:
                section += f"- **{finding.get('issue', 'Unknown Issue')}**\n"
                section += f"  - Metric: {finding.get('metric', 'N/A')}\n"
                section += f"  - Current Value: {finding.get('value', 'N/A')}\n"
                if 'threshold' in finding:
                    section += f"  - Threshold: {finding['threshold']}\n"
                if 'impact' in finding:
                    section += f"  - Impact: {finding['impact']}\n"
                section += "\n"
        else:
            section += "### 🔴 Critical Issues (0)\n\nNo critical issues detected.\n\n"
        
        # Warnings
        if warnings:
            section += f"### 🟠 Warnings ({len(warnings)})\n\n"
            for finding in warnings:
                section += f"- **{finding.get('issue', 'Unknown Issue')}**\n"
                section += f"  - Metric: {finding.get('metric', 'N/A')}\n"
                section += f"  - Current Value: {finding.get('value', 'N/A')}\n"
                if 'threshold' in finding:
                    section += f"  - Threshold: {finding['threshold']}\n"
                if 'impact' in finding:
                    section += f"  - Impact: {finding['impact']}\n"
                section += "\n"
        else:
            section += "### 🟠 Warnings (0)\n\nNo warnings.\n\n"
        
        # Info
        if info:
            section += f"### 🟢 Info ({len(info)})\n\n"
            for finding in info:
                section += f"- **{finding.get('issue', 'Unknown Issue')}**\n"
                section += f"  - Metric: {finding.get('metric', 'N/A')}\n"
                section += f"  - Current Value: {finding.get('value', 'N/A')}\n"
                if 'threshold' in finding:
                    section += f"  - Threshold: {finding['threshold']}\n"
                if 'impact' in finding:
                    section += f"  - Impact: {finding['impact']}\n"
                section += "\n"
        else:
            section += "### 🟢 Info (0)\n\nAll metrics within healthy ranges.\n"
        
        return section.rstrip()
    
    def _generate_recommendations_section(self) -> str:
        """
        Generate recommendations section with @recommend-agent placeholder.
        
        Returns:
            Markdown-formatted recommendations section
        """
        logger.debug("[DEBUG] [report_generator] Generating recommendations section")
        
        section = "## Recommendations\n\n"
        section += "Run `@recommend-agent` in GitHub Copilot Chat for AI-powered code-specific recommendations.\n\n"
        section += "### Priority Recommendations\n\n"
        section += "*(Recommendations will be added by @recommend-agent based on this assessment)*\n"
        
        return section
    
    def save_report(
        self,
        report: str,
        app_id: str,
        reports_dir: str = "reports"
    ) -> str:
        """
        Save report to file with timestamp-based naming.
        
        Args:
            report: Markdown report content
            app_id: Application ID for filename
            reports_dir: Directory to save reports (default: "reports")
        
        Returns:
            Full path to saved report file
        
        Raises:
            OSError: If directory creation or file write fails
        """
        logger.debug(f"[DEBUG] [report_generator] Saving report for app: {app_id}")
        
        # Create reports directory if it doesn't exist
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp (filesystem-safe format without colons)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
        
        # Generate filename
        filename = f"health-report-{app_id}-{timestamp}.md"
        filepath = os.path.join(reports_dir, filename)
        
        # Write report to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Get file size for logging
        file_size = os.path.getsize(filepath)
        
        # Log success
        logger.info(f"[INFO] [report_generator] Health report saved successfully")
        logger.debug(f"[DEBUG] [report_generator] Report size: {file_size} bytes")
        
        print(f"✓ Report generated: {filepath}")
        
        return filepath
