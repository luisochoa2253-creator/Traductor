// validator_ajv.js
// Requiere: npm install ajv ajv-formats
const Ajv = require("ajv");
const addFormats = require("ajv-formats");

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

const schema = {
  title: "User",
  type: "object",
  properties: {
    id: { type: "integer", minimum: 1 },
    name: { type: "string", minLength: 1, maxLength: 100 },
    email: { type: "string", format: "email" },
    age: { type: "integer", minimum: 0 },
    role: { type: "string", enum: ["user", "admin", "moderator"] }
  },
  required: ["id", "name", "email"]
};

const validate = ajv.compile(schema);

function validateData(data) {
  const valid = validate(data);
  return {
    valid,
    errors: validate.errors
  };
}

module.exports = { validateData };
