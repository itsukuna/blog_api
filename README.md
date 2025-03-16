# Blog API

This is a simple FastAPI project to manage blog posts with MongoDB as the database. The API provides endpoints to create, read, update, and delete articles, along with search functionality.
Inspired from [project](https://roadmap.sh/projects/blogging-platform-api) on Roadmap.sh

## Features

- Create new blog articles
- Retrieve all articles or a specific article by ID
- Update articles
- Delete articles
- Filter articles based on search terms

## Technologies Used

- FastAPI
- Pydantic
- MongoDB (via PyMongo)

## Prerequisites

- Python 3.10+
- MongoDB Atlas or a local MongoDB instance

## Installation

1. Clone the repository:

```bash
git clone https://github.com/itsukuna/blog_api.git
cd blog_api
```

2. Create a virtual environment and activate it:

```bash
pipenv shell
```

3. Install dependencies:

```bash
pipenv install
```

4. Set the MongoDB URI:

```bash
export MONGO_URI="your-mongo-uri"  # On Windows use: set MONGO_URI="your-mongo-uri"
```

## Running the API

Start the FastAPI server with:

```bash
fastapi dev main.py
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Root

```http
GET /
```

Response:

```json
{ "message": "Blog API" }
```

### Create Article

```http
POST /new_article/
```

Request Body:

```json
{
  "title": "My First Post",
  "content": "This is the content of the post.",
  "category": "Tech",
  "tags": ["fastapi", "mongodb"]
}
```

Response:

```json
{
  "id": "60f5a1a42f50c2f5a8b0b7d1",
  "title": "My First Post",
  "content": "This is the content of the post.",
  "category": "Tech",
  "tags": ["fastapi", "mongodb"],
  "createdAt": "2025-03-16T10:00:00",
  "updatedAt": "2025-03-16T10:00:00"
}
```

### Get All Articles

```http
GET /articles/
```

### Get Article by ID

```http
GET /articles/{article_id}
```

### Update Article

```http
PUT /update_article/{article_id}
```

### Delete Article

```http
DELETE /delete_article/{article_id}
```

### Filter Articles

```http
GET /filter_article/?search_term=fastapi
```

## Testing

You can test the API with tools like [Postman](https://www.postman.com/) or access the interactive docs at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is licensed under the MIT License.

## Author

[Ayush Arya](https://github.com/itsukuna)
