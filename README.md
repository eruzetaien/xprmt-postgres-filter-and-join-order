# SQL Filter Predicate and Join Order Experiment in PostgreSQL
A comic version of this experiment is available [here](comic.pdf)

## Background

This experiment was conducted to find out whether:

1. The order of filter predicates in the `WHERE` clause affects query performance.
2. The order of tables in `JOIN` operations affects query performance.

The database system used was PostgreSQL without any additional indexes.

Initially, my hypothesis was:

> SQL is a declarative language, therefore the order of predicates and joins in a query should not matter because the optimizer should determine the most optimal execution strategy.

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
We used Python to execute this experiment, so to minimize data transfer overhead between Python and the databas, we only select the `COUNT(*)`. The experiment was repeated 100 times using different `customer_id` values. 

The execution order between Query A and Query B was randomized accross 30 different random seeds to minimize bias due to OS memory management. So we can say we have 3000 samples in total. 

---

# Statistical Testing

We applied a paired t-test using `ttest_rel()` from `SciPy` to compare the two experiments. The function computes the statistical significance of the mean differences between paired samples.
## Null Hypothesis (H0)

>The filter predicates in the `WHERE` clause does not affect execution time.

## Alternative Hypothesis (H1)

> The filter predicates in the `WHERE` clause affects execution time.

We use Significance level of
```text
α = 0.05
```
This implies a 5% risk of incorrectly rejecting the null hypothesis (Type I error).

---

# Results

## Filter Predicate Experiment

```text
T-statistic : -193.82125833117516
P-value     : 0.0
Reject H0 → significant difference detected
```

This shows that **the order of filter predicate in `WHERE` clause really matter** if we don't provide any index.

---

# Discussions

## Predicate Reordering Behavior
When we executed the `EXPLAIN` keyword to obtain query plans, we got the filter order in those two were different. The optimizer appeared to preserve the textual order of predicates inside the query plan.

From we the samples, we can clearly see that query A, where `customer_id = X` appeared first, consistently performed faster than query B. Since `customer_id = X` is highly selective while `status = 'completed'` is not selective, this suggests that the optimizer may evaluate predicates sequentially during row filtering. And because of short-circuit evaluation, query A is less likely to evaluated the later predicate, which explain why query A was faster.

The short-circuit behavior is also mentioned in [PostgreSQL 18.4 Documentation: 4.2.14. Expression Evaluation Rules](https://www.postgresql.org/docs/18/sql-expressions.html#SYNTAX-EXPRESS-EVAL)

This result may suggest that the optimizer don't reorder the predicates in `WHERE` clause at all. However, the documentation itself says that we cannot rely on the order we write in the query to be preserved during execution. This implies that the optimizer is free to reorder predicates to produce a more optimal execution plan.

Based on [PostgreSQL 18.4 Documentation: 14.1. Using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html#USING-EXPLAIN), we can conclude that optimizer generates query plan based on excution cost and selectivity. We use the same type of operation for two predicates in the experiment, so the execution cost msut be the same. But, in terms of selectivity, `customer_id` is more selective than `status`. Therefore, `customer_id` should be evaluated first to reduce the need to check `status` column condition. However, this behavior was not observed in the experiment, suggesting that selectivity may not have been considered in determining the predicate evaluation order.

From [`order_qual_clauses()`](https://github.com/postgres/postgres/blob/2c4bd2bf5700db98be0602854a8b7fa2c16b5f4a/src/backend/optimizer/plan/createplan.c#L5266) function, specifically its comments, we can infer that predicate selectivity is not considered when determining filter order. The optimizer only determines the order based on security level and execution cost.

```sql
WHERE order_date >= NOW() - INTERVAL '30 days'
  AND status = 'completed';

WHERE customer_id = EXTRACT(DAY FROM NOW())
  AND status = 'completed';
```

Here, we tried to introduce a difference in execution cost between the predicates by adding the `NOW()` function to one of the queries. As expected, the predicate involving the function was pushed later in the filter order, since it has a higher execution cost.

---

# Conclusion

This experiment suggests that PostgreSQL does not use predicate selectivity when reordering conditions in the `WHERE` clause. Instead, predicate ordering appears to be based on execution cost and security level, without considering selectivity.

This also suggests that predicates order in `WHERE` clause can still matter when predicates have similar execution cost. In such cases, PostgreSQL tends to preserve the user-defined order, meaning that the textual order of predicates may influence evaluation order and, consequently, performance characteristics.


----
### TODO: Discuss the `JOIN` part