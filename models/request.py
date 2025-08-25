from dataclasses import dataclass

@dataclass
class Request:
    id: str
    request_type: str
    status: str
    created_at: str
    updated_at: str
    reporter_email: str
    assignee_email: str
    component:str
    channel: str
    message: str
    
