import time
from omoide_cache.examples.example_active_users.user_service import UserService

service = UserService()

# Simulate several consecutive calls
print(service.get_active_users())
print(service.get_active_users())
print(service.get_active_users())

# Break 1
time.sleep(7)
print('After break #1 (must show same users)')
print(service.get_active_users())
print(service.get_active_users())
print(service.get_active_users())

# Break 2
time.sleep(8)
print('After break #2 (must be refreshed)')
print(service.get_active_users())
print(service.get_active_users())
print(service.get_active_users())

exit(-1)