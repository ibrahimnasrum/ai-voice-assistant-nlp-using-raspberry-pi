FYP Malaysia Retail Chain Data Pack (Synthetic)
=============================================

This pack includes:
1) data/        : structured datasets (sales + HR)
2) docs/        : unstructured documents for RAG (Malaysia-flavoured)
3) images/      : sample table screenshots + charts for visual input demo
4) ground_truth : CSV outputs used as ground truth to verify answers

Datasets:
- Sales: MY_Retail_Sales_2024H1.csv (synthetic, RM currency, Malaysia states/branches)
- HR   : MY_Retail_HR_Employees.csv (synthetic, Malaysia states/branches)

Generated months:
- Latest sales month: 2024-06
- Previous sales month: 2024-05

Suggested demo questions (text):
- "sales bulan ni berapa?"
- "banding sales bulan ni vs bulan lepas"
- "top 3 product bulan 2024-06"
- "sales ikut state bulan 2024-06"
- "sales ikut branch bulan 2024-06"
- "headcount ikut state"
- "attrition rate ikut state"
- "average monthly income ikut department"

Suggested demo questions (visual):
- Upload images/sales_state_kpi_2024-06.png and ask: "summarize table ini"
- Upload images/hr_attrition_by_state.png and ask: "which state has highest attrition?"

Notes:
- Entire pack is synthetic and created for academic FYP demo. No real PII.
