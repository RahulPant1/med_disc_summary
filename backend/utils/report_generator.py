"""
Report generator for validation results
"""
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ReportGenerator:
    """Generate formatted text reports of validation results"""

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.report_file = self.output_dir / "latest_validation_report.txt"
        self.metadata_file = self.output_dir / "latest_report_metadata.json"

    def compute_content_hash(self, content: str, llm_provider: str) -> str:
        """
        Compute hash of content and provider for cache validation

        Args:
            content: Discharge summary content
            llm_provider: LLM provider used

        Returns:
            SHA256 hash string
        """
        # Create deterministic hash from content + provider with v2 prefix
        hash_input = f"v2:{content.strip()}|{llm_provider}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    def generate_report(
        self,
        content: str,
        results: Dict[str, List[Dict]],
        summary: Dict,
        llm_provider: str
    ) -> Tuple[str, str]:
        """
        Generate a formatted text report (overwrites existing)

        Args:
            content: Original discharge summary
            results: Validation results by agent
            summary: Summary statistics
            llm_provider: LLM provider used

        Returns:
            Tuple of (report_path, content_hash)
        """
        # Compute content hash
        content_hash = self.compute_content_hash(content, llm_provider)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Generate report
        with open(self.report_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("="* 80 + "\n")
            f.write(" DISCHARGE SUMMARY VALIDATION REPORT\n")
            f.write("="* 80 + "\n\n")

            # Metadata
            f.write(f"Generated: {timestamp}\n")
            f.write(f"LLM Provider: {llm_provider.upper()}\n")
            f.write(f"Processing Time: {summary.get('total_processing_time', 0):.2f} seconds\n")
            f.write(f"Content Hash: {content_hash}\n")
            f.write("\n")

            # Executive Summary
            f.write("-" * 80 + "\n")
            f.write(" EXECUTIVE SUMMARY\n")
            f.write("-" * 80 + "\n\n")
            f.write(f"Total Issues Found: {summary.get('total_issues', 0)}\n")
            f.write(f"  • HIGH Severity: {summary.get('high_severity_count', 0)}\n")
            f.write(f"  • MEDIUM Severity: {summary.get('medium_severity_count', 0)}\n")
            f.write(f"  • LOW Severity: {summary.get('low_severity_count', 0)}\n")
            f.write(f"Agents Completed: {summary.get('agents_completed', 0)}\n")
            f.write(f"Cache Hit Rate: {summary.get('cache_hit_rate', 0):.1f}%\n")
            f.write("\n\n")

            # Original Discharge Summary
            f.write("=" * 80 + "\n")
            f.write(" INPUT: ORIGINAL DISCHARGE SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(content)
            f.write("\n\n\n")

            # Detailed Issues by Agent
            f.write("=" * 80 + "\n")
            f.write(" OUTPUT: DETAILED VALIDATION RESULTS\n")
            f.write("=" * 80 + "\n\n")

            agent_order = ['linguistic', 'structural', 'clinical', 'terminology', 'critical_data']

            for agent_name in agent_order:
                agent_data = results.get(agent_name, {})
                issues = agent_data.get('issues', [])

                if not issues:
                    continue

                f.write("-" * 80 + "\n")
                f.write(f" {agent_name.upper().replace('_', ' ')} AGENT\n")
                f.write("-" * 80 + "\n")
                f.write(f"Issues Found: {len(issues)}\n")
                f.write(f"From Cache: {'Yes' if agent_data.get('from_cache') else 'No'}\n")
                if not agent_data.get('from_cache'):
                    f.write(f"Processing Time: {agent_data.get('processing_time', 0):.2f}s\n")
                f.write("\n")

                for idx, issue in enumerate(issues, 1):
                    f.write(f"\n{idx}. [{issue.get('severity', 'UNKNOWN')}] {issue.get('type', 'Unknown Type')}\n")
                    f.write(f"   Location: {issue.get('location', 'Not specified')}\n")
                    f.write(f"   Current: {issue.get('current', 'N/A')}\n")
                    f.write(f"   Suggestion: {issue.get('suggestion', 'N/A')}\n")
                    f.write(f"   Explanation: {issue.get('explanation', 'N/A')}\n")

                f.write("\n\n")

            # Footer
            f.write("=" * 80 + "\n")
            f.write(" END OF REPORT\n")
            f.write("=" * 80 + "\n")

        # Save metadata with results for caching
        metadata = {
            "content_hash": content_hash,
            "llm_provider": llm_provider,
            "timestamp": timestamp,
            "summary": summary,
            "results": results
        }

        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return str(self.report_file), content_hash

    def get_cached_results(self, content: str, llm_provider: str) -> Optional[Dict]:
        """
        Get cached results if they match the content hash

        Args:
            content: Discharge summary content
            llm_provider: LLM provider

        Returns:
            Cached results dict or None if no match
        """
        if not self.metadata_file.exists():
            return None

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Compute hash of current content
            current_hash = self.compute_content_hash(content, llm_provider)

            # Check if hash matches and provider matches
            if (metadata.get('content_hash') == current_hash and
                metadata.get('llm_provider') == llm_provider):
                return {
                    'results': metadata.get('results', {}),
                    'summary': metadata.get('summary', {}),
                    'from_cache': True,
                    'cached_at': metadata.get('timestamp')
                }

            return None

        except Exception as e:
            # If any error reading cache, just return None
            return None

    def get_latest_report(self) -> Optional[str]:
        """
        Get path to the latest report

        Returns:
            Path to latest report or None
        """
        if self.report_file.exists():
            return str(self.report_file)
        return None
