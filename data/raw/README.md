# data/raw

Acquired source files (PDFs, scans, XML dumps) live here locally and are **git-ignored**.

Rules:

1. Register every file in `registers/source_register.csv` (kind = `file_copy`) with its SHA-256, retrieval URL, retrieval date and the `rights_id` it falls under.
2. Never commit a file here unless `registers/rights_register.csv` marks it `redistributable = yes`.
3. Never overwrite a file; a new retrieval gets a new file name and a new `file_copy` record.
