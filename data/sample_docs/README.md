# Sample Project Documentation

Place your project documentation here for RAG ingestion.

## Supported Formats
- Markdown files (.md)
- Text files (.txt)
- JSON files (.json)

## Example Structure
```
data/sample_docs/
├── whitepaper.md        # Project whitepaper
├── tokenomics.md        # Token economics
├── roadmap.md           # Project roadmap
├── faq.md               # Frequently asked questions
├── team.md              # Team information
└── partnerships.md      # Strategic partnerships
```

## Ingestion
Use the `/api/rag/ingest` endpoint to ingest documents:

```json
{
    "project_id": "my-project",
    "documents": [
        {
            "id": "whitepaper",
            "content": "Your document content here...",
            "metadata": {"type": "whitepaper", "version": "1.0"}
        }
    ]
}
```
