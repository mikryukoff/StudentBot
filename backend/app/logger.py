import json
import sys
from typing import Any, Optional

from fastapi import Request
from loguru import logger


class StructuredLogger:
    def __init__(self):
        self.logger = logger
        self.setup_logger()
    
    def setup_logger(self):
        """Настройка логгера с выводом в stdout и файл"""
        
        # Удаляем все предыдущие обработчики
        self.logger.remove()

        self.logger = self.logger.patch(self.patching)
        
        # Создаем папку для логов, если её нет
        import os
        os.makedirs("logs", exist_ok=True)
        
        # Добавляем обработчик для stdout
        self.logger.add(
            sys.stdout,
            format="{extra[serialized]}",
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        
        # Добавляем обработчик для файла
        self.logger.add(
            "logs/app_{time}.json",
            format="{extra[serialized]}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True
        )

    def serialize(self, record):
        log_data = {
            "event": record.get("message", ""),
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": record["level"].name,
            "request_id": record["extra"].get("request_id", "N/A"),
            "method": record["extra"].get("method", "N/A"),
            "path": record["extra"].get("path", "N/A"),
            "client_host": record["extra"].get("client_host", "N/A"),
            "client_port": record["extra"].get("client_port", "N/A"),
            "query_params": record["extra"].get("query_params", {}),
            "path_params": record["extra"].get("path_params", {}),
            "headers": record["extra"].get("headers", {}),
            "cookies": record["extra"].get("cookies", {}),
            "body": record["extra"].get("body", "N/A"),
            "content_type": record["extra"].get("content_type", "N/A"),
            "status_code": record["extra"].get("status_code", "N/A"),
            "error_type": record["extra"].get("error_type", "N/A"),
            "error_message": record["extra"].get("error_message", "N/A"),
            "duration_ms": record["extra"].get("duration_ms", "N/A"),
            "traceback": record["extra"].get("traceback", "N/A")
        }
        return json.dumps(log_data)


    def patching(self, record):
        record["extra"]["serialized"] = self.serialize(record)
    
    async def log_error(
        self,
        request: Request, 
        exc: Exception, 
        *, 
        status_code: int, 
        request_id: str,
        duration_ms: Optional[float] = None
    ):
        """Логирует ошибку с полным контекстом запроса"""
        try:
            # Извлекаем контекст запроса
            method = request.method
            path = request.url.path
            client_host = request.client.host if request.client else "unknown"
            client_port = request.client.port if request.client else "unknown"
            query_params = dict(request.query_params)
            path_params = dict(request.path_params)
            
            # Маскируем заголовки
            headers = self.mask_headers(dict(request.headers))
            cookies = dict(request.cookies)
            content_type = request.headers.get("content-type", "unknown")
            
            # Асинхронно извлекаем тело
            body = await self.safe_extract_body(request)
            
            # Получаем информацию об ошибке
            error_type = type(exc).__name__
            error_message = str(exc)
            
            # Получаем traceback
            import traceback
            traceback_str = traceback.format_exc()
            
            # Логируем с привязкой контекста
            self.logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                client_host=client_host,
                client_port=client_port,
                query_params=query_params,
                path_params=path_params,
                headers=headers,
                cookies=cookies,
                body=body,
                content_type=content_type,
                status_code=status_code,
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
                traceback=traceback_str
            ).error("Request failed")
            
        except Exception as log_exc:
            # Фолбэк на случай ошибок в самом логировании
            fallback_logger = self.logger.bind(
                request_id=request_id,
                method=getattr(request, 'method', 'N/A'),
                path=getattr(request.url, 'path', 'N/A') if hasattr(request, 'url') else 'N/A',
                status_code=status_code
            )
            fallback_logger.error(f"Logging failed: {str(log_exc)}")
            fallback_logger.error(f"Original error: {str(exc)}")
    
    async def safe_extract_body(self, request: Request, max_length: int = 2048) -> Any:
        """Безопасно извлекает тело запроса с ограничением длины"""
        try:
            content_type = request.headers.get("content-type", "")
            
            # Для multipart/form-data извлекаем только метаданные
            if "multipart/form-data" in content_type:
                form_data = await request.form()
                files_meta = []
                
                for key, value in form_data.items():
                    if hasattr(value, "filename") and hasattr(value, "size"):
                        files_meta.append({
                            "field_name": key,
                            "file_name": value.filename,
                            "size": value.size,
                            "content_type": getattr(value, "content_type", "UNKNOWN")
                        })
                    else:
                        files_meta.append({
                            "field_name": key,
                            "value": str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        })
                
                return files_meta
            
            # Для других типов контента
            body = await request.body()
            if len(body) > max_length:
                return f"Body truncated: {len(body)} bytes"
                
            # Пытаемся разобрать JSON
            if "application/json" in content_type:
                try:
                    return self.mask_sensitive_data(json.loads(body))
                except Exception:
                    return body.decode('utf-8', errors='replace')[:max_length]
                    
            # Для других типов
            return body.decode('utf-8', errors='replace')[:max_length]
            
        except Exception as e:
            return f"Error extracting body: {str(e)}"
    
    def mask_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Маскирует чувствительные заголовки"""
        sensitive_headers = {'authorization', 'cookie', 'set-cookie', 'x-api-key'}
        masked = {}
        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in sensitive_headers):
                masked[key] = "***MASKED***"
            else:
                masked[key] = value
        return masked
    
    def mask_sensitive_data(self, data: Any) -> Any:
        """Маскирует чувствительные данные в структурах"""
        sensitive_fields = {'password', 'token', 'secret', 'key'}
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    masked[key] = "***MASKED***"
                else:
                    masked[key] = self.mask_sensitive_data(value)
            return masked
        elif isinstance(data, list):
            return [self.mask_sensitive_data(item) for item in data]
        else:
            return data

# Создаем глобальный экземпляр логгера
structured_logger = StructuredLogger()

# Создаем алиасы для удобства
log_error = structured_logger.log_error
setup_logger = structured_logger.setup_logger