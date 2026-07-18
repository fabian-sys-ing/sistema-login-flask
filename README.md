# Sistema de Login con Flask

Sistema web completo con autenticación de usuarios, gestión de perfiles y panel de administración. Desarrollado con Python, Flask y SQLite.

##  Características

### Autenticación
- ✅ Registro de usuarios con validación
- ✅ Login seguro con contraseñas encriptadas (bcrypt)
- ✅ Cierre de sesión
- ✅ Rutas protegidas con @login_required

### Gestión de Perfil
- ✅ Ver información del usuario
- ✅ Editar nombre de usuario
- ✅ Cambiar contraseña con validaciones
- ✅ Subir foto de perfil (PNG, JPG, GIF)

### Tracking y Actividad
- ✅ Fecha de registro automática
- ✅ Registro del último login
- ✅ Panel de administración con lista de usuarios

### Seguridad
- ✅ Contraseñas encriptadas con Werkzeug
- ✅ Validación de archivos de imagen
- ✅ Protección contra usuarios duplicados
- ✅ Límite de tamaño de archivo (5MB)

##  Capturas de Pantalla

### Página de Inicio
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura1.png

### Registro de Usuario
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura2.png

### Login
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura3.png

### Panel Privado
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura4.png

### Perfil de Usuario
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura5.png

### Panel de Administración
https://raw.githubusercontent.com/fabian-sys-ing/sistema-login-flask/main/captura6.png

##  Tecnologías Utilizadas

- *Backend:* Python 3 con Flask
- *Autenticación:* Flask-Login
- *Seguridad:* Werkzeug (hashing de contraseñas)
- *Base de Datos:* SQLite
- *Frontend:* HTML5, CSS3 (diseño responsive con gradientes)
- *Manejo de Archivos:* werkzeug.utils

##  Instalación y Ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/fabian-sys-ing/sistema-login-flask.git
   cd sistema-login-flask
