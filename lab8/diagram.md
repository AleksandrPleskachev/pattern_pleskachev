@startuml
class SalaryRequest {
  +employee
  +department
  +amount
  +reason
}

class ApprovalHandler {
  -ApprovalHandler _next
  +title
  +limit
  +set_next(handler)
  +handle(request, log)
}

class ChainApp

ApprovalHandler --> ApprovalHandler : next
ApprovalHandler ..> SalaryRequest : обрабатывает
ChainApp --> ApprovalHandler : запускает цепочку
@enduml

@startuml
participant GUI
participant TeamLead
participant DeptHead
participant HR
participant CEO

GUI -> TeamLead: handle(+80 000)
TeamLead -> DeptHead: сумма > 15 000
DeptHead -> HR: сумма > 50 000
HR -> GUI: одобрено, лимит 120 000
@enduml
