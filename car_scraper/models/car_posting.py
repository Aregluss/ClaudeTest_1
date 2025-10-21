"""Car posting data model"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CarPosting(BaseModel):
    """
    Data model for a car posting/listing.
    Uses Pydantic for validation and serialization.
    """

    # Unique identifier
    id: str = Field(..., description="Unique identifier for the posting")
    source_url: str = Field(..., description="URL of the original posting")
    source_platform: str = Field(default="responsemotors", description="Platform name")

    # Car details
    title: str = Field(..., description="Full title of the listing")
    make: Optional[str] = Field(None, description="Car manufacturer")
    model: Optional[str] = Field(None, description="Car model")
    year: Optional[int] = Field(None, description="Manufacturing year")
    mileage: Optional[int] = Field(None, description="Mileage in miles")
    price: Optional[float] = Field(None, description="Listing price")
    currency: str = Field(default="USD", description="Currency code")

    # Posting details
    description: Optional[str] = Field(None, description="Full description")
    location: Optional[str] = Field(None, description="Location of vehicle")

    # Images
    image_urls: List[str] = Field(default_factory=list, description="List of image URLs")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now, description="When this was scraped")

    # Additional features
    features: Dict[str, Any] = Field(default_factory=dict, description="Additional features/specs")
    condition: Optional[str] = Field(None, description="Vehicle condition (new/used/certified)")
    vin: Optional[str] = Field(None, description="Vehicle Identification Number")

    @field_validator('year')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        """Validate year is reasonable"""
        if v is not None:
            if v < 1900 or v > datetime.now().year + 1:
                raise ValueError(f"Year {v} is not valid")
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate price is positive"""
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator('mileage')
    @classmethod
    def validate_mileage(cls, v: Optional[int]) -> Optional[int]:
        """Validate mileage is positive"""
        if v is not None and v < 0:
            raise ValueError("Mileage cannot be negative")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: dict) -> 'CarPosting':
        """Create instance from dictionary"""
        return cls(**data)

    def __str__(self) -> str:
        """String representation"""
        return (
            f"{self.year or '????'} {self.make or 'Unknown'} {self.model or 'Unknown'} - "
            f"${self.price:,.0f if self.price else 0} - {self.mileage or '???'} miles"
        )
