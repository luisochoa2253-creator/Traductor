// validator_joi.js
// Generado automáticamente. Requiere: npm install joi
const Joi = require('joi');

const schema = Joi.object({
  "id": Joi.number().integer().min(1).required(),
  "name": Joi.string().min(1).max(100).required(),
  "email": Joi.string().email().required(),
  "age": Joi.number().integer().min(0).optional(),
  "role": Joi.string().valid("user", "admin", "moderator").optional(),
});

function validateData(data) {
  const result = schema.validate(data, { abortEarly: false });
  return {
    valid: !result.error,
    error: result.error ? result.error.details : null,
    value: result.value
  };
}

module.exports = { validateData };
