# lib/employee.py

from __init__ import CURSOR, CONN
from department import Department

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

        if id:
            Employee.all[id] = self

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}>"

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute(
                """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
                """,
                (self.name, self.job_title, self.department_id)
            )
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        employee_id, name, job_title, department_id = row
        if employee_id in cls.all:
            instance = cls.all[employee_id]
            instance.name = name
            instance.job_title = job_title
            instance.department_id = department_id
        else:
            instance = cls(name, job_title, department_id, id=employee_id)
            cls.all[employee_id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        if not self.id:
            raise Exception("Cannot update employee without an ID.")
        CURSOR.execute(
            """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
            """,
            (self.name, self.job_title, self.department_id, self.id)
        )
        CONN.commit()

    def delete(self):
        if not self.id:
            raise Exception("Cannot delete employee without an ID.")
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in Employee.all:
            del Employee.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM employees")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        from review import Review  # Avoid circular import
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]
    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

