# Importa cada modelo para que possam ser acessados diretamente do pacote 'models'
from .user_model import User, UserRole
from .part_model import Part
from .rnc_model import RNC, RNCStatus, RNCCondition, RNCCriticalLevel

# Opcional: define o que é exportado quando se usa "from app.models import *"
__all__ = [
    "Part",
    "User", "UserRole",
    "RNC", "RNCStatus", "RNCCondition", "RNCCriticalLevel"
]