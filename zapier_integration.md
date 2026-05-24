# Zapier Integration Guide

AI Freight Request Automation — external email processing via Zapier.

---

## Pipeline Overview

```
Gmail (New Email)
  → Filter by Zapier
  → ChatGPT (GPT-4o)
  → Code by Zapier (JS)
  → Google Sheets
```

---

## Step-by-Step Setup

### Step 1 — Gmail Trigger
- App: **Gmail**
- Event: **New Email**
- Account: your freight inbox

### Step 2 — Filter by Zapier

Only continues if email matches freight-related keywords:

| Condition | Field | Rule |
|-----------|-------|------|
| Continue if | Body Text | Contains `quote` |
| Or continue if | Subject | Contains `shipment` |
| And | Subject | Contains `freight` |

### Step 3 — ChatGPT (OpenAI)
- App: **ChatGPT (OpenAI)**
- Model: `gpt-4o`
- Instructions:

```
You are a freight logistics AI. Extract and classify freight requests.
Return ONLY this exact JSON, no backticks, no markdown, no extra fields:
{
  "request_type": "Quote",
  "origin": "Manila",
  "destination": "Dubai",
  "quantity": "500kg",
  "priority": "High",
  "department": "Sales",
  "recommended_action": "Provide shipment quote",
  "confidence_score": 0.95
}

request_type must be: Quote, Issue, or Follow-up
priority must be: High or Medium
department must be: Sales or Operations
```

### Step 4 — Code by Zapier (Run Javascript)
- App: **Code by Zapier**
- Event: **Run Javascript**

**Input Data:**
| Variable | Value |
|----------|-------|
| `gpt_response` | Step 3: Messages Content Text |

**Code:**
```javascript
const raw = inputData.gpt_response
  .replace(/```json/g, "")
  .replace(/```/g, "")
  .trim();

const data = JSON.parse(raw);

output = {
  shipment_details: `Origin: ${data.origin} | Destination: ${data.destination} | Qty: ${data.quantity}`,
  request_type:       data.request_type,
  priority:           data.priority,
  department:         data.department,
  recommended_action: data.recommended_action,
  confidence_score:   String(data.confidence_score)
};
```

> Note: Use `output =` not `return` — required syntax in Zapier Code steps.

### Step 5 — Google Sheets
- App: **Google Sheets**
- Event: **Create Spreadsheet Row**

**Column Mapping:**
| Sheet Column | Maps To |
|-------------|---------|
| Message | Step 1: Body Plain |
| Quote | Step 4: `request_type` |
| Shipment Details | Step 4: `shipment_details` |
| Priority | Step 4: `priority` |
| Department | Step 4: `department` |
| Recommended Action | Step 4: `recommended_action` |
| Confidence Score | Step 4: `confidence_score` |
| Status | `New` (static text) |

---

## Output Example

| Field | Value |
|-------|-------|
| Message | hi I need an urgent quote for 500kg from Manila to Dubai |
| Quote | Quote |
| Shipment Details | Origin: Manila \| Destination: Dubai \| Qty: 500kg |
| Priority | High |
| Department | Sales |
| Recommended Action | Provide shipment quote |
| Confidence Score | 0.95 |
| Status | New |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `undefined` values in Step 4 | Code step not tested yet | Go to Step 4 → Test tab → Test step |
| Raw JSON in Shipment Details | Step 5 mapped to Step 3 instead of Step 4 | Re-map to Step 4: `shipment_details` |
| Wrong Quote column value | GPT returning wrong JSON structure | Fix Step 3 prompt — ensure exact JSON format |
| `request_type` not in dropdown | Step 4 output not refreshed | Re-test Step 4 first, then re-open Step 5 |

---

*Part of the AI Freight Request Automation project by robdev37*
