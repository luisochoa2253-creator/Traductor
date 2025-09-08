// validator_zod.js
// Generado automáticamente. Requiere: npm install zod
import { z } from "zod";

const schema = z.object({
  id: z.number().int().min(1),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).optional(),
  role: z.enum(["user", "admin", "moderator"]).optional(),
});

function validateData(data) {
  const result = schema.safeParse(data);
  return {
    valid: result.success,
    error: result.success ? null : result.error.format()
  };
}

export { validateData, schema };
