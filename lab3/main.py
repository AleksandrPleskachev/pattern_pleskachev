"""
Лабораторная работа 3: Паттерны Адаптер + Мост
Предметная область: Филиалы и сотрудники

Адаптер — оборачиваем разные источники данных (CSV, JSON) в единый интерфейс.
Мост   — разделяем иерархию сотрудников (штатный/контрактный) и способы оплаты (почасовая/месячная/сдельная).
"""

import tkinter as tk
from tkinter import ttk
import csv
import json
import io
import os


# ============================================================
# Часть 1: Мост — Employee + PayStrategy
# ============================================================

class PayStrategy:
    """Мост: способ оплаты"""

    def calculate_salary(self, base_salary, extra=0):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__


class MonthlyPay(PayStrategy):
    """Фиксированная месячная зарплата"""

    def calculate_salary(self, base_salary, extra=0):
        return base_salary + extra

    def __repr__(self):
        return "Почасовая оплата"


class HourlyPay(PayStrategy):
    """Оплата по часам"""

    def calculate_salary(self, base_salary, extra=0):
        hours = base_salary  # base_salary здесь — кол-во часов
        return hours * 500 + extra  # 500 руб/час

    def __repr__(self):
        return "Почасовая оплата"


class PieceworkPay(PayStrategy):
    """Сдельная оплата"""

    def calculate_salary(self, base_salary, extra=0):
        # base_salary — количество выполненных заданий
        return base_salary * 1500 + extra  # 1500 руб/задание

    def __repr__(self):
        return "Сдельная оплата"


class Employee:
    """
    Мост: Employee использует PayStrategy через композицию.
    Два измерения независимы:
      - тип сотрудника (штатный / контрактный)
      - способ оплаты (почасовая / месячная / сдельная)
    """

    def __init__(self, name, department, position, base_salary, pay_strategy):
        self.name = name
        self.department = department
        self.position = position
        self.base_salary = base_salary
        self.pay_strategy = pay_strategy  # <-- МОСТ: встраиваем стратегию

    def get_salary(self):
        """Рассчитывает зарплату через мост"""
        return self.pay_strategy.calculate_salary(self.base_salary)

    def __repr__(self):
        return f"{self.name} | {self.department} | {self.pay_strategy} | {self.get_salary():,} руб."


# ============================================================
# Часть 2: Адаптер — источники данных
# ============================================================

class DataSource:
    """Абстрактный источник данных"""

    def get_employees(self):
        raise NotImplementedError


class CSVDataSource(DataSource):
    """Нативный CSV-источник"""

    def __init__(self, data):
        self.data = data  # список словарей

    def get_employees(self):
        """Возвращает список словарей: [{name, department, ...}, ...]"""
        return self.data


class JSONDataSource(DataSource):
    """JSON-источник — НЕ совпадает с интерфейсом CSVDataSource"""

    def __init__(self, data):
        self.data = data  # словарь: {"staff": [{...}, ...]}

    def get_raw_data(self):
        """JSON возвращает данные в формате {"staff": [...]}"""
        return self.data.get("staff", [])


class JSONToCSVAdapter(DataSource):
    """
    АДАПТЕР — оборачивает JSONDataSource и приводит его к интерфейсу DataSource.
    Клиент вызывает get_employees() и не знает, что внутри JSON.
    """

    def __init__(self, json_source):
        self.json_source = json_source  # оборачиваем JSON

    def get_employees(self):
        """Приводим JSON к формату CSV: просто список словарей"""
        raw = self.json_source.get_raw_data()
        return raw  # возвращаем тот же формат, что и CSVDataSource


# ============================================================
# GUI
# ============================================================

class AdapterBridgeApp:
    """GUI для демонстрации Адаптер + Мост"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 3: Адаптер + Мост")
        self.root.geometry("1000x580")

        self.employees = []
        self.sources_used = 0

        self._create_layout()

    def _create_layout(self):
        # === ЛЕВАЯ: Мост ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Мост: Employee + PayStrategy",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Два независимых измерения:", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(left, text="  1. Тип сотрудника: штатный / контрактный", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(left, text="  2. Способ оплаты: почасовая / месячная / сдельная", font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Должность:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.pos_entry = tk.Entry(left, width=30)
        self.pos_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="База (часы/задания/руб):", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.sal_entry = tk.Entry(left, width=30)
        self.sal_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Сотрудник:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.type_var = tk.StringVar(value="штатный")
        ttk.Combobox(left, textvariable=self.type_var,
                     values=["штатный", "контрактный"], state="readonly",
                     width=27).pack(fill=tk.X, pady=2)

        tk.Label(left, text="Оплата:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.pay_var = tk.StringVar(value="monthly")
        pay_opts = [("monthly", "Месячная (фикс)"),
                    ("hourly", "Почасовая (500 руб/час)"),
                    ("piecework", "Сдельная (1500 руб/задание)")]
        for val, desc in pay_opts:
            ttk.Radiobutton(left, text=desc, variable=self.pay_var, value=val).pack(anchor=tk.W)

        tk.Button(left, text="Создать (Мост)", command=self._create_with_bridge,
                  bg="#2c3e50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        # Лог моста
        self.bridge_log = tk.Text(left, width=35, height=6, font=("Consolas", 9))
        self.bridge_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.bridge_log.insert(tk.END, "# Мост: Employee + PayStrategy\n")
        self.bridge_log.insert(tk.END, "# pay_strategy встраивается в employee\n")
        self.bridge_log.insert(tk.END, "# employee.get_salary() вызывает pay_strategy.calculate_salary()\n")

        # === ПРАВАЯ: Адаптер ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Адаптер: DataSource",
                 font=("Arial", 11, "bold"), fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(right, text="CSV и JSON — разные форматы.", font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(right, text="Адаптер приводит JSON к формату CSV.", font=("Arial", 9)).pack(anchor=tk.W)

        # Кнопки загрузки
        tk.Button(right, text="Загрузить CSV", command=self._load_csv,
                  bg="#3498db", fg="white", font=("Arial", 9, "bold")).pack(pady=5)
        tk.Button(right, text="Загрузить JSON (через Адаптер)", command=self._load_json,
                  bg="#9b59b6", fg="white", font=("Arial", 9, "bold")).pack(pady=5)

        self.adapter_log = tk.Text(right, width=35, height=6, font=("Consolas", 9))
        self.adapter_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.adapter_log.insert(tk.END, "# Адаптер: JSONDataSource -> JSONToCSVAdapter\n")
        self.adapter_log.insert(tk.END, "# get_employees() работает одинаково\n")

        # Таблица
        tk.Label(right, text="Все сотрудники:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
        tree_frame = tk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "position", "type", "pay", "salary")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=14)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("position", text="Должность")
        self.tree.heading("type", text="Тип")
        self.tree.heading("pay", text="Оплата")
        self.tree.heading("salary", text="Зарплата")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.total_label = tk.Label(right, text="Всего: 0 | Фонд: 0 руб.",
                                    font=("Arial", 10, "bold"), fg="#2c3e50")
        self.total_label.pack(pady=5)

    # ======================== МОСТ ========================

    def _create_with_bridge(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        pos = self.pos_entry.get().strip()
        sal_text = self.sal_entry.get().strip()
        emp_type = self.type_var.get()
        pay_type = self.pay_var.get()

        if not all([name, dept, pos, sal_text]):
            return

        try:
            base = int(sal_text)
        except ValueError:
            return

        # Создаём стратегию оплаты (Мост)
        if pay_type == "monthly":
            pay = MonthlyPay()
        elif pay_type == "hourly":
            pay = HourlyPay()
        else:
            pay = PieceworkPay()

        # Создаём сотрудника с встраиваемой стратегией
        emp = Employee(name, dept, pos, base, pay)
        emp.emp_type = emp_type
        self.employees.append(emp)

        self.bridge_log.insert(tk.END, f"\n# pay = {pay}\n")
        self.bridge_log.insert(tk.END, f"# emp = Employee('{name}', '{dept}', '{pos}', {base}, pay)\n")
        self.bridge_log.insert(tk.END, f"# emp.get_salary() -> {pay}.calculate_salary({base}) = {emp.get_salary():,}\n")

        self._refresh()
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.pos_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

    # ======================== АДАПТЕР ========================

    def _load_csv(self):
        csv_data = [
            {"name": "Козлов А.С.", "department": "Продажи", "position": "Менеджер", "base_salary": 60000, "type": "штатный"},
            {"name": "Смирнова Е.В.", "department": "IT", "position": "Разработчик", "base_salary": 80000, "type": "штатный"},
            {"name": "Новиков Д.П.", "department": "Логистика", "position": "Водитель", "base_salary": 40, "type": "контрактный"},
        ]
        source = CSVDataSource(csv_data)
        data = source.get_employees()
        self._process_data(data, "CSV")
        self.adapter_log.insert(tk.END, f"\n[CSV] get_employees() -> {len(data)} записей\n")
        self.adapter_log.insert(tk.END, f"       Тип: CSVDataSource (нативный)\n")
        self.adapter_log.insert(tk.END, f"       Данные: {data}\n")

    def _load_json(self):
        json_data = {"staff": [
            {"name": "Волков И.И.", "department": "Бухгалтерия", "position": "Бухгалтер", "base_salary": 55000, "type": "штатный"},
            {"name": "Лебедева О.Н.", "department": "HR", "position": "Рекрутер", "base_salary": 30, "type": "контрактный"},
            {"name": "Соколов П.Р.", "department": "IT", "position": "Тестировщик", "base_salary": 70000, "type": "штатный"},
        ]}
        json_source = JSONDataSource(json_data)

        # АДАПТЕР оборачиваем JSONDataSource
        adapter = JSONToCSVAdapter(json_source)
        data = adapter.get_employees()  # тот же интерфейс, что и CSV!
        self._process_data(data, "JSON (адаптированный)")
        self.adapter_log.insert(tk.END, f"\n[JSON] adapter.get_employees() -> {len(data)} записей\n")
        self.adapter_log.insert(tk.END, f"       Тип: JSONToCSVAdapter (обёртка)\n")
        self.adapter_log.insert(tk.END, f"       JSON.get_raw_data() -> {data}\n")

    def _process_data(self, data, source_name):
        for item in data:
            pay = MonthlyPay() if item["type"] == "штатный" else HourlyPay()
            emp = Employee(item["name"], item["department"], item["position"],
                           item["base_salary"], pay)
            emp.emp_type = item["type"]
            self.employees.append(emp)
        self.sources_used += 1
        self._refresh()

    # ======================== ОБЩЕЕ ========================

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.employees:
            self.tree.insert("", tk.END, values=(
                emp.name, emp.department, emp.position,
                emp.emp_type, repr(emp.pay_strategy), f"{emp.get_salary():,}"))

        total = sum(e.get_salary() for e in self.employees)
        self.total_label.config(text=f"Всего: {len(self.employees)} | Фонд: {total:,} руб. | Источников: {self.sources_used}")


def main():
    root = tk.Tk()
    app = AdapterBridgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
