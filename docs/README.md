# Sistema de Gestión Programas de Posgrados

El diseño del sistema se registra en casos de uso y estructura de datos.

## Casos de Uso

Son textos breves que describen la funcionalidad deseada para cada
tipo de usuario. Hay tres categorías generales:

- [Usuarios en la coordinación del posgrado](coordinacion/)
- [Usuarios Académicos](academicos/)
- [Usuarios Estudiantes](estudiantes/)


## Usuarios registrados
- Registra solicitud miscelanea
- solicitar registro al posgrado como profesor
- solicitar registro al posgrado como estudiante

## Usuarios anónimos

Antes de registrarse un usuario es anónimo, sus casos de uso son:

- Registrarse en el sistema. Para registrarse el usuario brinda:
  - nombre de usuario
  - contraseña
  - correo electrónico
  
  El sistema crea el usuario y envía un correo electrónico con un código de activación. De esta manera se verifica el correo   electrónico. El registro podría cubrirse con [este módulo](http://django-registration.readthedocs.io/en/2.2/).

- Leer materiales accesibles en zonas públicas del sistema, como
  reglamentos y anuncios.

