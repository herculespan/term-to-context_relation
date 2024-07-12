from enum import Enum
class CrawlerStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'