"""
Лабораторная работа 8: Паттерн Цепочка обязанностей
Предметная область: Филиалы и сотрудники

Заявка на повышение зарплаты идёт по цепочке согласующих.
Каждый обработчик либо одобряет заявку в пределах своего лимита,
либо передаёт её следующему.
"""

import tkinter as tk
from tkinter import ttk


class SalaryRequest:
    """Запрос, который путешествует по цепочке."""

    def __init__(self, employee, department, amount, reason):
        self.employee = employee
        self.department = department
        self.amount = amount
        self.reason = reason

    def __repr__(self):
        return "{} / {} / +{:,} руб. ({})".format(
            self.employee, self.department, self.amount, self.reason)


class ApprovalHandler:
    """Базовый обработчик цепочки."""

    def __init__(self, title, limit):
        self.title = title
        self.limit = limit
        self._next = None

    def set_next(self, handler):
        self._next = handler
        return handler

    def handle(self, request, log):
        log.append("[{}] получил заявку: {}".format(self.title, request))
        if request.amount <= self.limit:
            log.append("[{}] лимит {:,} руб. — заявка одобрена".format(self.title, self.limit))
            return {
                "approved": True,
                "by": self.title,
                "request": request,
            }
        log.append("[{}] лимит {:,} руб. меньше суммы — передаю дальше".format(
            self.title, self.limit))
        if self._next is not None:
            return self._next.handle(request, log)
        log.append("[конец цепочки] одобрить заявку некому")
        return {"approved": False, "by": None, "request": request}


def build_chain():
    team_lead = ApprovalHandler("Тимлид", 15000)
    dept_head = ApprovalHandler("Руководитель отдела", 50000)
    hr = ApprovalHandler("HR-директор", 120000)
    ceo = ApprovalHandler("Генеральный директор", 400000)
    team_lead.set_next(dept_head).set_next(hr).set_next(ceo)
    return team_lead


class ChainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР8 — Цепочка обязанностей")
        self.root.geometry("860x560")
        self.chain = build_chain()
        self.history = []
        self._build()

    def _build(self):
        left = tk.Frame(self.root, padx=12, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left, text="Цепочка обязанностей", font=("Arial", 13, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Тимлид → Руководитель → HR → Директор",
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 8))

        limits = (
            "Лимиты:\n"
            "  Тимлид — 15 000\n"
            "  Руководитель отдела — 50 000\n"
            "  HR-директор — 120 000\n"
            "  Генеральный директор — 400 000"
        )
        tk.Label(left, text=limits, justify=tk.LEFT, font=("Consolas", 9),
                 bg="#f4f6f7", padx=8, pady=8).pack(fill=tk.X, pady=6)

        self.name = self._field(left, "ФИО")
        self.dept = self._field(left, "Отдел")
        self.amount = self._field(left, "Сумма повышения")
        self.reason = self._field(left, "Причина")
        self.reason.insert(0, "пересмотр оклада")

        tk.Button(left, text="Отправить заявку", command=self._submit,
                  bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=12)

        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Журнал прохождения цепочки",
                 font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.log = tk.Text(right, font=("Consolas", 10), height=16)
        self.log.pack(fill=tk.BOTH, expand=True, pady=6)

        columns = ("employee", "amount", "result", "by")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=8)
        self.tree.heading("employee", text="Сотрудник")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("result", text="Решение")
        self.tree.heading("by", text="Кто одобрил")
        self.tree.column("employee", width=160)
        self.tree.column("amount", width=100)
        self.tree.column("result", width=110)
        self.tree.column("by", width=180)
        self.tree.pack(fill=tk.X)

    def _field(self, parent, label):
        tk.Label(parent, text=label, font=("Arial", 9)).pack(anchor=tk.W, pady=(6, 0))
        entry = tk.Entry(parent, width=32)
        entry.pack(fill=tk.X)
        return entry

    def _submit(self):
        name = self.name.get().strip()
        dept = self.dept.get().strip()
        reason = self.reason.get().strip() or "без указания причины"
        try:
            amount = int(self.amount.get().strip())
        except ValueError:
            self._write("Сумма должна быть целым числом.\n")
            return
        if not name or not dept or amount <= 0:
            self._write("Заполните ФИО, отдел и положительную сумму.\n")
            return

        request = SalaryRequest(name, dept, amount, reason)
        trace = []
        decision = self.chain.handle(request, trace)
        self._write("=" * 48 + "\n")
        for line in trace:
            self._write(line + "\n")
        if decision["approved"]:
            result = "одобрено"
            by = decision["by"]
            self._write("Итог: ОДОБРЕНО ({})\n".format(by))
        else:
            result = "отклонено"
            by = "—"
            self._write("Итог: ОТКЛОНЕНО, сумма выше полномочий директора\n")
        self.tree.insert("", tk.END, values=(name, "{:,}".format(amount), result, by))
        self.amount.delete(0, tk.END)

    def _write(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    ChainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
