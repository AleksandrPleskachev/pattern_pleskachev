@startuml
class EmployeeSubject {
  -observers
  -state
  +attach()
  +notify()
  +change_state()
  +pay()
}
class EmployeeState {
  +pay()
  +handle()
}
class CandidateState
class ProbationState
class ActiveState
class VacationState
class DismissedState
class Observer {
  +update()
}

EmployeeSubject o--> EmployeeState
EmployeeState <|-- CandidateState
EmployeeState <|-- ProbationState
EmployeeState <|-- ActiveState
EmployeeState <|-- VacationState
EmployeeState <|-- DismissedState
EmployeeSubject o--> Observer
@enduml
