#!/usr/bin/env python3
"""
translator.py
Lee un esquema amigable en YAML o JSON y genera validadores JavaScript para Ajv, Zod y Joi.

Dependencias Python:
    pip install pyyaml

Uso:
    python translator.py example_schema.yaml --out out/
"""

import argparse
import json
import os
from typing import Dict, Any, List

try:
    import yaml
except Exception:
    print("Error: necesitas instalar pyyaml -> pip install pyyaml")
    raise

# ====================================================
# Normalización del esquema de entrada a JSON Schema
# ====================================================
def normalize_schema(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte un esquema simple (DSL) a JSON Schema.
    En este ejemplo asumimos que ya se parece bastante a JSON Schema.
    """
    return dict(raw)

# ====================================================
# Generador de código para Ajv
# ====================================================
def generate_ajv_code(json_schema: Dict[str, Any]) -> str:
    schema_str = json.dumps(json_schema, indent=2, ensure_ascii=False)
    return f"""// validator_ajv.js
// Generado automáticamente. Requiere: npm install ajv ajv-formats
const Ajv = require("ajv");
const addFormats = require("ajv-formats");

const ajv = new Ajv({{ allErrors: true }});
addFormats(ajv);

const schema = {schema_str};

const validate = ajv.compile(schema);

function validateData(data) {{
  const valid = validate(data);
  return {{
    valid,
    errors: validate.errors
  }};
}}

module.exports = {{ validateData }};
"""

# ====================================================
# Generador de código para Zod
# ====================================================
def _zod_type_from_prop(prop: Dict[str, Any]) -> str:
    t = prop.get("type", "any")

    if t == "string":
        s = "z.string()"
        if "minLength" in prop:
            s += f".min({prop['minLength']})"
        if "maxLength" in prop:
            s += f".max({prop['maxLength']})"
        if "pattern" in prop:
            s += f'.regex(new RegExp({json.dumps(prop["pattern"])}))'
        if "enum" in prop and all(isinstance(x, str) for x in prop["enum"]):
            s = f"z.enum({json.dumps(prop['enum'])})"
        if prop.get("format") == "email":
            s += ".email()"
        return s

    if t == "integer":
        s = "z.number().int()"
        if "minimum" in prop:
            s += f".min({prop['minimum']})"
        if "maximum" in prop:
            s += f".max({prop['maximum']})"
        return s

    if t == "number":
        s = "z.number()"
        if "minimum" in prop:
            s += f".min({prop['minimum']})"
        if "maximum" in prop:
            s += f".max({prop['maximum']})"
        return s

    if t == "boolean":
        return "z.boolean()"

    if t == "array":
        items = prop.get("items", {"type": "any"})
        return f"z.array({_zod_type_from_prop(items)})"

    if t == "object":
        props = prop.get("properties", {})
        inner = ", ".join([f'{json.dumps(k)}: {_zod_type_from_prop(v)}' for k, v in props.items()])
        return f"z.object({{{inner}}})"

    return "z.any()"

def generate_zod_code(json_schema: Dict[str, Any]) -> str:
    props = json_schema.get("properties", {})
    required = set(json_schema.get("required", []))

    zod_props = []
    for name, prop in props.items():
        ztype = _zod_type_from_prop(prop)
        if name not in required:
            ztype = f"{ztype}.optional()"
        zod_props.append(f'  {name}: {ztype},')

    zod_body = "\n".join(zod_props)

    return f"""// validator_zod.js
// Generado automáticamente. Requiere: npm install zod
import {{ z }} from "zod";

const schema = z.object({{
{zod_body}
}});

function validateData(data) {{
  const result = schema.safeParse(data);
  return {{
    valid: result.success,
    error: result.success ? null : result.error.format()
  }};
}}

export {{ validateData, schema }};
"""

# ====================================================
# Generador de código para Joi
# ====================================================
def _joi_from_prop(prop: Dict[str, Any]) -> str:
    t = prop.get("type", "any")

    if t == "string":
        s = "Joi.string()"
        if "minLength" in prop:
            s += f".min({prop['minLength']})"
        if "maxLength" in prop:
            s += f".max({prop['maxLength']})"
        if "pattern" in prop:
            s += f'.pattern(new RegExp({json.dumps(prop["pattern"])}))'
        if "enum" in prop:
            s += f".valid({', '.join(json.dumps(x) for x in prop['enum'])})"
        if prop.get("format") == "email":
            s += ".email()"
        return s

    if t == "integer":
        s = "Joi.number().integer()"
        if "minimum" in prop:
            s += f".min({prop['minimum']})"
        if "maximum" in prop:
            s += f".max({prop['maximum']})"
        return s

    if t == "number":
        s = "Joi.number()"
        if "minimum" in prop:
            s += f".min({prop['minimum']})"
        if "maximum" in prop:
            s += f".max({prop['maximum']})"
        return s

    if t == "boolean":
        return "Joi.boolean()"

    if t == "array":
        items = prop.get("items", {"type": "any"})
        return f"Joi.array().items({_joi_from_prop(items)})"

    if t == "object":
        props = prop.get("properties", {})
        inner = ", ".join([f'{json.dumps(k)}: {_joi_from_prop(v)}' for k, v in props.items()])
        return f"Joi.object({{{inner}}})"

    return "Joi.any()"

def generate_joi_code(json_schema: Dict[str, Any]) -> str:
    props = json_schema.get("properties", {})
    required = set(json_schema.get("required", []))

    joi_lines = []
    for name, prop in props.items():
        j = _joi_from_prop(prop)
        if name in required:
            j += ".required()"
        else:
            j += ".optional()"
        joi_lines.append(f"  {json.dumps(name)}: {j},")

    joi_body = "\n".join(joi_lines)

    return f"""// validator_joi.js
// Generado automáticamente. Requiere: npm install joi
const Joi = require('joi');

const schema = Joi.object({{
{joi_body}
}});

function validateData(data) {{
  const result = schema.validate(data, {{ abortEarly: false }});
  return {{
    valid: !result.error,
    error: result.error ? result.error.details : null,
    value: result.value
  }};
}}

module.exports = {{ validateData }};
"""

# ====================================================
# Entrada/Salida
# ====================================================
def load_input(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.lower().endswith((".yaml", ".yml")):
        return yaml.safe_load(text)
    return json.loads(text)

def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generado: {path}")

# ====================================================
# Main CLI
# ====================================================
def main():
    parser = argparse.ArgumentParser(description="Traductor de esquemas a validadores JS (Ajv, Zod, Joi).")
    parser.add_argument("input", help="Archivo YAML o JSON con el esquema.")
    parser.add_argument("--out", default="out", help="Directorio de salida.")
    args = parser.parse_args()

    raw = load_input(args.input)
    schema = normalize_schema(raw)

    ensure_outdir(args.out)

    write_file(os.path.join(args.out, "validator_ajv.js"), generate_ajv_code(schema))
    write_file(os.path.join(args.out, "validator_zod.js"), generate_zod_code(schema))
    write_file(os.path.join(args.out, "validator_joi.js"), generate_joi_code(schema))
    write_file(os.path.join(args.out, "schema.json"), json.dumps(schema, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
