@startuml
class EmployeeModel {
  +add()
  +remove()
  +by_department()
  +payroll()
}
class EmployeeView {
  +on_add
  +on_remove
  +on_filter
  +show_rows()
  +show_total()
}
class EmployeeController {
  +add_employee()
  +remove_employee()
  +apply_filter()
}
EmployeeController --> EmployeeModel
EmployeeController --> EmployeeView
EmployeeView ..> EmployeeController : колбэки
@enduml
