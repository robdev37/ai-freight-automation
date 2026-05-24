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

> Emails must match at least one condition group to pass through the filter.

### Step 3 — ChatGPT (OpenAI)
- App: **ChatGPT (OpenAI)**
- Model: `gpt-4o`
- Instructions:
```
You are a freight logistics AI. Extract and classify freight requests.
Return ONLY this exact JSON structure, no backticks, no markdown:
{
  "request_type": "Quote|Issue|Follow-up",
  "origin": "city or Unknown",
  "destination": "city or Unknown",
  "quantity": "amount or Unknown",
  "priority": "High|Medium",
  "department": "Sales|Operations",
  "recommended_action": "short action",
  "confidence_score": 0.0
}
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

return {
  shipment_details: `Origin: ${data.origin} | Destination: ${data.destination} | Qty: ${data.quantity}`,
  request_type:        data.request_type,
  priority:            data.priority,
  department:          data.department,
  recommended_action:  data.recommended_action,
  confidence_score:    String(data.confidence_score)
};
```

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
| Timestamp | Step 4: (auto) |

---

## Output Example

| Field | Value |
|-------|-------|
| Shipment Details | Origin: Manila \| Destination: Dubai \| Qty: 500kg |
| Priority | High |
| Department | Sales |
| Recommended Action | Provide shipment quote |
| Confidence Score | 0.95 |

---

*Part of the AI Freight Request Automation project by robdev37*
