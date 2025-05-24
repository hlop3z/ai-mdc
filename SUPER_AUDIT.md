# 📋 Core Audit Request

**Objective:**  
Quickly evaluate the system’s core to identify its building blocks, extension points, and fit with proven design patterns—then recommend how to keep it minimal, modular, maintainable, and enterprise-ready.

---

## 🎯 Goals

1. **Fundamental Components**
2. **Abstraction & Extension Points**
3. **Design Pattern Fit**

**Targets:** Modularity · Maintainability · Enterprise Readiness · Minimal Footprint · Easy Embedding

---

## 🔍 Focus Areas

### 1. Critical vs. Optional Logic

- “Must-have” behaviors → Core
- “Nice-to-have” features → Plug-ins/Add-ons

### 2. Core ⇄ Extension Separation

- Clear API boundaries
- Deployment-independent modules

### 3. Coupling & Cohesion

- Spot tight couplings → Propose decoupling
- Ensure high internal cohesion

### 4. Principles Alignment

- **Modularity** · **SoC** · **DRY** · **KISS** · **YAGNI** · **Fail-Fast**

---

## 🧩 Pattern Recommendations

| Pattern                    | When to Use                           | Trade-Offs (Time/Space)      |
| -------------------------- | ------------------------------------- | ---------------------------- |
| **Microkernel**            | Lightweight core + pluggable services | Higher orchestration cost    |
| **Ports & Adapters**       | Clear boundaries for external systems | Boilerplate adapters         |
| **Event-Driven / Pub-Sub** | Loose coupling, async workflows       | Potential for message storms |

> **Summary:**
>
> - Microkernel for a truly minimal core.
> - Hexagonal (Ports & Adapters) for testable boundaries.
> - Pub-Sub where decoupled async flows are needed.

---

## 📁 Context & Artifacts

- **Core Code:** `<repo/path or URL>`
- **Architecture Docs:** `<link>`
- **Extension Schemas:** `<specs or contracts>`

---

## 🧠 Optional Lenses

- Declarative vs. Imperative
- Convention-Over-Configuration
- Interface-First (schema-driven)
- Time & Space Complexity hotspots

---

## ✅ Deliverable

A concise report or inline comments covering:

1. **Key Findings**
2. **Refactoring & Modularization Proposals**
3. **Pattern Suggestions**
4. **Risks & Anti-Patterns**

> _Keep feedback **brief**, **actionable**, and **technology-agnostic**._
