# Users App

`users` handles authentication-related application logic: user registration endpoint and JWT docs wrappers used for Swagger grouping.

## Responsibilities

- Custom user model definition
- Registration serializer + API view
- Auth route wiring under `/api/auth/`
- Swagger tagging wrappers for JWT endpoints

## Key Files

- `users/models.py`: `CustomUser`
- `users/serializers.py`: `RegisterSerializer`
- `users/views.py`: `RegisterView`
- `users/docs_auth_views.py`: token obtain/refresh/verify docs wrappers
- `users/urls.py`: register + token endpoints

## API Notes

- Register: `POST /api/auth/register/`
- Token obtain: `POST /api/auth/token/`
- Token refresh: `POST /api/auth/token/refresh/`
- Token verify: `POST /api/auth/token/verify/`

## Development Notes

- Keep endpoint names stable (`token_obtain_pair`, `token_refresh`, `token_verify`) because tests and reverse lookups depend on them.
- Keep auth endpoints mounted from `users/urls.py` to avoid root-url shadowing issues.
