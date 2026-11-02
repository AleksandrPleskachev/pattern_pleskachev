"""
Лабораторная работа 1: Паттерн Builder
Предметная область: Филиалы и сотрудники

Builder собирает сотрудника по полям:
  - ФИО, отдел, должность, зарплата
  - тип сотрудника (штатный / контрактный)
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# Product: Employee — готовый сотрудник (неизменяемый)
# ============================================================

class Employee:
    """Готовый сотрудник"""

    def __init__(self, name, department, salary, position, emp_type="штатный"):
        self.name = name
        self.department = department
        self.salary = salary
        self.position = position
        self.emp_type = emp_type

    def __repr__(self):
        return f"[{self.name}] {self.department} | {self.position} | {self.salary:,} руб. ({self.emp_type})"


# ============================================================
# Builder: EmployeeBuilder
# ============================================================

class EmployeeBuilder:
    """
    Строитель сотрудника.
    Каждый метод возвращает self для цепочки вызовов.
    """

    def __init__(self):
        self._name = ""
        self._department = ""
        self._salary = 0
        self._position = ""
        self._emp_type = "штатный"

    def name(self, value):
        """Задаёт ФИО"""
        self._name = value
        return self

    def department(self, value):
        """Задаёт отдел"""
        self._department = value
        return self

    def position(self, value):
        """Задаёт должность"""
        self._position = value
        return self

    def salary(self, value):
        """Задаёт зарплату"""
        self._salary = value
        return self

    def emp_type(self, value):
        """Задаёт тип сотрудника"""
        self._emp_type = value
        return self

    def build(self):
        """Создаёт готового сотрудника"""
        if not self._name:
            raise ValueError("ФИО обязательно")
        if not self._department:
            raise ValueError("Отдел обязателен")
        if self._salary <= 0:
            raise ValueError("Зарплата должна быть больше 0")
        return Employee(
            name=self._name,
            department=self._department,
            salary=self._salary,
            position=self._position,
            emp_type=self._emp_type,
        )


# ============================================================
# GUI: Визуализация Builder
# ============================================================

class BuilderApp:
    """GUI для демонстрации паттерна Builder"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 1: Builder")
        self.root.geometry("850x520")

        self.builder = EmployeeBuilder()
        self.employees = []
        self.current_dots = []

        self._create_layout()

    def _create_layout(self):
        # Левая часть: форма ввода
        left = tk.Frame(self.root, padx=15, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="EmployeeBuilder — сборка сотрудника:",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)

        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Должность:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.pos_entry = tk.Entry(left, width=30)
        self.pos_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Тип:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.type_var = tk.StringVar(value="штатный")
        ttk.Combobox(left, textvariable=self.type_var,
                     values=["штатный", "контрактный"], state="readonly",
                     width=27).pack(fill=tk.X, pady=2)

        # Кнопка build
        tk.Button(left, text="build() -> создать сотрудника",
                  command=self._build, bg="#27ae60", fg="white",
                  font=("Arial", 10, "bold")).pack(pady=(15, 5))

        # Правая часть: лог Builder
        right = tk.Frame(self.root, padx=15, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Лог сборки:", font=("Arial", 10, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        self.log = tk.Text(right, width=40, height=18, font=("Consolas", 9))
        self.log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log.insert(tk.END, "builder = EmployeeBuilder()\n")

        # Таблица сотрудников
        tk.Label(right, text="Сотрудники:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
        tree_frame = tk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "position", "salary", "type")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("position", text="Должность")
        self.tree.heading("salary", text="Зарплата")
        self.tree.heading("type", text="Тип")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Итого
        self.total_label = tk.Label(right, text="Всего: 0",
                                    font=("Arial", 10), fg="#2c3e50")
        self.total_label.pack(pady=5)

        tk.Button(right, text="Очистить лог", command=self._clear_log,
                  bg="#e74c3c", fg="white", font=("Arial", 9)).pack(pady=5)

    def _log(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def _clear_log(self):
        self.log.delete(1.0, tk.END)
        self.log.insert(tk.END, "builder = EmployeeBuilder()\n")

    def _build(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        pos = self.pos_entry.get().strip()
        sal_text = self.sal_entry.get().strip()
        etype = self.type_var.get()

        # Показываем каждый шаг Builder
        self._log(f"builder.name('{name}')")
        self.builder.name(name)

        self._log(f"builder.department('{dept}')")
        self.builder.department(dept)

        self._log(f"builder.position('{pos}')")
        self.builder.position(pos)

        if sal_text:
            self._log(f"builder.salary({sal_text})")
            self.builder.salary(int(sal_text))

        self._log(f"builder.emp_type('{etype}')")
        self.builder.emp_type(etype)

        # Вызываем build
        try:
            emp = self.builder.build()
            self.employees.append(emp)
            self._log(f"  -> {emp}")
            self._log(f"  [OK] Сотрудник создан!")
            self._refresh()
        except ValueError as e:
            self._log(f"  [ERROR] {e}")

        # Очищаем форму
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.pos_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.employees:
            self.tree.insert("", tk.END, values=(
                emp.name, emp.department, emp.position,
                f"{emp.salary:,}", emp.emp_type))

        total = sum(e.salary for e in self.employees)
        self.total_label.config(text=f"Всего: {len(self.employees)} | Фонд: {total:,} руб.")


def main():
    root = tk.Tk()
    app = BuilderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
