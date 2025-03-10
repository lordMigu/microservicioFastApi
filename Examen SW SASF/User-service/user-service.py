# user_service
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Protocol
import bcrypt
import jwt

app = FastAPI()
global_database = []

# Modelo de datos para el usuario
class User(BaseModel):
    id: str
    name: str
    email: str
    password: str

# Modelo de datos para las credenciales de login
class Credentials(BaseModel):
    email: str
    password: str

# Interfaz para el UserRepository (ISP)
class IUserRepository(Protocol):
    def save(self, user: dict) -> dict:
        pass

    def find_by_email(self, email: str) -> Optional[dict]:
        pass

# Implementación concreta de UserRepository
class UserRepository(IUserRepository):
    def __init__(self):
        self.database = global_database  # Usar la variable global

    def save(self, user: dict) -> dict:
        self.database.append(user)
        print(f"Usuario guardado: {user}")
        print(f"Base de datos actual: {self.database}")
        return user

    def find_by_email(self, email: str) -> Optional[dict]:
        print(f"Base de datos actual: {self.database}")  # Depuración
        for user in self.database:
            if user["email"] == email:
                print(f"Usuario encontrado: {user}")
                return user
        return None

# UserService: Contiene la lógica de negocio
class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self._observers: List[Observer] = []

    def attach(self, observer: "Observer"):
        self._observers.append(observer)

    def notify(self, event: str):
        for observer in self._observers:
            observer.update(event)

    def register(self, user_data: dict) -> dict:
        # Validar que el correo electrónico no esté registrado
        if self.user_repository.find_by_email(user_data["email"]):
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        # Hashear la contraseña
        user_data["password"] = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt()).decode()
        # Guardar el usuario en la base de datos
        user = self.user_repository.save(user_data)
        # Notificar a los observadores
        self.notify("Usuario Creado")
        return user

    def login(self, credentials: Credentials) -> str:
    # Buscar el usuario por correo electrónico
        user = self.user_repository.find_by_email(credentials.email)
        print(f"Usuario encontrado: {user}")  # Depuración
        if not user:
            print("Usuario no encontrado")  # Depuración
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
        if not bcrypt.checkpw(credentials.password.encode(), user["password"].encode()):
            print("Contraseña incorrecta")  # Depuración
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
        # Generar un token JWT
        token = jwt.encode({"user_id": user["id"]}, "secret_key", algorithm="HS256")
        return token

# Observer: Interfaz para los observadores
class Observer(Protocol):
    def update(self, event: str) -> None:
        pass

# ProductService: Observador concreto
class ProductService(Observer):
    def update(self, event: str):
        if event == "Usuario Creado":
            print("ProductService: Recibido evento 'Usuario Creado'")

# UserController: Maneja las solicitudes HTTP
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def register_user(self, user_data: dict):
        try:
            user = self.user_service.register(user_data)
            return {"status": "success", "data": user}
        except HTTPException as e:
            return {"status": "error", "message": e.detail}

    def login_user(self, credentials: Credentials):
        try:
            token = self.user_service.login(credentials)
            return {"status": "success", "token": token}
        except HTTPException as e:
            return {"status": "error", "message": e.detail}

# Configuración de dependencias
def get_user_repository():
    return UserRepository()

def get_user_service(user_repository: IUserRepository = Depends(get_user_repository)):
    return UserService(user_repository)

def get_user_controller(user_service: UserService = Depends(get_user_service)):
    return UserController(user_service)

# Endpoints de FastAPI
@app.post("/register")
async def register(user: User, user_controller: UserController = Depends(get_user_controller)):
    return user_controller.register_user(user.dict())

@app.post("/login")
async def login(credentials: Credentials, user_controller: UserController = Depends(get_user_controller)):
    return user_controller.login_user(credentials)