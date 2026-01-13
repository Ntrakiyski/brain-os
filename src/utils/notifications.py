"""
Email/Webhook Notification Utility for Brain OS.

Sends HTTP POST requests to webhook URLs for email notifications.
Can be used by background tasks or called directly as a tool.

Usage:
    await send_email_notification(
        webhook_url=os.getenv("EMAIL_WEBHOOK_URL"),
        subject="Brain OS Weekly Summary",
        body="Your weekly cognitive summary is ready...",
        metadata={"task": "weekly_summary", "memories_count": 42}
    )
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


# Email template types
EMAIL_TEMPLATES = {
    "weekly_summary": {
        "subject": "Brain OS Weekly Cognitive Summary",
        "template": """
🧠 Brain OS Weekly Summary
{"=" * 50}

📊 Memory Statistics:
  Total Memories: {total_memories}
  New This Week: {new_memories}

📈 Sector Distribution:
{sector_distribution}

💡 Key Insights:
{insights}

🔄 Background Tasks:
  - Synaptic Pruning: {pruning_status}
  - Cloud Synthesis: {synthesis_status}
  - Health Check: {health_status}

Generated: {timestamp}
---
Brain OS - Your Cognitive Operating System
        """
    },
    "cloud_insight": {
        "subject": "Brain OS: New Reflective Insight Generated",
        "template": """
💡 New Cloud Insight

Your Brain OS has generated a new Reflective memory:

{insight_content}

🔗 Related Memories: {related_count}
📊 Salience: {salience}
📅 Generated: {timestamp}

This insight was automatically synthesized from your memory cluster.
---
Brain OS - Your Cognitive Operating System
        """
    },
    "system_alert": {
        "subject": "⚠️ Brain OS System Alert",
        "template": """
⚠️ System Alert: {alert_type}

{alert_message}

Details:
  Timestamp: {timestamp}
  Severity: {severity}
  Component: {component}

Recommended Action: {action}
---
Brain OS - Your Cognitive Operating System
        """
    },
    "task_report": {
        "subject": "Brain OS Background Task Report",
        "template": """
🔧 Background Task Report

Task: {task_name}
Status: {status}
Started: {start_time}
Completed: {end_time}
Duration: {duration}

Results:
{results}

---
Brain OS - Your Cognitive Operating System
        """
    }
}


async def send_email_notification(
    webhook_url: str,
    subject: str,
    body: str,
    metadata: Optional[Dict[str, Any]] = None,
    html: bool = False,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send an email notification via webhook HTTP POST.

    Args:
        webhook_url: The webhook URL to send the request to
        subject: Email subject line
        body: Email body content (plain text or HTML)
        metadata: Optional metadata dictionary for tracking
        html: Whether body is HTML (default: False for plain text)
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details

    Example:
        result = await send_email_notification(
            webhook_url="https://n8n.trakiyski.work/webhook/abc123",
            subject="Test Email",
            body="Hello from Brain OS!",
            metadata={"source": "test", "user": "nikol"},
            headers={"Authorization": "Bearer sf1Y4TZ3iRporOfxKfGwSeejlbkyoIoB"}
        )
    """
    payload = {
        "subject": subject,
        "body": body,
        "is_html": html,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }

    logger.info(f"Sending email notification: {subject}")

    try:
        # Merge custom headers with defaults
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "BrainOS/1.0"
        }
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers=request_headers
            )

            response.raise_for_status()

            logger.info(f"Email notification sent successfully: {response.status_code}")

            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text if response.text else "OK",
                "timestamp": datetime.utcnow().isoformat()
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending email: {e.response.status_code} - {e.response.text}")
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}",
            "details": e.response.text,
            "timestamp": datetime.utcnow().isoformat()
        }

    except httpx.RequestError as e:
        logger.error(f"Request error sending email: {str(e)}")
        return {
            "success": False,
            "error": "Request failed",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def send_templated_email(
    webhook_url: str,
    template_name: str,
    template_vars: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send a templated email notification.

    Args:
        webhook_url: The webhook URL to send the request to
        template_name: Name of the template (weekly_summary, cloud_insight, system_alert, task_report)
        template_vars: Variables to fill in the template
        metadata: Optional metadata for tracking
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details

    Example:
        result = await send_templated_email(
            webhook_url="https://n8n.trakiyski.work/webhook/abc123",
            template_name="weekly_summary",
            template_vars={
                "total_memories": 147,
                "new_memories": 12,
                "sector_distribution": "Semantic: 35%, Procedural: 30%...",
                "insights": "1. FastTrack project shows scope creep pattern...",
                "pruning_status": "✓ Complete",
                "synthesis_status": "✓ Complete",
                "health_status": "✓ Healthy"
            },
            headers={"Authorization": "Bearer your-token"}
        )
    """
    if template_name not in EMAIL_TEMPLATES:
        logger.error(f"Unknown template: {template_name}")
        return {
            "success": False,
            "error": f"Unknown template: {template_name}",
            "available_templates": list(EMAIL_TEMPLATES.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }

    template = EMAIL_TEMPLATES[template_name]

    # Fill template with variables
    try:
        body = template["template"].format(**template_vars, **{
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return {
            "success": False,
            "error": f"Missing template variable: {e}",
            "timestamp": datetime.utcnow().isoformat()
        }

    return await send_email_notification(
        webhook_url=webhook_url,
        subject=template["subject"],
        body=body.strip(),
        metadata=metadata or {"template": template_name},
        headers=headers
    )


async def send_weekly_summary_email(
    webhook_url: str,
    stats: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send weekly summary email (convenience wrapper).

    Args:
        webhook_url: The webhook URL
        stats: Statistics dictionary with:
            - total_memories: int
            - new_memories: int
            - sector_distribution: str
            - insights: str
            - pruning_status: str
            - synthesis_status: str
            - health_status: str
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details
    """
    return await send_templated_email(
        webhook_url=webhook_url,
        template_name="weekly_summary",
        template_vars=stats,
        metadata={"task": "weekly_summary", "auto_generated": True},
        headers=headers
    )


async def send_cloud_insight_email(
    webhook_url: str,
    insight: str,
    related_count: int,
    salience: float,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send cloud insight email (convenience wrapper).

    Args:
        webhook_url: The webhook URL
        insight: The insight content
        related_count: Number of related memories
        salience: Salience score
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details
    """
    return await send_templated_email(
        webhook_url=webhook_url,
        template_name="cloud_insight",
        template_vars={
            "insight_content": insight,
            "related_count": related_count,
            "salience": salience
        },
        metadata={"task": "cloud_synthesis", "auto_generated": True},
        headers=headers
    )


async def send_system_alert_email(
    webhook_url: str,
    alert_type: str,
    alert_message: str,
    severity: str,
    component: str,
    action: str,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send system alert email (convenience wrapper).

    Args:
        webhook_url: The webhook URL
        alert_type: Type of alert
        alert_message: Alert message
        severity: Severity level (critical, warning, info)
        component: Component that generated the alert
        action: Recommended action
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details
    """
    return await send_templated_email(
        webhook_url=webhook_url,
        template_name="system_alert",
        template_vars={
            "alert_type": alert_type,
            "alert_message": alert_message,
            "severity": severity,
            "component": component,
            "action": action
        },
        metadata={"task": "system_alert", "severity": severity},
        headers=headers
    )


async def send_task_report_email(
    webhook_url: str,
    task_name: str,
    status: str,
    start_time: str,
    end_time: str,
    duration: str,
    results: str,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Send task report email (convenience wrapper).

    Args:
        webhook_url: The webhook URL
        task_name: Name of the task
        status: Task status (success, failed, partial)
        start_time: Task start time
        end_time: Task end time
        duration: Task duration
        results: Task results summary
        headers: Optional custom headers (e.g., {"Authorization": "Bearer token"})

    Returns:
        Dictionary with status and response details
    """
    return await send_templated_email(
        webhook_url=webhook_url,
        template_name="task_report",
        template_vars={
            "task_name": task_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "results": results
        },
        metadata={"task": "task_report", "task_name": task_name},
        headers=headers
    )


# =============================================================================
# TEST FUNCTION (for development)
# =============================================================================

async def test_email_notification():
    """Test email notification with a sample webhook."""
    test_url = "https://hook.eu.make.com/YOUR_WEBHOOK_ID_HERE"

    result = await send_email_notification(
        webhook_url=test_url,
        subject="Brain OS Test Email",
        body="This is a test email from Brain OS notification system.\n\nIf you receive this, the webhook is working!",
        metadata={
            "test": True,
            "environment": "development",
            "user": "nikol"
        }
    )

    print("Test Result:", json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    # Run test
    asyncio.run(test_email_notification())
