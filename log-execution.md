```bash
sudo systemctl start postgresql
```

```sql
CREATE DATABASE dummy_ecommerce;
```

```bash
psql -U postgres -d dummy_ecommerce -f table-creation.sql
psql -U postgres -d dummy_ecommerce -f data-seeding.sql
```

```bash
python3 -m venv venv
source venv/bin/activate
which pip # check if pip pointed to venv 
pip install psycopg2-binary
pip install pandas
pip install tqdm
pip install scipy
python xprmt.py
python analysis.py
pip freeze > requirements.txt
```

```bash
psql -U postgres -d dummy_ecommerce
```

```sql 
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE status = 'completed'
  AND order_date >= NOW() - INTERVAL '30 days';

EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE order_date >= NOW() - INTERVAL '30 days'
  AND status = 'completed';
```


```sql
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE status = 'completed'
  AND customer_id = 106;

EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE customer_id = 106
  AND status = 'completed';
```

```sql
CREATE INDEX idx_orders_customer_id
ON orders(customer_id);
ANALYZE orders;
```