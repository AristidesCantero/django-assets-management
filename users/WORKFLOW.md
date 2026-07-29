# Workflows de la App Users

---

## Registro de usuario

```
UserRegisterAPIView
↓
UserRegisterSerializer
↓
Verifica si el email ya existe y está verificado → rechaza
↓
Si existe pero no está verificado → EmailVerificationToken.refresh_old_token()
↓
Si no existe → User.objects.create_user_unregistered() + AuthProvider + EmailVerificationToken.generate_token()
↓
EmailVerificationService.send_verification()
  ↓ _encode_pk(user)
  ↓ TokenGenerator.send_email() → renderiza email_template.html
  ↓ BaseTokenGenerator.send_email() → send_mail()
↓
Retorna 201 { "message": "Verification email sent" }
```

### Reglas

- No se puede registrar un email que ya esté verificado.
- Si el email existe pero no está verificado, se reenvía el token (sin crear nuevo usuario).
- El usuario se crea con `is_active=True` por defecto, pero `email_verified=False`.
- El token de verificación expira en 24 horas.

---

## Confirmación de registro

```
UserRegisterConfirmationAPIView
↓
Decodifica uid (base64) → obtiene user_id
↓
Obtiene User por pk
↓
Obtiene EmailVerificationToken del usuario
↓
Verifica si el usuario ya está verificado → retorna 208
↓
Hace hash SHA-256 del token recibido
↓
Compara con compare_digest(token_hash, received_hash)
↓
Si coincide → user.email_verified = True, user.save()
↓
Retorna { "message": "Email verified" }
```

### Reglas

- El token se compara usando `compare_digest` (timing-attack safe).
- Si el usuario ya estaba verificado, retorna HTTP 208.
- Si el token no coincide, retorna 400 "Invalid or expired token".

---

## Inicio de sesión

```
CustomizedTokenObtainPairView
↓
CustomTokenObtainPairSerializer
  ↓ Valida credenciales (email/password)
  ↓ Verifica que user.email_verified == True (si no, rechaza)
↓
Genera access_token + refresh_token (JWT)
↓
Setea access_token como cookie HttpOnly, Secure, SameSite=Strict
↓
Setea refresh_token como cookie HttpOnly, Secure, SameSite=Strict
↓
Retorna 200 { "detail": "Tokens generated successfully" }
```

### Reglas

- Solo usuarios con `email_verified=True` pueden iniciar sesión.
- Los tokens nunca se exponen en el body de la respuesta, solo en cookies HttpOnly.
- `secure` se deshabilita en DEBUG (desarrollo local).

---

## Refresco de token

```
CustomizedTokenRefreshView
↓
Lee refresh_token de la cookie
↓
Valida el refresh token con TokenRefreshView estándar
↓
Genera nuevo access_token
↓
Setea nueva cookie access_token
↓
Retorna 200 { "detail": "Token refreshed successfully" }
```

### Reglas

- El refresh token se lee exclusivamente de la cookie `refresh_token`.
- Si no hay cookie, retorna 400.
- Solo se renueva el access_token; el refresh_token permanece igual.

---

## Cierre de sesión

```
CustomizedTokenBlackListLogout
↓
Lee refresh_token de la cookie
↓
TokenBlacklistSerializer → blacklistea el refresh token
↓
Elimina cookies access_token y refresh_token de la respuesta
↓
Retorna 200 { "detail": "Successfully logged out." }
```

### Reglas

- Requiere autenticación (`CookieJWTAuthentication`).
- El refresh token se invalida permanentemente (blacklist).
- Las cookies se limpian en el cliente.

---

## Crear invitación

```
InvitationAPIView (POST)
↓
CookieJWTAuthentication + permissionToInviteUsers
↓
UserInvitationSerializer
  ↓ validate_business → existe Business?
  ↓ validate_receiver → existe User?
  ↓ validate → ya existe Invitation? si está accepted → rechaza
↓
create():
  ↓ Si ya hay invitation previa → Invitation.refresh_old_token() (renueva token)
  ↓ Si no hay invitation → Invitation.generate_token() (crea registro Invitation con token hash SHA-256)
  ↓ BusinessInvitationService.send_invitation()
      ↓ _encode_pk(user) → uid base64
      ↓ _encode_pk(business) → business_uid base64
      ↓ TokenInvitationGenerator.send_email() → renderiza invitation_template.html
      ↓ BaseTokenGenerator.send_email() → send_mail()
↓
Retorna 201 { "message": "Invitation email sent" }
```

### Reglas

- Solo un administrador con permiso `permissionToInviteUsers` puede invitar.
- Si ya existe una invitación aceptada (`is_accepted=True`), se rechaza la solicitud.
- Si existe una invitación no aceptada, se refresca el token en lugar de crear una nueva.
- El usuario invitado debe existir en el sistema.
- El token se almacena como hash SHA-256; el valor crudo se envía por email.

---

## Aceptar invitación

```
InvitationAcceptAPIView (GET)
↓
Lee uid, token, business de query params
↓
InvitationAcceptanceService.accept()
  ↓ 1. Decodifica uid y business_uid (base64)
  ↓ 2. Busca User por pk → si no existe: "user_not_found"
  ↓ 3. Busca Business por pk → si no existe: "business_not_found"
  ↓ 4. Verifica si ya es miembro (BusinessMembership) → "already_member"
  ↓ 5. Busca Invitation por user+business → si no existe: "invitation_not_found"
  ↓ 6. Hash SHA-256 del token crudo y compara con invitation.token → "invalid_token"
  ↓ 7. Obtiene rol "Worker" (GLOBAL scope)
  ↓ 8. Crea BusinessMembership + marca invitation.is_accepted = True
  ↓ (Todo en una transacción atómica)
↓
Mapea resultado a HTTP status y body
↓
Retorna respuesta según estado
```

### Reglas

- Todo el flujo corre dentro de `transaction.atomic`.
- El rol asignado por defecto es "Worker" con scope GLOBAL.
- Si el usuario ya es miembro del negocio, retorna 200 con mensaje "already_member".
- Si el token no coincide (hash), retorna 400 "invalid_token".
- Si el rol "Worker" no existe en el sistema, retorna 500.

---

## Obtener / actualizar / desactivar usuario por empresa

```
UserAPIView (GET/PATCH/DELETE)
↓
CookieJWTAuthentication + permissionsToCheckUser
↓
GET:
  ↓ get_queryset(user_id, business_id) → User.objects.get_user_if_in_business()
  ↓ Si usuario no existe o is_active=False → 404
  ↓ UserSerializer.to_representation() → datos básicos del usuario
  ↓ Retorna 200 { "data": { ... } }

PATCH:
  ↓ get_queryset → mismo lookup
  ↓ UserSerializer (partial=True)
  ↓ serializer.update() → actualiza username y/o password
  ↓ Retorna 200 con datos actualizados

DELETE:
  ↓ get_queryset → mismo lookup
  ↓ user.deactivate() → deleted_at=now, is_active=False
  ↓ Retorna 200 { "message": "User status updated successfully." }
```

### Reglas

- Solo usuarios que pertenecen al negocio pueden ser consultados/modificados.
- Usuarios inactivos (`is_active=False`) se tratan como no encontrados (404).
- El DELETE es soft-delete: `deactivate()`.

---

## Listado de usuarios por empresa

```
UserListAPIView (GET)
↓
CookieJWTAuthentication + permissionsToCheckUsers
↓
Verifica request.business → si no es válido: 404
↓
User.objects.get_business_users(business_id)
  ↓ Obtiene ids de usuarios con BusinessMembership en el negocio
  ↓ Filtra Users activos (is_active=True)
↓
UserSerializer(many=True) → array de datos básicos
↓
Retorna 200 { "data": [...] }
```

### Reglas

- Solo retorna usuarios activos (`is_active=True`).
- El business se obtiene del request (middleware/authentication).
- Requiere permiso `permissionsToCheckUsers`.

---

## Activación / reactivación de usuario

```
UserDeactivatedAPIView (GET/PATCH)
↓
CookieJWTAuthentication + SuperAdminAccess
↓
GET:
  ↓ Busca User por user_id con is_active=False → si no existe: 404
  ↓ UserDeactivatedSerializer → { name, is_active }
  ↓ Retorna 200

PATCH:
  ↓ Mismo lookup
  ↓ user.activate() → deleted_at=None, is_active=True
  ↓ Retorna 200 { "message": "User status updated successfully." }
```

### Reglas

- Solo superadmins (`SuperAdminAccess`) pueden acceder.
- Solo opera sobre usuarios inactivos.
- La activación restaura `is_active=True` y limpia `deleted_at`.

---

## Gestión de grupos

```
GroupListAPIView (GET/POST)
↓
CookieJWTAuthentication + permissionsToCheckGroups
↓
GET:
  ↓ Group.objects.all()
  ↓ GroupListSerializer(many=True)
  ↓ Retorna 200 { "data": [...] }

POST:
  ↓ GroupListSerializer → valida name único + permissions
  ↓ Crea Group + set_group_permissions()
  ↓ Retorna 200

GroupAPIView (GET/PATCH/DELETE)
↓
CookieJWTAuthentication + permissionsToCheckGroups
↓
GET:
  ↓ Group.objects.get(pk=pk)
  ↓ GroupSerializer → { id, name, permissions }
  ↓ Retorna 200

PATCH:
  ↓ Group.objects.get(pk=pk)
  ↓ GroupSerializer (partial)
  ↓ Actualiza name y/o permissions (set_group_permissions)
  ↓ Retorna 200

DELETE:
  ↓ Group.objects.get(pk=pk)
  ↓ group.delete()
  ↓ Retorna 200 con datos del grupo eliminado
```

### Reglas

- Nombre de grupo debe ser único (`UniqueValidator`).
- Los permisos se asignan mediante `set_group_permissions()`.
- Solo usuarios con permiso `permissionsToCheckGroups`.
