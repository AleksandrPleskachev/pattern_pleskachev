"""
Лабораторная работа 7: Паттерны Команда + Итератор
Предметная область: Филиалы и сотрудники

Команда — оборачиваем операции как объекты. Можно отменять (undo).
  - AddCommand, RemoveCommand, ChangeSalaryCommand
  - CommandHistory хранит историю для Undo/Redo

Итератор — обходим сотрудников разными способами.
  - Iterator по алфавиту, по зарплате, по отделу
  - Клиент не знает о внутренней структуре
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# Часть 1: Команда (Command)
# ============================================================

class Employee:
    """Сотрудник"""

    def __init__(self, name, department, position, salary):
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary

    def __repr__(self):
        return "{} | {} | {} | {:,} руб.".format(self.name, self.department, self.position, self.salary)


class EmployeeManager:
    """Реципиент — управляет сотрудниками"""

    def __init__(self):
        self.employees = []

    def add_employee(self, name, department, position, salary):
        emp = Employee(name, department, position, salary)
        self.employees.append(emp)
        return emp

    def remove_employee(self, name):
        for i, emp in enumerate(self.employees):
            if emp.name == name:
                removed = self.employees.pop(i)
                return removed
        return None

    def change_salary(self, name, new_salary):
        for emp in self.employees:
            if emp.name == name:
                old_salary = emp.salary
                emp.salary = new_salary
                return old_salary
        return None


class Command:
    """Базовый интерфейс команды"""

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


class AddCommand(Command):
    """Команда: добавить сотрудника"""

    def __init__(self, manager, name, department, position, salary):
        self.manager = manager
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary
        self.employee = None

    def execute(self):
        self.employee = self.manager.add_employee(self.name, self.department, self.position, self.salary)
        return self.employee

    def undo(self):
        self.manager.remove_employee(self.name)


class RemoveCommand(Command):
    """Команда: удалить сотрудника"""

    def __init__(self, manager, name):
        self.manager = manager
        self.name = name
        self.employee = None

    def execute(self):
        self.employee = self.manager.remove_employee(self.name)
        return self.employee

    def undo(self):
        if self.employee:
            self.manager.add_employee(self.employee.name, self.employee.department,
                                      self.employee.position, self.employee.salary)


class ChangeSalaryCommand(Command):
    """Команда: изменить зарплату"""

    def __init__(self, manager, name, new_salary):
        self.manager = manager
        self.name = name
        self.new_salary = new_salary
        self.old_salary = None

    def execute(self):
        self.old_salary = self.manager.change_salary(self.name, self.new_salary)
        return self.old_salary

    def undo(self):
        if self.old_salary is not None:
            self.manager.change_salary(self.name, self.old_salary)


class CommandHistory:
    """История команд — Undo/Redo"""

    def __init__(self):
        self._history = []
        self._redo_stack = []

    def execute(self, command):
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()

    def undo(self):
        if self._history:
            command = self._history.pop()
            command.undo()
            self._redo_stack.append(command)

    def redo(self):
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._history.append(command)


# ============================================================
# Часть 2: Итератор (Iterator)
# ============================================================

class EmployeeIterator:
    """Базовый интерфейс итератора"""

    def first(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

    def current(self):
        raise NotImplementedError


class AlphabeticalIterator(EmployeeIterator):
    """Итератор: по алфавиту"""

    def __init__(self, employees):
        self._sorted = sorted(employees, key=lambda e: e.name)
        self._index = 0

    def first(self):
        self._index = 0
        return self.current()

    def next(self):
        self._index += 1
        return self.current()

    def is_done(self):
        return self._index >= len(self._sorted)

    def current(self):
        if 0 <= self._index < len(self._sorted):
            return self._sorted[self._index]
        return None


class SalaryIterator(EmployeeIterator):
    """Итератор: по зарплате (по убыванию)"""

    def __init__(self, employees):
        self._sorted = sorted(employees, key=lambda e: e.salary, reverse=True)
        self._index = 0

    def first(self):
        self._index = 0
        return self.current()

    def next(self):
        self._index += 1
        return self.current()

    def is_done(self):
        return self._index >= len(self._sorted)

    def current(self):
        if 0 <= self._index < len(self._sorted):
            return self._sorted[self._index]
        return None


class DepartmentIterator(EmployeeIterator):
    """Итератор: по отделам"""

    def __init__(self, employees):
        self._sorted = sorted(employees, key=lambda e: e.department)
        self._index = 0

    def first(self):
        self._index = 0
        return self.current()

    def next(self):
        self._index += 1
        return self.current()

    def is_done(self):
        return self._index >= len(self._sorted)

    def current(self):
        if 0 <= self._index < len(self._sorted):
            return self._sorted[self._index]
        return None


class EmployeesAggregate:
    """Агрегат — создаёт итераторы"""

    def __init__(self):
        self.employees = []

    def add(self, emp):
        self.employees.append(emp)

    def create_alphabetical_iterator(self):
        return AlphabeticalIterator(self.employees)

    def create_salary_iterator(self):
        return SalaryIterator(self.employees)

    def create_department_iterator(self):
        return DepartmentIterator(self.employees)


# ============================================================
# GUI
# ============================================================

class CommandIteratorApp:
    """GUI для демонстрации Команда + Итератор"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 7: Команда + Итератор")
        self.root.geometry("1100x600")

        self.manager = EmployeeManager()
        self.history = CommandHistory()
        self.aggregate = EmployeesAggregate()

        self._create_layout()

    def _create_layout(self):
        # === ЛЕВАЯ: Команда ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Команда (Command):",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Операции как объекты + Undo/Redo",
                 font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        # Кнопки команд
        btn_frame = tk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="Добавить", command=self._cmd_add,
                  bg="#27ae60", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Изменить зарплату", command=self._cmd_change,
                  bg="#f39c12", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Удалить", command=self._cmd_remove,
                  bg="#e74c3c", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        # Undo/Redo
        undo_frame = tk.Frame(left)
        undo_frame.pack(fill=tk.X, pady=5)

        tk.Button(undo_frame, text="Undo", command=self._undo,
                  bg="#9b59b6", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(undo_frame, text="Redo", command=self._redo,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=2)

        # Лог команд
        self.cmd_log = tk.Text(left, width=35, height=10, font=("Consolas", 9))
        self.cmd_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # === ПРАВАЯ: Итератор ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Итератор (Iterator):",
                 font=("Arial", 11, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(right, text="Обходим сотрудников разными способами:",
                 font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(right, text="Выберите итератор:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 2))

        iter_frame = tk.Frame(right)
        iter_frame.pack(fill=tk.X, pady=5)

        tk.Button(iter_frame, text="По алфавиту", command=self._iter_alpha,
                  bg="#2ecc71", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(iter_frame, text="По зарплате", command=self._iter_salary,
                  bg="#e67e22", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(iter_frame, text="По отделу", command=self._iter_dept,
                  bg="#1abc9c", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        # Лог итератора
        self.iter_log = tk.Text(right, width=35, height=10, font=("Consolas", 9))
        self.iter_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица
        tk.Label(right, text="Все сотрудники:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        tree_frame = tk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "position", "salary")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("position", text="Должность")
        self.tree.heading("salary", text="Зарплата")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    # ======================== КОМАНДА ========================

    def _cmd_add(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        sal_text = self.sal_entry.get().strip()

        if not all([name, dept, sal_text]):
            return

        try:
            salary = int(sal_text)
        except ValueError:
            return

        cmd = AddCommand(self.manager, name, dept, "Сотрудник", salary)
        self.history.execute(cmd)

        self.cmd_log.insert(tk.END, "[EXECUTE] AddCommand('{}', {:,})\n".format(name, salary))
        self.cmd_log.insert(tk.END, "  -> {}\n".format(self.manager.employees[-1]))

        self._refresh_tree()
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

    def _cmd_change(self):
        name = self.name_entry.get().strip()
        sal_text = self.sal_entry.get().strip()

        if not name or not sal_text:
            return

        try:
            new_salary = int(sal_text)
        except ValueError:
            return

        cmd = ChangeSalaryCommand(self.manager, name, new_salary)
        self.history.execute(cmd)

        self.cmd_log.insert(tk.END, "[EXECUTE] ChangeSalaryCommand('{}', {:,})\n".format(name, new_salary))
        self._refresh_tree()

    def _cmd_remove(self):
        name = self.name_entry.get().strip()
        if not name:
            return

        cmd = RemoveCommand(self.manager, name)
        self.history.execute(cmd)

        self.cmd_log.insert(tk.END, "[EXECUTE] RemoveCommand('{}')\n".format(name))
        self._refresh_tree()

    def _undo(self):
        self.history.undo()
        self.cmd_log.insert(tk.END, "[UNDO] <- последняя команда отменена\n")
        self._refresh_tree()

    def _redo(self):
        self.history.redo()
        self.cmd_log.insert(tk.END, "[REDO] -> команда повторена\n")
        self._refresh_tree()

    # ======================== ИТЕРАТОР ========================

    def _iter_alpha(self):
        self._show_iterator("По алфавиту", self.aggregate.create_alphabetical_iterator())

    def _iter_salary(self):
        self._show_iterator("По зарплате (убыв.)", self.aggregate.create_salary_iterator())

    def _iter_dept(self):
        self._show_iterator("По отделу", self.aggregate.create_department_iterator())

    def _show_iterator(self, iter_name, it):
        self.iter_log.delete(1.0, tk.END)
        self.iter_log.insert(tk.END, "Итератор: {}\n".format(iter_name))
        self.iter_log.insert(tk.END, "=" * 40 + "\n")

        it.first()
        while not it.is_done():
            emp = it.current()
            self.iter_log.insert(tk.END, "  {:15s} | {:>8,d} | {}\n".format(emp.name, emp.salary, emp.department))
            it.next()

    def _refresh_tree(self):
        self.aggregate.employees = list(self.manager.employees)
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.manager.employees:
            self.tree.insert("", tk.END, values=(emp.name, emp.department,
                                                 emp.position, "{:,}".format(emp.salary)))


def main():
    root = tk.Tk()
    app = CommandIteratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
