"""
Лабораторная работа 4: Паттерны Компоновщик + Декоратор
Предметная область: Филиалы и сотрудники

Компоновщик — иерархия: Филиал -> Отдел -> Сотрудник
  get_salary() работает одинаково на любом уровне дерева.

Декоратор — надбавки к зарплате:
  Базовый сотрудник + надбавка за стаж + надбавка за категорию + премия.
  Каждый декоратор оборачивает сотрудника и добавляет что-то к зарплате.
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# Часть 1: Компоновщик — иерархия Филиал -> Отдел -> Сотрудник
# ============================================================

class BranchComponent:
    """
    Базовый компонент для Компоновщика.
    И сотрудник, и отдел имеют метод get_salary().
    """

    def get_salary(self):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.get_name()}: {self.get_salary():,} руб."


class Employee(BranchComponent):
    """Листья дерева — сотрудник"""

    def __init__(self, name, position, salary):
        self.name = name
        self.position = position
        self.salary = salary

    def get_salary(self):
        return self.salary

    def get_name(self):
        return f"{self.name} ({self.position})"


class Department(BranchComponent):
    """
    Композит — отдел содержит сотрудников и подотделы.
    get_salary() суммирует зарплату всех дочерних компонентов.
    """

    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, component):
        self._children.append(component)

    def remove(self, component):
        self._children.remove(component)

    def get_salary(self):
        """Суммирует зарплаты всех дочерних компонентов"""
        return sum(child.get_salary() for child in self._children)

    def get_name(self):
        return self.name

    def get_children(self):
        return self._children


class Branch(BranchComponent):
    """
    Корень дерева — филиал содержит отделы.
    """

    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, component):
        self._children.append(component)

    def get_salary(self):
        return sum(child.get_salary() for child in self._children)

    def get_name(self):
        return self.name

    def get_children(self):
        return self._children


# ============================================================
# Часть 2: Декоратор — надбавки к зарплате
# ============================================================

class SalaryComponent:
    """Базовый интерфейс для Декоратора"""

    def get_salary(self):
        raise NotImplementedError

    def get_description(self):
        raise NotImplementedError


class BaseEmployee(SalaryComponent):
    """Базовый сотрудник — компонент"""

    def __init__(self, name, base_salary):
        self.name = name
        self.base_salary = base_salary

    def get_salary(self):
        return self.base_salary

    def get_description(self):
        return f"{self.name}: {self.base_salary:,} руб."


class SeniorityDecorator(SalaryComponent):
    """Декоратор: надбавка за стаж (10% от базы)"""

    def __init__(self, component, years):
        self.component = component
        self.years = years

    def get_salary(self):
        return self.component.get_salary() + int(self.component.get_salary() * self.years * 0.10)

    def get_description(self):
        return f"{self.component.get_description()} + стаж({self.years}г, +{int(self.component.get_salary() * self.years * 0.10):,})"


class CategoryDecorator(SalaryComponent):
    """Декоратор: надбавка за категорию (фиксированная сумма)"""

    def __init__(self, component, category_bonus):
        self.component = component
        self.category_bonus = category_bonus

    def get_salary(self):
        return self.component.get_salary() + self.category_bonus

    def get_description(self):
        return f"{self.component.get_description()} + категория(+{self.category_bonus:,})"


class BonusDecorator(SalaryComponent):
    """Декоратор: премия (фиксированная сумма)"""

    def __init__(self, component, bonus_amount):
        self.component = component
        self.bonus_amount = bonus_amount

    def get_salary(self):
        return self.component.get_salary() + self.bonus_amount

    def get_description(self):
        return f"{self.component.get_description()} + премия(+{self.bonus_amount:,})"


# ============================================================
# GUI
# ============================================================

class CompositeDecoratorApp:
    """GUI для демонстрации Компоновщик + Декоратор"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 4: Компоновщик + Декоратор")
        self.root.geometry("1100x600")

        self.branch = Branch("Головной офис")
        self.decorator_log = []

        self._create_layout()
        self._load_sample_data()

    def _create_layout(self):
        # === ЛЕВАЯ: Компоновщик ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Компоновщик: Филиал -> Отдел -> Сотрудник",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="get_salary() работает на любом уровне:", font=("Arial", 9)).pack(anchor=tk.W)

        # Форма
        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Должность:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.pos_entry = tk.Entry(left, width=30)
        self.pos_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Добавить в:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_var = tk.StringVar(value="IT")
        ttk.Combobox(left, textvariable=self.dept_var,
                     values=["IT", "Бухгалтерия", "Продажи", "Головной офис"],
                     state="readonly", width=27).pack(fill=tk.X, pady=2)

        tk.Button(left, text="Добавить сотрудника", command=self._add_employee,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

        # Дерево
        tk.Label(left, text="Структура:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
        self.tree = ttk.Treeview(left, columns=("name", "salary"), show="headings", height=12)
        self.tree.heading("name", text="Название")
        self.tree.heading("salary", text="Фонд")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.branch_label = tk.Label(left, text="Фонд филиала: 0 руб.",
                                     font=("Arial", 10, "bold"), fg="#2c3e50")
        self.branch_label.pack(pady=5)

        # === ПРАВАЯ: Декоратор ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Декоратор: Надбавки к зарплате",
                 font=("Arial", 11, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(right, text="Каждый декоратор оборачивает сотрудника и добавляет надбавку:",
                 font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(right, text="ФИО сотрудника:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.dec_name_entry = tk.Entry(right, width=30)
        self.dec_name_entry.pack(fill=tk.X, pady=2)

        tk.Label(right, text="Базовая зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dec_sal_entry = tk.Entry(right, width=30)
        self.dec_sal_entry.pack(fill=tk.X, pady=2)

        # Чекбоксы декораторов
        tk.Label(right, text="Надбавки:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 2))

        self.seniority_var = tk.IntVar()
        self.seniority_spin = tk.Spinbox(right, from_=0, to=30, width=5)
        self.seniority_spin.insert(0, "5")
        tk.Checkbutton(right, text="За стаж (10% в год):", variable=self.seniority_var,
                       command=lambda: self._update_decorators()).pack(anchor=tk.W)
        tk.Label(right, text="  Лет:", font=("Arial", 8)).pack(anchor=tk.W)
        self.seniority_spin.pack(anchor=tk.W, padx=(20, 0))

        self.category_var = tk.IntVar()
        tk.Checkbutton(right, text="За категорию:", variable=self.category_var,
                       command=lambda: self._update_decorators()).pack(anchor=tk.W)
        self.category_spin = tk.Spinbox(right, from_=0, to=50000, increment=5000, width=8)
        self.category_spin.insert(0, "10000")
        self.category_spin.pack(anchor=tk.W, padx=(20, 0))

        self.bonus_var = tk.IntVar()
        tk.Checkbutton(right, text="Премия:", variable=self.bonus_var,
                       command=lambda: self._update_decorators()).pack(anchor=tk.W)
        self.bonus_spin = tk.Spinbox(right, from_=0, to=100000, increment=5000, width=8)
        self.bonus_spin.insert(0, "15000")
        self.bonus_spin.pack(anchor=tk.W, padx=(20, 0))

        tk.Button(right, text="Рассчитать", command=self._calculate_decorator,
                  bg="#8e44ad", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # Лог декоратора
        self.dec_log = tk.Text(right, width=40, height=12, font=("Consolas", 9))
        self.dec_log.pack(fill=tk.BOTH, expand=True, pady=5)

        self.dec_total = tk.Label(right, text="Итого: 0 руб.",
                                  font=("Arial", 11, "bold"), fg="#8e44ad")
        self.dec_total.pack(pady=5)

    # ======================== КОМПОНОВЩИК ========================

    def _load_sample_data(self):
        """Загружает пример иерархии"""
        it_dept = Department("IT")
        it_dept.add(Employee("Иванов А.А.", "Разработчик", 80000))
        it_dept.add(Employee("Петрова Б.Б.", "Тестировщик", 60000))

        acc_dept = Department("Бухгалтерия")
        acc_dept.add(Employee("Сидорова В.В.", "Бухгалтер", 55000))

        sales_dept = Department("Продажи")
        sales_dept.add(Employee("Козлов Г.Г.", "Менеджер", 50000))
        sales_dept.add(Employee("Новикова Д.Д.", "Менеджер", 50000))

        self.branch.add(it_dept)
        self.branch.add(acc_dept)
        self.branch.add(sales_dept)
        self._refresh_tree()

    def _add_employee(self):
        name = self.name_entry.get().strip()
        pos = self.pos_entry.get().strip()
        sal_text = self.sal_entry.get().strip()
        dept_name = self.dept_var.get()

        if not all([name, pos, sal_text]):
            return

        try:
            salary = int(sal_text)
        except ValueError:
            return

        emp = Employee(name, pos, salary)

        # Находим куда добавлять
        if dept_name == "Головной офис":
            self.branch.add(emp)
        else:
            for child in self.branch.get_children():
                if child.get_name() == dept_name:
                    child.add(emp)
                    break

        self._refresh_tree()
        self.name_entry.delete(0, tk.END)
        self.pos_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._add_to_tree(self.branch, "")

        total = self.branch.get_salary()
        self.branch_label.config(text=f"Фонд филиала: {total:,} руб.")

    def _add_to_tree(self, component, prefix):
        name = component.get_name()
        salary = component.get_salary()
        self.tree.insert("", tk.END, values=(f"{prefix}{name}", f"{salary:,}"))

        if hasattr(component, "get_children"):
            for child in component.get_children():
                self._add_to_tree(child, prefix + "  ")

    # ======================== ДЕКОРАТОР ========================

    def _calculate_decorator(self):
        name = self.dec_name_entry.get().strip()
        sal_text = self.dec_sal_entry.get().strip()

        if not all([name, sal_text]):
            return

        try:
            base = int(sal_text)
        except ValueError:
            return

        # Создаём базового сотрудника
        emp = BaseEmployee(name, base)
        description = f"BaseEmployee({name}, {base:,})"

        self.decorator_log = [description]

        # Применяем декораторы
        if self.seniority_var.get():
            years = int(self.seniority_spin.get())
            emp = SeniorityDecorator(emp, years)
            desc = f"SeniorityDecorator({years}г, +{int(base * years * 0.10):,})"
            self.decorator_log.append(desc)

        if self.category_var.get():
            bonus = int(self.category_spin.get())
            emp = CategoryDecorator(emp, bonus)
            self.decorator_log.append(f"CategoryDecorator(+{bonus:,})")

        if self.bonus_var.get():
            bonus = int(self.bonus_spin.get())
            emp = BonusDecorator(emp, bonus)
            self.decorator_log.append(f"BonusDecorator(+{bonus:,})")

        total = emp.get_salary()

        # Показываем лог
        self.dec_log.delete(1.0, tk.END)
        for i, step in enumerate(self.decorator_log):
            if i == 0:
                self.dec_log.insert(tk.END, f"{i+1}. {step}\n")
            else:
                self.dec_log.insert(tk.END, f"   └─ {step}\n")
            self.dec_log.insert(tk.END, f"      get_salary() = {emp.get_salary():,}\n")

        self.dec_total.config(text=f"Итого: {total:,} руб. (база: {base:,})")

    def _update_decorators(self):
        pass


def main():
    root = tk.Tk()
    app = CompositeDecoratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
