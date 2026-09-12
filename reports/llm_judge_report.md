# Secondary LLM-as-a-Judge Evaluation Report

**Evaluation Status:** `UNAVAILABLE`  
**Judge Role:** `SECONDARY_QUALITATIVE_SIGNAL`  
**Judge Model:** `gemini-2.5-flash`  
**Prompt Version:** `v1.0.0-trust-gated-eval`  
**Cases Evaluated:** `0`  

## Critical Methodological Disclaimer
This qualitative LLM-as-a-judge layer provides an ancillary, advisory signal and **NEVER** replaces, alters, or overrides the primary deterministic golden-set evaluation or human expert annotations. Deterministic accuracy, safety interception rates, and frozen ground truth remain the sole primary authorities.

### Operational Notice
The LLM Judge was marked **UNAVAILABLE** because `Live LLM judge API call failed: LLM Judge API HTTP error 429: {
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-2.5-flash\nPlease retry in 467.069948ms.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Gemini API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-2.5-flash"
            },
            "quotaValue": "20"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "0s"
      }
    ]
  }
}
`.
In accordance with production integrity rules, no synthetic, mock, or fabricated scores were generated.
To run live LLM judging, configure the `GEMINI_API_KEY` environment variable with valid provider credentials.
