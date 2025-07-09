# Logout Issue Fix Update

## Problem
Users were still being automatically logged out when performing certain actions in the application. This was occurring because some API endpoints were still requiring superuser privileges, causing 403 errors that triggered the global error handler to log users out.

## Root Cause
After investigating, we identified several key API endpoints that were still requiring superuser privileges:

1. `GET /tenants/` - Used by multiple components including AddUser, EditUser
2. `GET /users/` - Used in admin components for listing users
3. `PATCH /users/{user_id}` - Used when updating user information
4. `DELETE /users/{user_id}` - Used when deleting users
5. `POST /users/` - Used when creating new users

These endpoints were being called during normal user interactions, and when non-superusers attempted to access them, they received 403 errors that triggered the automatic logout.

## Solution
We modified all these endpoints to:

1. Remove the superuser dependency requirement
2. Add tenant isolation to ensure users can only see and modify data from their own tenant
3. Maintain the same response format and functionality
4. Add proper permission checks to ensure security

### Changes Made:

#### 1. Tenants Endpoint (`backend/app/api/routes/tenants.py`)
- Removed `dependencies=[Depends(get_current_active_superuser)]`
- Added `current_user: CurrentUser` parameter
- Added tenant filtering for non-superusers: `if not current_user.is_superuser: statement = statement.where(col(Tenant.id) == current_user.tenant_id)`
- Applied the same filtering to the count query

#### 2. Users Endpoints (`backend/app/api/routes/users.py`)
- For `GET /users/`:
  - Removed superuser dependency
  - Added tenant filtering for non-superusers
  - Applied the same filtering to the count query

- For `PATCH /users/{user_id}`:
  - Removed superuser dependency
  - Added permission check to ensure users can only update users in their own tenant
  - Added check to prevent non-superusers from changing tenant_id

- For `DELETE /users/{user_id}`:
  - Removed superuser dependency
  - Added permission check to ensure users can only delete users in their own tenant
  - Updated error message for self-deletion attempts

- For `POST /users/`:
  - Removed superuser dependency
  - Added permission check to ensure users can only create users in their own tenant
  - Kept the functionality to default to the current user's tenant_id if not specified

## Security Considerations
- The changes maintain proper data isolation - users can only see and modify data from their own tenant
- Superusers retain the ability to see and modify all data across tenants
- No additional permissions were granted beyond what users should have access to
- All permission checks are performed server-side to ensure security

## Testing
To verify the fix:
1. Login as a non-superuser
2. Navigate to pages that use these endpoints
3. Perform actions that would previously cause logout (create, update, delete users)
4. Confirm that the user remains logged in and can continue using the application

## Additional Notes
- The global error handler in `main.tsx` was also updated with better logging to help diagnose similar issues in the future
- These changes complement the previous fixes for the audit log endpoints 