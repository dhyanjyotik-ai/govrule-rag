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
