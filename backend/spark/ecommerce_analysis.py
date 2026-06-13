from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal

import psycopg
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col,
    countDistinct,
    current_timestamp,
    date_trunc,
    dense_rank,
    lit,
    sum as spark_sum,
    when,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="E-commerce sales and inventory analysis")
    parser.add_argument("--jdbc-url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--driver", default="org.opengauss.Driver")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = (
        SparkSession.builder.appName("ecommerce-sales-inventory-analysis")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    jdbc_options = {
        "url": args.jdbc_url,
        "user": args.user,
        "password": args.password,
        "driver": args.driver,
    }

    products = read_table(spark, jdbc_options, "products")
    orders = read_table(spark, jdbc_options, "orders")
    order_items = read_table(spark, jdbc_options, "order_items")

    valid_orders = orders.filter(col("status") != lit("cancelled"))
    fact = (
        order_items.alias("oi")
        .join(valid_orders.alias("o"), col("oi.order_id") == col("o.id"), "inner")
        .join(products.alias("p"), col("oi.product_id") == col("p.id"), "inner")
        .select(
            col("o.id").alias("order_id"),
            col("o.order_time"),
            col("p.id").alias("product_id"),
            col("p.name").alias("product_name"),
            col("p.category"),
            col("oi.quantity"),
            col("oi.line_total"),
        )
    )

    generated_at = datetime.utcnow()

    daily_sales = [
        (
            row["sales_date"],
            int(row["order_count"]),
            int(row["item_count"]),
            to_decimal(row["sales_amount"]),
            generated_at,
        )
        for row in (
            fact.groupBy(date_trunc("DAY", col("order_time")).alias("sales_date"))
            .agg(
                countDistinct("order_id").alias("order_count"),
                spark_sum("quantity").alias("item_count"),
                spark_sum("line_total").alias("sales_amount"),
            )
            .orderBy("sales_date")
            .collect()
        )
    ]

    product_rank_window = Window.orderBy(col("sales_amount").desc(), col("quantity_sold").desc())
    product_sales = [
        (
            int(row["product_id"]),
            row["product_name"],
            row["category"],
            int(row["quantity_sold"]),
            to_decimal(row["sales_amount"]),
            int(row["rank_no"]),
            generated_at,
        )
        for row in (
            fact.groupBy("product_id", "product_name", "category")
            .agg(
                spark_sum("quantity").alias("quantity_sold"),
                spark_sum("line_total").alias("sales_amount"),
            )
            .withColumn("rank_no", dense_rank().over(product_rank_window))
            .orderBy("rank_no")
            .collect()
        )
    ]

    category_sales = [
        (
            row["category"],
            int(row["quantity_sold"]),
            to_decimal(row["sales_amount"]),
            generated_at,
        )
        for row in (
            fact.groupBy("category")
            .agg(
                spark_sum("quantity").alias("quantity_sold"),
                spark_sum("line_total").alias("sales_amount"),
            )
            .orderBy(col("sales_amount").desc())
            .collect()
        )
    ]

    inventory_alerts = [
        (
            int(row["product_id"]),
            row["product_name"],
            row["category"],
            int(row["current_stock"]),
            int(row["safety_stock"]),
            row["alert_level"],
            generated_at,
        )
        for row in (
            products.select(
                col("id").alias("product_id"),
                col("name").alias("product_name"),
                col("category"),
                col("current_stock"),
                col("safety_stock"),
                when(col("current_stock") <= col("safety_stock") * lit(0.5), lit("critical"))
                .when(col("current_stock") <= col("safety_stock"), lit("warning"))
                .otherwise(lit("normal"))
                .alias("alert_level"),
            )
            .filter(col("alert_level") != lit("normal"))
            .orderBy(col("alert_level").asc(), col("current_stock").asc())
            .collect()
        )
    ]

    write_results(args, daily_sales, product_sales, category_sales, inventory_alerts)
    print(
        "analysis completed: "
        f"{len(daily_sales)} daily rows, "
        f"{len(product_sales)} product rows, "
        f"{len(category_sales)} category rows, "
        f"{len(inventory_alerts)} inventory alerts"
    )
    spark.stop()


def read_table(spark: SparkSession, jdbc_options: dict[str, str], table: str):
    return spark.read.format("jdbc").options(**jdbc_options).option("dbtable", table).load()


def to_decimal(value) -> Decimal:
    return Decimal(str(value or "0")).quantize(Decimal("0.01"))


def write_results(
    args: argparse.Namespace,
    daily_sales: list[tuple],
    product_sales: list[tuple],
    category_sales: list[tuple],
    inventory_alerts: list[tuple],
) -> None:
    conninfo = jdbc_to_psycopg_conninfo(args.jdbc_url, args.user, args.password)
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM analysis_daily_sales")
            cur.execute("DELETE FROM analysis_product_sales")
            cur.execute("DELETE FROM analysis_category_sales")
            cur.execute("DELETE FROM analysis_inventory_alerts")

            cur.executemany(
                """
                INSERT INTO analysis_daily_sales
                    (sales_date, order_count, item_count, sales_amount, generated_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                daily_sales,
            )
            cur.executemany(
                """
                INSERT INTO analysis_product_sales
                    (product_id, product_name, category, quantity_sold, sales_amount, rank_no, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                product_sales,
            )
            cur.executemany(
                """
                INSERT INTO analysis_category_sales
                    (category, quantity_sold, sales_amount, generated_at)
                VALUES (%s, %s, %s, %s)
                """,
                category_sales,
            )
            cur.executemany(
                """
                INSERT INTO analysis_inventory_alerts
                    (product_id, product_name, category, current_stock, safety_stock, alert_level, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                inventory_alerts,
            )


def jdbc_to_psycopg_conninfo(jdbc_url: str, user: str, password: str) -> str:
    prefixes = ("jdbc:opengauss://", "jdbc:postgresql://")
    prefix = next((item for item in prefixes if jdbc_url.startswith(item)), None)
    if prefix is None:
        raise ValueError(f"Unsupported JDBC URL: {jdbc_url}")
    host_port_db = jdbc_url[len(prefix) :]
    host_port, database = host_port_db.split("/", 1)
    if ":" in host_port:
        host, port = host_port.split(":", 1)
    else:
        host, port = host_port, "5432"
    return f"host={host} port={port} dbname={database} user={user} password={password}"


if __name__ == "__main__":
    main()
