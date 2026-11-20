"""
Лабораторная работа 11: Паттерны Стратегия + Шаблонный метод
Предметная область: Филиалы и сотрудники

Стратегия — способ расчёта оплаты подменяется без смены
остального кода: оклад, почасовая, оклад с премией.

Шаблонный метод — общий скелет отчёта (шапка, тело, итог),
а оформление шагов задают текстовый и HTML-отчёты.
"""

import tkinter as tk
from tkinter import ttk


class Employee:
    def __init__(self, name, department, scheme, base, hours, rate, bonus):
        self.name = name
        self.department = department
        self.scheme = scheme
        self.base = base
        self.hours = hours
        self.rate = rate
        self.bonus = bonus


class PayStrategy:
    title = "стратегия"

    def calculate(self, employee):
        raise NotImplementedError


class FixedStrategy(PayStrategy):
    title = "оклад"

    def calculate(self, employee):
        return employee.base


class HourlyStrategy(PayStrategy):
    title = "почасовая"

    def calculate(self, employee):
        return employee.hours * employee.rate


class BonusStrategy(PayStrategy):
    title = "оклад + премия"

    def calculate(self, employee):
        return employee.base + int(employee.base * employee.bonus / 100)


STRATEGIES = {
    "оклад": FixedStrategy(),
    "почасовая": HourlyStrategy(),
    "оклад + премия": BonusStrategy(),
}


class PayrollContext:
    """Контекст стратегии. Алгоритм подменяется через set_strategy."""

    def __init__(self):
        self.strategy = FixedStrategy()

    def set_strategy(self, strategy):
        self.strategy = strategy

    def amount(self, employee):
        self.set_strategy(STRATEGIES[employee.scheme])
        return self.strategy.calculate(employee)


class ReportTemplate:
    """Шаблонный метод: порядок шагов зафиксирован в generate()."""

    def generate(self, title, rows):
        total = sum(row["amount"] for row in rows)
        return "\n".join([
            self.header(title),
            self.body(rows),
            self.footer(len(rows), total),
        ])

    def header(self, title):
        raise NotImplementedError

    def body(self, rows):
        raise NotImplementedError

    def footer(self, count, total):
        raise NotImplementedError


class TextReport(ReportTemplate):
    def header(self, title):
        return "=== {} ===".format(title)

    def body(self, rows):
        lines = []
        for row in rows:
            lines.append("{:16} | {:16} | {:>10,} | {}".format(
                row["name"], row["department"], row["amount"], row["scheme"]))
        return "\n".join(lines) if lines else "(нет сотрудников)"

    def footer(self, count, total):
        return "---\nСотрудников: {} | Фонд: {:,} руб.".format(count, total)


class HtmlReport(ReportTemplate):
    def header(self, title):
        return "<h1>{}</h1>\n<table>".format(title)

    def body(self, rows):
        lines = ["<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            row["name"], row["department"], row["amount"], row["scheme"]) for row in rows]
        return "\n".join(lines) if lines else "<tr><td>пусто</td></tr>"

    def footer(self, count, total):
        return "</table>\n<p>Сотрудников: {} | Фонд: {:,}</p>".format(count, total)


class StrategyTemplateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР11 — Стратегия и Шаблонный метод")
        self.root.geometry("980x600")
        self.employees = []
        self.payroll = PayrollContext()
        self.reports = {"текст": TextReport(), "HTML": HtmlReport()}
        self._build()

    def _build(self):
        left = tk.Frame(self.root, padx=10, pady=8)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Стратегия (Strategy)", font=("Arial", 13, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Схема оплаты подменяется объектом-стратегией",
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 6))

        self.name = self._entry(left, "ФИО")
        self.dept = self._entry(left, "Отдел")
        self.scheme = ttk.Combobox(left, values=list(STRATEGIES.keys()), state="readonly")
        self.scheme.set("оклад")
        self.scheme.pack(fill=tk.X, pady=4)
        self.base = self._entry(left, "Оклад", "80000")
        self.hours = self._entry(left, "Часы", "160")
        self.rate = self._entry(left, "Ставка в час", "500")
        self.bonus = self._entry(left, "Премия, %", "15")

        tk.Button(left, text="Добавить сотрудника", command=self._add,
                  bg="#27ae60", fg="white").pack(fill=tk.X, pady=8)

        tk.Label(left, text="Шаблонный метод", font=("Arial", 12, "bold"),
                 fg="#8e44ad").pack(anchor=tk.W, pady=(8, 2))
        self.report_kind = ttk.Combobox(left, values=["текст", "HTML"], state="readonly")
        self.report_kind.set("текст")
        self.report_kind.pack(fill=tk.X)
        tk.Button(left, text="Сформировать отчёт", command=self._report,
                  bg="#8e44ad", fg="white").pack(fill=tk.X, pady=8)

        right = tk.Frame(self.root, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        columns = ("name", "dept", "scheme", "amount")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=8)
        for col, title in zip(columns, ("ФИО", "Отдел", "Стратегия", "К выплате")):
            self.tree.heading(col, text=title)
        self.tree.pack(fill=tk.X)
        self.output = tk.Text(right, font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True, pady=8)

    def _entry(self, parent, label, value=""):
        tk.Label(parent, text=label).pack(anchor=tk.W)
        entry = tk.Entry(parent, width=28)
        entry.insert(0, value)
        entry.pack(fill=tk.X, pady=(0, 4))
        return entry

    def _number(self, entry, default=0):
        text = entry.get().strip()
        if not text:
            return default
        return int(text)

    def _add(self):
        name = self.name.get().strip()
        dept = self.dept.get().strip()
        if not name or not dept:
            return
        try:
            employee = Employee(
                name, dept, self.scheme.get(),
                self._number(self.base), self._number(self.hours),
                self._number(self.rate), self._number(self.bonus),
            )
        except ValueError:
            self.output.insert(tk.END, "Числовые поля должны быть целыми.\n")
            return
        self.employees.append(employee)
        amount = self.payroll.amount(employee)
        self.tree.insert("", tk.END, values=(
            name, dept, employee.scheme, "{:,}".format(amount)))
        self.output.insert(tk.END, "[Strategy: {}] {} -> {:,} руб.\n".format(
            self.payroll.strategy.title, name, amount))
        self.output.see(tk.END)

    def _rows(self):
        rows = []
        for employee in self.employees:
            rows.append({
                "name": employee.name,
                "department": employee.department,
                "scheme": employee.scheme,
                "amount": self.payroll.amount(employee),
            })
        return rows

    def _report(self):
        kind = self.report_kind.get()
        report = self.reports[kind]
        text = report.generate("Фонд оплаты филиала", self._rows())
        self.output.insert(tk.END, "\n[Template Method: {}]\n".format(kind))
        self.output.insert(tk.END, "шаги: header() -> body() -> footer()\n")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)


def main():
    root = tk.Tk()
    StrategyTemplateApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
