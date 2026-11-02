"""
Исходная программа: Филиалы и сотрудники
Без использования паттернов проектирования

Простой менеджер сотрудников:
- Добавление сотрудников
- Просмотр списка
- Фильтрация по отделу
- Расчёт фонда оплаты
"""

import tkinter as tk
from tkinter import ttk


class Employee:
    """Сотрудник"""

    def __init__(self, name, department, salary, position):
        self.name = name
        self.department = department
        self.salary = salary
        self.position = position

    def __repr__(self):
        return f"{self.name} | {self.department} | {self.position} | {self.salary} руб."


class Branch:
    """Филиал — набор сотрудников"""

    def __init__(self, name):
        self.name = name
        self.employees = []

    def add_employee(self, emp):
        self.employees.append(emp)

    def remove_employee(self, name):
        self.employees = [e for e in self.employees if e.name != name]

    def get_by_department(self, dept):
        return [e for e in self.employees if e.department == dept]

    def total_salary(self):
        return sum(e.salary for e in self.employees)


class BranchApp:
    """GUI: Филиалы и сотрудники"""

    def __init__(self, root):
        self.root = root
        self.root.title("Филиалы и сотрудники")
        self.root.geometry("700x500")

        self.branch = Branch("Главный офис")
        self._create_layout()

    def _create_layout(self):
        # Форма
        form = tk.LabelFrame(self.root, text="Добавить сотрудника", padx=10, pady=10)
        form.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form, text="ФИО:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.name_entry = tk.Entry(form, width=20)
        self.name_entry.grid(row=0, column=1, pady=3)

        tk.Label(form, text="Отдел:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=3)
        self.dept_entry = tk.Entry(form, width=15)
        self.dept_entry.grid(row=0, column=3, pady=3)

        tk.Label(form, text="Должность:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.pos_entry = tk.Entry(form, width=20)
        self.pos_entry.grid(row=1, column=1, pady=3)

        tk.Label(form, text="Зарплата:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=3)
        self.sal_entry = tk.Entry(form, width=15)
        self.sal_entry.grid(row=1, column=3, pady=3)

        tk.Button(form, text="Добавить", command=self._add,
                  bg="#27ae60", fg="white").grid(row=2, column=0, columnspan=4, pady=10)

        # Таблица
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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

        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Обновить", command=self._refresh,
                  bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить выбранного", command=self._remove,
                  bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)

        # Итого
        self.total_label = tk.Label(self.root, text="Фонд оплаты: 0 руб.",
                                    font=("Arial", 11, "bold"), fg="#2c3e50")
        self.total_label.pack(pady=5)

        self._refresh()

    def _add(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        pos = self.pos_entry.get().strip()
        sal_text = self.sal_entry.get().strip()

        if not all([name, dept, pos, sal_text]):
            return

        try:
            salary = int(sal_text)
        except ValueError:
            return

        emp = Employee(name, dept, salary, pos)
        self.branch.add_employee(emp)
        self._refresh()

        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.pos_entry.delete(0, tk.END)
        self.sal_entry.delete(0, tk.END)

    def _remove(self):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel[0])["values"][0]
        self.branch.remove_employee(name)
        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.branch.employees:
            self.tree.insert("", tk.END, values=(emp.name, emp.department,
                                                 emp.position, f"{emp.salary:,}"))

        total = self.branch.total_salary()
        self.total_label.config(text=f"Фонд оплаты: {total:,} руб. | Сотрудников: {len(self.branch.employees)}")


def main():
    root = tk.Tk()
    app = BranchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
