"""Validated request and response shapes for personalized PDF markup."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

HexColor = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]


class _StrictSchema(BaseModel):
    model_config = {"extra": "forbid"}


class NormalizedPoint(_StrictSchema):
    """A location relative to page width and height."""

    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)


class NormalizedRect(_StrictSchema):
    """A normalized rectangle that must remain inside the page."""

    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)
    width: float = Field(..., gt=0, le=1)
    height: float = Field(..., gt=0, le=1)

    @model_validator(mode="after")
    def validate_page_bounds(self):
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("Rectangle must remain within normalized page bounds")
        return self


class TextMarkupGeometry(_StrictSchema):
    rects: list[NormalizedRect] = Field(..., min_length=1, max_length=100)


class PointGeometry(_StrictSchema):
    point: NormalizedPoint


class InkGeometry(_StrictSchema):
    paths: list[list[NormalizedPoint]] = Field(..., min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_paths(self):
        if any(len(path) < 2 for path in self.paths):
            raise ValueError("Every ink path must contain at least two points")
        if sum(len(path) for path in self.paths) > 10_000:
            raise ValueError("Ink annotations may contain at most 10000 points")
        return self


class BoundsGeometry(_StrictSchema):
    bounds: NormalizedRect


class LineGeometry(_StrictSchema):
    start: NormalizedPoint
    end: NormalizedPoint


class TextMarkupStyle(_StrictSchema):
    color: HexColor
    opacity: float = Field(..., ge=0, le=1)


class StickyNoteStyle(_StrictSchema):
    color: HexColor


class StrokeStyle(_StrictSchema):
    stroke_color: HexColor
    stroke_width: float = Field(..., gt=0, le=0.05)
    opacity: float = Field(..., ge=0, le=1)


class ShapeStyle(StrokeStyle):
    fill_color: Optional[HexColor] = None


class _AnnotationPayloadBase(_StrictSchema):
    client_id: UUID
    manual_version_number: int = Field(..., ge=1)
    page_number: int = Field(..., ge=1)


class TextMarkupPayload(_AnnotationPayloadBase):
    annotation_type: Literal["highlight", "underline", "strikeout"]
    geometry: TextMarkupGeometry
    style: TextMarkupStyle
    selected_text: Optional[str] = Field(default=None, max_length=2000)
    note_text: Optional[str] = Field(default=None, max_length=5000)


class StickyNotePayload(_AnnotationPayloadBase):
    annotation_type: Literal["sticky_note"]
    geometry: PointGeometry
    style: StickyNoteStyle
    note_text: str = Field(..., min_length=1, max_length=5000)


class InkPayload(_AnnotationPayloadBase):
    annotation_type: Literal["ink"]
    geometry: InkGeometry
    style: StrokeStyle


class ShapePayload(_AnnotationPayloadBase):
    annotation_type: Literal["rectangle", "ellipse"]
    geometry: BoundsGeometry
    style: ShapeStyle


class LinePayload(_AnnotationPayloadBase):
    annotation_type: Literal["line"]
    geometry: LineGeometry
    style: StrokeStyle


AnnotationPayload = Annotated[
    Union[TextMarkupPayload, StickyNotePayload, InkPayload, ShapePayload, LinePayload],
    Field(discriminator="annotation_type"),
]


class ManualAnnotationReplace(_StrictSchema):
    expected_revision: int = Field(..., ge=1)
    annotation: AnnotationPayload


class AnnotationUpsertChange(_StrictSchema):
    operation: Literal["upsert"]
    expected_revision: int = Field(..., ge=0)
    annotation: AnnotationPayload


class AnnotationDeleteChange(_StrictSchema):
    operation: Literal["delete"]
    client_id: UUID
    expected_revision: int = Field(..., ge=1)


AnnotationSyncChange = Annotated[
    Union[AnnotationUpsertChange, AnnotationDeleteChange],
    Field(discriminator="operation"),
]


class ManualAnnotationSyncRequest(_StrictSchema):
    manual_version_number: int = Field(..., ge=1)
    changes: list[AnnotationSyncChange] = Field(..., max_length=500)

    @model_validator(mode="after")
    def validate_unique_client_ids(self):
        client_ids = [
            change.annotation.client_id
            if change.operation == "upsert"
            else change.client_id
            for change in self.changes
        ]
        if len(client_ids) != len(set(client_ids)):
            raise ValueError("Each client_id may appear only once per sync request")
        return self


class ManualAnnotationOut(BaseModel):
    id: int
    client_id: UUID
    manual_id: int
    manual_version_number: int
    annotation_type: str
    page_number: int
    geometry: dict
    style: dict
    selected_text: Optional[str] = None
    note_text: Optional[str] = None
    revision: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ManualAnnotationCollectionOut(BaseModel):
    manual_id: int
    manual_version_number: int
    annotations: list[ManualAnnotationOut]


class AnnotationAppliedOut(BaseModel):
    operation: Literal["upsert", "delete"]
    client_id: UUID
    revision: int


class AnnotationConflictOut(BaseModel):
    operation: Literal["upsert", "delete"]
    client_id: UUID
    reason: str
    server_revision: Optional[int] = None
    server_deleted: bool = False
    server_annotation: Optional[ManualAnnotationOut] = None


class ManualAnnotationSyncOut(ManualAnnotationCollectionOut):
    applied: list[AnnotationAppliedOut]
    conflicts: list[AnnotationConflictOut]
