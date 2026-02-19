from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class CompanyCreate(BaseModel):
    name: str
    website: str | None = None

    @field_validator("website")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # use HttpUrl to validate and canonicalize, then return string
        return str(HttpUrl(v))


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    website: str | None = None
