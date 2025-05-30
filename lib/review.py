from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    all = {}  # cache: id -> Review instance

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def save(self):
        if self.id is None:
            sql = '''
                INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)
            '''
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id = row[0]
        if review_id in cls.all:
            instance = cls.all[review_id]
            # Update attributes from row (in case changed)
            instance.year = row[1]
            instance.summary = row[2]
            instance.employee_id = row[3]
            return instance
        else:
            instance = cls(row[1], row[2], row[3], id=review_id)
            cls.all[review_id] = instance
            return instance

    @classmethod
    def find_by_id(cls, id):
        if id in cls.all:
            return cls.all[id]
        sql = 'SELECT * FROM reviews WHERE id = ?'
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        if self.id is None:
            raise Exception("Cannot update Review without id")
        sql = '''
            UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
        '''
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        if self.id is None:
            raise Exception("Cannot delete Review without id")
        sql = 'DELETE FROM reviews WHERE id = ?'
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = 'SELECT * FROM reviews'
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError("summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # You should check the employee_id exists in employees table
        sql = 'SELECT id FROM employees WHERE id = ?'
        CURSOR.execute(sql, (value,))
        if CURSOR.fetchone() is None:
            raise ValueError(f"employee_id {value} does not exist in employees table")
        self._employee_id = value

