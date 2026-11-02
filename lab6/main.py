"""
Лабораторная работа 6: Паттерн Заместитель (Proxy)
Предметная область: Филиалы и сотрудники

Заместитель (Proxy) — оборачивает объект и контролирует доступ.
  - LazyProxy: ленивая загрузка данных (загружаются только при обращении)
  - AccessProxy: контроль доступа (стажёр не видит зарплату)
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# Заместитель (Proxy) — EmployeeProxy
# ============================================================

class Employee:
    """
    Реальный объект — сотрудник с полными данными.
    Данные могут быть тяжёлыми (загрузка из БД, расчёты).
    """

    def __init__(self, name, department, position, salary, bonus, has_children):
        self.name = name
        self.department = department
        self.position = position
        self.salary = salary
        self.bonus = bonus
        self.has_children = has_children

    def get_full_info(self):
        """Возвращает все данные сотрудника"""
        return {
            "name": self.name,
            "department": self.department,
            "position": self.position,
            "salary": self.salary,
            "bonus": self.bonus,
            "has_children": self.has_children,
            "total": self.salary + self.bonus,
        }

    def get_salary(self):
        return self.salary

    def get_bonus(self):
        return self.bonus

    def get_total(self):
        return self.salary + self.bonus

    def __repr__(self):
        return f"{self.name} | {self.department} | {self.position}"


class EmployeeProxy:
    """
    Заместитель для Employee.
    Контролирует доступ к реальному объекту.
    """

    def __init__(self, name, department, position, role="employee"):
        self.name = name
        self.department = department
        self.position = position
        self.role = role  # "manager" или "employee" (стажёр)
        self._real_employee = None  # Реальный объект загружается лениво

    def _ensure_loaded(self):
        """Ленивая загрузка — создаём реальный объект только при первом обращении"""
        if self._real_employee is None:
            print(f"  [LAZY LOAD] Загружаю данные для '{self.name}' из БД...")
            self._real_employee = self._load_from_database()
            print(f"  [OK] Данные загружены: {self._real_employee}")

    def _load_from_database(self):
        """Симулируем тяжёлую загрузку из БД"""
        # В реальности: запрос к БД, расчёты, сетевые вызовы
        # Здесь — генерируем данные
        import hashlib
        seed = hash(self.name) % 100000
        salary = 50000 + (seed % 50000)
        bonus = 5000 + (seed % 20000)
        has_children = seed % 3 == 0
        return Employee(self.name, self.department, self.position, salary, bonus, has_children)

    def get_full_info(self):
        """Защищённый доступ — проверяем роль перед возвратом данных"""
        self._ensure_loaded()  # 1. Загружаем данные
        self._check_access()   # 2. Проверяем права
        return self._real_employee.get_full_info()

    def get_salary(self):
        self._ensure_loaded()
        self._check_access()
        return self._real_employee.get_salary()

    def get_bonus(self):
        self._ensure_loaded()
        self._check_access()
        return self._real_employee.get_bonus()

    def get_total(self):
        self._ensure_loaded()
        self._check_access()
        return self._real_employee.get_total()

    def get_basic_info(self):
        """Базовая информация — доступна ВСЕМ, даже без загрузки"""
        return f"{self.name} | {self.department} | {self.position}"

    def _check_access(self):
        """Проверяем права доступа"""
        if self.role == "employee":
            raise PermissionError("Доступ запрещён: у вас нет прав на просмотр зарплат")

    def __repr__(self):
        return f"Proxy({self.name}, role={self.role})"


# ============================================================
# GUI
# ============================================================

class ProxyApp:
    """GUI для демонстрации Заместителя"""

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная 6: Заместитель (Proxy)")
        self.root.geometry("1000x580")

        self.employees = []
        self.proxy_log = []

        self._create_layout()

    def _create_layout(self):
        # === ЛЕВАЯ: Форма ===
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="Заместитель (Proxy):",
                 font=("Arial", 11, "bold"), fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Lazy load — данные загружаются только при обращении",
                 font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(left, text="Access control — стажёр не видит зарплату",
                 font=("Arial", 9)).pack(anchor=tk.W)

        tk.Label(left, text="ФИО:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.name_entry = tk.Entry(left, width=30)
        self.name_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Отдел:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.dept_entry = tk.Entry(left, width=30)
        self.dept_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Должность:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.pos_entry = tk.Entry(left, width=30)
        self.pos_entry.pack(fill=tk.X, pady=2)

        tk.Label(left, text="Роль:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 0))
        self.role_var = tk.StringVar(value="manager")
        ttk.Combobox(left, textvariable=self.role_var,
                     values=["manager", "employee"], state="readonly",
                     width=27).pack(fill=tk.X, pady=2)

        tk.Button(left, text="Добавить (с Proxy)", command=self._add_employee,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

        # Кнопки тестирования
        btn_frame = tk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="Посмотреть данные", command=self._view_data,
                  bg="#3498db", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Посмотреть зарплату", command=self._view_salary,
                  bg="#f39c12", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        # Лог
        self.log = tk.Text(left, width=35, height=16, font=("Consolas", 9))
        self.log.pack(fill=tk.BOTH, expand=True, pady=5)

        # === ПРАВАЯ: Таблица ===
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Сотрудники:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        tree_frame = tk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "department", "position", "role", "loaded")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=16)
        self.tree.heading("name", text="ФИО")
        self.tree.heading("department", text="Отдел")
        self.tree.heading("position", text="Должность")
        self.tree.heading("role", text="Роль")
        self.tree.heading("loaded", text="Данные загружены")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    # ======================== PROXY ========================

    def _add_employee(self):
        name = self.name_entry.get().strip()
        dept = self.dept_entry.get().strip()
        pos = self.pos_entry.get().strip()
        role = self.role_var.get()

        if not all([name, dept, pos]):
            return

        # Создаём ЗАМЕСТИТЕЛЯ, а не реального сотрудника
        proxy = EmployeeProxy(name, dept, pos, role)
        self.employees.append(proxy)

        self.log.insert(tk.END, f"\n[CREATE] proxy = EmployeeProxy('{name}', role='{role}')\n")
        self.log.insert(tk.END, f"  _real_employee = None  # Данные ещё НЕ загружены\n")
        self.log.insert(tk.END, f"  proxy.get_basic_info() -> '{proxy.get_basic_info()}'\n")
        self.log.insert(tk.END, f"  # get_basic_info() НЕ требует загрузки — возвращает базовые данные\n")

        self._refresh_tree()
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.pos_entry.delete(0, tk.END)

    def _view_data(self):
        if not self.employees:
            self.log.insert(tk.END, "\n[ERROR] Нет сотрудников\n")
            return

        proxy = self.employees[-1]
        self.log.insert(tk.END, f"\n[CALL] proxy.get_full_info()\n")

        try:
            info = proxy.get_full_info()
            self.log.insert(tk.END, f"[OK] {info}\n")
            self._refresh_tree()
        except PermissionError as e:
            self.log.insert(tk.END, f"[ACCESS DENIED] {e}\n")

    def _view_salary(self):
        if not self.employees:
            self.log.insert(tk.END, "\n[ERROR] Нет сотрудников\n")
            return

        proxy = self.employees[-1]
        self.log.insert(tk.END, f"\n[CALL] proxy.get_salary()\n")

        try:
            salary = proxy.get_salary()
            self.log.insert(tk.END, f"[OK] Зарплата: {salary:,} руб.\n")
            self._refresh_tree()
        except PermissionError as e:
            self.log.insert(tk.END, f"[ACCESS DENIED] {e}\n")

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for proxy in self.employees:
            loaded = "Да" if proxy._real_employee is not None else "Нет"
            self.tree.insert("", tk.END, values=(
                proxy.name, proxy.department, proxy.position,
                proxy.role, loaded))


def main():
    root = tk.Tk()
    app = ProxyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
