@startuml
skinparam class {
  BackgroundColor White
  BorderColor Black
  ArrowColor Black
}

class Employee {
  +String name
  +String department
  +String position
  +int salary
  +String emp_type
  +matches(other) bool
}

class EmployeeBuilder {
  -String _name
  -String _department
  -String _position
  -int _salary
  -String _emp_type
  +name(value) EmployeeBuilder
  +department(value) EmployeeBuilder
  +position(value) EmployeeBuilder
  +salary(value) EmployeeBuilder
  +emp_type(value) EmployeeBuilder
  +build() Employee
}

class GUI {
  +_create_layout()
  +_build()
  +_log(text)
}

EmployeeBuilder --> Employee : builds
GUI --> EmployeeBuilder : uses
@enduml

@startuml
actor User
participant "GUI" as GUI
participant "Builder" as Builder
participant "Employee" as Employee

User -> GUI: Заполняет форму
GUI -> Builder: builder.name("Иванов")
Builder -> Builder: _name = "Иванов"
GUI -> Builder: builder.department("IT")
Builder -> Builder: _department = "IT"
GUI -> Builder: builder.salary(80000)
Builder -> Builder: _salary = 80000
GUI -> Builder: builder.build()
Builder -> Employee: new Employee(...)
Builder -> GUI: Employee
GUI -> User: Сотрудник создан
@enduml
