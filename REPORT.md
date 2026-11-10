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

### MySQL setup

- Created database `govrule` (utf8mb4) and a project-only user with access
  to that database alone, instead of using root.
- Table `documents`: doc_id, filename, ref_no, issue_date, is_scanned,
  extraction_method, full_text.
- Loaded all 12 cleaned documents. Character counts in MySQL match the
  cleaning output exactly, so no text was lost in loading.
- Database password is entered at run time (getpass) and never stored in
  the repo.
- Limitation: ref_no is a rough guess (first line starting with "No"), and
  for portal files it is the portal number, not the real file number.
  To be improved when building the amendment layer.

### Next steps (updated)

- Write 20 to 25 evaluation questions by hand (simple lookups plus
  "which version is current?" questions).
- Build keyword-search baseline and measure it.
- Find failure cases, then add the amendment layer and re-measure.

## Day 3 log

### Evaluation set (v1)

- 14 questions drafted with AI assistance. Every answer was checked by me
  against the source document before use.
- 12 lookup questions, 1 audience question, 2 "which version is current"
  questions (types overlap in rows 13 and 14).

### Baseline: BM25 keyword search over 12 documents

- Original run: Top-1 10/14.
- Question correction made after seeing results: rows 2 and 3 do not name
  an audience, so both the central and the AIS incentive orders are valid
  answers. Both are now accepted. Corrected: Top-1 11/14.
- Top-3 is 14/14 but is not informative with only 12 documents.

### Baseline failures (3)

1. Row 1: question asks about central government employees, but search
   returned the AIS incentive order. The two orders are almost word-for-word
   identical, so keyword matching cannot separate audiences.
2. Row 6: search returned the 2023 study leave order instead of the 2024
   consolidated order, which contains the "2 months" rule.
3. Row 13: search returned the older 2023 order instead of the 2024
   consolidated order.

### Limitations

- Many questions reuse document wording, which favours keyword search, so
  11/14 is probably optimistic. Plan: add paraphrased questions.
- Row 14 cannot truly fail yet, because the older 1985, 1990 and 1999 orders
  are not in the corpus.
- Only 12 documents and 14 questions, so results are counts, not
  percentages, and show failure modes rather than general performance.
