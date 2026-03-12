# ListingGen Pro

**ListingGen Pro** is an AI-powered workflow designed for cross-border e-commerce sellers to automatically generate high-quality product listings (Title / Bullet Points / Description) from structured product data.  

The goal of this project is to transform AI from a one-off content generator into a **controllable, reusable, and scalable production pipeline**, reducing manual copywriting costs and improving consistency across listings.

---

## Background & Motivation

In real-world cross-border e-commerce operations, creating product listings is often a repetitive and labor-intensive task.

Common problems include:
- High manual copywriting cost
- Inconsistent writing style across products
- Low efficiency when handling large SKU volumes
- Unstable results when using AI in a single-call manner

**ListingGen Pro** was built to address these issues by engineering the listing creation process into a structured AI workflow that can be reused, extended, and maintained.

---

## What Problems Does It Solve?

- ❌ Manual listing writing is slow and hard to scale  
  → ✅ Batch generation using structured prompts and workflows  

- ❌ One-off AI calls are unstable and unpredictable  
  → ✅ Provider abstraction with retry and timeout handling  

- ❌ AI-generated content is hard to reuse  
  → ✅ Structured outputs (CSV / TXT) ready for platform upload    

---

## Core Workflow

The system follows a clear and extensible pipeline:

Structured Product Data (CSV / Fields)
↓
Prompt Rendering & Task Splitting
↓
AI Batch Generation (Title / Bullets / Description)
↓
Retry & Validation Handling
↓
Structured Output (CSV / TXT)


This workflow is designed to support real listing scenarios such as Amazon, TikTok Shop, and independent e-commerce websites.

---

## Project Structure

The project adopts a modular architecture to separate responsibilities and improve maintainability:

- `provider`  
  Handles LLM API calls, including timeout and retry logic

- `engine`  
  Orchestrates task execution and workflow control

- `types`  
  Defines core data structures and typing

- `renderer`  
  Builds prompts and renders AI input content

- `output / exporter`  
  Formats and exports generated results

This structure allows easy replacement of models or extension of new task types in the future.

---

## Tech Stack

- Python  
- LLM API (Volcengine Ark)  
- CSV / File Processing  
- Modular Engineering Design (separation of concerns, error handling)

---

## Current Status

**Completed**
- Basic listing generation pipeline
- Task splitting for Title / Bullets / Description
- Retry and timeout handling for AI calls
- Structured output formats
- Business-oriented README documentation

**Planned**
- More fine-grained content validation rules
- Image + copy generation linkage (AI + PS workflow)
- Simple CLI or UI interface
- Support for additional platforms and templates

---

## Typical Use Cases

- Amazon product listing content generation  
- TikTok Shop product pages  
- Independent e-commerce product detail pages  

---

## Notes

This project focuses on **practical business scenarios** rather than pure algorithm research.  
The emphasis is on building AI systems that can be reliably used in real production environments.
