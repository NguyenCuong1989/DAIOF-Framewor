#!/usr/bin/env python3
"""
GitHub Digital Organism - Health Monitor
Theo dõi sức khỏe và vital signs của sinh thể kỹ thuật số

Tuân thủ 4 Pillars:
- An toàn: Chỉ đọc metrics, không thay đổi
- Đường dài: Track trends theo thời gian
- Tin vào số liệu: Data-driven health assessment
- Hạn chế rủi ro: Automated monitoring, alerts
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml

try:
    from github import Github
except ImportError:
    print("Installing PyGithub...")
    os.system("pip install -q PyGithub")
    from github import Github


class DigitalOrganismHealthMonitor:
    """Monitor vital signs của GitHub Digital Organism"""

    def __init__(self, genome_file: str = ".github/DIGITAL_ORGANISM_GENOME.yml"):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME", os.getenv("GITHUB_REPOSITORY"))

        if not self.token:
            print("⚠️  GITHUB_TOKEN not found. Using unauthenticated mode (limited).")
            self.gh = Github()
        else:
            self.gh = Github(self.token)

        if self.repo_name:
            self.repo = self.gh.get_repo(self.repo_name)
        else:
            self.repo = None
            print("⚠️  REPO_NAME not set. Some features limited.")

        # Load genome configuration
        self.genome = self._load_genome(genome_file)
        self.health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": 0.0,
            "vital_signs": {},
            "warnings": [],
            "recommendations": [],
        }

    def _load_genome(self, genome_file: str) -> Dict:
        """Load genome configuration"""
        try:
            with open(genome_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Could not load genome: {e}")
            return {}

    def check_vital_signs(self) -> Dict:
        """Kiểm tra các chỉ số sinh tồn cơ bản"""
        print("🏥 Checking vital signs...")

        if not self.repo:
            print("⚠️  Repository not available")
            return {}

        vitals = {}

        # 1. Contribution Streak
        vitals["contribution_streak"] = self._check_contribution_streak()

        # 2. Community Engagement
        vitals["community_engagement"] = self._check_community_engagement()

        # 3. Code Quality Score
        vitals["code_quality"] = self._check_code_quality()

        # 4. Response Time
        vitals["response_time"] = self._check_response_time()

        # 5. Growth Metrics
        vitals["growth_metrics"] = self._check_growth_metrics()

        self.health_report["vital_signs"] = vitals
        return vitals

    def _check_contribution_streak(self) -> Dict:
        """Kiểm tra contribution streak"""
        try:
            commits = list(
                self.repo.get_commits(since=datetime.utcnow() - timedelta(days=30))
            )

            # Count commits per day
            daily_commits = {}
            for commit in commits:
                date = commit.commit.author.date.date()
                daily_commits[date] = daily_commits.get(date, 0) + 1

            # Calculate current streak
            streak = 0
            current_date = datetime.utcnow().date()
            while current_date in daily_commits:
                streak += 1
                current_date -= timedelta(days=1)

            healthy_range = (
                self.genome.get("health_monitoring", {})
                .get("vital_signs", [{}])[0]
                .get("healthy_range", [5, 365])
            )
            is_healthy = healthy_range[0] <= streak <= healthy_range[1]

            result = {
                "value": streak,
                "unit": "days",
                "healthy_range": healthy_range,
                "status": "✅" if is_healthy else "⚠️",
                "is_healthy": is_healthy,
            }

            if not is_healthy and streak < healthy_range[0]:
                self.health_report["warnings"].append(
                    f"Contribution streak ({streak} days) below healthy minimum ({healthy_range[0]} days)"
                )
                self.health_report["recommendations"].append(
                    "💡 Increase commit frequency to maintain organism vitality"
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "❌"}

    def _check_community_engagement(self) -> Dict:
        """Kiểm tra mức độ tương tác với community"""
        try:
            # Count recent community interactions
            since = datetime.utcnow() - timedelta(days=7)

            issues = list(self.repo.get_issues(state="all", since=since))
            pulls = list(self.repo.get_pulls(state="all"))

            # Count interactions
            issue_comments = sum(issue.comments for issue in issues)
            pr_comments = sum(pr.comments for pr in pulls[:10])  # Recent 10 PRs

            total_interactions = len(issues) + len(pulls) + issue_comments + pr_comments

            # Normalize to 0-1 scale (assume 50+ interactions/week = 1.0)
            engagement_score = min(1.0, total_interactions / 50.0)

            healthy_range = [0.7, 1.0]
            is_healthy = healthy_range[0] <= engagement_score <= healthy_range[1]

            result = {
                "value": round(engagement_score, 2),
                "unit": "score",
                "details": {
                    "issues": len(issues),
                    "prs": len(pulls),
                    "comments": issue_comments + pr_comments,
                },
                "healthy_range": healthy_range,
                "status": "✅" if is_healthy else "⚠️",
                "is_healthy": is_healthy,
            }

            if not is_healthy:
                self.health_report["warnings"].append(
                    f"Community engagement ({engagement_score:.2f}) below healthy range"
                )
                self.health_report["recommendations"].append(
                    "💡 Increase interaction with community: respond to issues, review PRs"
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "❌"}

    def _check_code_quality(self) -> Dict:
        """Kiểm tra chất lượng code"""
        try:
            # Simple quality checks
            quality_indicators = {
                "has_ci": False,
                "has_tests": False,
                "has_docs": False,
                "has_contributing": False,
                "has_license": False,
            }

            # Check for CI
            try:
                workflows = list(self.repo.get_workflows())
                quality_indicators["has_ci"] = len(workflows) > 0
            except:
                pass

            # Check for tests
            try:
                contents = self.repo.get_contents("")
                for content in contents:
                    if "test" in content.name.lower():
                        quality_indicators["has_tests"] = True
                    if content.name in ["README.md", "docs"]:
                        quality_indicators["has_docs"] = True
                    if content.name == "CONTRIBUTING.md":
                        quality_indicators["has_contributing"] = True
                    if content.name == "LICENSE":
                        quality_indicators["has_license"] = True
            except:
                pass

            # Calculate quality score
            quality_score = sum(quality_indicators.values()) / len(quality_indicators)

            healthy_range = [0.8, 1.0]
            is_healthy = quality_score >= healthy_range[0]

            result = {
                "value": round(quality_score, 2),
                "unit": "score",
                "details": quality_indicators,
                "healthy_range": healthy_range,
                "status": "✅" if is_healthy else "⚠️",
                "is_healthy": is_healthy,
            }

            if not is_healthy:
                missing = [k for k, v in quality_indicators.items() if not v]
                self.health_report["warnings"].append(
                    f"Code quality score ({quality_score:.2f}) needs improvement"
                )
                self.health_report["recommendations"].append(
                    f"💡 Add missing quality indicators: {', '.join(missing)}"
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "❌"}

    def _check_response_time(self) -> Dict:
        """Kiểm tra thời gian phản hồi"""
        try:
            # Check recent issues
            issues = list(self.repo.get_issues(state="closed"))[:10]

            response_times = []
            for issue in issues:
                if issue.comments > 0:
                    comments = list(issue.get_comments())
                    if comments:
                        first_comment = comments[0]
                        response_time = (
                            first_comment.created_at - issue.created_at
                        ).total_seconds() / 3600
                        response_times.append(response_time)

            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            healthy_range = [0, 24]
            is_healthy = (
                avg_response_time <= healthy_range[1] if response_times else True
            )

            result = {
                "value": round(avg_response_time, 1),
                "unit": "hours",
                "sample_size": len(response_times),
                "healthy_range": healthy_range,
                "status": "✅" if is_healthy else "⚠️",
                "is_healthy": is_healthy,
            }

            if not is_healthy:
                self.health_report["warnings"].append(
                    f"Average response time ({avg_response_time:.1f}h) exceeds target (24h)"
                )
                self.health_report["recommendations"].append(
                    "💡 Enable AI Agent for faster automated responses"
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "❌"}

    def _check_growth_metrics(self) -> Dict:
        """Kiểm tra các chỉ số tăng trưởng"""
        try:
            metrics = {
                "stars": self.repo.stargazers_count,
                "forks": self.repo.forks_count,
                "watchers": self.repo.watchers_count,
                "open_issues": self.repo.open_issues_count,
                "subscribers": self.repo.subscribers_count,
            }

            # Load historical data if exists
            metrics_dir = Path("metrics")
            historical_data = []
            if metrics_dir.exists():
                for file in sorted(metrics_dir.glob("daily_*.json")):
                    try:
                        with open(file, "r") as f:
                            historical_data.append(json.load(f))
                    except:
                        pass

            # Calculate growth
            growth = {}
            if len(historical_data) >= 2:
                old_metrics = historical_data[0].get("metrics", {})
                for key in metrics:
                    old_val = old_metrics.get(key, 0)
                    new_val = metrics[key]
                    growth[key] = new_val - old_val

            result = {
                "current": metrics,
                "growth": growth if growth else "insufficient_data",
                "status": "✅",
                "is_healthy": True,
            }

            # Check if meeting targets
            genome_targets = self.genome.get("health_monitoring", {}).get(
                "growth_metrics", []
            )
            for target in genome_targets:
                metric_name = target.get("metric")
                if metric_name == "stars":
                    target_value = 50  # First week target
                    if metrics["stars"] < target_value:
                        self.health_report["recommendations"].append(
                            f"💡 Stars ({metrics['stars']}) below first week target ({target_value}). Execute launch strategy."
                        )

            return result

        except Exception as e:
            return {"error": str(e), "status": "❌"}

    def calculate_overall_health(self) -> float:
        """Tính toán sức khỏe tổng thể"""
        vitals = self.health_report.get("vital_signs", {})

        health_scores = []
        for vital_name, vital_data in vitals.items():
            if isinstance(vital_data, dict) and vital_data.get("is_healthy"):
                health_scores.append(1.0)
            elif isinstance(vital_data, dict) and "is_healthy" in vital_data:
                health_scores.append(0.0)

        overall_health = (
            sum(health_scores) / len(health_scores) if health_scores else 0.0
        )
        self.health_report["overall_health"] = round(overall_health, 2)

        return overall_health

    def generate_health_report(self) -> str:
        """Tạo báo cáo sức khỏe"""
        print("\n" + "=" * 60)
        print("🧬 GITHUB DIGITAL ORGANISM - HEALTH REPORT")
        print("=" * 60)

        # Check vitals
        self.check_vital_signs()

        # Calculate overall health
        overall_health = self.calculate_overall_health()

        # Health status emoji
        if overall_health >= 0.8:
            health_emoji = "💚"
            health_status = "EXCELLENT"
        elif overall_health >= 0.6:
            health_emoji = "💛"
            health_status = "GOOD"
        elif overall_health >= 0.4:
            health_emoji = "🧡"
            health_status = "FAIR"
        else:
            health_emoji = "❤️"
            health_status = "NEEDS ATTENTION"

        print(
            f"\n{health_emoji} Overall Health: {overall_health:.0%} - {health_status}\n"
        )

        # Vital Signs
        print("📊 VITAL SIGNS:")
        print("-" * 60)
        for vital_name, vital_data in self.health_report["vital_signs"].items():
            if isinstance(vital_data, dict) and "status" in vital_data:
                value = vital_data.get("value", "N/A")
                unit = vital_data.get("unit", "")
                status = vital_data.get("status", "❓")
                print(
                    f"{status} {vital_name.replace('_', ' ').title()}: {value} {unit}"
                )

                if "details" in vital_data:
                    for key, val in vital_data["details"].items():
                        print(f"    - {key}: {val}")

        # Warnings
        if self.health_report["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.health_report['warnings'])}):")
            print("-" * 60)
            for warning in self.health_report["warnings"]:
                print(f"  • {warning}")

        # Recommendations
        if self.health_report["recommendations"]:
            print(
                f"\n💡 RECOMMENDATIONS ({len(self.health_report['recommendations'])}):"
            )
            print("-" * 60)
            for rec in self.health_report["recommendations"]:
                print(f"  • {rec}")

        print("\n" + "=" * 60)
        print(f"📅 Report Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60 + "\n")

        # Save report
        self._save_report()

        return json.dumps(self.health_report, indent=2)

    def _save_report(self):
        """Lưu báo cáo vào file"""
        metrics_dir = Path("metrics")
        metrics_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = metrics_dir / f"health_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(self.health_report, f, indent=2)

        print(f"💾 Report saved: {report_file}")


def main():
    """Main entry point"""
    print("🧬 Starting GitHub Digital Organism Health Monitor...")

    monitor = DigitalOrganismHealthMonitor()
    report = monitor.generate_health_report()

    # Exit code based on health
    overall_health = monitor.health_report["overall_health"]
    if overall_health < 0.5:
        print("⚠️  Health below 50% - needs attention!")
        sys.exit(1)
    else:
        print("✅ Organism health acceptable")
        sys.exit(0)


if __name__ == "__main__":
    main()
