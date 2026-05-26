# API Documentation

Base URL: `/api`

## Authentication

### `POST /auth/register`
Create a new user account.
- **Body**: `{ "full_name": "string", "email": "string", "password": "string" }`
- **Response**: `{ "access_token": "string", "token_type": "bearer", "user": { ... } }`

### `POST /auth/login`
Authenticate a user.
- **Body**: `{ "email": "string", "password": "string" }`
- **Response**: `{ "access_token": "string", "token_type": "bearer", "user": { ... } }`

### `GET /auth/me`
Get current user details. Requires Bearer Token.

### `PUT /auth/me`
Update current user. Requires Bearer Token.

## Notes

### `GET /notes/`
List notes. Requires Bearer Token.
- **Query Params**: `search` (optional), `subject` (optional)

### `POST /notes/`
Upload a new note. Requires Bearer Token.
- **Content-Type**: `multipart/form-data`
- **Form Fields**: `title` (string), `subject` (string), `description` (string, optional), `file` (binary)

### `GET /notes/stats`
Get high-level counts. Requires Bearer Token.
- **Response**: `{ "total_notes": int, "subjects_count": int, "recent_uploads": [...] }`

### `DELETE /notes/{note_id}`
Delete a note and its file from S3. Requires Bearer Token.

### `GET /notes/{note_id}/download`
Get a temporary S3 presigned URL for downloading the file. Requires Bearer Token.
- **Response**: `{ "download_url": "https://s3.amazonaws.com/..." }`

## Analytics

### `GET /analytics/`
Get PySpark-computed analytics data. Requires Bearer Token.
- **Response**: 
```json
{
  "top_subjects": [{ "subject": "Math", "count": 10 }],
  "monthly_uploads": [{ "month": "May 2026", "count": 5 }],
  "file_type_distribution": [{ "type": "PDF", "count": 8 }],
  "total_files": 15
}
```
