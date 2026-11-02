# Лабораторная работа 5: Паттерны Фасад + Приспособленец

## Предметная область
**Филиалы и сотрудники** — упрощение расчётов и экономия памяти.

## Паттерн 1: Фасад (Facade)

### Назначение
Предоставляет упрощённый интерфейс к сложной подсистеме.

### Проблема
Расчёт зарплаты требует множества вычислений:
```python
# Без фасада — клиент знает всё
tax = TaxCalculator()
income_tax = tax.calculate_income_tax(base)
social_tax = tax.calculate_social_tax(base)
bonus = BonusCalculator()
bonus_amount = bonus.calculate_bonus(base, 10)
deduction = DeductionCalculator()
ded = deduction.calculate_deductions(base, True)
total = base + bonus_amount - income_tax - social_tax - ded
```

### Решение
Один метод фасада — полный расчёт:
```python
result = facade.calculate_payroll(base, bonus_percent, has_children)
# Внутри: НДФЛ 13%, страховые 30%, вычеты 4%
```

### Участники
| Участник | Роль | В коде |
|---|---|---|
| Facade | Упрощённый интерфейс | `PayrollFacade.calculate_payroll()` |
| Subsystem | Сложная подсистема | `TaxCalculator`, `BonusCalculator`, `DeductionCalculator` |

### Что видно в GUI
- **Справа:** вводишь зарплату → нажимаешь «Рассчитать» → видишь полный расчёт и сравнение «без фасада» vs «с фасадом»

## Паттерн 2: Приспособленец (Flyweight)

### Назначение
Экономит память, разделяя общие данные между объектами.

### Проблема
1000 сотрудников с 5 отделами. Если каждый сотрудник хранит копию отдела — 1000 копий одних и тех же данных.

### Решение
Отделы создаются один раз и разделяются:
```python
# Первый раз — создаётся
dept1 = DepartmentFactory.get_department("IT", 1000000, "Директор")
# Остальные 999 раз — возвращается из кеша
dept2 = DepartmentFactory.get_department("IT", 1000000, "Директор")
# dept1 is dept2 -> True
```

### Участники
| Участник | Роль | В коде |
|---|---|---|
| Flyweight | Легковесный объект | `DepartmentFlyweight` — общие данные |
| FlyweightFactory | Фабрика легковесных | `DepartmentFactory._departments` — кеш |
| Client | Использует | `get_department()` — получает из кеша или создаёт |

### Как запустить
```bash
python lab5/main.py
```

### Что видно в GUI
- **Приспособленец (слева):** добавляешь сотрудников → в логе видно `[CREATE]` и `[REUSE]` → статистика отделов
- **Фасад (справа):** расчёт зарплаты одним методом vs 5+ вызовов
