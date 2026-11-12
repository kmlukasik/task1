# Zadanie 1 – Domain-Driven Design (Bezpieczna Aplikacja Bankowa)

## Opis zadania
Celem zadania jest zamodelowanie wybranego fragmentu bezpiecznej aplikacji bankowej (procesu inicjowania, autoryzacji i realizacji przelewu wychodzącego) zgodnie z zasadami Domain-Driven Desgji. System podzielono na trzy konteksty ograniczone, pomiędzy którymi granice pełnią rolę granic zaufania i minimalizacji danych.

---

## 1. Bounded Contexts (Konteksty Ograniczone)

1. **Przelewy (*Core Domain*)**  
   Odpowiada za cykl życia dyspozycji przelewu (maszynę stanów), pilnowanie niezmienników operacji oraz wymuszenie autoryzacji przed realizacją. Nie przechowuje danych osobowych klienta (zasada minimalizacji danych).
2. **Zarządzanie Kontem (*Supporting Domain*)**  
   Przechowuje dane rachunku, saldo, limit dzienny oraz tożsamość właśc.iciela konta Odpowiada za bezpieczne sprawdzenie limitów i pobranie środków z konta w jednejnie środków.
3. **Uwierzytelnienie (*Generic/Supporting Domain*)**  
   Odpowiada za weryfikację tożsamości użytkownika (2FA/MFA). Na styku z kontekstem *Pewy* działa **warstwa antypcyjna (ACL)**, która tłumaczy i waliduje zewnętrzne poświadczenie na zaufany obiekt domenowy `Potwierdzenie2FA`.

---

## 2. Diagram modelu domenowego

![Model DDD - Przelew Bankowy](./model-ddd.png)



## 3. Przyjęte założenia, formaty danych i niezmienniki

| Element | Typ DDD | Atrybuty i akceptowane formaty | Niezmienniki (reguły bezpieczeństwa) i integracja między kontekstami |
| :--- | :--- | :--- | :--- |
| **`KontoBankowe`** | **Agregat** *(Aggregate Root)* | `id` (`KontoId` – UUIDv4), `klientId` (`KlientId` – UUIDv4), `numerRachunku` (`NumerIBAN`), `saldoDostepne` (`Kwota`), `limitDzienny` (`Kwota`), `status` (`AKTYWNE` / `ZABLOKOWANE`) | Odwołuje się do klienta tylko przez `KlientId`. Nie ma setterów – saldo zmienia się wyłącznie przez metodę `obciaz(kwota)`. Operacja uda się tylko, gdy konto jest `AKTYWNE`, saldo wystarcza, a kwota nie przekracza limitu dziennego. |
| **`Przelew`** | **Agregat** *(Aggregate Root)* | `id` (`PrzelewId` – UUIDv4), `kontoNadawcyId` (`KontoId`), `rachunekOdbiorcy` (`NumerIBAN`), `kwota` (`Kwota`), `status` (`UTWORZONY`, `ZAUTORYZOWANY`, `ZŁączy się z kontem nadawcy wyłącznie przez `KontoId`. Wymusza kolejność kroków: nie da się zrealizować przelewu bez wcześniejszej autoryzacji 2FA (dla tego konkretnego `PrzelewId`) oraz potwierdzenia pobrania środków z kontekstu Zarządzanie Kontem.ntekstu *Zarządzanie Kontem*. |
| **`Klient`** | **Encja / Agregat** *(Entity)* | `id` (`KlientId` – UUIDv4), `daneOsobowe` (`ImieNazwisko`, 2–100 znaków), `Osobny agregat – edycja danych klienta nie blokuje operacji na koncie. Dane klienta nie wychodzą poza kontekst Zarządzanie Kontem. żliwość wykonywania przelewów. |
| **`NumerIBAN`** | **Obiekt Wartości** *(Domain Primitive)* | `wartosc` (String: `PL` + 2Niezmienny po utworzeniu. Przy tworzeniu sprawdza długość, dozwolone znaki, format oraz sumę kontrolną. Rachunek odbiorcy nie może być taki sam jak rachunek nadawcy. taki sam jak rachunek nadawcy. |
| **`Kwota`** | **Obiekt Wartości** *(Domain Primitive)* | `wartosc` (`Decimal`, max 2 miejsca po przecinku), `Niezmienny. Odrzuca kwoty mniejsze lub równe `0.00`, dzięki czemu nie da się zrobić przelewu na ujemną kwotę. Waluta przelewu musi zgadzać się z walutą konta.musi zgadzać się z walutą konta. |
| **`Potwierdzenie2FA`** | **Obiekt Wartości** *(Domain Primitive)* | `przelewId` (`PrzelewId`), `idSesjiAutoryzacji` (32 znaki hex),Powstaje na granicy kontekstów Uwierzytelnienie i Przelewy (przez ACL) dopiero po sprawdzeniu ważności i podpisu autoryzacji. Przypisanie do `przelewId` blokuje ponowne użycie tego samego kodu 2FA do innego przelewu.mego kodu 2FA do innego przelewu. |