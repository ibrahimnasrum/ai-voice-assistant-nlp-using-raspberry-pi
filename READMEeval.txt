FYP Auto Evaluation Pack
=======================

Files in this ZIP:
- questions.csv
- run_auto_eval.py
- README.txt

What this does:
- Runs your assistant function (rag_query_ui or multimodal_query) for every question
- Repeats for each Ollama model you specify
- Saves:
  1) results_raw.csv     (all outputs + latency + errors)
  2) results_summary.csv (avg latency + error rate per model/category)  [needs pandas]

Step-by-step (Windows):
-----------------------
1) Put both files somewhere easy, e.g.:
   C:\Users\User\eval\questions.csv
   C:\Users\User\eval\run_auto_eval.py

2) Update the visual image paths (optional):
   - Open questions.csv
   - Edit image_path for V01..V05 to your real image files.

3) Run:
   conda activate burger
   python C:\Users\User\eval\run_auto_eval.py ^
     --assistant "C:\Users\User\oneclick_my_retailchain_v2_models_logging.py" ^
     --questions "C:\Users\User\eval\questions.csv" ^
     --outdir "C:\Users\User\eval\out" ^
     --models llama3:latest mistral:latest qwen2.5:7b ^
     --repeat 1

Notes:
------
- KPI categories (sales_kpi/hr_kpi) should NOT depend on model: good sign your routing is correct.
- RAG + visual will vary by model: use this for comparison.

Manual scoring:
--------------
For RAG/visual quality, open results_raw.csv and add:
  human_label = Correct / Partial / Wrong / Hallucination
Then compute accuracy % per model.

If you want, you can extend the runner to auto-score KPI (exact numeric match) after you define expected answers.
