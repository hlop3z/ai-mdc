# 🧩 **Go Modular Platform with WASM Plugins**

---

## 🌟 At a Glance: The Vision

Build dynamic, high-performance SaaS platforms with **unprecedented flexibility and robust multi-tenancy**. Our schema-first orchestration engine empowers you to:

- **Leverage a minimalist Go orchestrator** for core operations and lightning-fast startups.
- **Extend capabilities with hot-swappable Rust-to-WASM plugins** for secure, high-performance business logic.
- **Implement Rhai scripts** for rapid, on-the-fly logic changes, executed within a Rust-based WASM engine.
- **Maintain JSON as the universal contract**, ensuring cohesion across schemas, logic, and UI.

> **Model once, deploy everywhere** — your entire system, from data structures to business logic and user interfaces, driven by declarative JSON.

---

## 🎯 Core Problem & Solution

Traditional monolithic or tightly-coupled microservice architectures often struggle with rapid iteration, isolated deployments, and true multi-tenant customization.

Our platform offers a **modular, headless "business operating system"** that directly addresses these challenges:

- **Swap complex business logic modules (WASM plugins) like LEGOs.**
- **Orchestrate services and data flow with the robustness of Go.**
- **Achieve fine-grained control and rapid iteration** for custom features and tenant-specific needs, all while ensuring **strong data isolation** for multi-tenant environments.

---

## ⚙️ How It Works: Architecture Overview

Our system revolves around a central Go orchestrator that manages plugins, scripts, and data, all governed by a unified JSON schema system.

### **Multi-Tenant Structure**

The Go-based host manages a **central "management database"**, much like AWS handles identity. A **superuser** can create new users, but each user must also provide an **organization ID** to log in, ensuring explicit association with a specific tenant (organization).

**Each organization is fully isolated:**

- It possesses its **own dedicated Postgres and S3/MinIO instances**.
- **No data, storage, or query access is shared** across tenants.
- Even if the same user (e.g., an admin) exists in multiple organizations, their sessions and access remain strictly isolated.

The **only shared layer is the authentication console**, akin to the AWS Console. This central portal allows users to:

- Log in and create organizations.
- Initialize and connect projects.
- Manage users and resources.

Once an organization is set up, all runtime behavior — including data access and function execution — is **scoped entirely to that tenant’s isolated environment**.

We **auto-generate most CRUD operations** directly from the schema, keeping input/output methods minimal. The system is designed for safe extensibility via:

- **Reusable CTE-based queries** for custom logic or aggregations.
- **Fine-grained methods** for critical financial operations (e.g., rollbacks, tax calculations).
- **Secure query composition**, where system-level filters (e.g., `AND org_id = ?`) are automatically injected to sandbox user queries, preventing cross-tenant data exposure.

This architecture ensures business logic remains **stateless, modular, and secure**, while giving tenants the freedom to define their own flows within their isolated environments.

---

### System Services Interaction

The Go orchestrator interacts with essential persistent services:

```text
┌──────────────────────────────────────────────────────────────┐
│      External System & Data Persistence                      │
│ ┌──────────────┐   (Defines/Validates)   ┌─────────────────┐ │
│ │ Orchestrator │────────────────────────>│ Schema Registry │ │
│ │    (Go)      │                         │  (PostgreSQL)   │ │
│ └───────┬──────┘                         └───────┬─────────┘ │
│         │ (Loads/Executes)                       │           │
│         │                                        │           │
│         │ (Plugins Register Schemas)             │           │
│         │                                        │           │
│         ▼                                        │           │
│ ┌───────────────────┐                            │           │
│ │   Plugin Store    │<───────────────────────────┘           │
│ │  (MinIO/S3-like)  │ (Stores WASM & Manifests)              │
│ │ (Versioned WASM)  │                                        │
│ └───────────────────┘                                        │
└──────────────────────────────────────────────────────────────┘
```

- **Schema Registry (PostgreSQL):** The single source of truth for all JSON schemas defining data models, APIs, and plugin contracts.
- **Plugin Store (MinIO/S3):** Stores versioned WASM plugin artifacts and their descriptive manifests.

### Internal Orchestrator Components

The Go orchestrator manages these key internal modules:

```text
┌────────────────────────────┐
│     Orchestrator (Go)      │
│ ┌──────────────────────┐   │
│ │   Schema Management  │   |◄─ Consumed by UI, Plugins, Scripts
│ └──────────────────────┘   │   │
│ ┌──────────────────────┐   │   │
│ │ Plugin Runtime (WASM)│   │   │
│ │ (Powered by Wasmer)  │   │   │
│ └──────────────────────┘   │   │   ┌─────────────────────┐
│ ┌──────────────────────┐   │   │   │ Declarative UI      │
│ │ Rhai Scripting Engine│   │   └───┤ (e.g., Preact/TSX)  │
│ │ (Runs Rhai in WASM)  │   │       │ (Renders via Schema)│
│ └──────────────────────┘   │       └─────────────────────┘
└────────────────────────────┘
```

---

## 💎 Core Data Types (Schema Primitives)

| Name         | Go Type                            | PostgreSQL Type                   | Notes                                          |
| :----------- | :--------------------------------- | :-------------------------------- | :--------------------------------------------- |
| **Ref**      | `struct { ID int64 }` (example)    | `INTEGER`/`BIGINT` → `REFERENCES` | Represents a foreign key relationship.         |
| **ID**       | `int64` (or `string` for opaque)   | `BIGSERIAL PRIMARY KEY`           |                                                |
| **UUID**     | `uuid.UUID`                        | `UUID`                            |                                                |
| **Int**      | `int32`                            | `INTEGER`                         |                                                |
| **Int64**    | `int64`                            | `BIGINT`                          |                                                |
| **Float**    | `float64`                          | `DOUBLE PRECISION`                |                                                |
| **Decimal**  | `string` (for arbitrary precision) | `NUMERIC(precision, scale)`       | Handled as string in Go to preserve precision. |
| **String**   | `string`                           | `VARCHAR(n)`                      |                                                |
| **Text**     | `string`                           | `TEXT`                            |                                                |
| **Boolean**  | `bool`                             | `BOOLEAN`                         |                                                |
| **Base64**   | `[]byte`                           | `BYTEA`                           | Binary data encoded as Base64.                 |
| **DateTime** | `time.Time` (UTC)                  | `TIMESTAMP WITH TIME ZONE`        | Always stored and processed in UTC.            |
| **Date**     | `time.Time` (date part only)       | `DATE`                            |                                                |
| **Time**     | `time.Time` (time part only)       | `TIME WITH TIME ZONE`             |                                                |
| **Dict**     | `map[string]interface{}`           | `JSONB`                           | Flexible key-value store.                      |
| **List**     | `[]interface{}`                    | `JSONB`                           | Flexible ordered collection.                   |

---

## 🌐 Virtual ORM & Declarative Data Modeling

Our platform employs a **minimal, declarative DSL (Domain Specific Language)**, akin to a "virtual ORM," to define data models and their relationships. This system, though not a full Object-Relational Mapper in the traditional sense, deterministically generates database schemas and provides rich metadata for cross-language code generation.

This approach ensures:

- **Convention-based naming** for association tables in many-to-many relationships, simplifying schema understanding.
- **Automatic SQL generation** from high-level Python-like definitions.
- **Custom JSON annotations** that enrich the schema, enabling auto-generation of data-populating code across various programming languages (e.g., Python, JavaScript/TypeScript). This is crucial for enabling frontend developers, analytics, and custom external automation with consistent data structures.

### 🧩 Minimal Declarative DSL (Auto-Naming Join Table)

Define your entities and relationships concisely:

```python
model = Model(plugin="accounts")

# Relationships
@model(
    docs="User DB Table",
    unique_together=[("name", "email")]
)
class User:
    name = String(max_length=255)
    email = String(max_length=255)


@model()
class Project:
    name = String(unique=True)
    description = String()
    no_longer_used = String(deprecated="deprecation reason.")

# Relationships
many_to_many("accounts.User", "accounts.Project", back_populates=["projects", "users"])
```

---

#### Optional: Allow Custom Name Override and Additional Metadata

For more granular control or to add specific metadata to the join table:

```python
@many_to_many("accounts.User", "accounts.Project", table_name="project_membership", back_populates=["projects", "users"])
class ProjectUser:
    role =  String()
    joined_at= Datetime(auto_now=True)
```

---

### 🧠 Join Table Auto-Naming Rule

Our convention for `many-to-many` association tables:

> Sort entity names alphabetically and generate as:
> `lowercase(entityA)__lowercase(entityB)__link`

For example:

- `many_to_many(User, Project)` &rarr; `project__user__link`
- `many_to_many(Tag, Product)` &rarr; `product__tag__link`

---

### 🔄 Auto-Generated SQL

The declarative definitions are compiled into robust SQL, ready for execution. For the `User` and `Project` relationship, this would generate:

```sql
CREATE TABLE project_user_link (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (user_id, project_id)
);
```

---

## Auto-Generated Database Schemas / Models

All models automatically include 4 built-in fields for consistency and auditability:

- `ID`: Primary key, auto-incrementing.
- `created_at`: UTC datetime, automatically filled on creation.
- `updated_at`: UTC datetime, automatically filled on creation/update.
- `deleted_at`: UTC datetime, automatically filled on soft-delete operations.

### CRUD System Overview

Our schema-driven approach auto-generates core CRUD operations, allowing developers to focus on custom business logic.

**CUD Operations (Single & Batched):**

- `create`
- `update`
- `delete` (hard delete)
- `remove` (soft delete)

**Read Operations:**

- `detail`: Fetch one row using `user_query + system_query`
- `filter`: Fetch many rows (paginated) using `user_query + system_query`

---

## 🔩 Key Capabilities

| Feature             | Description                                                                                           | Performance Aspect  |
| :------------------ | :---------------------------------------------------------------------------------------------------- | :------------------ |
| **Lean Kernel**     | `O(1)` Go startup; secure, multi-tenant WASM runtime via Wasmer.                                      | `O(1)` startup      |
| **Schema-Driven**   | JSON-first for data validation, contract evolution, API generation, and UI rendering.                 | `O(n)` validation   |
| **Hot-Swap Logic**  | Dynamically load, version, and replace Rust/WASM plugins at runtime without service downtime.         | `O(1)` load/swap    |
| **Plugin Interop**  | Plugins securely invoke each other via `host.invoke("plugin.module.function")`, mediated by the host. | `O(1)` dispatch     |
| **Agile Scripting** | Update business rules with Rhai scripts without recompiling WASM plugins.                             | Fast interpretation |
| **Event-Driven**    | Trigger workflows based on defined event sequences (e.g., DAGs) or state changes.                     | `O(1)` dispatch     |
| **Adapters/Hooks**  | Extend lifecycle events and connect to third-party services seamlessly.                               | Flexible            |

---

## 🔄 Lifecycle Flow: From Model to Execution

1. **Model**: Define entities, intents, and workflows declaratively using JSON schemas in the Schema Registry.
2. **Develop**: Create business logic as Rust functions, compile to WASM, and define a `plugin.json` manifest.
3. **Deploy**: Upload WASM plugins and manifests to the Plugin Store. The Orchestrator can hot-swap them.
4. **Boot**: Start the Go orchestrator – low memory footprint, optimized for fast cold starts.
5. **Invoke**: Execute plugin logic directly via `host.invoke()` or trigger execution through event-driven workflows.
6. **Adapt**: Introduce or modify fine-grained business rules using Rhai scripts, or customize via adapters, without full redeployments.

---

## 🔌 Plugin Design: Rust → WASM Modules

Plugins are self-contained, versioned units of business logic, compiled from Rust to WASM for portability, performance, and security.

### Standardized Entry & Communication

All WASM plugins expose a consistent C-ABI function for host interaction, using JSON for input/output.

```rust
// #[no_mangle] pub extern "C" fn run(ptr: *const u8, len: usize) -> i32 { ... }
// Simplified conceptual flow:
fn handle_request(json_input: &str) -> Result<String, String> {
    // 1. Deserialize input from host (JSON)
    let request: PluginRequest = serde_json::from_str(json_input)?;
    // 2. Route to appropriate internal function
    let response_payload = match request.action.as_str() {
        "create_invoice" => handle_create_invoice(request.payload),
        "get_invoice_status" => handle_get_invoice_status(request.payload),
        _ => return Err("Unsupported action".to_string()),
    };
    // 3. Execute logic & Serialize output (JSON)
    serde_json::to_string(&response_payload).map_err(|e| e.to_string())
}
```

### Plugin-to-Plugin Communication (Host Mediated)

The Go host manages calls between plugins (`host.invoke`):

- Validates ACLs and tenant permissions.
- Checks memoization cache (based on manifest).
- Meters the call (observability).
- Routes to the target plugin.
- Returns the result (JSON) to the caller plugin.

This ensures safety, observability, and isolation, simulating shared services securely.

### Plugin Manifest (`plugin.json`)

Each plugin includes a manifest for discovery, schema definition, function exposure, caching hints, and UI guidance.
Plugins that use `internal` that are developed by 3rd parties must be approved by us.

```json
{
  "name": "finance",
  "version": "1.0.2",
  "internal": false, // is it a plugin for the `internal-system` or the `users`
  "description": "Handles invoicing and tax calculations.",
  "tags": ["finance", "billing", "invoice", "tax"],
  "dependencies": ["account.user", "sales.tax"],

  "modules": {
    // Publicly callable functions: host.invoke('finance.invoice.create_invoice', payload)
    "invoice": {
      "create_invoice": {
        "cacheable": false, // Do not cache response
        "timeout_ms": 500 // Max execution time in ms
      },
      "get_invoice_details": {
        "cacheable": true, // Response can be cached
        "cache_ttl_sec": 3600 // Cache duration in seconds (1 hour)
      }
    },
    "tax": {
      "calculate_tax": {
        "cacheable": true,
        "cache_ttl_sec": 86400 // Cache for 1 day
      }
    }
  },

  // Reusable value sets
  "enums": {
    "demo_enum": {
      "value1": "Human-readable Label 1",
      "value2": "Human-readable Label 2"
    }
  },

  // Global Reusable input structures
  "input": {
    "Pagination": {
      /*...*/
    }
  },

  // Global return types and SQL schema definitions
  "types": {
    // Invoice schema
    "Invoice": {
      /*...*/
    }
  },

  // UI configuration hints
  "ui": {
    "components": ["InvoiceEditorForm", "InvoiceStatusBadge"],
    "views": {
      "invoice": {
        "component": "InvoiceView",
        // Search Query Params
        "query": {
          "id": "ID"
        }
      }
    }
  }
}
```

---

## ✍️ Lightweight Scripting with Rhai

The Rhai scripting engine, running within its own sandboxed WASM module, enables dynamic logic modification:

- **Rapid Customization:** Embed or update business rules, transformations, or simple workflows without recompiling core WASM plugins. Ideal for tenant-specific adjustments or A/B testing.
- **Safe Execution:** Scripts run in a secure, sandboxed environment with tenant-scoped contexts and resource limits.
- **JSON Native:** Seamlessly manipulate JSON data passed to and from scripts, interacting with the plugin ecosystem.
- **Minimal Host API:** Scripts use a curated set of host functions, ensuring stability and security.

---

## 🔐 Security & Observability by Design

| Feature               | Purpose                                                                                             |
| :-------------------- | :-------------------------------------------------------------------------------------------------- |
| **WASM Sandboxing**   | Strict memory and capability isolation for plugins via Wasmer runtime.                              |
| **Tenant Isolation**  | Enforce memory, CPU, and resource quotas per-tenant for plugins and scripts.                        |
| **RBAC/ABAC**         | Fine-grained RBAC/ABAC for plugin invocation, data access, and administrative functions.            |
| **Audit Logs**        | Immutable, traceable history of all significant operations, invocations, and configuration changes. |
| **Metrics & Traces**  | Per-plugin, per-script, and per-tenant observability via OpenTelemetry.                             |
| **Structured Errors** | Consistent, localized, and detailed error objects for robust debugging and monitoring.              |

---

## 🌐 Declarative UI Engine: Extending Schemas to the Frontend

Leverage the schema-first paradigm to drive the presentation layer:

- **Schema-Driven UI Generation**: Dynamically render forms, tables, and other UI components directly from the JSON schemas defining your data models and plugin manifests.
- **Reusable UI Components**: Develop a library of presentation components (e.g., using TSX with Preact or SolidJS) that map to schema types, structures, and UI hints from plugin manifests.
- **Decoupled & Consistent Frontend**: The UI consumes declarative definitions, keeping frontend logic focused on presentation. Business logic remains in backend plugins, ensuring a consistent user experience driven by shared schemas.

---

## ✨ Key Benefits & Differentiators

| Benefit                     | Impact                                                                                                    |
| :-------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **Accelerated Iteration**   | Deploy new features and logic as plugins or scripts instantly, without core system downtime or rebuilds.  |
| **Unmatched Modularity**    | Business logic is encapsulated in independent, versioned WASM plugins, like "LEGOs for your backend."     |
| **Robust Isolation**        | Secure multi-tenancy with resource quotas, RBAC/ABAC, and strong WASM sandboxing for plugins and scripts. |
| **Composable by Design**    | Declaratively mix and match plugins, scripts, and event-driven workflows to build complex applications.   |
| **Schema-Centric Cohesion** | JSON schemas ensure consistency across data, APIs, plugin contracts, and even UI generation.              |
| **High Performance**        | Go orchestrator, Rust/WASM plugins, and Rhai offer efficient execution for demanding workloads.           |
| **Reduced Vendor Lock-in**  | Core logic in portable WASM & Rhai, with declarative JSON contracts, promotes platform agnosticism.       |
| **Enhanced Testability**    | Isolate and test plugins as pure functions; mock host interactions for comprehensive unit testing.        |

---

## 💡 Core Design Principles

- **Hexagonal Architecture (Ports & Adapters)**: Clear separation of core, plugins, scripts, and external services.
- **Composition over Inheritance**: Build functionality by combining independent, focused units.
- **Declarative Configuration**: Define _what_ (via JSON schemas/manifests), not _how_.
- **Portability First**: WASM, JSON, and Rhai ensure logic runs across diverse environments.
- **Performance by Design**: Focus on optimal complexity for core operations (e.g., `O(1)` dispatch).
- **Secure by Default**: Principle of least privilege for host APIs exposed to plugins/scripts.

---

## ✅ Development Best Practices

- **Stateless & Idempotent Plugins**: Design plugins to be stateless; operations should be idempotent where possible.
- **Explicit Naming & Versioning**: Use clear, hierarchical naming and robust versioning for plugins, schemas, and modules.
- **Metadata-Driven Behavior**: Leverage plugin manifests for declarative control over runtime behaviors (caching, timeouts).

---

## Tech-Stack

| Component              | Choice               | Pros                                                                |
| :--------------------- | :------------------- | :------------------------------------------------------------------ |
| **S3**                 | MinIO                | S3-compatible, easy to self-host, great for on-prem or hybrid-cloud |
| **SQL**                | Postgres             | Rock-solid, rich features (JSONB, extensions), scalable             |
| **NoSQL**              | MongoDB              | Flexible JSON docs, good for unstructured data                      |
| **In-Memory Cache**    | Redis                | Fast, pub/sub support, TTL, persistence                             |
| **Search**             | Elasticsearch        | Powerful, mature, real-time search                                  |
| **Message Broker**     | RabbitMQ             | Reliable, mature, supports complex routing                          |
| **Monitoring/Logging** | Prometheus + Grafana | Best-in-class observability stack, extensible                       |
