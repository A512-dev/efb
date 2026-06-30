# Manual Category Path API

This feature adds hierarchical category paths for manuals.

The frontend can build a UX-friendly cascading selector by loading root categories first, then loading children after the user selects a parent.

## Default category tree

```text
1. A300/600
   1.1 Aircraft documents
   1.2 Aircraft Performance
   1.3 Fleet memos
   1.4 General
   1.5 MEL CDI
   1.6 training documents

2. Iranair
   2.1 Aircraft documents
   2.2 Aircraft Performance
   2.3 Fleet memos
   2.4 General
   2.5 MEL CDI
   2.6 training documents

3. Training and resources
   3.1 Aircraft documents
   3.2 Aircraft Performance
   3.3 Fleet memos
   3.4 General
   3.5 MEL CDI
   3.6 training documents

4. Forms
   4.1 REPORTS
   4.2 sms
   4.3 training

5. Safety Issue
   5.1 Aircraft documents
   5.2 Aircraft Performance
   5.3 Fleet memos
   5.4 General
   5.5 MEL CDI
   5.6 training documents
```

## Database changes

Migration:

```text
alembic/versions/0004_manual_category_paths.py
```

Creates:

```text
manual_categories
```

Adds to `manuals`:

```text
category_id
```

Existing manuals are backfilled to:

```text
Iranair / General
```

## Category endpoints

### List root categories

```http
GET /api/v1/manual-categories/roots
```

Returns only level-1 categories.

### List children of selected category

```http
GET /api/v1/manual-categories/{category_id}/children
```

Use this after the user selects a category. If the response is empty, the selected category is a leaf and can be used for manual upload.

### Get full tree

```http
GET /api/v1/manual-categories/tree
```

Returns the entire nested category tree.

Each tree node includes `has_children` and `is_leaf`. For manual upload, the frontend should only submit categories where `is_leaf=true`.

### Get breadcrumb path

```http
GET /api/v1/manual-categories/{category_id}/path
```

Example response:

```json
[
  {"id": 2, "name": "Iranair", "slug": "iranair"},
  {"id": 6, "name": "General", "slug": "general"}
]
```

## Admin category management

Only admins can mutate the category tree.

### Create category

```http
POST /api/v1/manual-categories
```

Body:

```json
{
  "name": "New Folder",
  "parent_id": 123
}
```

Use `parent_id: null` or omit it to create a root category.

The backend rejects duplicate active sibling names and rejects creating a child under a category that already contains active manuals.

### Rename category

```http
PATCH /api/v1/manual-categories/{category_id}
```

Body:

```json
{
  "name": "Renamed Folder"
}
```

Rename changes the display name only. The category `slug` stays stable.

### Move category

```http
PATCH /api/v1/manual-categories/{category_id}/move
```

Body:

```json
{
  "parent_id": 456
}
```

Use `parent_id: null` to move the category to the root level.

The backend rejects moves into the category itself or one of its descendants. It also rejects moving under a category that contains active manuals.

### Reorder sibling categories

```http
PATCH /api/v1/manual-categories/reorder
```

Body:

```json
{
  "parent_id": 123,
  "category_ids": [7, 5, 6]
}
```

`category_ids` must contain every active direct child under `parent_id` exactly once. Use `parent_id: null` for root ordering.

### Delete category

```http
DELETE /api/v1/manual-categories/{category_id}
```

Delete is a soft delete: the category subtree is hidden by setting `is_active=false`.

The backend returns `409` if the category or any descendant contains a non-deleted manual. Delete or move those manuals first.

## Manual upload changes

Manual upload now requires a final leaf category:

```http
POST /api/v1/manuals/upload
```

Multipart fields:

```text
title       required
category_id required, must be a leaf category
note        optional
file        required PDF
```

If a non-leaf category is selected, backend returns `400`.

## Manual update changes

Manual update can optionally change category:

```http
POST /api/v1/manuals/{manual_id}/update
```

Multipart fields:

```text
file        required replacement PDF
title       optional
category_id optional, must be a leaf category if provided
note        optional
```

## Manual list changes

Manual list supports category filtering:

```http
GET /api/v1/manuals?category_id=123&include_descendants=true
```

If `include_descendants=true`, selecting a top-level category returns manuals inside all child categories.

Manual responses now include:

```json
{
  "category_id": 6,
  "category_path": [
    {"id": 2, "name": "Iranair", "slug": "iranair"},
    {"id": 6, "name": "General", "slug": "general"}
  ],
  "category_path_text": "Iranair / General"
}
```

## Frontend implementation suggestion

For a cascading picker:

1. Call `GET /api/v1/manual-categories/roots`.
2. User selects a root category.
3. Call `GET /api/v1/manual-categories/{id}/children`.
4. Continue until the response is empty.
5. Submit the final selected category id as `category_id`.
