# Importa cada modelo para que possam ser acessados diretamente do pacote 'models'
from .user_model import User
from .part_model import Part
from .machine_model import Machine
from .rnc_observation_model import RNC_Observation
from .rnc_defect_model import RNC_Defect
from .rnc_model import RNC

# Opcional: define o que é exportado quando se usa "from app.models import *"
__all__ = [
    "Part",
    "Machine",
    "User",
    "RNC_Defect",
    "RNC_Observation",
    "RNC",
]