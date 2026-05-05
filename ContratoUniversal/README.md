# ContratoUniversal - Generador de Contratos Legales PDF

#### Video Demo:  [URL DE TU VIDEO AQUÍ]

#### Descripción:

## ¿Qué es ContratoUniversal?

ContratoUniversal es una aplicación web completa desarrollada con Flask, SQLite, HTML/CSS/JavaScript que permite a usuarios generar contratos legales profesionales en formato PDF de manera rápida e intuitiva. Esta solución nace de la necesidad de pequeños emprendedores, freelancers y profesionales independientes que requieren formalizar sus servicios sin incurrir en costos de abogados o plantillas genéricas.

La aplicación se ejecuta completamente en el navegador y utiliza el sistema de impresión nativo para generar PDFs, eliminando la dependencia de librerías pesadas de generación de PDF del lado del servidor. Esto hace que la aplicación sea ligera, rápida y fácil de desplegar en cualquier entorno.

## Problema que Resuelve

En México y Latinoamérica, millones de trabajadores independientes realizan servicios diarios sin ningún tipo de contrato formal. Esto genera problemas de:
- Incumplimiento de pagos
- Malentendidos en el alcance del servicio
- Falta de protección legal para ambas partes
- Pérdida de tiempo en redactar documentos desde cero

ContratoUniversal democratiza el acceso a documentos legales profesionales, permitiendo que cualquier persona con acceso a internet pueda crear un contrato válido en menos de 5 minutos.

## Características Principales

### 1. Formulario Intuitivo con UX/UI Moderna
- **Tema oscuro profesional**: Diseñado para reducir la fatiga visual durante sesiones prolongadas
- **Diseño responsive**: Funciona perfectamente en móviles, tablets y computadoras de escritorio
- **Campos condicionales inteligentes**: Los campos se muestran u ocultan dinámicamente según las selecciones del usuario
- **Validación en tiempo real**: Previene errores antes del envío del formulario
- **Upload de logo estilizado**: Área de carga de archivos moderna con vista previa inmediata

### 2. Lógica de Negocio Inteligente
- **Sistema de pagos adaptable**: Soporta pagos únicos, anticipos y pagos parciales
- **Cálculos automáticos**: Calcula automáticamente montos restantes cuando se usa anticipo
- **Cláusulas dinámicas**: El contrato final solo incluye las cláusulas relevantes según las opciones seleccionadas
- **Validaciones condicionales**: Requiere información bancaria solo si se selecciona transferencia, detalles de materiales solo si se incluyen, etc.

### 3. Generación de PDF Profesional
- **Formato A4 estándar**: Márgenes de 2.5cm, tipografía Times New Roman para apariencia legal
- **Estructura jurídica correcta**: Incluye encabezado, partes involucradas, cláusulas numeradas y sección de firmas
- **Personalización completa**: Logo del prestador, datos de contacto, RFCs, direcciones
- **Adaptabilidad contextual**: Omite cláusulas de penalización si el pago es por adelantado, incluye garantía solo si se especifica

### 4. Sistema de Historial
- **Almacenamiento local**: Guarda metadatos de contratos generados en SQLite
- **Gestión completa**: Permite visualizar y eliminar contratos anteriores
- **Búsqueda rápida**: Acceso inmediato a contratos previos

## Arquitectura Técnica

### Backend (Flask + Python)
El backend está construido con Flask, un microframework ligero pero poderoso. Las principales responsabilidades incluyen:

- **Rutas principales**: `/` (formulario), `/generate` (generación PDF), `/history` (historial), `/delete/<id>` (eliminar)
- **Validaciones robustas**: Implementadas en `rules.py`, verifican integridad de datos, formatos y reglas de negocio
- **Base de datos SQLite**: Almacena historial de contratos con tablas normalizadas
- **Manejo de archivos**: Subida segura de logos con validación de tipo y tamaño

### Frontend (HTML5 + CSS3 + JavaScript)
El frontend sigue principios de diseño moderno:

- **Grid/Flexbox**: Para layouts responsivos que se adaptan a cualquier dispositivo
- **Variables CSS**: Facilitan mantenimiento y cambios de tema
- **JavaScript vainilla**: Sin dependencias externas, maneja lógica condicional y validaciones
- **Animaciones CSS**: Transiciones suaves para mejorar experiencia de usuario

### Base de Datos (SQLite)
Esquema simple pero efectivo:
```sql
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name TEXT NOT NULL,
    client_name TEXT NOT NULL,
    service_title TEXT NOT NULL,
    total_amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pdf_filename TEXT,
    logo_filename TEXT
);
```

## Decisiones de Diseño

### ¿Por qué no usar una librería de PDF como ReportLab?
Inicialmente consideré usar ReportLab o WeasyPrint para generación de PDF, pero decidí utilizar el sistema de impresión del navegador por varias razones:

1. **Simplicidad**: Elimina dependencias complejas y problemas de compatibilidad
2. **Calidad**: Los navegadores modernos generan PDFs de excelente calidad
3. **Control del usuario**: El usuario puede ajustar márgenes, orientación y otras opciones antes de guardar
4. **Performance**: No hay procesamiento pesado en el servidor

### ¿Por qué tema oscuro?
El tema oscuro fue elegido porque:
- Reduce fatiga visual en sesiones prolongadas
- Es tendencia actual en diseño de interfaces
- Da apariencia profesional y moderna
- Mejora accesibilidad para usuarios con sensibilidad a la luz

### ¿Por qué SQLite en lugar de PostgreSQL/MySQL?
Para este proyecto, SQLite es ideal porque:
- No requiere configuración de servidor
- Es perfecto para aplicaciones de pequeña a mediana escala
- Facilita el deployment en cualquier entorno
- El overhead de una base de datos cliente-servidor no está justificado para este caso de uso

## Estructura de Archivos

```
/workspace/ContratoUniversal/
├── app.py                 # Aplicación Flask principal con todas las rutas
├── rules.py               # Funciones de validación y manejo de base de datos
├── templates/
│   ├── index.html         # Formulario principal con diseño moderno
│   ├── pdf_template.html  # Plantilla HTML para generación de PDF
│   └── history.html       # Página de historial de contratos
├── static/
│   ├── style.css          # Hoja de estilos con tema oscuro responsive
│   └── script.js          # Lógica JavaScript para interactividad
├── uploads/               # Directorio para logos subidos (creado automáticamente)
├── contracts.db           # Base de datos SQLite (creada automáticamente)
└── README.md              # Este archivo de documentación
```

## Funcionalidades Detalladas

### Validaciones Implementadas
1. **Datos básicos obligatorios**: Nombres (>3 caracteres), teléfono cliente (≥10 dígitos)
2. **Servicio**: Descripción (>10 caracteres), título del servicio
3. **Pagos**: Monto total (>0), fecha límite (futura)
4. **Condicionales**: 
   - Si incluye materiales → requerir detalles
   - Si es transferencia → requerir datos bancarios
   - Si es anticipo → anticipo + resto = total
   - Si incluye firmas → requerir nombres para firmar
5. **Seguridad**: Logo solo .png/.jpg (<2MB), sanitización de inputs contra XSS

### Cláusulas Dinámicas del Contrato
El contrato generado adapta su contenido según las selecciones:

- **Cláusula de Materiales**: Cambia radicalmente si los materiales son incluidos o proporcionados por el cliente
- **Cláusula de Pagos**: Diferente estructura para pago único, anticipo o parcial; incluye datos bancarios si aplica
- **Cláusula de Incumplimiento**: Solo aparece si el pago es posterior al servicio (no tiene sentido penalizar si ya se pagó por adelantado)
- **Cláusula de Confidencialidad**: Opcional según checkbox
- **Sección de Firmas**: Solo si se solicita, con espacio para testigo opcional

## Impacto Potencial

Esta aplicación tiene el potencial de:
- **Formalizar la economía informal**: Permitir que trabajadores independientes operen con mayor seguridad jurídica
- **Educar sobre derechos**: Los usuarios aprenden qué cláusulas son importantes en un contrato
- **Ahorrar tiempo y dinero**: Elimina necesidad de abogados para contratos simples
- **Escalabilidad**: Puede adaptarse a diferentes países con ajustes menores en las cláusulas

## Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal del backend
- **Flask 2.x**: Framework web
- **SQLite3**: Base de datos embebida
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos con variables y flexbox/grid
- **JavaScript ES6**: Lógica del lado del cliente
- **Jinja2**: Motor de plantillas para HTML dinámico

## Cómo Ejecutar el Proyecto

1. Instalar dependencias: `pip install flask`
2. Ejecutar aplicación: `python app.py`
3. Abrir navegador en: `http://127.0.0.1:5000`
4. Completar formulario y generar contrato
5. Usar "Imprimir" del navegador para guardar como PDF

## Futuras Mejoras

- Integración con APIs de geolocalización para llenado automático de ciudad/fecha
- Plantillas predefinidas para diferentes tipos de servicios
- Firma digital integrada
- Envío por email automático
- Multi-idioma (inglés/español)
- Autenticación de usuarios para historial en la nube

## Autor

Desarrollado como proyecto final para CS50x de Harvard University.

---

*Este proyecto demuestra la aplicación práctica de conceptos aprendidos en CS50: desarrollo web full-stack, bases de datos, validación de datos, seguridad básica, diseño UX/UI, y arquitectura de software.*
