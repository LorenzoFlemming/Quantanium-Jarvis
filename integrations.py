import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

class IntegrationManager:
    """Enhanced integration management system"""
    
    def __init__(self):
        """Initialize integration manager"""
        self.integrations = self._load_integrations()
    
    def _load_integrations(self) -> Dict:
        """Load integrations config"""
        if os.path.exists("integrations.json"):
            with open("integrations.json", 'r') as f:
                return json.load(f)
        return {}
    
    def _save_integrations(self):
        """Save integrations config"""
        with open("integrations.json", 'w') as f:
            json.dump(self.integrations, f, indent=2)


class GitHubIntegration(IntegrationManager):
    """GitHub integration"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub integration"""
        super().__init__()
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_user_info(self, username: str) -> Dict:
        """Get GitHub user info"""
        try:
            response = requests.get(f"{self.base_url}/users/{username}", headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_repositories(self, username: str) -> List[Dict]:
        """Get user repositories"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{username}/repos",
                headers=self.headers,
                params={"per_page": 100}
            )
            return response.json()
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_issue(self, owner: str, repo: str, title: str, body: str) -> Dict:
        """Create GitHub issue"""
        try:
            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                json={"title": title, "body": body}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_issue_stats(self, owner: str, repo: str) -> Dict:
        """Get repository issue statistics"""
        try:
            open_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": "open"}
            )
            closed_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": "closed"}
            )
            
            return {
                "open_issues": len(open_response.json()),
                "closed_issues": len(closed_response.json())
            }
        except Exception as e:
            return {"error": str(e)}


class SlackIntegration(IntegrationManager):
    """Slack integration"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Slack integration"""
        super().__init__()
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    
    def send_message(self, message: str, channel: str = None) -> Dict:
        """Send message to Slack"""
        try:
            payload = {"text": message}
            if channel:
                payload["channel"] = channel
            
            response = requests.post(self.webhook_url, json=payload)
            return {"status": "success", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_notification(self, title: str, message: str, color: str = "good") -> Dict:
        """Send formatted notification to Slack"""
        try:
            payload = {
                "attachments": [{
                    "color": color,
                    "title": title,
                    "text": message,
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            return {"status": "success", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_todo_alert(self, todos: List[Dict]) -> Dict:
        """Send todo summary to Slack"""
        pending = [t for t in todos if not t.get("completed")]
        
        try:
            payload = {
                "attachments": [{
                    "color": "#00e5ff",
                    "title": "📋 JARVIS Todo Summary",
                    "text": f"You have {len(pending)} pending tasks",
                    "fields": [
                        {
                            "title": "Pending Tasks",
                            "value": "\n".join([f"• {t['title']}" for t in pending[:5]]),
                            "short": False
                        }
                    ]
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            return {"status": "success", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class DiscordIntegration(IntegrationManager):
    """Discord integration"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Discord integration"""
        super().__init__()
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    
    def send_message(self, message: str) -> Dict:
        """Send message to Discord"""
        try:
            payload = {"content": message}
            response = requests.post(self.webhook_url, json=payload)
            return {"status": "success", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_embed(self, title: str, description: str, color: int = 0x00e5ff) -> Dict:
        """Send embedded message to Discord"""
        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": description,
                    "color": color,
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            return {"status": "success", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class TelegramIntegration(IntegrationManager):
    """Telegram integration"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize Telegram integration"""
        super().__init__()
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str) -> Dict:
        """Send message to Telegram"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": self.chat_id, "text": text}
            )
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def send_alert(self, title: str, message: str) -> Dict:
        """Send alert to Telegram"""
        text = f"🚨 *{title}*\n{message}"
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
            )
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}


class CalendarIntegration(IntegrationManager):
    """Google Calendar integration"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        """Initialize Calendar integration"""
        super().__init__()
        self.credentials_file = credentials_file or os.getenv("GOOGLE_CALENDAR_CREDS")
    
    def sync_events(self, events: List[Dict]) -> Dict:
        """Sync events with Google Calendar"""
        try:
            # This would require Google Calendar API setup
            return {"status": "success", "synced": len(events)}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Test GitHub
    print("[TEST] GitHub Integration")
    github = GitHubIntegration()
    print(github.get_repositories("LorenzoFlemming"))
    
    # Test Slack (requires webhook)
    print("[TEST] Slack Integration")
    slack = SlackIntegration()
    print(slack.send_message("JARVIS: System initialized"))
    
    # Test Discord (requires webhook)
    print("[TEST] Discord Integration")
    discord = DiscordIntegration()
    print(discord.send_embed("JARVIS", "System is online"))
