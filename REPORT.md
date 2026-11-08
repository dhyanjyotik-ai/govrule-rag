# Amendment-Aware Search over Government Orders: Project Log

## Goal

Build a search and Q&A system over public Government of India orders on
leave and allowances, measure where it fails (especially on superseded or
amended rules), and test a fix.

## Corpus (Day 1)

- Source: DoPT Circulars portal (doptcirculars.nic.in), public documents only.
- 8 documents downloaded: 2021 to 2025, topics: LTC, study leave,
  ex-India leave, leave encashment, higher-qualification incentive.
- All 8 PDFs are digital (1,448 to 3,165 characters per page), none scanned.

## Observations from text extraction

1. **Page junk:** the PDFs were printed from a browser, so every page
   contains a header and footer (date/time, "about:blank", page numbers)
   that gets mixed into the extracted text.
2. **Misplaced tables:** in the higher-qualification incentive order (2022),
   the rates table is extracted _before_ its heading "II Rates for
   Incentives", leaving blank lines where the table belongs.
3. **Split table cells:** long cells are broken across several lines.
4. **Document pairs found:**
   - The 2024 consolidated ex-India study leave order cites the 2023 order
     (file no. 11020/02/2023-AIS-III) by number.
   - The 2021 AIS and 2022 central incentive orders have near-identical
     rates for different audiences.
5. **Expiry date inside a document:** the 2025 LTC guidelines say an
   air-travel scheme runs until 25 September 2026. Whether it was
   extended is unknown from the document alone.

## Next steps

- Clean the extracted text (remove page junk).
- Load documents into MySQL.

## Day 2 log

### Environment

- Created a virtual environment (.venv) and requirements.txt so the project
  is reproducible.
- Installing PyMuPDF in the global Python raised a dependency conflict:
  mysql-connector-python 8.0.33 requires protobuf<=3.20.3, but PyMuPDF's
  dependencies installed protobuf 7.x. Isolating the project in a virtual
  environment avoids this.
- Updated `import fitz` to `import pymupdf` after a deprecation warning.

### Corpus growth

- Corpus is now 12 documents (8 original + 4 found by following citations
  inside the existing documents).
- Method: the 2025 leave summary cites four source OMs by file number and
  date; I located each on the DoPT circulars portal.

### Scanned documents and OCR

- 1 of 12 documents is a scan (2019 leave encashment for contract officers):
  1 character extracted across 2 pages by direct text extraction.
- Ran Tesseract 5.5.3 OCR at 300 dpi: 3,029 characters recovered.
- Observed OCR error: "DoPT" read as "DoPI". This would break a search for
  "DoPT". Added a documented correction in the cleaning step. The raw OCR
  output is kept unchanged in data/text.
- Limitation: other OCR errors may exist. I have not yet measured the OCR
  error rate.
- Known issue: re-running extract.py overwrites OCR output with empty text,
  so ocr.py must be run after it. To be merged later.

### Text cleaning

- clean.py removes the browser print header and footer (date/time line,
  repeated title, "about:blank", page numbers).
- Effect: for example 41,157 to 39,883 characters in the 13-page LTC order
  (about 3 percent removed).
- Not fixed: the misplaced rates table, table cells split across lines, and
  stray "**\*\***" lines.
- Limitation: the script deletes any line that is only a fraction like
  "3/4", which could remove real content in other documents.

### Amendment chain found

- The 2019 order (14028/1/2019-Estt.(L)) says contract-officer leave terms
  come from a 1985 OM, amended by OMs of 1990, 1999 and 2011. The
  encashment cap rose from 180 to 240 to 300 days.
- A system that retrieves only the 1985 order would give an outdated
  answer. This is the failure case the project will measure.
- The older OMs (1985, 1990, 1999, 2011) are not yet in the corpus and are
  candidates to download.

### Next steps

- Run text extraction on all documents and check OCR output by eye.
- Load documents into MySQL.
- Collect more amendment pairs and write evaluation questions.
