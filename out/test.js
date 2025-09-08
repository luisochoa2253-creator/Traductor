// test.js
const { validateData } = require("./validator_ajv.js");

const goodData = {
  id: 1,
  name: "Luis",
  email: "luis@example.com",
  age: 25,
  role: "admin"
};

const badData = {
  id: 0,  // ❌ debe ser >= 1
  name: "",
  email: "no-es-email",
  role: "superuser" // ❌ no permitido
};

console.log("✅ Probando goodData:");
let result = validateData(goodData);
console.log(result.valid ? "Válido" : result.errors);

console.log("\n❌ Probando badData:");
result = validateData(badData);
console.log(result.valid ? "Válido" : result.errors);
