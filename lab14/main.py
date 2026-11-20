"""
Лабораторная работа 14: Паттерны Repository и Unit of Work
Предметная область: Филиалы и сотрудники

Repository прячет JSON-файл за коллекцией сотрудников.
Unit of Work копит добавления, правки и удаления и записывает
их в репозиторий одним commit либо выбрасывает через rollback.
"""

import json
import os
import tkinter as tk
from tkinter import ttk


class Employee:
    def __init__(self, emp_id, name, department, position, salary):
        self.emp_id = emp_id
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary

    def to_dict(self):
        return {
            "id": self.emp_id,
            "name": self.name,
            "department": self.department,
            "position": self.position,
            "salary": self.salary,
        }

    @staticmethod
    def from_dict(data):
        return Employee(data["id"], data["name"], data["department"], data["position"], data["salary"])


class JsonEmployeeRepository:
    """Репозиторий: бизнес-код видит коллекцию, а не файл."""

    def __init__(self, path):
        self.path = path
        self._items = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            self._items = {}
            return
        with open(self.path, "r", encoding="utf-8") as handle:
            raw = handle.read().strip()
        if not raw:
            self._items = {}
            return
        rows = json.loads(raw)
        self._items = {row["id"]: Employee.from_dict(row) for row in rows}

    def _flush(self):
        rows = [emp.to_dict() for emp in self._items.values()]
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, ensure_ascii=False, indent=2)

    def next_id(self):
        if not self._items:
            return 1
        return max(self._items) + 1

    def add(self, employee):
        self._items[employee.emp_id] = employee
        self._flush()

    def update(self, employee):
        self._items[employee.emp_id] = employee
        self._flush()

    def delete(self, emp_id):
        self._items.pop(emp_id, None)
        self._flush()

    def get(self, emp_id):
        return self._items.get(emp_id)

    def get_all(self):
        return list(self._items.values())


class UnitOfWork:
    """Единица работы: изменения копятся до commit."""

    def __init__(self, repository):
        self.repository = repository
        self.new = []
        self.dirty = []
        self.removed = []

    def register_new(self, employee):
        self.new.append(employee)

    def register_dirty(self, employee):
        for index, item in enumerate(self.new):
            if item.emp_id == employee.emp_id:
                self.new[index] = employee
                return
        self.dirty = [item for item in self.dirty if item.emp_id != employee.emp_id]
        self.dirty.append(employee)

    def register_removed(self, emp_id):
        self.new = [item for item in self.new if item.emp_id != emp_id]
        self.dirty = [item for item in self.dirty if item.emp_id != emp_id]
        if emp_id not in self.removed:
            self.removed.append(emp_id)

    def commit(self):
        for employee in self.new:
            self.repository.add(employee)
        for employee in self.dirty:
            self.repository.update(employee)
        for emp_id in self.removed:
            self.repository.delete(emp_id)
        count = len(self.new) + len(self.dirty) + len(self.removed)
        self.rollback()
        return count

    def rollback(self):
        self.new.clear()
        self.dirty.clear()
        self.removed.clear()

    def pending_text(self):
        return "новые: {} | изменённые: {} | удалённые: {}".format(
            len(self.new), len(self.dirty), len(self.removed))


class DataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР14 — Repository и Unit of Work")
        self.root.geometry("900x560")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employees.json")
        self.repository = JsonEmployeeRepository(path)
        self.uow = UnitOfWork(self.repository)
        self._draft_id = self.repository.next_id()
        self._build()
        self._reload()

    def _build(self):
        left = tk.Frame(self.root, padx=10, pady=8)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Unit of Work", font=("Arial", 13, "bold")).pack(anchor=tk.W)
        tk.Label(left, text="Файл меняется только по Commit", font=("Arial", 9)).pack(anchor=tk.W)
        self.name = self._entry(left, "ФИО")
        self.dept = self._entry(left, "Отдел")
        self.position = self._entry(left, "Должность")
        self.salary = self._entry(left, "Зарплата")
        tk.Button(left, text="Зарегистрировать нового", command=self._new,
                  bg="#27ae60", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(left, text="Изменить выбранного", command=self._dirty,
                  bg="#f39c12", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(left, text="Удалить выбранного", command=self._remove,
                  bg="#c0392b", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(left, text="Commit", command=self._commit,
                  bg="#2980b9", fg="white").pack(fill=tk.X, pady=(12, 3))
        tk.Button(left, text="Rollback", command=self._rollback,
                  bg="#7f8c8d", fg="white").pack(fill=tk.X, pady=3)
        self.pending = tk.Label(left, text="", font=("Arial", 9, "bold"))
        self.pending.pack(anchor=tk.W, pady=8)

        right = tk.Frame(self.root, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="Repository: employees.json", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.tree = ttk.Treeview(right, columns=("id", "name", "dept", "pos", "salary", "mark"),
                                  show="headings", height=12)
        for col, title, width in (
            ("id", "ID", 40), ("name", "ФИО", 140), ("dept", "Отдел", 100),
            ("pos", "Должность", 120), ("salary", "Зарплата", 90), ("mark", "В UoW", 90),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.log = tk.Text(right, height=8, font=("Consolas", 9))
        self.log.pack(fill=tk.X, pady=6)

    def _entry(self, parent, label):
        tk.Label(parent, text=label).pack(anchor=tk.W)
        entry = tk.Entry(parent, width=28)
        entry.pack(fill=tk.X, pady=(0, 4))
        return entry

    def _form_employee(self, emp_id):
        try:
            salary = int(self.salary.get().strip())
        except ValueError:
            self._write("Зарплата должна быть числом")
            return None
        name = self.name.get().strip()
        dept = self.dept.get().strip()
        position = self.position.get().strip()
        if not all([name, dept, position]):
            self._write("Заполните ФИО, отдел и должность")
            return None
        return Employee(emp_id, name, dept, position, salary)

    def _new(self):
        employee = self._form_employee(self._draft_id)
        if employee is None:
            return
        self.uow.register_new(employee)
        self._draft_id += 1
        self._write("[UoW] register_new id={}".format(employee.emp_id))
        self._reload()

    def _dirty(self):
        selected = self._selected()
        if selected is None:
            return
        employee = self._form_employee(selected)
        if employee is None:
            return
        self.uow.register_dirty(employee)
        self._write("[UoW] register_dirty id={}".format(employee.emp_id))
        self._reload()

    def _remove(self):
        selected = self._selected()
        if selected is None:
            return
        self.uow.register_removed(selected)
        self._write("[UoW] register_removed id={}".format(selected))
        self._reload()

    def _commit(self):
        count = self.uow.commit()
        self._write("[Repository] commit записал {} изменений в JSON".format(count))
        self._reload()

    def _rollback(self):
        self.uow.rollback()
        self._write("[UoW] rollback, файл не тронут")
        self._reload()

    def _selected(self):
        selected = self.tree.selection()
        if not selected:
            self._write("Выберите строку")
            return None
        return int(self.tree.item(selected[0])["values"][0])

    def _mark(self, emp_id):
        if any(item.emp_id == emp_id for item in self.uow.new):
            return "новый"
        if emp_id in self.uow.removed:
            return "удалить"
        if any(item.emp_id == emp_id for item in self.uow.dirty):
            return "изменён"
        return ""

    def _reload(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        shown = {emp.emp_id: emp for emp in self.repository.get_all()}
        for emp in self.uow.dirty:
            shown[emp.emp_id] = emp
        for emp in self.uow.new:
            shown[emp.emp_id] = emp
        for emp_id in sorted(shown):
            if emp_id in self.uow.removed and emp_id not in {e.emp_id for e in self.uow.new}:
                emp = shown[emp_id]
                self.tree.insert("", tk.END, values=(
                    emp.emp_id, emp.name, emp.department, emp.position,
                    "{:,}".format(emp.salary), "удалить"))
                continue
            emp = shown[emp_id]
            self.tree.insert("", tk.END, values=(
                emp.emp_id, emp.name, emp.department, emp.position,
                "{:,}".format(emp.salary), self._mark(emp.emp_id)))
        self.pending.config(text=self.uow.pending_text())

    def _write(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    DataApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
