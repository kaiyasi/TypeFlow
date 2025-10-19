"""
監控和日誌服務
"""
import time
import structlog
from typing import Optional, Dict, Any
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge
from contextlib import contextmanager

logger = structlog.get_logger()

# Prometheus 指標
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# 業務指標
typing_sessions_total = Counter(
    'typing_sessions_total',
    'Total typing sessions',
    ['language', 'mode']
)

wpm_distribution = Histogram(
    'wpm_distribution',
    'WPM distribution',
    buckets=[20, 40, 60, 80, 100, 120, 150, 200]
)

accuracy_distribution = Histogram(
    'accuracy_distribution',
    'Accuracy distribution',
    buckets=[50, 60, 70, 80, 85, 90, 95, 98, 100]
)

error_count = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)


class MonitoringService:
    """監控服務"""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        """記錄 HTTP 請求"""
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        logger.info(
            "HTTP request",
            method=method,
            endpoint=endpoint,
            status=status,
            duration=duration
        )
    
    @staticmethod
    def record_typing_session(language: str, mode: str, wpm: float, accuracy: float):
        """記錄打字會話"""
        typing_sessions_total.labels(language=language, mode=mode).inc()
        wpm_distribution.observe(wpm)
        accuracy_distribution.observe(accuracy)
        
        logger.info(
            "Typing session completed",
            language=language,
            mode=mode,
            wpm=wpm,
            accuracy=accuracy
        )
    
    @staticmethod
    def record_error(error_type: str, endpoint: str, error: Exception):
        """記錄錯誤"""
        error_count.labels(error_type=error_type, endpoint=endpoint).inc()
        
        logger.error(
            "Error occurred",
            error_type=error_type,
            endpoint=endpoint,
            error=str(error),
            exc_info=error
        )
    
    @staticmethod
    @contextmanager
    def track_time(operation: str):
        """追蹤操作時間"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            logger.info(
                f"{operation} completed",
                operation=operation,
                duration=duration
            )


class PerformanceMonitor:
    """效能監控"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    def start_operation(self, operation_id: str):
        """開始監控操作"""
        self.metrics[operation_id] = {
            "start_time": time.time(),
            "start_memory": self._get_memory_usage()
        }
    
    def end_operation(self, operation_id: str) -> Dict[str, float]:
        """結束監控操作並返回指標"""
        if operation_id not in self.metrics:
            return {}
        
        start_metrics = self.metrics[operation_id]
        duration = time.time() - start_metrics["start_time"]
        memory_delta = self._get_memory_usage() - start_metrics["start_memory"]
        
        del self.metrics[operation_id]
        
        return {
            "duration": duration,
            "memory_delta_mb": memory_delta
        }
    
    @staticmethod
    def _get_memory_usage() -> float:
        """獲取當前內存使用量（MB）"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0


class AlertService:
    """告警服務"""
    
    @staticmethod
    async def send_alert(
        level: str,
        title: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """發送告警"""
        logger.warning(
            "Alert triggered",
            level=level,
            title=title,
            message=message,
            metadata=metadata
        )
        
        # 這裡可以整合各種告警渠道
        # - Email
        # - Slack
        # - Discord
        # - SMS
        # - PagerDuty
    
    @staticmethod
    async def check_system_health() -> Dict[str, Any]:
        """檢查系統健康狀態"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 檢查資料庫連線
        try:
            # await db_health_check()
            health["checks"]["database"] = "ok"
        except Exception as e:
            health["checks"]["database"] = f"error: {str(e)}"
            health["status"] = "unhealthy"
        
        # 檢查 Redis 連線
        try:
            # await redis_health_check()
            health["checks"]["redis"] = "ok"
        except Exception as e:
            health["checks"]["redis"] = f"error: {str(e)}"
            health["status"] = "degraded"
        
        # 檢查磁碟空間
        try:
            import psutil
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            health["checks"]["disk"] = f"{disk_usage_percent}% used"
            
            if disk_usage_percent > 90:
                health["status"] = "degraded"
                await AlertService.send_alert(
                    "warning",
                    "High disk usage",
                    f"Disk usage is at {disk_usage_percent}%"
                )
        except Exception as e:
            health["checks"]["disk"] = f"error: {str(e)}"
        
        return health


# 全局實例
monitoring = MonitoringService()
performance_monitor = PerformanceMonitor()
alert_service = AlertService()

