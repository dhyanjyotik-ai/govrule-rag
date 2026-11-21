# Experiment 2: Retrieval and Question Answering over Assam Public Service Commission Notices

This is a small personal study built from public documents. It is not an official project of the Commission, and no candidate data is used.

## 1. Question

Public recruitment advertisements are often changed by later notices: a postponement, a stay ordered by a court, an addendum that adds posts, a corrigendum that removes a vacancy. A question such as "When is the screening test?" can have an old answer in one notice and a current answer in another.

This study asks two things:

1. Can a simple search find the right notice, and can a language model answer correctly from it?
2. Does grouping all notices of the same advertisement (in date order) help, compared with giving the model only the top search results?

## 2. Data

- 31 public documents downloaded from the Commission's website by the author: 12 advertisements (numbers 07, 12, 13, 17, 18, 22, 26, 30, 31, 33, 34 and 35 of 2025) and their later notices, addenda and corrigenda.
- Five advertisements (07, 12, 22, 31, 33) have real changes over time.
- Documents containing lists of candidates or roll numbers were excluded. The original PDFs are not stored in this repository.
- Each document is listed in `data/apsc/catalog.csv`: advertisement number, type, date and post. The column `changes_earlier_notice` is an answer key used only for checking; the system never reads it.
- The date of each notice is taken from the file name.

## 3. Method

1. **Reading the pages (OCR).** Every page is turned into an image at 300 dpi and read with Tesseract 5.5.3. All pages are read the same way because the text layers inside the PDFs contain errors.
2. **Search.** BM25, a keyword-scoring method, over the full text of each notice.
3. **Answering.** Claude Haiku 5.5 answers from the retrieved notices and must say "Not found in the provided notices" when the answer is missing.
4. **Two modes.**
   - Plain: the three best-matching notices, labelled only "Notice 1, 2, 3", with no dates added.
   - Amendment-aware: the same three, plus every other notice of the same advertisement numbers, in date order with the date written on each, and an instruction that a later notice overrides an earlier one.
5. **Scoring.** Retrieval and answering are scored separately.

## 4. Question set

17 questions, written from the PDFs, each with a reference answer and the source notices: 9 about facts that changed over time, 3 stable facts, 3 table questions, 1 question needing several notices, 1 question whose answer is not in the documents.

The reference answers for the table questions (6, 12, 16, 17) were checked against page images. The 31/2025 screening test date and paper timings (question 1) were checked by the author against the PDF. The other reference answers were read from clean text.

## 5. Results

### Search only (31 notices, 16 questions with a right notice)

| Measure                   | OCR version 1 | OCR version 2 |
| ------------------------- | ------------- | ------------- |
| Right notice ranked first | 13 of 16      | 13 of 16      |
| Right notice in top three | 15 of 16      | 15 of 16      |
| Main notice ranked first  | 12 of 16      | 12 of 16      |

### Answers (17 questions)

|               | Plain search      | Amendment-aware          |
| ------------- | ----------------- | ------------------------ |
| OCR version 1 | 14 right, 3 wrong | 16 right, 1 wrong        |
| OCR version 2 | 15 right, 2 wrong | 16 right, 1 partly right |

OCR version 1 used Tesseract page mode 6 (one plain block of text). OCR version 2 used page mode 4, found by testing four modes on one table page.

## 6. Findings

1. **Grouping notices by advertisement helped on two questions in both runs.** Question 3 (number of posts) was missed by search because the advertisement ranked fourth behind three notices that repeat the same words. Question 15 (the order of changes) needs three notices, and search returned one. Grouping supplied the missing notices.
2. **Date ordering did not visibly help.** On the questions where a newer notice overrides an older one (1, 4, 5, 9), plain mode was already correct, because the newer notice was among the top three and the model could read the dates in the text. The study does not show that date ordering fixes superseded facts.
3. **Search can rank the old notice first.** For question 4, the old 10 July notice (certificate date 03-08-2026) ranked above the new 2 September notice (17-09-2026). The model still answered correctly because both were in front of it, but search alone could not tell which is newer.
4. **OCR was the main cause of wrong answers.** With page mode 6, a table row (Mathematics and Statistics) was lost, and the model confidently stated that no subject was scheduled. Page mode 4 recovered the row and nothing that was right became wrong. Other OCR problems: a split date in a table ("27-09-" and "2026" on different lines), "II" read as "Il", and "1st August" read as "15t August", which made the model report a date mismatch that does not exist.
5. **The model refused correctly when it should.** The question about cut-off marks (not in the documents) was answered "Not found" in all four runs.

## 7. Limits

- Small: 17 questions, 31 documents, one organisation, one model.
- Two runs per mode, and model answers vary between runs, so small differences may be noise.
- The first grading pass was done by Claude. The uncertain answers were checked against the page images. Not every answer was checked by the author.
- The question set was written for documents where changes exist, so it over-represents changes.
- Reading tables with free tools is unreliable. A different OCR tool might do better.
- The results do not say anything about how the Commission works or how its notices should be written.

## 8. Files

- `src/apsc_ocr.py`, `src/apsc_ocr_v2.py`: reading the pages
- `src/apsc_load_db.py`: loading into MySQL
- `src/eval_apsc_bm25.py`: search evaluation
- `src/answer_apsc.py`: answering in both modes
- `src/ocr_table_test.py`: page mode test
- `eval/apsc_questions.csv`: questions and reference answers
- `eval/apsc_answers_graded.csv`: all answers and grades
