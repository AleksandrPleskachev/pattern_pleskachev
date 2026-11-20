@startuml
class HRMediator {
  +register(dept)
  +notify(sender, event, data)
}

class Department {
  +name
  +staff
  +hire()
  +transfer()
  +announce()
}

HRMediator o--> Department
Department --> HRMediator

class BranchOriginator {
  +save(label) Memento
  +restore(Memento)
}
class Memento {
  -state
  +label
}
class Caretaker {
  +push(Memento)
  +pop() Memento
}
BranchOriginator --> Memento : создаёт
Caretaker o--> Memento
@enduml
