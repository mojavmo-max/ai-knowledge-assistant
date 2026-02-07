from pydantic import BaseModel
from typing import Optional

class Invoice(BaseModel):
    invoice_number: Optional[str]
    date: Optional[str]
    total: Optional[str]
    vendor: Optional[str]
