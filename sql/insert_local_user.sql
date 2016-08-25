INSERT INTO users (email, password)
VALUES (${email}, ${password})
RETURNING id;
