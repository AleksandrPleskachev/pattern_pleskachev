"""
Лабораторная работа 12: Архитектурный паттерн MVC
Предметная область: Филиалы и сотрудники

Model хранит сотрудников и считает фонд.
View рисует форму и таблицу и не содержит бизнес-правил.
Controller принимает события интерфейса, меняет модель и обновляет вид.
"""

import tkinter as tk
from tkinter import ttk


class Employee:
    def __init__(self, name, department, position, salary):
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary


class EmployeeModel:
    """Модель: данные и операции, без tkinter."""

    def __init__(self):
        self.employees = []

    def add(self, employee):
        self.employees.append(employee)

    def remove(self, name):
        self.employees = [emp for emp in self.employees if emp.name != name]

    def by_department(self, department):
        if not department or department == "все":
            return list(self.employees)
        return [emp for emp in self.employees if emp.department == department]

    def payroll(self, rows):
        return sum(emp.salary for emp in rows)


class EmployeeView:
    """Вид: только виджеты. События отдаёт наружу через колбэки."""

    def __init__(self, root):
        self.root = root
        self.root.title("ЛР12 — MVC: филиалы и сотрудники")
        self.root.geometry("860x520")
        self.on_add = None
        self.on_remove = None
        self.on_filter = None

        form = tk.LabelFrame(root, text="Вид: форма (без логики)", padx=8, pady=8)
        form.pack(fill=tk.X, padx=10, pady=8)
        self.name = self._field(form, "ФИО", 0)
        self.department = self._field(form, "Отдел", 1)
        self.position = self._field(form, "Должность", 2)
        self.salary = self._field(form, "Зарплата", 3)
        tk.Button(form, text="Добавить", bg="#27ae60", fg="white",
                  command=self._click_add).grid(row=2, column=0, columnspan=2, pady=8, sticky=tk.W)
        tk.Button(form, text="Удалить выбранного", bg="#c0392b", fg="white",
                  command=self._click_remove).grid(row=2, column=2, columnspan=2, pady=8, sticky=tk.W)

        filt = tk.Frame(root)
        filt.pack(fill=tk.X, padx=10)
        tk.Label(filt, text="Фильтр отдела:").pack(side=tk.LEFT)
        self.filter_entry = tk.Entry(filt, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=6)
        tk.Button(filt, text="Показать", command=self._click_filter).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(root, columns=("name", "dept", "pos", "salary"),
                                  show="headings", height=12)
        for col, title in (("name", "ФИО"), ("dept", "Отдел"), ("pos", "Должность"), ("salary", "Зарплата")):
            self.tree.heading(col, text=title)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.total = tk.Label(root, text="Фонд: 0", font=("Arial", 11, "bold"))
        self.total.pack(anchor=tk.W, padx=12)
        self.log = tk.Text(root, height=6, font=("Consolas", 9))
        self.log.pack(fill=tk.X, padx=10, pady=6)

    def _field(self, parent, label, column):
        tk.Label(parent, text=label).grid(row=0, column=column, sticky=tk.W, padx=4)
        entry = tk.Entry(parent, width=18)
        entry.grid(row=1, column=column, padx=4, pady=2)
        return entry

    def read_form(self):
        return {
            "name": self.name.get().strip(),
            "department": self.department.get().strip(),
            "position": self.position.get().strip(),
            "salary": self.salary.get().strip(),
        }

    def selected_name(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return self.tree.item(selected[0])["values"][0]

    def filter_text(self):
        return self.filter_entry.get().strip()

    def show_rows(self, employees):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for emp in employees:
            self.tree.insert("", tk.END, values=(
                emp.name, emp.department, emp.position, "{:,}".format(emp.salary)))

    def show_total(self, count, total):
        self.total.config(text="Показано: {} | Фонд оплаты: {:,} руб.".format(count, total))

    def log_line(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def clear_form(self):
        for entry in (self.name, self.department, self.position, self.salary):
            entry.delete(0, tk.END)

    def _click_add(self):
        if self.on_add:
            self.on_add()

    def _click_remove(self):
        if self.on_remove:
            self.on_remove()

    def _click_filter(self):
        if self.on_filter:
            self.on_filter()


class EmployeeController:
    """Контроллер: связывает вид и модель."""

    def __init__(self, model, view):
        self.model = model
        self.view = view
        view.on_add = self.add_employee
        view.on_remove = self.remove_employee
        view.on_filter = self.apply_filter
        self.apply_filter()
        view.log_line("[MVC] Controller подписался на события View")
        view.log_line("[MVC] Model не знает о виджетах")

    def add_employee(self):
        form = self.view.read_form()
        if not all([form["name"], form["department"], form["position"], form["salary"]]):
            self.view.log_line("[Controller] форма заполнена не до конца")
            return
        try:
            salary = int(form["salary"])
        except ValueError:
            self.view.log_line("[Controller] зарплата должна быть числом")
            return
        if salary < 0:
            self.view.log_line("[Controller] зарплата не может быть отрицательной")
            return
        employee = Employee(form["name"], form["department"], form["position"], salary)
        self.model.add(employee)
        self.view.log_line("[Controller] Model.add({})".format(employee.name))
        self.view.clear_form()
        self.apply_filter()

    def remove_employee(self):
        name = self.view.selected_name()
        if not name:
            self.view.log_line("[Controller] сотрудник не выбран")
            return
        self.model.remove(name)
        self.view.log_line("[Controller] Model.remove({})".format(name))
        self.apply_filter()

    def apply_filter(self):
        department = self.view.filter_text()
        rows = self.model.by_department(department)
        self.view.show_rows(rows)
        self.view.show_total(len(rows), self.model.payroll(rows))
        self.view.log_line("[Controller] обновил View, отдел: {}".format(department or "все"))


def main():
    root = tk.Tk()
    model = EmployeeModel()
    view = EmployeeView(root)
    EmployeeController(model, view)
    root.mainloop()


if __name__ == "__main__":
    main()
