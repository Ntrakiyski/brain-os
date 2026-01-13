"""
Email notification tool wrapper for Brain OS MCP server.

Provides tools for sending email notifications via webhook.
Can be used manually or called by background tasks.
"""

from fastmcp import FastMCP
from pydantic import Field

from src.utils.notifications import (
    send_email_notification,
    send_templated_email,
    send_weekly_summary_email,
    send_cloud_insight_email,
    send_system_alert_email,
    send_task_report_email,
    EMAIL_TEMPLATES
)


def register_notification_tools(mcp: FastMCP) -> None:
    """Register all notification tools with the MCP server."""

    @mcp.tool
    async def send_email(
        subject: str = Field(description="Email subject line"),
        body: str = Field(description="Email body content (plain text)"),
        webhook_url: str = Field(default="", description="Your webhook URL (set via EMAIL_WEBHOOK_URL env var)"),
        metadata: str = Field(default="", description="Optional JSON metadata for tracking"),
        authorization: str = Field(default="", description="Authorization header (set via EMAIL_AUTHORIZATION env var)")
    ) -> str:
        """
        Send an email notification via webhook.

        Use this tool to send yourself email notifications from Brain OS.
        The webhook will forward the email to your configured email address.

        **Environment Variables:**
        Set these in Coolify or .env file:
        - EMAIL_WEBHOOK_URL: Your N8N/Make.com webhook URL
        - EMAIL_AUTHORIZATION: Your webhook auth token (if required)

        **Common Use Cases:**
        - Weekly cognitive summaries
        - System alerts and notifications
        - Task completion reports
        - New insight notifications

        **Getting a Webhook URL:**
        1. Use a service like Make.com (formerly Integromat) or N8N
        2. Create a webhook scenario
        3. Add Gmail/SendGrid/Email action
        4. Copy the webhook URL and set as EMAIL_WEBHOOK_URL env var

        Example:
        ```
        send_email(
            subject="Brain OS Alert",
            body="Your weekly summary is ready!"
        )
        ```
        """
        import os
        import json

        # Read from environment variables if not provided
        webhook_url = webhook_url or os.getenv("EMAIL_WEBHOOK_URL", "")
        authorization = authorization or os.getenv("EMAIL_AUTHORIZATION", "")

        if not webhook_url:
            return "Error: EMAIL_WEBHOOK_URL not configured. Set this environment variable with your webhook URL."

        metadata_dict = {}
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                return "Error: Invalid JSON in metadata parameter"

        # Prepare headers with authorization
        headers = {}
        if authorization:
            headers["Authorization"] = authorization

        result = await send_email_notification(
            webhook_url=webhook_url,
            subject=subject,
            body=body,
            metadata=metadata_dict,
            headers=headers if headers else None
        )

        if result["success"]:
            return f"""✅ Email notification sent successfully!

Subject: {subject}
Status: {result['status_code']}
Sent: {result['timestamp']}

Your email should arrive shortly."""
        else:
            return f"""❌ Failed to send email notification

Error: {result.get('error', 'Unknown error')}
Details: {result.get('details', 'No details')}

Please check your webhook URL and try again."""

    @mcp.tool
    async def send_templated_email(
        template: str = Field(description=f"Template name: {', '.join(EMAIL_TEMPLATES.keys())}"),
        variables: str = Field(description="JSON string of template variables"),
        webhook_url: str = Field(default="", description="Your webhook URL (set via EMAIL_WEBHOOK_URL env var)"),
        authorization: str = Field(default="", description="Authorization header (set via EMAIL_AUTHORIZATION env var)")
    ) -> str:
        """
        Send a templated email notification.

        Pre-built templates for common Brain OS notifications.

        **Available Templates:**

        1. **weekly_summary** - Weekly cognitive summary with statistics
           Variables: total_memories, new_memories, sector_distribution, insights,
                     pruning_status, synthesis_status, health_status

        2. **cloud_insight** - New Reflective memory generated
           Variables: insight_content, related_count, salience

        3. **system_alert** - System warning or alert
           Variables: alert_type, alert_message, severity, component, action

        4. **task_report** - Background task completion report
           Variables: task_name, status, start_time, end_time, duration, results

        **Example:**
        ```
        send_templated_email(
            webhook_url="https://hook.eu.make.com/abc123",
            template="cloud_insight",
            variables='{"insight_content": "Project shows scope creep pattern", "related_count": 5, "salience": 0.8}'
        )
        ```
        """
        import os
        import json

        # Read from environment variables if not provided
        webhook_url = webhook_url or os.getenv("EMAIL_WEBHOOK_URL", "")
        authorization = authorization or os.getenv("EMAIL_AUTHORIZATION", "")

        if not webhook_url:
            return "Error: EMAIL_WEBHOOK_URL not configured. Set this environment variable with your webhook URL."

        try:
            template_vars = json.loads(variables)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in variables parameter: {e}"

        # Prepare headers with authorization
        headers = {}
        if authorization:
            headers["Authorization"] = authorization

        result = await send_templated_email(
            webhook_url=webhook_url,
            template_name=template,
            template_vars=template_vars,
            headers=headers if headers else None
        )

        if result["success"]:
            return f"""✅ Templated email sent successfully!

Template: {template}
Subject: {EMAIL_TEMPLATES[template]['subject']}
Sent: {result['timestamp']}

Your email should arrive shortly."""
        else:
            return f"""❌ Failed to send templated email

Error: {result.get('error', 'Unknown error')}
Details: {result.get('details', 'No details')}

Please check the template name and variables."""

    @mcp.tool
    async def test_email_webhook(
        webhook_url: str = Field(default="", description="Your webhook URL to test (set via EMAIL_WEBHOOK_URL env var)"),
        authorization: str = Field(default="", description="Authorization header (set via EMAIL_AUTHORIZATION env var)")
    ) -> str:
        """
        Test your email webhook configuration.

        Sends a test email to verify your webhook is working correctly.

        **Usage:**
        1. Set EMAIL_WEBHOOK_URL environment variable with your webhook URL
        2. Set EMAIL_AUTHORIZATION environment variable with your auth token (if required)
        3. Run this tool
        4. Check if you receive the test email

        **Example:**
        ```
        test_email_webhook()
        ```
        """
        import os

        # Read from environment variables if not provided
        webhook_url = webhook_url or os.getenv("EMAIL_WEBHOOK_URL", "")
        authorization = authorization or os.getenv("EMAIL_AUTHORIZATION", "")

        if not webhook_url:
            return """Error: EMAIL_WEBHOOK_URL not configured.

To use email notifications:
1. Set EMAIL_WEBHOOK_URL environment variable with your N8N/Make.com webhook URL
2. Set EMAIL_AUTHORIZATION environment variable with your auth token (if required)
3. Run this tool again to test

Example environment variables:
EMAIL_WEBHOOK_URL=https://n8n.example.com/webhook/abc-123
EMAIL_AUTHORIZATION=your-auth-token-here
"""

        # Prepare headers with authorization
        headers = {}
        if authorization:
            headers["Authorization"] = authorization

        result = await send_email_notification(
            webhook_url=webhook_url,
            subject="Brain OS Webhook Test",
            body="""This is a test email from Brain OS.

If you receive this, your webhook is configured correctly! 🎉

You can now use email notifications for:
- Weekly summaries
- System alerts
- Task reports
- Custom notifications

---
Brain OS - Your Cognitive Operating System""",
            metadata={"test": True, "environment": "verification"},
            headers=headers if headers else None
        )

        if result["success"]:
            return f"""✅ Test email sent successfully!

Your webhook is working! Check your email inbox.

If you don't see the email within a minute:
- Check your spam folder
- Verify the webhook URL is correct
- Check your webhook service (Make.com, etc.) is active

Webhook URL: {webhook_url}
Status: {result['status_code']}
Timestamp: {result['timestamp']}"""
        else:
            return f"""❌ Test email failed

The webhook didn't respond correctly.

Error: {result.get('error', 'Unknown error')}
Details: {result.get('details', 'No details')}

Troubleshooting:
1. Verify the webhook URL is correct
2. Check your webhook service is active
3. Ensure the webhook accepts POST requests with JSON
4. Check webhook service logs for errors"""

    @mcp.tool
    async def list_email_templates() -> str:
        """List all available email templates with their required variables."""
        lines = ["## Brain OS Email Templates", ""]
        lines.append("Available templates for `send_templated_email`:")
        lines.append("")

        for name, template in EMAIL_TEMPLATES.items():
            lines.append(f"### {name}")
            lines.append(f"**Subject:** {template['subject']}")
            lines.append("**Variables:**")

            # Extract variables from template (simplified)
            import re
            vars_found = set(re.findall(r'\{(\w+)\}', template['template']))
            vars_found.discard('timestamp')  # Auto-added

            if vars_found:
                for var in sorted(vars_found):
                    lines.append(f"  - `{var}`")
            else:
                lines.append("  (no variables required)")

            lines.append("")

        lines.append("**Usage:**")
        lines.append("```")
        lines.append('send_templated_email(')
        lines.append('    webhook_url="https://hook.eu.make.com/abc123",')
        lines.append('    template="weekly_summary",')
        lines.append('    variables=\'{"total_memories": 147, "new_memories": 12}\'')
        lines.append(')')
        lines.append("```")

        return "\n".join(lines)
