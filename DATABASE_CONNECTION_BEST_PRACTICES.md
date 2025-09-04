# Database Connection Management Best Practices

This document outlines the best practices for managing database connections in the user-service application.

## Connection Pooling

The application uses SQLAlchemy's connection pooling to efficiently manage database connections. Connection pooling helps reduce the overhead of creating new connections for each request and improves application performance.

### Configuration

The following environment variables control the connection pool settings:

- `DATABASE_POOL_SIZE`: The number of connections to maintain in the pool (default: 20)
- `DATABASE_MAX_OVERFLOW`: The maximum number of connections that can be created beyond the pool size (default: 30)
- `DATABASE_POOL_TIMEOUT`: The number of seconds to wait before giving up on getting a connection from the pool (default: 30)
- `DATABASE_POOL_RECYCLE`: The number of seconds after which to recreate database connections (default: 3600)

## Proper Connection Management

### Using Dependency Injection

The application uses FastAPI's dependency injection system to manage database sessions. The `get_db()` function in `app/db/database.py` provides a database session that is automatically managed:

```python
async def get_db():
    """
    Dependency to get a database session.
    
    This function provides a database session that is properly managed
    with async context management. The session is automatically closed
    when the request is completed.
    """
    async with SessionLocal() as session:
        yield session
```

### In Message Queue Consumers

For message queue consumers, we use the same SessionLocal factory to ensure consistent connection management:

```python
async with SessionLocal() as db:
    # Perform database operations
    await db.commit()  # Explicitly commit transactions
```

### Error Handling and Rollbacks

When using database sessions, always handle exceptions properly to ensure transactions are rolled back in case of errors:

```python
async with SessionLocal() as db:
    try:
        # Perform database operations
        await db.commit()
    except Exception as e:
        await db.rollback()  # Rollback on error
        raise e
```

## Best Practices

1. **Always use context managers**: Use `async with` statements to ensure connections are properly closed.

2. **Explicit transaction management**: Use `await db.commit()` to explicitly commit transactions and `await db.rollback()` to rollback on errors.

3. **Connection pool monitoring**: Monitor connection pool usage in production to optimize pool settings.

4. **Graceful shutdown**: Ensure all database connections are properly closed when the application shuts down.

5. **Avoid long-running transactions**: Keep database transactions as short as possible to prevent connection pool exhaustion.

6. **Use appropriate isolation levels**: Choose the right isolation level for your use case to balance consistency and performance.

7. **Handle connection failures**: Implement retry logic for transient database connection failures.

## Testing Connection Management

To verify that database connections are properly managed, you can run the demonstration script:

```bash
python demonstrate_connection_management.py
```

This script shows how to properly manage database connections using context managers and ensures connections are closed after use.