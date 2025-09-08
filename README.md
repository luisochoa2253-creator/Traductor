# 📌 Translator: Generador de validadores JavaScript desde esquemas YAML/JSON

Este proyecto busca **automatizar la creación de validadores de datos** en JavaScript/Node.js a partir de un único esquema definido en **YAML o JSON**.  
El objetivo es que con una sola definición de esquema, el sistema genere automáticamente validadores equivalentes en distintas librerías populares:

- [Ajv](https://ajv.js.org/) (basado en JSON Schema)
- [Zod](https://zod.dev/) (TypeScript-first, validación declarativa)
- [Joi](https://joi.dev/) (validación robusta y flexible)

De esta forma, el desarrollador puede **definir el esquema una sola vez** y obtener implementaciones listas para usar en distintos ecosistemas o proyectos.

---

## 🚀 Objetivos del trabajo

- **Unificar** la definición de validación en un solo esquema sencillo (YAML/JSON).  
- **Generar automáticamente** validadores en diferentes librerías de JavaScript.  
- **Asegurar consistencia**: todas las librerías validan con las mismas reglas.  
- **Facilitar pruebas y prototipos**: puedes comparar cómo se comporta Ajv vs Zod vs Joi frente a los mismos datos.  
- **Aumentar la productividad**: evitar reescribir las mismas reglas varias veces.

---
