"""
Лабораторная работа 5: Паттерны Фасад + Приспособленец (Flyweight)
Предметная область: Филиалы и сотрудники

Фасад — упрощаем сложный расчёт зарплаты (налоги, страховые, бонусы)
  через один метод calculate_payroll().

Приспособленец (Flyweight) — разделяем общие данные (отделы) между
  сотрудниками. 1000 сотрудников с 5 отделами = 5 объектов отделов,
  а не 1000 копий.
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# Часть 1: Приспособленец (Flyweight) — отделы
# ============================================================

class DepartmentFlyweight:
    """
    Легковесный объект — отдел.
    Общие данные хранятся один раз и разделяются между сотрудниками.
    """

    def __init__(self, name, budget, manager):
        self.name = name
        self.budget = budget
        self.manager = manager

    def __repr__(self):
        return f"Dept({self.name})"


class DepartmentFactory:
    """
    Фабрика легковесных объектов.
    Хранит созданные отделы и возвращает существующие,
    а не создаёт новые.
    """

    _departments = {}

    @classmethod
    def get_department(cls, name, budget, manager):
        """
        Возвращает существующий отдел или создаёт новый.
        Ключ — название отдела.
        """
        key = name
        if key not in cls._departments:
            cls._departments[key] = DepartmentFlyweight(name, budget, manager)
            print(f"  [CREATE] {key} -> {cls._departments[key]}")
        else:
            print(f"  [REUSE]  {key} -> {cls._departments[key]} (из кеша)")
        return cls._departments[key]

    @classmethod
    def get_stats(cls):
        """Статистика: сколько отделов создано vs сколько запросов"""
        return len(cls._departments)


# ============================================================
# Часть 2: Фасад — расчёт зарплаты
# ============================================================

class TaxCalculator:
    """Налоги"""

    def calculate_income_tax(self, salary):
        return int(salary * 0.13)  # НДФЛ 13%

    def calculate_social_tax(self, salary):
        return int(salary * 0.30)  # Страховые 30%


class BonusCalculator:
    """Бонусы"""

    def calculate_bonus(self, salary, bonus_percent):
        return int(salary * bonus_percent / 100)


class DeductionCalculator:
    """Вычеты"""

    def calculate_deductions(self, salary, has_children):
        if has_children:
            return int(salary * 0.04)  # Стандартный вычет 4%
        return 0


class PayrollFacade:
    """
    Фасад — упрощённый интерфейс для расчёта зарплаты.
    Клиент вызывает один метод и не знает о налогах, страховых, вычетах.
    """

    def __init__(self):
        self.tax = TaxCalculator()
        self.bonus = BonusCalculator()
        self.deduction = DeductionCalculator()

    def calculate_payroll(self, base_salary, bonus_percent=0, has_children=False):
        """
        Фасад: один метод — полный расчёт зарплаты.

        Args:
            base_salary: базовая зарплата
            bonus_percent: процент премии
            has_children: есть дети (для вычета)

        Returns:
            dict с полным расчётом
        """
        income_tax = self.tax.calculate_income_tax(base_salary)
        social_tax = self.tax.calculate_social_tax(base_salary)
        bonus = self.bonus.calculate_bonus(base_salary, bonus_percent)
        deductions = self.deduction.calculate_deductions(base_salary, has_children)

        total = base_salary + bonus - income_tax - deductions

        return {
            "base": base_salary,
            "bonus": bonus,
            "income_tax": income_tax,
            "social_tax": social_tax,
            "deductions": deductions,
            "total": total,
        }

    def get_summary(self, result):
        """Форматирует результат для отображения"""
        lines = [
            f"  Базовая:      {result['base']:>8,} руб.",
            f"  Премия:       {result['bonus']:>8,} руб.",
            f"  НДФЛ (13%):  -{result['income_tax']:>8,} руб.",
            f"  Страховые:   -{result['social_tax']:>8,} руб.",
            f"  Вычеты:      -{result['deductions']:>8,} руб.",
            f"  {'='*30}",
            f"  ИТОГО:        {result['total']:>8,} руб.",
        ]
        return "\n".join(lines)


# ============================================================
# GUI
# ============================================================

class FacadeFlyweightApp:
    """GUI для демонстрации Фасад + Приспособленец"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 5: Фасад + Приспособленец")
        self.root.geometry("1100x600")

        self.employees = []
        self.facade = PayrollFacade()
        self.flyweight_log = []

        self._create_layout()

    def _create_layout(self):
        # === ЛЕВАЯ: Приспособленец ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Приспособленец (Flyweight): Отделы",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Отделы создаются ОДИН РАЗ и разделяются", font=("Arial", 9)).pack(anchor=tk.W)

        # Форма
        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        tk.Button(left, text="Добавить сотрудника", command=self._add_employee,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # Лог приспособленца
        self.fly_log = tk.Text(left, width=35, height=10, font=("Consolas", 9))
        self.fly_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Статистика
        self.fly_stats = tk.Label(left, text="Отделов создано: 0",
                                  font=("Arial", 10, "bold"), fg="#8e44ad")
        self.fly_stats.pack(pady=5)

        # Таблица
        tk.Label(left, text="Сотрудники:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        tree_frame = tk.Frame(left)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "salary")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("salary", text="Зарплата")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # === ПРАВАЯ: Фасад ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Фасад: Расчёт зарплаты",
                 font=("Arial", 11, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(right, text="Один метод — полный расчёт (налоги, страховые, вычеты)",
                 font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(right, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.dec_name_entry = tk.Entry(right, width=30)
        self.dec_name_entry.pack(fill=tk.X, pady=2)

        tk.Label(right, text="Базовая зарплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dec_sal_entry = tk.Entry(right, width=30)
        self.dec_sal_entry.pack(fill=tk.X, pady=2)

        tk.Label(right, text="Премия (%):", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.bonus_entry = tk.Entry(right, width=30)
        self.bonus_entry.insert(0, "0")
        self.bonus_entry.pack(fill=tk.X, pady=2)

        self.children_var = tk.IntVar()
        tk.Checkbutton(right, text="Есть дети (вычет 4%)",
                       variable=self.children_var).pack(anchor=tk.W, pady=5)

        tk.Button(right, text="Рассчитать зарплату", command=self._calculate,
                  bg="#8e44ad", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # Лог фасада
        self.facade_log = tk.Text(right, width=40, height=12, font=("Consolas", 9))
        self.facade_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Сравнение
        tk.Label(right, text="Сравнение без фасада:", font=("Arial", 9, "bold"), fg="#e74c3c").pack(anchor=tk.W, pady=(5, 0))
        self.compare_log = tk.Text(right, width=40, height=8, font=("Consolas", 8), fg="#e74c3c")
        self.compare_log.pack(fill=tk.BOTH, expand=True)

    # ======================== ПРИСПОСОБЛЕНЕЦ ========================

    def _add_employee(self):
        name = self.name_entry.get().strip()
        dept_name = self.dept_entry.get().strip()
        sal_text = self.sal_entry.get().strip()

        if not all([name, dept_name, sal_text]):
            return

        try:
            salary = int(sal_text)
        except ValueError:
            return

        # Приспособленец: получаем отдел из фабрики
        dept = DepartmentFactory.get_department(dept_name, 0, "")
        self.flyweight_log.append(dept)

        emp = {"name": name, "department": dept_name, "salary": salary, "flyweight": dept}
        self.employees.append(emp)

        self._refresh_tree()
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

        self.fly_stats.config(text=f"Отделов создано: {DepartmentFactory.get_stats()}")

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.employees:
            self.tree.insert("", tk.END, values=(emp["name"], emp["department"], f"{emp['salary']:,}"))

    # ======================== ФАСАД ========================

    def _calculate(self):
        name = self.dec_name_entry.get().strip()
        sal_text = self.dec_sal_entry.get().strip()
        bonus_text = self.bonus_entry.get().strip()

        if not all([name, sal_text]):
            return

        try:
            base = int(sal_text)
            bonus = int(bonus_text)
        except ValueError:
            return

        has_children = bool(self.children_var.get())

        # ФАСАД: один метод — полный расчёт
        result = self.facade.calculate_payroll(base, bonus, has_children)

        # Показываем результат фасада
        self.facade_log.delete(1.0, tk.END)
        self.facade_log.insert(tk.END, f"Расчёт для: {name}\n")
        self.facade_log.insert(tk.END, self.facade.get_summary(result))

        # Показываем как было БЕЗ фасада
        self.compare_log.delete(1.0, tk.END)
        self.compare_log.insert(tk.END, "БЕЗ фасада (клиент должен знать всё):\n")
        self.compare_log.insert(tk.END, "  tax = TaxCalculator()\n")
        self.compare_log.insert(tk.END, "  tax.calculate_income_tax(base)\n")
        self.compare_log.insert(tk.END, "  tax.calculate_social_tax(base)\n")
        self.compare_log.insert(tk.END, "  bonus = BonusCalculator()\n")
        self.compare_log.insert(tk.END, "  bonus.calculate_bonus(base, 10)\n")
        self.compare_log.insert(tk.END, "  deduction = DeductionCalculator()\n")
        self.compare_log.insert(tk.END, "  deduction.calculate_deductions(base, True)\n")
        self.compare_log.insert(tk.END, "  total = base + bonus - tax1 - tax2 - ded\n")
        self.compare_log.insert(tk.END, "\nС ФАСАДОМ (один метод):\n")
        self.compare_log.insert(tk.END, "  result = facade.calculate_payroll(base, bonus, has_children)\n")
        self.compare_log.insert(tk.END, "  # Всё внутри — налоги, страховые, вычеты\n")

    def _refresh_flyweight_log(self):
        pass


def main():
    root = tk.Tk()
    app = FacadeFlyweightApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
