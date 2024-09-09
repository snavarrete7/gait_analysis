from dataclasses import dataclass

@dataclass
class Patient:
    userID: str = ""
    email: str = ""
    firstname: str = ""
    lastname: str = ""
    age: float = 0
    phone: str = ""
    address: str = ""
    note: str = ""
    sizeOfInsole: float = 0
    ampelOnPhone: bool = False