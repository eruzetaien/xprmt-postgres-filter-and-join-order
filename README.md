# SQL Filter Predicate and Join Order Experiment in PostgreSQL

## Background

This experiment was conducted to investigate whether:

1. The order of filter predicates in the `WHERE` clause affects query performance.
2. The order of tables in `JOIN` operations affects query performance.

The database system used was PostgreSQL without any additional indexes. All tables were scanned sequentially.

Initially, my hypothesis was:

> SQL is a declarative language, therefore the textual order of predicates and joins should not matter because the optimizer should determine the execution strategy independently from the query writing order.

---

# Database Schema

The experiment used a simple ecommerce schema:

- customers
- orders
- products
- order_items

No foreign keys or indexes were defined.

---

# Experiment Setup

## Filter Predicate Experiment

Two logically equivalent queries were tested repeatedly:

### Query A

```sql
SELECT COUNT(*)
FROM orders
WHERE customer_id = X
  AND status = 'completed';
```

### Query B

```sql
SELECT COUNT(*)
FROM orders
WHERE status = 'completed'
  AND customer_id = X;
```

The experiment was repeated 100 times using different `customer_id` values.

The execution order between Query A and Query B was randomized with a deterministic random seed to minimize cache bias.

---

## Join Order Experiment

Two logically equivalent join queries were tested repeatedly:

### Query A

```sql
SELECT COUNT(*)
FROM products p
JOIN order_items oi
    ON oi.product_id = p.product_id
JOIN orders o
    ON o.order_id = oi.order_id
JOIN customers c
    ON c.customer_id = o.customer_id;
```

### Query B

```sql
SELECT COUNT(*)
FROM customers c
JOIN orders o
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON oi.order_id = o.order_id
JOIN products p
    ON p.product_id = oi.product_id;
```

The experiment was also repeated 100 times with randomized execution order.

---

# Statistical Testing

A paired t-test was used for both experiments.

## Null Hypothesis (H0)

The execution order does not affect execution time.

## Alternative Hypothesis (H1)

The execution order affects execution time.

Significance level:

```text
α = 0.05
```

---

# Results

## Filter Predicate Experiment

```text
T-statistic : -37.165234641113045
P-value     : 5.888950107269085e-60
Reject H0 → significant difference detected
```

## Join Order Experiment

```text
T-statistic : 0.63895747219867
P-value     : 0.5243261791579176
Fail to reject H0 → no significant difference
```

---

# Observations

## Predicate Reordering Behavior

Initially, the experiment used:

```sql
WHERE status = 'completed'
  AND order_date >= NOW() - INTERVAL '30 days'
```

and its reversed version.

Using `EXPLAIN ANALYZE`, PostgreSQL consistently normalized the predicate order internally. The execution plan always displayed:

```text
(status = ...)
AND
(order_date >= ...)
```

regardless of the order written by the user.

This suggests that PostgreSQL performs predicate normalization or internal predicate reordering for this type of expression.

---

## Equality Predicate Case

The experiment was later changed to:

```sql
WHERE customer_id = X
  AND status = 'completed'
```

and its reversed form.

In this case, PostgreSQL appeared to preserve the textual order of predicates inside the execution plan.

The query where `customer_id = X` appeared first consistently performed slightly better.

Since `customer_id = X` is highly selective while `status = 'completed'` is not selective, this suggests that PostgreSQL may evaluate predicates sequentially during row filtering.

This behavior resembles lazy evaluation or short-circuit evaluation:

- highly selective predicates eliminate rows earlier
- later predicates are evaluated less frequently

However, both queries still used the same overall execution strategy:

```text
Parallel Seq Scan
```

No indexes were involved.

Therefore, the observed difference likely exists at the executor level rather than at the optimizer planning level.

---

# Join Order Observation

For the join experiment, the statistical test failed to reject the null hypothesis.

This suggests that PostgreSQL successfully optimized the join operations independently from the textual order written by the user.

The execution plans remained effectively equivalent across both queries.

This behavior aligns with the declarative nature of SQL and PostgreSQL's cost-based optimizer.

---

# Conclusion

The experiment produced mixed results.

## Filter Predicate Order

The filter predicate experiment detected statistically significant execution time differences.

The evidence suggests:

- PostgreSQL may internally reorder some predicate types
- predicate evaluation order can still influence execution time during sequential scans
- highly selective predicates evaluated earlier may slightly improve performance

However:

- the differences were relatively small
- the overall execution plan remained identical
- no indexes were involved

Therefore, the effect appears to occur mainly during predicate evaluation inside the executor rather than from major optimizer strategy differences.

---

## Join Order

The join order experiment showed no statistically significant difference.

This supports the hypothesis that PostgreSQL's optimizer treats joins declaratively and can rearrange join execution independently from the textual query order.

---

# Final Interpretation

This experiment suggests that:

- join order generally does not matter in PostgreSQL for logically equivalent queries
- filter predicate order can produce measurable differences in sequential scan scenarios, especially when predicate selectivity differs significantly
- PostgreSQL still preserves the declarative nature of SQL at the optimizer level, even if small executor-level effects remain observable