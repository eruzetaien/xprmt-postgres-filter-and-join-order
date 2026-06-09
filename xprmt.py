import psycopg2
import time
import pandas as pd
import random
import os
from tqdm import tqdm


random_seed = 106
# rng = random.Random(random_seed)


os.makedirs("results", exist_ok=True)


conn = psycopg2.connect(
    dbname="dummy_ecommerce",
    user="postgres",
    password="postgres",
    host="localhost"
)

cur = conn.cursor()


def run_query(query):
    start = time.perf_counter()

    cur.execute(query)
    cur.fetchall()

    elapsed_seconds = time.perf_counter() - start

    return elapsed_seconds


def run_filter_experiment(random_seed):
    seeds = [random_seed + i for i in range(30)]
    total_experiment = 100

    total = len(seeds) * total_experiment

    with tqdm(total=total, desc="Filter experiment") as pbar:
        results = []
        for seed in seeds:
            rng = random.Random(seed)

            for customer_id in range(1, total_experiment + 1):

                query_a = f"""
                SELECT COUNT(*)
                FROM orders
                WHERE customer_id = {customer_id}
                AND status = 'completed'
                """

                query_b = f"""
                SELECT COUNT(*)
                FROM orders
                WHERE status = 'completed'
                AND customer_id = {customer_id}
                """

                if rng.random() < 0.5:
                    t_a = run_query(query_a)
                    t_b = run_query(query_b)
                    order = "A_then_B"
                else:
                    t_b = run_query(query_b)
                    t_a = run_query(query_a)
                    order = "B_then_A"

                results.append((customer_id, order, t_a, t_b))
                pbar.update(1)

    df = pd.DataFrame(
        results,
        columns=[
            "customer_id",
            "execution_order",
            "time_a",
            "time_b"
        ]
    )

    df.to_csv(
        "results/filter_order_results.csv",
        index=False,
        mode="w"
    )

    print("Saved → results/filter_order_results.csv")


def run_join_experiment(rng):
    results = []

    query_a = """
    SELECT COUNT(*)
    FROM products p
    JOIN order_items oi
        ON oi.product_id = p.product_id
    JOIN orders o
        ON o.order_id = oi.order_id
    JOIN customers c
        ON c.customer_id = o.customer_id;
    """

    query_b = """
    SELECT COUNT(*)
    FROM customers c
    JOIN orders o
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON oi.order_id = o.order_id
    JOIN products p
        ON p.product_id = oi.product_id;
    """

    for i in tqdm(range(100), desc="Join experiment"):

        if rng.random() < 0.5:
            t_a = run_query(query_a)
            t_b = run_query(query_b)
            order = "A_then_B"
        else:
            t_b = run_query(query_b)
            t_a = run_query(query_a)
            order = "B_then_A"

        results.append((i, order, t_a, t_b))

    df = pd.DataFrame(
        results,
        columns=[
            "run_id",
            "execution_order",
            "time_a",
            "time_b"
        ]
    )

    df.to_csv(
        "results/join_order_results.csv",
        index=False,
        mode="w"
    )

    print("Saved → results/join_order_results.csv")


# MAIN
if __name__ == "__main__":
    run_filter_experiment(16)
    # run_join_experiment()