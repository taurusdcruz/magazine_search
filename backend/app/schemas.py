MOCKAROO_SCHEMA = {
  "fields": [
    {
      "name": "id",
      "type": "Row Number"
    },
    {
      "name": "title",
      "type": "Movie Title"
    },
    {
      "name": "author",
      "type": "Full Name"
    },
    {
      "name": "publication_date",
      "type": "Datetime",
      "date_format": "%Y-%m-%d" 
    },
    {
      "name": "category",
      "type": "Custom List",
      "values": [
        "item 1",
        "item 2",
        "item 3"
      ]
    },
    {
      "name": "content_id",
      "type": "Row Number"
    },
    {
      "name": "content",
      "type": "Paragraphs",
      "min_paragraphs": 1,
      "max_paragraphs": 3
    }
  ]
}