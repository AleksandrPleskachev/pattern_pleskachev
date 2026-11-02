"""
Лабораторная работа 2: Паттерны Фабричный метод + Прототип
Предметная область: Филиалы и сотрудники

Фабричный метод — создание разных типов сотрудников
Прототип — клонирование шаблона сотрудника с модификацией
"""

import tkinter as tk
from tkinter import ttk
import copy


# ============================================================
# Часть 1: Фабричный метод — создание сотрудников
# ============================================================

class Employee:
    """Базовый класс сотрудника"""

    def __init__(self, name, department, salary, position, emp_type="общий"):
        self.name = name
        self.department = department
        self.salary = salary
        self.position = position
        self.emp_type = emp_type

    def bonus(self):
        return 0

    def __repr__(self):
        return f"[{self.name}] {self.department} | {self.position} | {self.salary:,} руб. ({self.emp_type})"


class Manager(Employee):
    """Менеджер — бонус 20% от зарплаты"""

    def __init__(self, name, department, salary):
        super().__init__(name, department, salary, "Менеджер", "менеджер")

    def bonus(self):
        return int(self.salary * 0.2)


class Engineer(Employee):
    """Инженер — бонус 15% от зарплаты"""

    def __init__(self, name, department, salary):
        super().__init__(name, department, salary, "Инженер", "инженер")

    def bonus(self):
        return int(self.salary * 0.15)


class Accountant(Employee):
    """Бухгалтер — бонус 10% от зарплаты"""

    def __init__(self, name, department, salary):
        super().__init__(name, department, salary, "Бухгалтер", "бухгалтер")

    def bonus(self):
        return int(self.salary * 0.1)


class Director(Employee):
    """Директор — бонус 30% от зарплаты"""

    def __init__(self, name, department, salary):
        super().__init__(name, department, salary, "Директор", "директор")

    def bonus(self):
        return int(self.salary * 0.3)


class EmployeeFactory:
    """
    Фабричный метод — создаёт сотрудника по типу.
    """

    _registry = {
        "manager": Manager,
        "engineer": Engineer,
        "accountant": Accountant,
        "director": Director,
    }

    @classmethod
    def create(cls, emp_type, name, department, salary):
        """
        Фабричный метод: строка -> объект сотрудника.
        """
        cls_name = cls._registry.get(emp_type)
        if cls_name is None:
            raise ValueError(f"Неизвестный тип: {emp_type}. Доступны: {list(cls._registry.keys())}")
        return cls_name(name, department, salary)


# ============================================================
# Часть 2: Прототип — клонирование шаблона
# ============================================================

class EmployeePrototype:
    """Сотрудник-шаблон, который можно клонировать"""

    def __init__(self, name, department, salary, position):
        self.name = name
        self.department = department
        self.salary = salary
        self.position = position

    def __repr__(self):
        return f"Template({self.name}, {self.department}, {self.salary:,}, {self.position})"

    def clone(self):
        """Глубокое копирование"""
        return copy.deepcopy(self)

    def with_name(self, name):
        """Клон + новое ФИО"""
        cloned = self.clone()
        cloned.name = name
        return cloned

    def with_department(self, dept):
        """Клон + новый отдел"""
        cloned = self.clone()
        cloned.department = dept
        return cloned

    def with_salary(self, salary):
        """Клон + новая зарплата"""
        cloned = self.clone()
        cloned.salary = salary
        return cloned

    def with_position(self, pos):
        """Клон + новая должность"""
        cloned = self.clone()
        cloned.position = pos
        return cloned


# ============================================================
# GUI: Визуализация Factory + Prototype
# ============================================================

class FactoryPrototypeApp:
    """GUI для демонстрации Factory + Prototype"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 2: Factory + Prototype")
        self.root.geometry("950x550")

        self.employees = []
        self.templates = []
        self.base_template = EmployeePrototype("Иванов И.И.", "IT", 80000, "Разработчик")

        self._create_layout()

    def _create_layout(self):
        # === ЛЕВАЯ: Factory ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Фабричный метод:", font=("Arial", 11, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(left, text="Создание сотрудника по типу:", font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Тип сотрудника:", font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 0))
        self.type_var = tk.StringVar(value="manager")
        types = [("manager", "Менеджер (бонус 20%)"),
                 ("engineer", "Инженер (бонус 15%)"),
                 ("accountant", "Бухгалтер (бонус 10%)"),
                 ("director", "Директор (бонус 30%)")]
        for val, desc in types:
            ttk.Radiobutton(left, text=desc, variable=self.type_var, value=val).pack(anchor=tk.W)

        tk.Label(left, text="Создан:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(8, 0))
        self.factory_label = tk.Label(left, text="Не создан", font=("Consolas", 9), fg="#8e44ad")
        self.factory_label.pack(anchor=tk.W)

        tk.Button(left, text="Создать сотрудника", command=self._create_employee,
                  bg="#8e44ad", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # === ЦЕНТР: Таблица ===
        center = tk.Frame(self.root, padx=10, pady=10)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(center, text="Все сотрудники:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        tree_frame = tk.Frame(center)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "position", "salary", "type", "bonus")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=16)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("position", text="Должность")
        self.tree.heading("salary", text="Зарплата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("bonus", text="Бонус")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Итого
        self.total_label = tk.Label(center, text="Всего: 0 | Фонд: 0 | Бонусы: 0",
                                    font=("Arial", 10, "bold"), fg="#2c3e50")
        self.total_label.pack(pady=5)

        # === ПРАВАЯ: Prototype ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Прототип:", font=("Arial", 11, "bold"), fg="#d35400").pack(anchor=tk.W)
        tk.Label(right, text="Клонирование шаблона:", font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(right, text="Шаблон:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.template_label = tk.Label(right, text=f"{self.base_template}",
                                       font=("Consolas", 9), fg="#d35400")
        self.template_label.pack(anchor=tk.W)

        self.proto_log = tk.Text(right, width=35, height=10, font=("Consolas", 9))
        self.proto_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.proto_log.insert(tk.END, "base = Template('Иванов', 'IT', 80000, 'Разработчик')\n")

        btn_frame = tk.Frame(right)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="with_name", command=self._proto_name,
                  bg="#d35400", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="with_dept", command=self._proto_dept,
                  bg="#d35400", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="with_salary", command=self._proto_salary,
                  bg="#d35400", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="chain", command=self._proto_chain,
                  bg="#d35400", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)

        tk.Label(right, text="Клоны:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(5, 0))
        self.clones_label = tk.Label(right, text="Нет клонов",
                                     font=("Consolas", 8), fg="#e74c3c")
        self.clones_label.pack(anchor=tk.W)

    # ======================== FACTORY ========================

    def _create_employee(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        sal_text = self.sal_entry.get().strip()

        if not all([name, dept, sal_text]):
            return

        try:
            salary = int(sal_text)
        except ValueError:
            return

        emp_type = self.type_var.get()

        try:
            emp = EmployeeFactory.create(emp_type, name, dept, salary)
            self.employees.append(emp)
            self.factory_label.config(text=str(emp), fg="#27ae60")
            self._refresh()
        except ValueError as e:
            self.factory_label.config(text=f"Error: {e}", fg="#e74c3c")

    # ======================== PROTOTYPE ========================

    def _proto_log(self, text):
        self.proto_log.insert(tk.END, text + "\n")
        self.proto_log.see(tk.END)

    def _proto_name(self):
        name = "Петров"
        cloned = self.base_template.with_name(name)
        self._log_proto(cloned)
        self.templates.append(cloned)

    def _proto_dept(self):
        dept = "Бухгалтерия"
        cloned = self.base_template.with_department(dept)
        self._log_proto(cloned)
        self.templates.append(cloned)

    def _proto_salary(self):
        salary = 120000
        cloned = self.base_template.with_salary(salary)
        self._log_proto(cloned)
        self.templates.append(cloned)

    def _proto_chain(self):
        cloned = (self.base_template
                      .with_name("Сидоров")
                      .with_department("HR")
                      .with_salary(95000))
        self._log_proto(cloned)
        self.templates.append(cloned)

    def _log_proto(self, cloned):
        self._proto_log(f"p = base.with_...()")
        self._proto_log(f"-> {cloned}")
        self._proto_log(f"base is p: {self.base_template is cloned}")
        clones = self.clones_label.cget("text")
        self.clones_label.config(text=f"{clones}\n  {cloned}", fg="#27ae60")

    # ======================== ОБЩЕЕ ========================

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.employees:
            bonus = emp.bonus() if hasattr(emp, "bonus") else 0
            self.tree.insert("", tk.END, values=(
                emp.name, emp.department, emp.position,
                f"{emp.salary:,}", emp.emp_type, f"{bonus:,}"))

        total = sum(e.salary for e in self.employees)
        bonuses = sum(e.bonus() if hasattr(e, "bonus") else 0 for e in self.employees)
        self.total_label.config(text=f"Всего: {len(self.employees)} | Фонд: {total:,} | Бонусы: {bonuses:,}")


def main():
    root = tk.Tk()
    app = FactoryPrototypeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
