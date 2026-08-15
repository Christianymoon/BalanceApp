# Balance

Aplicación de finanzas personales construida con **Flet (Python)**. Tema oscuro, diseño moderno e intuitivo.

## Características

- **Panel principal** — Vista general de tu balance, liquidez e ingresos/gastos
- **Transacciones** — Registra ingresos y gastos con categorías personalizables
- **Activos** — Gestiona acciones, bonos, cripto, bienes raíces y más
- **Pasivos** — Controla deudas con estado de pago visual
- **Préstamos** — Registra préstamos realizados y recibidos
- **Transferencias** — Movimientos entre cuentas propias
- **Asistente IA** — Chat financiero Kara AI
- **Gráficas** — Visualización de tu patrimonio con matplotlib


## Instalación

**Requisitos:** Python 3.9+

```bash
git clone <repository-url>
cd financeapp
```

Instala dependencias con **uv** (recomendado):
```bash
uv sync
```

O con pip:
```bash
pip install .
```

Ejecuta la app:
```bash
cd src
flet run
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_api_key_aquí
```

## Estructura del Proyecto

```
financeapp/
├── src/
│   ├── main.py                # Punto de entrada
│   ├── router.py              # Enrutamiento de vistas
│   ├── setup.py               # Configuración inicial
│   ├── views/                 # Vistas (UI)
│   ├── controllers/           # Lógica de negocio
│   ├── components/            # Componentes reutilizables
│   ├── db/                    # Base de datos y migraciones
│   ├── dto/                   # Objetos de transferencia de datos
│   ├── client/                # Cliente HTTP
│   ├── external/              # Integraciones externas (Gemini)
│   ├── core/                  # Configuración central
│   ├── themes/                # Temas y estilos
│   ├── assets/                # Recursos (imágenes, fuentes)
│   └── storage/               # Almacenamiento local
├── pyproject.toml
└── README.md
```

## Tech Stack

| Tecnología | Uso |
|---|---|
| **Flet 0.28.3** | Framework UI |
| **SQLite** | Base de datos local |
| **Matplotlib** | Gráficas |
| **Gemini AI** | Asistente financiero |
| **HTTPX** | Cliente HTTP |

## Compilación Móvil

```bash
flet build apk   # Android
flet build ipa   # iOS
```

## Licencia

Copyright (C) 2025 por Christianymoon Ltd.

## Autor

**Christian Vergara** — imchrisyt15@gmail.com

---

*Balance — Tu compañero de finanzas personales* ✨
