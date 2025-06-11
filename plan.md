### ✅ 1. **\[40 pts] Build an App with KBs**

> Build an app that uses `CREATE KNOWLEDGE_BASE`, `INSERT INTO`, `SELECT ... WHERE`, and `CREATE INDEX`.

**How we align:**

* App creates a KB called `codebase_kb` via `CREATE KNOWLEDGE_BASE`.
* Uses `INSERT INTO codebase_kb (...)` for ingesting parsed code files.
* Queries via `SELECT * FROM codebase_kb WHERE content = '<query>'`.
* Creates an index to optimize search: `CREATE INDEX ON codebase_kb`.

**Action Items:**

* ✅ Write a Python/Golang script to do all 4 operations.
* ✅ Wrap them in CLI commands: `kb:init`, `kb:ingest`, `kb:query`, `kb:index`.

---

### ✅ 2. **\[10 pts] Use Metadata Columns**

> Use `metadata_columns` and combine them in `WHERE` clauses with semantic queries.

**How we align:**

* Each code chunk inserted will include metadata like:

  * `filepath`, `language`, `function_name`, `repo`, `last_modified`.

**Action Items:**

* ✅ In your `INSERT INTO`, declare `metadata_columns=('filepath', 'language', ...)`.
* ✅ Demo hybrid queries like:

  ```sql
  SELECT * FROM codebase_kb
  WHERE content = 'oauth validation'
  AND language = 'Python'
  AND filepath LIKE '%/auth/%';
  ```

---

### ✅ 3. **\[10 pts] Integrate JOBS**

> Use `CREATE JOB` to automate ingestion from an external source.

**How we align:**

* We'll create a job that syncs the latest changes from a GitHub repo (or local mirror) and re-ingests any changed code.

**Action Items:**

* ✅ Use:

  ```sql
  CREATE JOB repo_sync
  RUN SELECT * FROM github_code_view
  INSERT INTO codebase_kb;
  ```
* ✅ OR write a script that updates a SQL view and schedule the job with `EVERY 6 HOURS`.

---

### ✅ 4. **\[10 pts] Use AI Tables or Agents**

> Pipe semantic query results into an AI Table for classification/summarization.

**How we align:**

* Take retrieved code snippets and pass them to an AI Table that classifies their purpose (e.g., `auth`, `payment`, `network`).

**Action Items:**

* ✅ Create an AI Table:

  ```sql
  CREATE TABLE code_purpose_model AS
  SELECT content, classify(content) AS purpose
  FROM codebase_kb;
  ```
* ✅ Use this in semantic queries with filters:

  ```sql
  SELECT * FROM codebase_kb
  WHERE content = 'logging setup'
  AND purpose = 'infrastructure';
  ```

---

### ✅ 5. **\[30 pts] Upload a Video + Write a Great README**

> Demo your app + include setup and instructions in README.

**How we align:**

* Short video showing:

  * Code ingestion
  * Query demo
  * Metadata filtering
  * Job-based ingestion
  * AI Table-based classification
* README will include:

  * Setup (Python + MindsDB)
  * How to use each command
  * Architecture diagram
  * Example KB query output

**Action Items:**

* ✅ Record video (CLI screen capture)
* ✅ Write a clean `README.md` + diagram
* ✅ Add query logs (e.g., `queries_per_minute.csv`) to show stress testing

---

### ✅ 6. **\[5 pts] Document the Process**

> Publish a blog post (Medium, Dev.to, etc.) showing the app and practical uses.

**Action Items:**

* ✅ Write a technical blog titled *"Building a Semantic Code Navigator with MindsDB KBs"*

  * Introduce problem → tool → KB → AI Table → stress results
  * Link GitHub repo + video demo

---

### ✅ 7. **\[5 pts] Submit Product Feedback**

> Fill [Product Feedback Form](https://quira-org.typeform.com/to/magewvh9) and suggest ideas to MindsDB.

**Action Items:**

* ✅ Mention any issues faced (e.g., slow re-indexing, LLM throttling)
* ✅ Suggest: “Batch reranking evaluation”, “Chained AI Table pipelines”, etc.

---

### ✅ 8. **\[20 pts] Project Quality Bonus**

> Awarded by MindsDB team based on:

* Usefulness
* UX polish
* Creativity
* Stress testing depth

**How to maximize:**

* Run query benchmarks:

  * `qps`: Queries per second
  * `avg/p95 latency`
  * Error rate under 1000+ concurrent queries
* Log:

  * Total records indexed
  * KB size (e.g., 10k functions from 3 repos)
* Create visual dashboard (optional)

---

### ✅ 9. **\[up to \$100] Bug Hunt & Stress Test Reports**

> Create:

* 🐞 Bug reports
* 📊 Benchmarking reports
* 🔥 Stress test writeups
* 🧠 Reranking evaluations

**Action Items:**

* ✅ Simulate 1K+ semantic queries via script, document latency.
* ✅ Push to 50K+ KB entries, note performance drop-off.
* ✅ Create report: Google Doc or PDF with graphs.
* ✅ Submit multiple if needed: performance, failure mode, reranker insights.

---

### 🏁 Summary Table

| Criteria                            | Points      | Covered? | Action Needed           |
| ----------------------------------- | ----------- | -------- | ----------------------- |
| Build with KBs                      | 40          | ✅        | Done via CLI+KB         |
| Metadata columns                    | 10          | ✅        | Use filepath/lang       |
| Jobs                                | 10          | ✅        | Ingest sync job         |
| AI Tables / Agents                  | 10          | ✅        | Add purpose classifier  |
| Video + README                      | 30          | ✅        | Record demo + write doc |
| Document Process (Blog)             | 5           | ✅        | Write article           |
| Product Feedback                    | 5           | ✅        | Submit Typeform         |
| Project Quality (bonus)             | 20          | ✅        | Optimize + polish UX    |
| Bug/Benchmark/Stress/Rerank reports | up to \$400 | ✅        | Write & submit reports  |

---