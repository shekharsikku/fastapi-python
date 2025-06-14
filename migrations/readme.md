## **Generic single database configuration with an async dbapi.**

By using virtual environment use - .venv/Scripts/alembic

### **Create migrations template**

```bash
alembic init -t async migrations
```

### **Generate migrations with version**

```bash
alembic revision --autogenerate -m '<message>'
```

### **Apply migrations to database**

```bash
alembic upgrade head
```
