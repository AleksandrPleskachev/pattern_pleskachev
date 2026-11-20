@startuml
class Employee {
  +emp_id
  +name
  +department
  +salary
}
class JsonEmployeeRepository {
  +add()
  +update()
  +delete()
  +get_all()
}
class UnitOfWork {
  +new
  +dirty
  +removed
  +register_new()
  +register_dirty()
  +register_removed()
  +commit()
  +rollback()
}
UnitOfWork --> JsonEmployeeRepository
JsonEmployeeRepository o--> Employee
@enduml
