# 📊 Data Warehouse - Expert Guide

<div align="center">

**Master Data Warehouses: structured analytics and business intelligence**

[![Data Warehouse](https://img.shields.io/badge/Data%20Warehouse-Analytics-blue?style=for-the-badge)](./)
[![BI](https://img.shields.io/badge/BI-Business%20Intelligence-green?style=for-the-badge)](./)
[![ETL](https://img.shields.io/badge/ETL-Processing-orange?style=for-the-badge)](./)

*Comprehensive guide to data warehouses: architecture, design, and implementation*

</div>

---

## 🎯 Data Warehouse Fundamentals

<div align="center">

### What is a Data Warehouse?

**A data warehouse is a centralized repository of integrated data from multiple sources, designed for query and analysis.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📊 Structured Data** | Organized, cleaned, transformed |
| **🔒 Schema-on-Write** | Schema defined before loading |
| **📈 OLAP** | Online Analytical Processing |
| **🔄 ETL** | Extract, Transform, Load |
| **📉 Denormalized** | Optimized for queries |

**Mental Model:** Think of a data warehouse like a library - books (data) are organized by category (schema), indexed (optimized), and easy to find (query).

</div>

---

## 📚 Core Concepts

<div align="center">

### Q1: What is a Data Warehouse and why is it used?

**A:** A data warehouse is a centralized repository that stores integrated data from multiple sources for analytics and reporting.

**Why Use Data Warehouses:**

1. **Business Intelligence:** Support decision-making
2. **Historical Analysis:** Long-term data storage
3. **Performance:** Optimized for analytical queries
4. **Data Integration:** Combine data from multiple sources
5. **Consistency:** Single source of truth

**Key Benefits:**
- ✅ Fast analytical queries
- ✅ Historical data analysis
- ✅ Data integration
- ✅ Business intelligence support
- ✅ Optimized for reporting

---

### Q2: What is the difference between OLTP and OLAP?

**A:**

| Aspect | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|:---:|:---:|:---:|
| **Purpose** | Transaction processing | Analytics, reporting |
| **Data** | Current, detailed | Historical, aggregated |
| **Operations** | INSERT, UPDATE, DELETE | SELECT (read-heavy) |
| **Schema** | Normalized | Denormalized |
| **Users** | Operational users | Analysts, executives |
| **Performance** | Fast writes | Fast reads |
| **Example** | E-commerce orders | Sales reports |

**OLTP Example:**
```sql
-- Transactional database
INSERT INTO orders (user_id, product_id, quantity) 
VALUES (123, 456, 2);

UPDATE users SET balance = balance - 100 WHERE id = 123;
```

**OLAP Example:**
```sql
-- Analytical query
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as revenue,
    COUNT(*) as orders
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY month
ORDER BY month;
```

---

### Q3: What is the difference between Data Warehouse and Database?

**A:**

| Aspect | Database | Data Warehouse |
|:---:|:---:|:---:|
| **Purpose** | Transaction processing | Analytics |
| **Data** | Current, operational | Historical, analytical |
| **Schema** | Normalized | Denormalized |
| **Operations** | CRUD operations | Read-heavy |
| **Optimization** | Fast writes | Fast reads |
| **Users** | Applications | Analysts |

**Database:**
- Supports applications
- Current data
- Normalized schema
- Fast transactions

**Data Warehouse:**
- Supports analytics
- Historical data
- Denormalized schema
- Fast queries

---

### Q4: What are the key components of a Data Warehouse architecture?

**A:**

**Core Components:**

1. **Data Sources:**
   - Operational databases
   - External sources
   - Files, APIs

2. **ETL Layer:**
   - Extract data
   - Transform data
   - Load into warehouse

3. **Storage Layer:**
   - Staging area
   - Data warehouse
   - Data marts

4. **Metadata Layer:**
   - Data dictionary
   - ETL metadata
   - Business metadata

5. **Access Layer:**
   - BI tools
   - SQL queries
   - Reporting tools

**Architecture:**
```
┌─────────────┐
│ Data Sources│ ← Operational DBs, Files
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ETL Layer  │ ← Extract, Transform, Load
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Staging   │ ← Temporary storage
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Warehouse │ ← Integrated data
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Data Marts │ ← Department-specific
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  BI Tools   │ ← Reporting, Analytics
└─────────────┘
```

---

### Q5: What is ETL (Extract, Transform, Load)?

**A:** ETL is the process of moving data from source systems to a data warehouse.

**ETL Process:**

1. **Extract:**
   - Pull data from sources
   - Databases, files, APIs
   - Full or incremental

2. **Transform:**
   - Clean data
   - Validate data
   - Aggregate data
   - Apply business rules

3. **Load:**
   - Load into warehouse
   - Update existing data
   - Maintain history

**Example:**
```python
# Extract
source_data = extract_from_database("orders_db")

# Transform
cleaned_data = clean_data(source_data)
aggregated_data = aggregate_by_month(cleaned_data)
validated_data = validate(aggregated_data)

# Load
load_to_warehouse(validated_data, "sales_fact")
```

**ETL Tools:**
- Informatica
- Talend
- Apache Airflow
- AWS Glue
- Azure Data Factory

---

### Q6: What is a Star Schema?

**A:** Star schema is a data warehouse design with a central fact table and dimension tables.

**Components:**

1. **Fact Table:**
   - Central table
   - Contains measures (metrics)
   - Foreign keys to dimensions

2. **Dimension Tables:**
   - Descriptive attributes
   - Textual data
   - Hierarchies

**Example:**
```
Fact Table: sales_fact
  - sale_id
  - date_id (FK)
  - product_id (FK)
  - customer_id (FK)
  - quantity
  - amount

Dimension Tables:
  - dim_date (date_id, date, month, year)
  - dim_product (product_id, name, category)
  - dim_customer (customer_id, name, region)
```

**Benefits:**
- ✅ Simple queries
- ✅ Fast performance
- ✅ Easy to understand
- ✅ Optimized for analytics

---

### Q7: What is a Snowflake Schema?

**A:** Snowflake schema is a normalized version of star schema with normalized dimension tables.

**Difference from Star Schema:**

**Star Schema:**
- Denormalized dimensions
- Flat dimension tables

**Snowflake Schema:**
- Normalized dimensions
- Hierarchical dimension tables

**Example:**
```
Star Schema:
dim_product
  - product_id
  - name
  - category_name
  - supplier_name

Snowflake Schema:
dim_product
  - product_id
  - name
  - category_id (FK)

dim_category
  - category_id
  - category_name
  - supplier_id (FK)

dim_supplier
  - supplier_id
  - supplier_name
```

**Trade-offs:**
- ✅ Less storage (normalized)
- ❌ More joins (slower queries)
- ❌ More complex

---

### Q8: What is a Fact Table?

**A:** Fact table contains measurable, quantitative data about business events.

**Characteristics:**

1. **Measures:** Numeric values (sales, quantity)
2. **Foreign Keys:** Links to dimension tables
3. **Grain:** Level of detail (transaction, daily, monthly)

**Types of Facts:**

1. **Additive:** Can be summed (sales amount)
2. **Semi-Additive:** Can be summed across some dimensions (balance)
3. **Non-Additive:** Cannot be summed (ratios, percentages)

**Example:**
```sql
CREATE TABLE sales_fact (
    sale_id BIGINT PRIMARY KEY,
    date_id INT,
    product_id INT,
    customer_id INT,
    store_id INT,
    quantity INT,           -- Additive
    amount DECIMAL(10,2),   -- Additive
    discount DECIMAL(10,2), -- Additive
    FOREIGN KEY (date_id) REFERENCES dim_date,
    FOREIGN KEY (product_id) REFERENCES dim_product,
    FOREIGN KEY (customer_id) REFERENCES dim_customer,
    FOREIGN KEY (store_id) REFERENCES dim_store
);
```

---

### Q9: What is a Dimension Table?

**A:** Dimension table contains descriptive attributes for analyzing facts.

**Characteristics:**

1. **Textual Data:** Names, descriptions
2. **Hierarchies:** Year → Quarter → Month → Day
3. **Slowly Changing:** Attributes change over time

**Types of Dimensions:**

1. **Conformed Dimensions:** Shared across data marts
2. **Junk Dimensions:** Miscellaneous attributes
3. **Degenerate Dimensions:** Stored in fact table

**Example:**
```sql
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10,2),
    created_date DATE,
    updated_date DATE
);
```

---

### Q10: What is Slowly Changing Dimension (SCD)?

**A:** SCD handles changes to dimension data over time.

**Types:**

**SCD Type 1:**
- Overwrite old value
- No history
- Simple

**SCD Type 2:**
- Create new record
- Maintain history
- Most common

**SCD Type 3:**
- Add new column
- Limited history
- Current + previous

**Example - SCD Type 2:**
```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    customer_id INT,
    name VARCHAR(255),
    address VARCHAR(255),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN
);

-- Customer moves
INSERT INTO dim_customer VALUES 
(1, 123, 'John', 'Old Address', '2024-01-01', '2024-06-30', FALSE),
(2, 123, 'John', 'New Address', '2024-07-01', NULL, TRUE);
```

---

### Q11: What is Data Mart?

**A:** Data mart is a subset of a data warehouse focused on a specific business area.

**Types:**

1. **Dependent Data Mart:** Built from data warehouse
2. **Independent Data Mart:** Built directly from sources
3. **Hybrid Data Mart:** Combination

**Data Mart vs Data Warehouse:**

| Aspect | Data Warehouse | Data Mart |
|:---:|:---:|:---:|
| **Scope** | Enterprise-wide | Department-specific |
| **Size** | Large (TB-PB) | Smaller (GB-TB) |
| **Users** | Multiple departments | Single department |
| **Data** | Comprehensive | Focused |

**Example:**
```
Data Warehouse
  ├── Sales Data Mart
  ├── Marketing Data Mart
  └── Finance Data Mart
```

---

### Q12: What is the difference between Inmon and Kimball approaches?

**A:**

**Inmon Approach (Top-Down):**
- Enterprise data warehouse first
- Normalized design
- Data marts built from warehouse
- Single source of truth

**Kimball Approach (Bottom-Up):**
- Data marts first
- Star schema design
- Warehouse = union of marts
- Faster implementation

**Comparison:**

| Aspect | Inmon | Kimball |
|:---:|:---:|:---:|
| **Design** | Normalized | Denormalized |
| **Approach** | Top-down | Bottom-up |
| **Time** | Longer | Faster |
| **Complexity** | Higher | Lower |
| **Flexibility** | More flexible | Less flexible |

---

### Q13: What are the best practices for Data Warehouse design?

**A:**

**Best Practices:**

1. **Dimensional Modeling:**
   - Use star/snowflake schema
   - Separate facts and dimensions
   - Conformed dimensions

2. **ETL Design:**
   - Incremental loads
   - Data quality checks
   - Error handling

3. **Performance:**
   - Indexing
   - Partitioning
   - Materialized views

4. **Data Quality:**
   - Validation rules
   - Data profiling
   - Monitoring

5. **Documentation:**
   - Data dictionary
   - ETL documentation
   - Business rules

---

### Q14: What cloud data warehouses are available?

**A:**

**Major Platforms:**

1. **Amazon Redshift:**
   - Columnar storage
   - MPP architecture
   - SQL interface

2. **Google BigQuery:**
   - Serverless
   - Petabyte-scale
   - Pay per query

3. **Snowflake:**
   - Cloud-native
   - Separation of storage/compute
   - Multi-cloud

4. **Azure Synapse Analytics:**
   - Integrated analytics
   - Spark + SQL
   - Data lake integration

**Comparison:**

| Platform | Architecture | Pricing Model |
|:---:|:---:|:---:|
| **Redshift** | Cluster-based | Per hour |
| **BigQuery** | Serverless | Per query |
| **Snowflake** | Cloud-native | Per compute hour |
| **Synapse** | Integrated | Per hour |

---

### Q15: How to implement incremental loading in ETL?

**A:**

**Strategies:**

1. **Timestamp-Based:**
   - Track last update timestamp
   - Extract records after timestamp

2. **Change Data Capture (CDC):**
   - Track changes in source
   - Extract only changed records

3. **Hash Comparison:**
   - Compare hash values
   - Extract changed records

**Example - Timestamp-Based:**
```python
def incremental_load():
    # Get last load timestamp
    last_load = get_last_load_timestamp("sales")
    
    # Extract new/changed records
    new_records = extract_from_source(
        "sales",
        filter=f"updated_at > '{last_load}'"
    )
    
    # Transform
    transformed = transform(new_records)
    
    # Load
    load_to_warehouse(transformed)
    
    # Update timestamp
    update_last_load_timestamp("sales", datetime.now())
```

---

## 🎯 Advanced Topics

<div align="center">

### Data Warehouse Patterns

**ETL Patterns:**
- Full load
- Incremental load
- CDC (Change Data Capture)

**Modeling Patterns:**
- Star schema
- Snowflake schema
- Fact constellation

**Architecture Patterns:**
- Hub and spoke
- Data vault
- Inmon vs Kimball

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Data Warehouse Purpose** | Structured analytics and BI |
| **Schema-on-Write** | Schema defined before loading |
| **ETL Process** | Extract, Transform, Load |
| **Star Schema** | Fact table + dimension tables |
| **SCD** | Handle dimension changes |

**💡 Remember:** Data warehouses are optimized for analytical queries. Use dimensional modeling (star schema), proper ETL processes, and incremental loading for optimal performance.

</div>

---

<div align="center">

**Master Data Warehouses for business intelligence! 🚀**

*From architecture to implementation - comprehensive guide to data warehouses.*

</div>

