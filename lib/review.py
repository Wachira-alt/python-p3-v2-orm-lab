from __init__ import CURSOR, CONN
from employee import Employee  # Only used in the employee.setter


class Review:
    all = {}

    def __init__(self, year, summary, employee, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee = employee  # This is an instance of Employee
        if id:
            Review.all[id] = self

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee {self.employee.id}>"

    # === TABLE METHODS ===
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    # === ORM INSTANCE METHODS ===
    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee.id)
            )
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee):
        from employee import Employee  # Avoid circular import

        if isinstance(employee, int):
            employee = Employee.find_by_id(employee)
        if not isinstance(employee, Employee):
            raise ValueError("Must pass a valid Employee instance or ID.")

        review = cls(year, summary, employee)
        review.save()
        return review


    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        if id in cls.all:
            return cls.all[id]
        employee = Employee.find_by_id(employee_id)
        review = cls(year, summary, employee, id)
        cls.all[id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee.id, self.id)
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # === PROPERTIES ===
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip() != "":
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        from employee import Employee  # Avoid circular import
        if isinstance(value, Employee) and value.id:
            self._employee = value
        else:
            raise ValueError("Employee must be an Employee instance with a valid id")
    @property
    def employee_id(self):
        return self._employee.id if self._employee else None

