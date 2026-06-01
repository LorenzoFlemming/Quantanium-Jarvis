import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnalyticsManager:
    """Enhanced analytics and insights system"""
    
    ANALYTICS_FILE = "analytics.json"
    
    def __init__(self):
        """Initialize analytics manager"""
        self.data = self._load_analytics()
    
    def track_event(self, event_type: str, data: Dict = None):
        """Track an event"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        if "events" not in self.data:
            self.data["events"] = []
        
        self.data["events"].append(event)
        self._save_analytics()
    
    def track_api_call(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Track API call"""
        if "api_calls" not in self.data:
            self.data["api_calls"] = []
        
        self.data["api_calls"].append({
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_analytics()
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        events = self.data.get("events", [])
        api_calls = self.data.get("api_calls", [])
        
        # Calculate stats
        total_events = len(events)
        total_api_calls = len(api_calls)
        
        # Average response time
        if api_calls:
            avg_response_time = sum(c["response_time"] for c in api_calls) / len(api_calls)
        else:
            avg_response_time = 0
        
        # Error rate
        errors = len([c for c in api_calls if c["status_code"] >= 400])
        error_rate = (errors / total_api_calls * 100) if total_api_calls > 0 else 0
        
        # Most called endpoints
        endpoints = {}
        for call in api_calls:
            endpoint = call["endpoint"]
            endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
        
        top_endpoints = sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_events": total_events,
            "total_api_calls": total_api_calls,
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "top_endpoints": [{"endpoint": e[0], "calls": e[1]} for e in top_endpoints],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_insights(self) -> List[Dict]:
        """Get AI-powered insights"""
        insights = []
        stats = self.get_dashboard_stats()
        
        # Insight 1: High error rate
        if stats["error_rate"] > 10:
            insights.append({
                "type": "warning",
                "title": "High Error Rate Detected",
                "message": f"Error rate is {stats['error_rate']:.1f}%. Check API logs.",
                "severity": "high"
            })
        
        # Insight 2: Slow API response
        if stats["avg_response_time"] > 1.0:
            insights.append({
                "type": "warning",
                "title": "Slow API Response",
                "message": f"Average response time: {stats['avg_response_time']:.2f}s",
                "severity": "medium"
            })
        
        # Insight 3: Most used endpoint
        if stats["top_endpoints"]:
            top = stats["top_endpoints"][0]
            insights.append({
                "type": "info",
                "title": "Most Used Endpoint",
                "message": f"{top['endpoint']} called {top['calls']} times",
                "severity": "low"
            })
        
        return insights
    
    def _load_analytics(self) -> Dict:
        """Load analytics data"""
        try:
            if os.path.exists(self.ANALYTICS_FILE):
                with open(self.ANALYTICS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[ANALYTICS] Error loading: {e}")
        return {}
    
    def _save_analytics(self):
        """Save analytics data"""
        try:
            with open(self.ANALYTICS_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[ANALYTICS] Error saving: {e}")


class BackupManager:
    """Enhanced backup and recovery system"""
    
    def __init__(self, backup_dir: str = "backups"):
        """Initialize backup manager"""
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, files: List[str]) -> Dict:
        """Create a backup of specified files"""
        import shutil
        import tarfile
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                for file in files:
                    if os.path.exists(file):
                        tar.add(file, arcname=os.path.basename(file))
            
            return {
                "status": "success",
                "backup_file": backup_path,
                "timestamp": datetime.now().isoformat(),
                "files_backed_up": len(files)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for file in os.listdir(self.backup_dir):
            if file.startswith("backup_") and file.endswith(".tar.gz"):
                path = os.path.join(self.backup_dir, file)
                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                
                backups.append({
                    "name": file,
                    "path": path,
                    "size": size,
                    "created_at": mtime
                })
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def restore_backup(self, backup_file: str, extract_path: str = ".") -> Dict:
        """Restore from backup"""
        import tarfile
        
        try:
            if not os.path.exists(backup_file):
                return {"status": "error", "message": "Backup file not found"}
            
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(path=extract_path)
            
            return {
                "status": "success",
                "message": "Backup restored successfully",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def auto_backup(self, files: List[str], max_backups: int = 10) -> Dict:
        """Automatically create backups and maintain limit"""
        result = self.create_backup(files)
        
        if result["status"] == "success":
            backups = self.list_backups()
            
            # Remove old backups if exceeding limit
            while len(backups) > max_backups:
                old_backup = backups.pop()
                try:
                    os.remove(old_backup["path"])
                except Exception as e:
                    print(f"[BACKUP] Error removing old backup: {e}")
        
        return result


class HealthCheck:
    """Enhanced system health monitoring"""
    
    def __init__(self):
        """Initialize health check"""
        self.checks = {}
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            percent_used = (used / total) * 100
            
            return {
                "status": "healthy" if percent_used < 90 else "warning",
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_used": round(percent_used, 2)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_memory(self) -> Dict:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                "status": "healthy" if memory.percent < 80 else "warning",
                "total_mb": round(memory.total / (1024**2), 2),
                "available_mb": round(memory.available / (1024**2), 2),
                "percent_used": round(memory.percent, 2)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_cpu(self) -> Dict:
        """Check CPU usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "status": "healthy" if cpu_percent < 80 else "warning",
                "percent_used": round(cpu_percent, 2),
                "cores": psutil.cpu_count()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_full_report(self) -> Dict:
        """Get full system health report"""
        return {
            "disk": self.check_disk_space(),
            "memory": self.check_memory(),
            "cpu": self.check_cpu(),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test analytics
    analytics = AnalyticsManager()
    analytics.track_event("app_start", {"version": "1.0.0"})
    analytics.track_api_call("/api/todos", "GET", 200, 0.05)
    
    print("[ANALYTICS] Stats:", analytics.get_dashboard_stats())
    print("[ANALYTICS] Insights:", analytics.get_insights())
    
    # Test backup
    backup = BackupManager()
    result = backup.create_backup(["config.json"])
    print("[BACKUP]", result)
    
    # Test health check
    health = HealthCheck()
    print("[HEALTH]", health.get_full_report())
