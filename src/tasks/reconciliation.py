# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Parameters
dbutils.widgets.text("catalog", "rch-dbx-dev-catalog")
dbutils.widgets.text("schema", "analytics")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

# DBTITLE 1,Create budget_alloted table with dummy data
# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE `${catalog}`.`${schema}`.budget_alloted AS
# MAGIC SELECT * FROM VALUES
# MAGIC   ('Marketing',    2026, 'Q1', CAST(500000.00 AS DECIMAL(18,2)), CAST(450000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Marketing',    2026, 'Q2', CAST(500000.00 AS DECIMAL(18,2)), CAST(480000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Engineering',  2026, 'Q1', CAST(800000.00 AS DECIMAL(18,2)), CAST(750000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Engineering',  2026, 'Q2', CAST(800000.00 AS DECIMAL(18,2)), CAST(800000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Sales',        2026, 'Q1', CAST(600000.00 AS DECIMAL(18,2)), CAST(550000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Sales',        2026, 'Q2', CAST(600000.00 AS DECIMAL(18,2)), CAST(300000.00 AS DECIMAL(18,2)), 'PENDING',   current_timestamp(), current_timestamp()),
# MAGIC   ('HR',           2026, 'Q1', CAST(300000.00 AS DECIMAL(18,2)), CAST(280000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('HR',           2026, 'Q2', CAST(300000.00 AS DECIMAL(18,2)), CAST(150000.00 AS DECIMAL(18,2)), 'PENDING',   current_timestamp(), current_timestamp()),
# MAGIC   ('Operations',   2026, 'Q1', CAST(400000.00 AS DECIMAL(18,2)), CAST(400000.00 AS DECIMAL(18,2)), 'APPROVED',  current_timestamp(), current_timestamp()),
# MAGIC   ('Operations',   2026, 'Q2', CAST(400000.00 AS DECIMAL(18,2)), CAST(0.00     AS DECIMAL(18,2)), 'DRAFT',     current_timestamp(), current_timestamp())
# MAGIC AS t(department, fiscal_year, quarter, budget_amount, alloted_amount, status, created_at, updated_at)

# COMMAND ----------

# DBTITLE 1,Verify data
# MAGIC %sql
# MAGIC SELECT * FROM `${catalog}`.`${schema}`.budget_alloted ORDER BY department, quarter

# COMMAND ----------

print("xixixixixi")
print("xixixixixi")
print("xixixixixi")
print("xixixixixi")
print("xixixixixi")