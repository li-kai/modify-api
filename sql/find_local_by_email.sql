SELECT users.id, users.email, users.password
FROM users
WHERE users.email = ${email}
