from datetime import datetime
from enum import Enum
from typing import List, Callable


class NotificationType(Enum):
    """Tipos de notificaciones disponibles"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Notification:
    """Modelo de una notificación individual"""
    def __init__(self, title: str, message: str, notification_type: NotificationType = NotificationType.INFO):
        self.id = id(self)  # ID único basado en el objeto
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.created_at = datetime.now().strftime("%H:%M")
        self.read = False


class NotificationManager:
    """Gestor centralizado de notificaciones para toda la app"""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.max_notifications = 20  # Mantener máximo 20 notificaciones en memoria
        self.on_notification_added: Callable = None  # Callback cuando se agrega una notificación
    
    def add_notification(self, title: str, message: str, notification_type: NotificationType = NotificationType.INFO) -> Notification:
        """Agregar una nueva notificación"""
        notification = Notification(title, message, notification_type)
        self.notifications.insert(0, notification)  # Agregar al inicio para que las más recientes estén arriba
        
        # Mantener el límite de notificaciones
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
        
        # Ejecutar callback si existe
        if self.on_notification_added:
            self.on_notification_added(notification)
        
        return notification
    
    def get_unread_count(self) -> int:
        """Obtener cantidad de notificaciones no leídas"""
        return sum(1 for n in self.notifications if not n.read)
    
    def mark_as_read(self, notification_id: int):
        """Marcar una notificación como leída"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                break
    
    def mark_all_as_read(self):
        """Marcar todas las notificaciones como leídas"""
        for notification in self.notifications:
            notification.read = True
    
    def remove_notification(self, notification_id: int):
        """Eliminar una notificación"""
        self.notifications = [n for n in self.notifications if n.id != notification_id]
    
    def clear_all(self):
        """Limpiar todas las notificaciones"""
        self.notifications.clear()
    
    def get_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """Obtener notificaciones de un tipo específico"""
        return [n for n in self.notifications if n.notification_type == notification_type]
    
    def get_all(self) -> List[Notification]:
        """Obtener todas las notificaciones"""
        return self.notifications
