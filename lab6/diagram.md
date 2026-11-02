@startuml
class Employee {
  +String name
  +String department
  +String position
  +int salary
  +int bonus
  +boolean has_children
  +get_full_info() dict
  +get_salary() int
  +get_bonus() int
}

class EmployeeProxy {
  +String name
  +String department
  +String position
  +String role
  -Employee _real_employee
  +get_basic_info() String
  +get_full_info() dict
  +get_salary() int
  +_ensure_loaded()
  +_check_access()
}

class GUI {
  +_add_employee()
  +_view_data()
  +_view_salary()
}

EmployeeProxy --> Employee : wraps (lazy load)
GUI --> EmployeeProxy : uses
@enduml

@startuml
participant User
participant GUI
participant Proxy
participant Employee

User -> GUI: Добавляет "Иванов", роль employee
GUI -> Proxy: EmployeeProxy("Иванов", role="employee")
Proxy -> Proxy: _real_employee = null

User -> GUI: Нажимает "Посмотреть зарплату"
GUI -> Proxy: proxy.get_salary()
Proxy -> Proxy: _ensure_loaded()
Proxy -> Employee: new Employee(...)
Proxy -> Proxy: _real_employee загружен
Proxy -> Proxy: _check_access()

alt role == "manager"
  Proxy -> Employee: get_salary()
  Employee -> Proxy: 80000
  Proxy -> GUI: 80000
else role == "employee"
  Proxy -> GUI: PermissionError!
end
@enduml
